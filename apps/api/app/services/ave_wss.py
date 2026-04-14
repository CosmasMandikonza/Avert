from __future__ import annotations

import asyncio
import contextlib
from copy import deepcopy
import json
import logging
from datetime import UTC, datetime
from threading import Lock
from typing import Any

import websockets

from app.config import Settings, get_settings
from app.database import SessionLocal


logger = logging.getLogger(__name__)


def _iso_now() -> str:
    return datetime.now(UTC).isoformat()


def _normalize_token_id(token_id: str) -> str:
    if "-" not in token_id:
        return token_id.strip()
    address, chain = token_id.rsplit("-", 1)
    normalized_address = address.lower() if address.startswith("0x") else address
    return f"{normalized_address}-{chain.lower()}"


def _coerce_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "").replace("$", "")
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _extract_token_id(payload: dict[str, Any]) -> str | None:
    candidate_id = payload.get("id")
    if isinstance(candidate_id, str) and "-" in candidate_id:
        return candidate_id

    token = payload.get("token") or payload.get("address")
    chain = payload.get("chain")
    if isinstance(token, str) and isinstance(chain, str) and token.strip() and chain.strip():
        return f"{token.strip()}-{chain.strip()}"
    return None


def _extract_price_usd(payload: dict[str, Any]) -> float | None:
    for key in (
        "price_usd",
        "priceUsd",
        "usd",
        "current_price_usd",
        "currentPriceUsd",
        "price",
        "close",
    ):
        price = _coerce_float(payload.get(key))
        if price is not None:
            return price
    return None


def _extract_price_events(payload: Any) -> list[tuple[str, float]]:
    events: list[tuple[str, float]] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            token_id = _extract_token_id(node)
            price = _extract_price_usd(node)
            if token_id and price is not None:
                events.append((token_id, price))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(payload)
    return events


class AVEPriceWSSMonitor:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()
        self._prices: dict[str, dict[str, Any]] = {}
        self._subscriptions: set[str] = set()
        self._lock = Lock()
        self._message_id = 0
        self._last_target_tokens: list[str] = []

    async def start(self) -> None:
        if self.settings.app_mode != "LIVE_MODE":
            logger.info("AVE WSS monitor skipped because app is not in LIVE_MODE.")
            return
        if not self.settings.ave_api_key:
            logger.info("AVE WSS monitor skipped because AVE_API_KEY is missing.")
            return
        if self._task and not self._task.done():
            return
        self._stop_event = asyncio.Event()
        self._task = asyncio.create_task(self._run(), name="avert-ave-wss")

    async def stop(self) -> None:
        self._stop_event.set()
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None

    def get_prices(self) -> dict[str, dict[str, Any]]:
        with self._lock:
            return json.loads(json.dumps(self._prices))

    def get_price_for_token(self, token_id: str) -> float | None:
        normalized = _normalize_token_id(token_id)
        with self._lock:
            record = self._prices.get(normalized)
            return _coerce_float(record.get("price_usd")) if record else None

    async def _run(self) -> None:
        reconnect_delay = max(self.settings.ave_wss_reconnect_seconds, 5)
        while not self._stop_event.is_set():
            try:
                targets = await asyncio.to_thread(self._resolve_target_tokens)
                if not targets:
                    await asyncio.sleep(min(self.settings.ave_wss_subscription_refresh_seconds, 15))
                    continue
                async with websockets.connect(
                    self.settings.ave_wss_base_url,
                    additional_headers={"X-API-KEY": self.settings.ave_api_key},
                    ping_interval=None,
                    open_timeout=self.settings.ave_wss_open_timeout_seconds,
                    close_timeout=10,
                ) as ws:
                    self._subscriptions = set()
                    await self._subscribe(ws, targets)
                    heartbeat_task = asyncio.create_task(self._heartbeat(ws))
                    refresh_task = asyncio.create_task(self._refresh_subscriptions(ws))
                    try:
                        while not self._stop_event.is_set():
                            message = await ws.recv()
                            self._ingest_message(message)
                    finally:
                        heartbeat_task.cancel()
                        refresh_task.cancel()
                        with contextlib.suppress(asyncio.CancelledError):
                            await heartbeat_task
                        with contextlib.suppress(asyncio.CancelledError):
                            await refresh_task
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.warning("AVE WSS monitor disconnected or failed: %s", exc)
                if self._stop_event.is_set():
                    break
                await asyncio.sleep(reconnect_delay)

    async def _heartbeat(self, ws: websockets.ClientConnection) -> None:
        while not self._stop_event.is_set():
            await asyncio.sleep(self.settings.ave_wss_heartbeat_seconds)
            try:
                await ws.send(json.dumps({"action": "ping"}))
                pong_waiter = await ws.ping()
                await asyncio.wait_for(pong_waiter, timeout=10)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.warning("AVE WSS heartbeat failed: %s", exc)
                break

    async def _refresh_subscriptions(self, ws: websockets.ClientConnection) -> None:
        while not self._stop_event.is_set():
            await asyncio.sleep(self.settings.ave_wss_subscription_refresh_seconds)
            try:
                targets = await asyncio.to_thread(self._resolve_target_tokens)
                normalized_targets = {_normalize_token_id(token_id) for token_id in targets}
                if normalized_targets == self._subscriptions:
                    continue
                if self._subscriptions and normalized_targets != self._subscriptions:
                    await self._send(ws, {"jsonrpc": "2.0", "method": "unsubscribe", "params": [], "id": self._next_message_id()})
                    self._subscriptions = set()
                if targets:
                    await self._subscribe(ws, targets)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.warning("AVE WSS subscription refresh failed: %s", exc)

    async def _subscribe(self, ws: websockets.ClientConnection, token_ids: list[str]) -> None:
        if not token_ids:
            return
        await self._send(
            ws,
            {
                "jsonrpc": "2.0",
                "method": "subscribe",
                "params": ["price", token_ids],
                "id": self._next_message_id(),
            },
        )
        self._subscriptions = {_normalize_token_id(token_id) for token_id in token_ids}
        logger.info("AVE WSS subscribed to %s price streams.", len(token_ids))

    async def _send(self, ws: websockets.ClientConnection, payload: dict[str, Any]) -> None:
        await ws.send(json.dumps(payload))

    def _next_message_id(self) -> int:
        self._message_id += 1
        return self._message_id

    def _resolve_target_tokens(self) -> list[str]:
        from app.services.repository import _LIVE_BASE_SNAPSHOT_CACHE, _LIVE_BASE_SNAPSHOT_LOCK, SnapshotRepository

        snapshot = None
        with _LIVE_BASE_SNAPSHOT_LOCK:
            cached_snapshot = _LIVE_BASE_SNAPSHOT_CACHE.get("snapshot")
            if cached_snapshot is not None:
                snapshot = deepcopy(cached_snapshot)

        if snapshot is None:
            if self._last_target_tokens:
                return list(self._last_target_tokens)
            return []

        try:
            if not snapshot.get("narratives") or not snapshot.get("candidates"):
                with SessionLocal() as db:
                    snapshot = SnapshotRepository(db).get_snapshot()
        except Exception as exc:
            if self._last_target_tokens:
                logger.warning(
                    "AVE WSS target resolution failed; reusing last subscription set: %s",
                    exc,
                )
                return list(self._last_target_tokens)
            return []

        narratives = [
            narrative
            for narrative in snapshot["narratives"]
            if narrative.get("state") != "invalidated"
            and narrative.get("stage_bias") not in {"EXIT", "COOLDOWN"}
        ]
        if not narratives:
            narratives = snapshot["narratives"]

        tokens: list[str] = []
        for narrative in narratives:
            candidates = [
                candidate
                for candidate in snapshot["candidates"]
                if candidate["narrative_id"] == narrative["id"]
            ]
            if not candidates:
                continue
            top_candidate = max(candidates, key=lambda item: item.get("investability_score", 0))
            token_id = top_candidate.get("id")
            if isinstance(token_id, str) and "-" in token_id:
                tokens.append(token_id)

        seen: set[str] = set()
        ordered_unique: list[str] = []
        for token_id in tokens:
            normalized = _normalize_token_id(token_id)
            if normalized in seen:
                continue
            seen.add(normalized)
            ordered_unique.append(token_id)
        self._last_target_tokens = list(ordered_unique)
        return ordered_unique

    def _ingest_message(self, message: str | bytes) -> None:
        raw = message.decode("utf-8") if isinstance(message, bytes) else message
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return

        events = _extract_price_events(payload)
        if not events:
            return

        now = _iso_now()
        with self._lock:
            for token_id, price in events:
                normalized = _normalize_token_id(token_id)
                self._prices[normalized] = {
                    "token_id": token_id,
                    "price_usd": price,
                    "updated_at": now,
                }


def get_ave_wss_monitor() -> AVEPriceWSSMonitor:
    global _AVE_WSS_MONITOR
    try:
        return _AVE_WSS_MONITOR
    except NameError:
        _AVE_WSS_MONITOR = AVEPriceWSSMonitor()
        return _AVE_WSS_MONITOR
