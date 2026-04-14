from __future__ import annotations

import json
import math
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import fmean
from typing import Any

import httpx
from pydantic import ValidationError

from app.config import get_settings
from app.demo_seed import build_default_budget, clamp, get_demo_contract_risk, get_demo_topic_ranks, get_demo_topic_tokens, load_raw_demo
from app.services.ave_contracts import (
    AVEContractError,
    AVEContractRiskPayload,
    AVEEnvelope,
    AVEHolderPayload,
    AVEKlinePayload,
    AVEPublicSignalPayload,
    AVERankedTokenPayload,
    AVESupportedChainPayload,
    AVESmartWalletPayload,
    AVETokenDetailPayload,
    AVETopicPayload,
    AVETrendingTokensPayload,
    NormalizedAVENarrativeInput,
    NormalizedAVETokenInput,
)


class AVEUnavailableError(Exception):
    """Raised when live AVE data cannot be fetched or trusted."""


_SUPPORTED_CHAINS_CACHE: list[str] | None = None


def _log_metric(value: float | int | None) -> float:
    if value is None:
        return 0.0
    return math.log10(max(float(value), 1.0))


def _safe_float(value: float | int | None) -> float:
    return float(value) if value is not None else 0.0


def _kline_trend(points: list[Any]) -> str:
    if not points:
        return "flat"
    first = points[0]
    last = points[-1]
    open_price = _safe_float(getattr(first, "open", None))
    close_price = _safe_float(getattr(last, "close", None))
    if open_price <= 0 or close_price <= 0:
        return "flat"
    change_ratio = (close_price - open_price) / max(open_price, 1e-9)
    if abs(change_ratio) <= 0.01:
        return "flat"
    return "up" if change_ratio > 0 else "down"


def _scale_map(raw_values: dict[str, float]) -> dict[str, int]:
    if not raw_values:
        return {}
    values = list(raw_values.values())
    minimum = min(values)
    maximum = max(values)
    if math.isclose(minimum, maximum):
        if math.isclose(maximum, 0.0):
            return {key: 0 for key in raw_values}
        return {key: 50 for key in raw_values}
    return {
        key: clamp(((value - minimum) / (maximum - minimum)) * 100)
        for key, value in raw_values.items()
    }


def _topic_display_name(topic: AVETopicPayload) -> str:
    display_name = (topic.name_en or "").strip()
    return display_name if display_name else topic.id


def _extract_appendix_note(raw: str | None) -> str | None:
    if not raw:
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    for key in ("description", "website", "twitter", "telegram"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _top_dex(risk: AVEContractRiskPayload) -> tuple[str, float]:
    if not risk.dex:
        return "none", 0.0
    best = max(risk.dex, key=lambda item: _safe_float(item.liquidity))
    provider = (best.amm or "").strip() or "none"
    return provider, _safe_float(best.liquidity)


def _risk_toxicity(risk: AVEContractRiskPayload) -> int:
    base = _safe_float(risk.risk_score) * 0.32
    base += (_safe_float(risk.buy_tax) + _safe_float(risk.sell_tax)) * 2.8
    if risk.is_honeypot and risk.is_honeypot > 0:
        base += 45
    if risk.cannot_buy:
        base += 20
    if risk.cannot_sell_all:
        base += 24
    if risk.has_mint_method:
        base += 10
    if risk.has_black_method:
        base += 12
    if risk.external_call:
        base += 8
    if risk.is_proxy:
        base += 6
    if risk.can_take_back_ownership:
        base += 8
    if risk.slippage_modifiable or risk.personal_slippage_modifiable:
        base += 7
    return clamp(base)


def _risk_coverage(risk: AVEContractRiskPayload) -> int:
    score = 100 - _safe_float(risk.risk_score)
    if risk.analysis_lp_current_adequate:
        score += 10
    if risk.has_owner_removed_risk:
        score += 6
    if risk.cannot_buy:
        score -= 18
    if risk.cannot_sell_all:
        score -= 22
    if risk.has_mint_method:
        score -= 10
    if risk.has_black_method:
        score -= 12
    if risk.is_honeypot and risk.is_honeypot > 0:
        score -= 35
    return clamp(score)


def _route_stability(risk: AVEContractRiskPayload) -> int:
    provider, dex_liquidity = _top_dex(risk)
    score = _log_metric(dex_liquidity) * 11
    score += 18 if risk.analysis_lp_current_adequate else 0
    score += 10 if risk.is_in_dex else 0
    score += 6 if not risk.is_proxy else 0
    score += 6 if not risk.external_call else 0
    score += 6 if not risk.slippage_modifiable else 0
    score += 6 if provider != "none" else 0
    score += _safe_float(risk.pair_lock_percent) * 10
    return clamp(score)


def _smart_flow_raw(token: AVERankedTokenPayload) -> float:
    buy_flow = _safe_float(token.token_buy_tx_volume_usd_5m or token.token_buy_volume_u_5m)
    sell_flow = _safe_float(token.token_sell_tx_volume_usd_5m or token.token_sell_volume_u_5m)
    flow_balance = 0.0
    if buy_flow or sell_flow:
        flow_balance = (buy_flow - sell_flow) / max(buy_flow + sell_flow, 1.0) * 100
    return (
        max(_safe_float(token.token_price_change_1h), 0.0) * 0.34
        + max(_safe_float(token.token_price_change_4h), 0.0) * 0.28
        + _log_metric(token.token_tx_volume_usd_1h or token.tx_volume_u_24h) * 10
        + flow_balance * 0.18
    )


def _leadership_raw(token: AVERankedTokenPayload) -> float:
    return (
        _log_metric(token.market_cap) * 0.46
        + _log_metric(token.token_tx_volume_usd_24h or token.tx_volume_u_24h) * 0.34
        + _log_metric(token.holders) * 0.20
    )


def _liquidity_raw(token: AVERankedTokenPayload, risk: AVEContractRiskPayload) -> float:
    _, dex_liquidity = _top_dex(risk)
    return _log_metric(token.main_pair_tvl or token.tvl) * 0.65 + _log_metric(dex_liquidity) * 0.35


def _scout_size_pct(leadership: int, liquidity: int, route_stability: int, risk_coverage: int) -> float:
    size = ((leadership * 0.26) + (liquidity * 0.24) + (route_stability * 0.25) + (risk_coverage * 0.25)) / 100
    return round(max(0.0, min(0.9, size * 0.8)), 2)


def _hard_stop_pct(
    *,
    token: AVERankedTokenPayload,
    route_stability: int,
    risk_coverage: int,
    toxicity: int,
) -> float | None:
    if route_stability < 52 or risk_coverage < 52:
        return None
    recent_move = abs(
        _safe_float(token.token_price_change_1h)
        or _safe_float(token.token_price_change_4h)
        or _safe_float(token.token_price_change_24h)
        or _safe_float(token.price_change_24h)
    )
    return round(max(3.5, min(12.0, 3.4 + recent_move * 0.42 + toxicity * 0.05)), 1)


def _time_stop_hours(
    *,
    acceleration_score: int,
    persistence_score: int,
    hard_stop_pct: float | None,
) -> int | None:
    if hard_stop_pct is None:
        return None
    return max(6, min(30, 24 - round(acceleration_score / 9) + round((100 - persistence_score) / 12)))


def _stage_bias(acceleration_score: int, breadth_score: int, deterioration_base: int) -> str:
    if deterioration_base >= 78:
        return "EXIT"
    if acceleration_score >= 82 and breadth_score >= 72:
        return "CONFIRM"
    if acceleration_score >= 68 and breadth_score >= 52:
        return "SCOUT"
    return "WATCH"


class AVEClient(ABC):
    @abstractmethod
    def fetch_topic_ranks(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def fetch_ranked_tokens_by_topic(self, topic: str) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def fetch_contract_risk(self, token_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_supported_chains(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def build_normalized_inputs(self) -> tuple[list[NormalizedAVENarrativeInput], list[NormalizedAVETokenInput]]:
        raise NotImplementedError


class DemoAVEClient(AVEClient):
    def fetch_topic_ranks(self) -> list[dict]:
        return get_demo_topic_ranks()

    def fetch_ranked_tokens_by_topic(self, topic: str) -> list[dict]:
        return get_demo_topic_tokens(topic)

    def fetch_contract_risk(self, token_id: str) -> dict:
        return get_demo_contract_risk(token_id)

    def get_supported_chains(self) -> list[str]:
        return []

    def build_normalized_inputs(self) -> tuple[list[NormalizedAVENarrativeInput], list[NormalizedAVETokenInput]]:
        raw = load_raw_demo()
        narratives = [NormalizedAVENarrativeInput.model_validate(item) for item in raw["narratives"]]
        tokens = [NormalizedAVETokenInput.model_validate(item) for item in raw["tokens"]]
        return narratives, tokens


class LiveAVEClient(AVEClient):
    def __init__(self) -> None:
        self.settings = get_settings()
        if not self.settings.ave_api_key:
            raise AVEUnavailableError("LIVE_MODE requires AVE_API_KEY before AVE ingestion can run.")
        self.headers = {"X-API-KEY": self.settings.ave_api_key}
        self.client = httpx.Client(
            base_url=self.settings.ave_api_base_url,
            headers=self.headers,
            timeout=self.settings.ave_request_timeout_seconds,
        )
        self._supported_chains_cache: list[str] | None = None

    def _request_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        try:
            response = self.client.get(path, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise AVEUnavailableError(
                f"AVE request failed for {path} with status {exc.response.status_code}."
            ) from exc
        except httpx.HTTPError as exc:
            raise AVEUnavailableError(f"AVE request failed for {path}: {exc}") from exc
        try:
            return response.json()
        except ValueError as exc:
            raise AVEContractError(f"{path} returned a non-JSON payload.") from exc

    def _validate_envelope(self, payload: Any, endpoint: str) -> AVEEnvelope:
        try:
            envelope = AVEEnvelope.model_validate(payload)
        except ValidationError as exc:
            raise AVEContractError(f"{endpoint} did not match the documented AVE envelope: {exc}") from exc
        if envelope.status != 1:
            raise AVEUnavailableError(f"{endpoint} returned AVE status {envelope.status}: {envelope.msg}")
        return envelope

    def _fetch_topic_contracts(self) -> list[AVETopicPayload]:
        envelope = self._validate_envelope(self._request_json("/ranks/topics"), "/ranks/topics")
        if not isinstance(envelope.data, list):
            raise AVEContractError("/ranks/topics returned a non-list data payload.")
        topics: list[AVETopicPayload] = []
        for index, row in enumerate(envelope.data):
            try:
                topics.append(AVETopicPayload.model_validate(row))
            except ValidationError as exc:
                raise AVEContractError(f"/ranks/topics row {index} is invalid: {exc}") from exc
        return topics

    def _fetch_ranked_token_contracts(self, topic: str) -> list[AVERankedTokenPayload]:
        envelope = self._validate_envelope(
            self._request_json(
                "/ranks",
                params={"topic": topic, "limit": self.settings.ave_topic_token_limit},
            ),
            f"/ranks?topic={topic}",
        )
        if not isinstance(envelope.data, list):
            raise AVEContractError(f"/ranks?topic={topic} returned a non-list data payload.")
        tokens: list[AVERankedTokenPayload] = []
        for index, row in enumerate(envelope.data):
            try:
                tokens.append(AVERankedTokenPayload.model_validate(row))
            except ValidationError as exc:
                raise AVEContractError(f"/ranks?topic={topic} row {index} is invalid: {exc}") from exc
        return tokens

    def _fetch_smart_wallet_contracts(self, chain: str, limit: int = 20) -> list[AVESmartWalletPayload]:
        envelope = self._validate_envelope(
            self._request_json("/address/smart_wallet/list", params={"chain": chain, "limit": limit}),
            f"/address/smart_wallet/list?chain={chain}",
        )
        if not isinstance(envelope.data, list):
            raise AVEContractError(f"/address/smart_wallet/list?chain={chain} returned a non-list data payload.")
        wallets: list[AVESmartWalletPayload] = []
        for index, row in enumerate(envelope.data):
            try:
                wallets.append(AVESmartWalletPayload.model_validate(row))
            except ValidationError as exc:
                raise AVEContractError(
                    f"/address/smart_wallet/list?chain={chain} row {index} is invalid: {exc}"
                ) from exc
        return wallets

    def _fetch_public_signal_contracts(self, limit: int = 50) -> list[AVEPublicSignalPayload]:
        envelope = self._validate_envelope(
            self._request_json("/signals/public/list", params={"limit": limit}),
            "/signals/public/list",
        )
        if not isinstance(envelope.data, list):
            raise AVEContractError("/signals/public/list returned a non-list data payload.")
        signals: list[AVEPublicSignalPayload] = []
        for index, row in enumerate(envelope.data):
            try:
                signals.append(AVEPublicSignalPayload.model_validate(row))
            except ValidationError as exc:
                raise AVEContractError(f"/signals/public/list row {index} is invalid: {exc}") from exc
        return signals

    def _fetch_trending_token_contracts(self, chain: str, limit: int = 50) -> list[AVERankedTokenPayload]:
        envelope = self._validate_envelope(
            self._request_json("/tokens/trending", params={"chain": chain, "limit": limit}),
            f"/tokens/trending?chain={chain}",
        )
        if not isinstance(envelope.data, dict):
            raise AVEContractError(f"/tokens/trending?chain={chain} returned a non-object data payload.")
        try:
            trending = AVETrendingTokensPayload.model_validate(envelope.data)
        except ValidationError as exc:
            raise AVEContractError(f"/tokens/trending?chain={chain} is invalid: {exc}") from exc
        return trending.tokens

    def _fetch_supported_chain_contracts(self) -> list[str]:
        global _SUPPORTED_CHAINS_CACHE

        if self._supported_chains_cache is not None:
            return list(self._supported_chains_cache)
        if _SUPPORTED_CHAINS_CACHE is not None:
            self._supported_chains_cache = list(_SUPPORTED_CHAINS_CACHE)
            return list(self._supported_chains_cache)

        envelope = self._validate_envelope(
            self._request_json("/supported_chains"),
            "/supported_chains",
        )
        if not isinstance(envelope.data, list):
            raise AVEContractError("/supported_chains returned a non-list data payload.")

        supported_chains: list[str] = []
        for index, row in enumerate(envelope.data):
            if isinstance(row, str):
                candidate = row.strip()
            elif isinstance(row, dict):
                try:
                    payload = AVESupportedChainPayload.model_validate(row)
                except ValidationError as exc:
                    raise AVEContractError(f"/supported_chains row {index} is invalid: {exc}") from exc
                candidate = (
                    (payload.chain or "").strip()
                    or (payload.id or "").strip()
                    or (payload.name or "").strip()
                    or (payload.symbol or "").strip()
                )
            else:
                raise AVEContractError(f"/supported_chains row {index} is not a string or object.")

            if candidate and candidate not in supported_chains:
                supported_chains.append(candidate)

        self._supported_chains_cache = supported_chains
        _SUPPORTED_CHAINS_CACHE = list(supported_chains)
        return list(supported_chains)

    def _fetch_holder_contracts(self, token_id: str, limit: int = 10) -> list[AVEHolderPayload]:
        envelope = self._validate_envelope(
            self._request_json(f"/tokens/holders/{token_id}", params={"limit": limit}),
            f"/tokens/holders/{token_id}",
        )
        if not isinstance(envelope.data, list):
            raise AVEContractError(f"/tokens/holders/{token_id} returned a non-list data payload.")
        holders: list[AVEHolderPayload] = []
        for index, row in enumerate(envelope.data):
            try:
                holders.append(AVEHolderPayload.model_validate(row))
            except ValidationError as exc:
                raise AVEContractError(f"/tokens/holders/{token_id} row {index} is invalid: {exc}") from exc
        return holders

    def _fetch_kline_contract(self, token_id: str, interval: str = "1h", limit: int = 24) -> AVEKlinePayload:
        envelope = self._validate_envelope(
            self._request_json(f"/klines/token/{token_id}", params={"interval": interval, "limit": limit}),
            f"/klines/token/{token_id}",
        )
        if not isinstance(envelope.data, dict):
            raise AVEContractError(f"/klines/token/{token_id} returned a non-object data payload.")
        try:
            return AVEKlinePayload.model_validate(envelope.data)
        except ValidationError as exc:
            raise AVEContractError(f"/klines/token/{token_id} is invalid: {exc}") from exc

    def _fetch_token_detail_contract(self, token_id: str) -> AVERankedTokenPayload:
        envelope = self._validate_envelope(self._request_json(f"/tokens/{token_id}"), f"/tokens/{token_id}")
        if not isinstance(envelope.data, dict):
            raise AVEContractError(f"/tokens/{token_id} returned a non-object data payload.")
        try:
            token_detail = AVETokenDetailPayload.model_validate(envelope.data)
        except ValidationError as exc:
            raise AVEContractError(f"/tokens/{token_id} is invalid: {exc}") from exc
        if token_detail.token is None:
            raise AVEContractError(f"/tokens/{token_id} did not include a token payload.")
        return token_detail.token

    def _fetch_risk_contract(self, token_id: str) -> AVEContractRiskPayload:
        envelope = self._validate_envelope(self._request_json(f"/contracts/{token_id}"), f"/contracts/{token_id}")
        if not isinstance(envelope.data, dict):
            raise AVEContractError(f"/contracts/{token_id} returned a non-object data payload.")
        try:
            risk = AVEContractRiskPayload.model_validate(envelope.data)
        except ValidationError as exc:
            raise AVEContractError(f"/contracts/{token_id} is invalid: {exc}") from exc
        if risk.err_code not in {None, "", "0", 0}:
            raise AVEUnavailableError(
                f"/contracts/{token_id} returned AVE risk error {risk.err_code}: {risk.err_msg or 'unknown'}"
            )
        return risk

    def fetch_topic_ranks(self) -> list[dict]:
        return [topic.model_dump() for topic in self._fetch_topic_contracts()]

    def fetch_ranked_tokens_by_topic(self, topic: str) -> list[dict]:
        return [token.model_dump() for token in self._fetch_ranked_token_contracts(topic)]

    def fetch_contract_risk(self, token_id: str) -> dict:
        return self._fetch_risk_contract(token_id).model_dump()

    def get_supported_chains(self) -> list[str]:
        if self._supported_chains_cache is None:
            return []
        return list(self._supported_chains_cache)

    def _fetch_topic_risks(
        self,
        ranked_tokens: list[AVERankedTokenPayload],
    ) -> tuple[dict[str, AVEContractRiskPayload], list[AVERankedTokenPayload]]:
        if not ranked_tokens:
            return {}, []

        risks: dict[str, AVEContractRiskPayload] = {}
        max_workers = min(8, len(ranked_tokens))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self._fetch_risk_contract, token.token_id): token for token in ranked_tokens}
            for future in as_completed(futures):
                token = futures[future]
                try:
                    risks[token.token_id] = future.result()
                except (AVEUnavailableError, AVEContractError):
                    continue

        filtered_tokens = [token for token in ranked_tokens if token.token_id in risks]
        return risks, filtered_tokens

    def _fetch_top_candidate_enrichment(
        self,
        token_id: str,
    ) -> tuple[str, AVERankedTokenPayload | None, float | None, str]:
        detail: AVERankedTokenPayload | None = None
        top_holder_pct: float | None = None
        kline_trend = "flat"

        try:
            detail = self._fetch_token_detail_contract(token_id)
        except (AVEUnavailableError, AVEContractError):
            detail = None

        try:
            holders = self._fetch_holder_contracts(token_id, limit=10)
            top_ratio = next((holder.balance_ratio for holder in holders if holder.balance_ratio is not None), None)
            if top_ratio is not None:
                top_holder_pct = round(top_ratio * 100 if top_ratio <= 1 else top_ratio, 2)
        except (AVEUnavailableError, AVEContractError):
            top_holder_pct = None

        try:
            kline = self._fetch_kline_contract(token_id, interval="1h", limit=24)
            kline_trend = _kline_trend(kline.points)
        except (AVEUnavailableError, AVEContractError):
            kline_trend = "flat"

        return token_id, detail, top_holder_pct, kline_trend

    def build_normalized_inputs(self) -> tuple[list[NormalizedAVENarrativeInput], list[NormalizedAVETokenInput]]:
        try:
            self._fetch_supported_chain_contracts()
        except (AVEUnavailableError, AVEContractError):
            self._supported_chains_cache = []

        trending_token_addresses: set[str] = set()
        try:
            trending_token_addresses = {
                token.token
                for token in self._fetch_trending_token_contracts(chain="solana", limit=50)
                if token.token
            }
        except (AVEUnavailableError, AVEContractError):
            trending_token_addresses = set()

        topics = self._fetch_topic_contracts()[: self.settings.ave_topic_limit]
        topic_rows: list[dict[str, Any]] = []
        topic_names: dict[str, str] = {}

        for rank, topic in enumerate(topics, start=1):
            ranked_tokens = self._fetch_ranked_token_contracts(topic.id)
            if not ranked_tokens:
                continue
            risks, ranked_tokens = self._fetch_topic_risks(ranked_tokens)
            if not ranked_tokens:
                continue
            topic_rows.append(
                {
                    "topic": topic,
                    "rank": rank,
                    "tokens": ranked_tokens,
                    "risks": risks,
                }
            )
            topic_names[topic.id] = _topic_display_name(topic)

        if not topic_rows:
            raise AVEUnavailableError("AVE did not return any ranked topics with tokens.")

        flow_raw = {
            row["topic"].id: (
                _log_metric(
                    sum(_safe_float(token.token_tx_volume_usd_24h or token.tx_volume_u_24h) for token in row["tokens"])
                )
                * 0.68
                + _log_metric(sum(_safe_float(token.token_tx_count_24h or token.tx_count_24h) for token in row["tokens"]))
                * 0.14
                + _log_metric(sum(_safe_float(token.main_pair_tvl or token.tvl) for token in row["tokens"])) * 0.18
            )
            for row in topic_rows
        }
        acceleration_raw = {
            row["topic"].id: (
                max(fmean(_safe_float(token.token_price_change_5m) for token in row["tokens"]), 0.0) * 0.22
                + max(fmean(_safe_float(token.token_price_change_1h) for token in row["tokens"]), 0.0) * 0.36
                + max(fmean(_safe_float(token.token_price_change_4h) for token in row["tokens"]), 0.0) * 0.24
                + _log_metric(sum(_safe_float(token.token_tx_volume_usd_1h) for token in row["tokens"])) * 5.5
                + _log_metric(sum(_safe_float(token.token_tx_volume_usd_5m) for token in row["tokens"])) * 4.0
            )
            for row in topic_rows
        }
        breadth_raw = {}
        price_expansion_raw = {}
        persistence_raw = {}
        capital_demand_raw = {}
        leader_concentration_raw = {}
        risk_drag_raw = {}
        breadth_counts: dict[str, int] = {}

        for row in topic_rows:
            topic_id = row["topic"].id
            tokens = row["tokens"]
            positive_breadth = [
                token
                for token in tokens
                if (_safe_float(token.token_price_change_1h) > 0 or _safe_float(token.token_price_change_4h) > 0)
                and (_safe_float(token.token_tx_volume_usd_24h or token.tx_volume_u_24h) > 0)
            ]
            breadth_counts[topic_id] = len(positive_breadth)
            breadth_ratio = len(positive_breadth) / max(len(tokens), 1)
            persistence_ratio = (
                sum(
                    1
                    for token in tokens
                    if _safe_float(token.token_price_change_1h) > 0
                    and _safe_float(token.token_price_change_4h) > 0
                    and _safe_float(token.token_price_change_24h or token.price_change_24h) > 0
                )
                / max(len(tokens), 1)
            )
            total_market_cap = sum(_safe_float(token.market_cap) for token in tokens)
            top_market_cap = max((_safe_float(token.market_cap) for token in tokens), default=0.0)
            leader_concentration_raw[topic_id] = (top_market_cap / max(total_market_cap, 1.0)) * 100
            breadth_raw[topic_id] = breadth_ratio * 100 + _log_metric(sum(_safe_float(token.holders) for token in tokens)) * 7.5
            price_expansion_raw[topic_id] = (
                max(fmean(_safe_float(token.token_price_change_1h) for token in tokens), 0.0) * 0.30
                + max(fmean(_safe_float(token.token_price_change_4h) for token in tokens), 0.0) * 0.38
                + max(fmean(_safe_float(token.token_price_change_24h or token.price_change_24h) for token in tokens), 0.0) * 0.32
            )
            persistence_raw[topic_id] = persistence_ratio * 100 + max(
                fmean(_safe_float(token.token_price_change_24h or token.price_change_24h) for token in tokens),
                0.0,
            )
            capital_demand_raw[topic_id] = (
                _log_metric(sum(_safe_float(token.token_tx_volume_usd_24h or token.tx_volume_u_24h) for token in tokens))
                * 0.42
                + _log_metric(sum(_safe_float(token.market_cap) for token in tokens)) * 0.28
                + _log_metric(sum(_safe_float(token.main_pair_tvl or token.tvl) for token in tokens)) * 0.30
            )
            risk_drag_raw[topic_id] = fmean(
                _safe_float(row["risks"][token.token_id].risk_score) for token in tokens
            )

        flow_score = _scale_map(flow_raw)
        acceleration_score = _scale_map(acceleration_raw)
        breadth_score = _scale_map(breadth_raw)
        price_expansion_score = _scale_map(price_expansion_raw)
        persistence_score = _scale_map(persistence_raw)
        capital_demand_score = _scale_map(capital_demand_raw)
        leader_concentration = _scale_map(leader_concentration_raw)

        narrative_records: dict[str, NormalizedAVENarrativeInput] = {}
        smart_money_signal = "unavailable"
        for chain in ("solana", "bsc"):
            try:
                smart_wallets = self._fetch_smart_wallet_contracts(chain=chain, limit=20)
                smart_money_signal = "active" if smart_wallets else "quiet"
                break
            except (AVEUnavailableError, AVEContractError):
                continue

        for index, row in enumerate(topic_rows):
            topic = row["topic"]
            topic_id = topic.id
            crowding = clamp(
                leader_concentration[topic_id] * 0.58
                + max(0, capital_demand_score[topic_id] - breadth_score[topic_id]) * 0.42
            )
            deterioration = clamp(
                crowding * 0.42
                + leader_concentration[topic_id] * 0.26
                + (100 - persistence_score[topic_id]) * 0.18
                + (100 - breadth_score[topic_id]) * 0.14
                + risk_drag_raw[topic_id] * 0.15
            )
            display_name = _topic_display_name(topic)
            competing = []
            if index > 0:
                competing.append(_topic_display_name(topic_rows[index - 1]["topic"]))
            if index < len(topic_rows) - 1:
                competing.append(_topic_display_name(topic_rows[index + 1]["topic"]))

            provisional = NormalizedAVENarrativeInput(
                id=topic_id,
                name=display_name,
                thesis=(
                    f"{display_name} is being scored from live AVE ranked-token flow, "
                    "breadth, price expansion, and contract-risk signals."
                ),
                aveTopicRank=row["rank"],
                aveRankDelta=0,
                flowScore=flow_score[topic_id],
                accelerationScore=acceleration_score[topic_id],
                breadthScore=breadth_score[topic_id],
                breadthTokens=breadth_counts[topic_id],
                priceExpansionScore=price_expansion_score[topic_id],
                persistenceScore=persistence_score[topic_id],
                capitalDemandScore=capital_demand_score[topic_id],
                crowdingScore=crowding,
                leaderConcentration=leader_concentration[topic_id],
                deteriorationBase=deterioration,
                stageBiasHint=_stage_bias(acceleration_score[topic_id], breadth_score[topic_id], deterioration),
                competingNarratives=competing,
                notes=[
                    f"Flow score {flow_score[topic_id]} is derived from ranked-token volume and TVL.",
                    f"Breadth is {breadth_counts[topic_id]} live names with acceleration {acceleration_score[topic_id]}.",
                    f"Crowding {crowding} and deterioration base {deterioration} come from concentration and risk drag.",
                ],
                tokenIds=[token.token_id for token in row["tokens"]],
                budget={},
                smartMoneySignal=smart_money_signal,
            )
            narrative_records[topic_id] = provisional.model_copy(update={"budget": build_default_budget(provisional)})

        signal_confirmations: dict[str, int] = {}
        try:
            for signal in self._fetch_public_signal_contracts(limit=50):
                token_address = (signal.token or "").strip()
                if token_address:
                    signal_confirmations[token_address] = signal_confirmations.get(token_address, 0) + 1
        except (AVEUnavailableError, AVEContractError):
            signal_confirmations = {}

        top_candidate_token_ids = {
            max(row["tokens"], key=_leadership_raw).token_id
            for row in topic_rows
            if row["tokens"]
        }
        enriched_token_details: dict[str, AVERankedTokenPayload] = {}
        top_holder_pct_by_token_id: dict[str, float] = {}
        kline_trend_by_token_id: dict[str, str] = {}
        if top_candidate_token_ids:
            max_workers = min(4, len(top_candidate_token_ids))
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self._fetch_top_candidate_enrichment, token_id): token_id
                    for token_id in top_candidate_token_ids
                }
                for future in as_completed(futures):
                    try:
                        token_id, detail, top_holder_pct, kline_trend = future.result()
                    except Exception:
                        continue
                    if detail is not None:
                        enriched_token_details[token_id] = detail
                    if top_holder_pct is not None:
                        top_holder_pct_by_token_id[token_id] = top_holder_pct
                    if kline_trend:
                        kline_trend_by_token_id[token_id] = kline_trend

        token_membership: dict[str, list[str]] = {}
        for row in topic_rows:
            for token in row["tokens"]:
                token_membership.setdefault(token.token_id, []).append(row["topic"].id)

        normalized_tokens: list[NormalizedAVETokenInput] = []
        for row in topic_rows:
            topic = row["topic"]
            tokens = row["tokens"]
            risks = row["risks"]
            topic_id = topic.id
            leadership_scale = _scale_map({token.token_id: _leadership_raw(token) for token in tokens})
            liquidity_scale = _scale_map(
                {token.token_id: _liquidity_raw(token, risks[token.token_id]) for token in tokens}
            )
            smart_flow_scale = _scale_map({token.token_id: _smart_flow_raw(token) for token in tokens})

            for token in tokens:
                risk = risks[token.token_id]
                detail = enriched_token_details.get(token.token_id)
                token_symbol = token.symbol or (detail.symbol if detail else None) or token.token[:6].upper()
                token_name = token.name or (detail.name if detail else None) or token.symbol or token.token
                route_provider, _ = _top_dex(risk)
                route_stability = _route_stability(risk)
                risk_coverage = _risk_coverage(risk)
                toxicity = _risk_toxicity(risk)
                leadership = leadership_scale[token.token_id]
                liquidity = liquidity_scale[token.token_id]
                smart_flow_alignment = smart_flow_scale[token.token_id]
                hard_stop_pct = _hard_stop_pct(
                    token=token,
                    route_stability=route_stability,
                    risk_coverage=risk_coverage,
                    toxicity=toxicity,
                )
                time_stop_hours = _time_stop_hours(
                    acceleration_score=narrative_records[topic_id].accelerationScore,
                    persistence_score=narrative_records[topic_id].persistenceScore,
                    hard_stop_pct=hard_stop_pct,
                )
                price_expansion_pct = (
                    _safe_float(token.token_price_change_1h)
                    or _safe_float(token.token_price_change_4h)
                    or _safe_float(token.token_price_change_24h or token.price_change_24h)
                )
                overlap_topics = [
                    topic_names[item]
                    for item in token_membership.get(token.token_id, [])
                    if item != topic_id and item in topic_names
                ]
                note = (
                    token.intro_en
                    or (detail.intro_en if detail else None)
                    or _extract_appendix_note(token.appendix)
                    or _extract_appendix_note(detail.appendix if detail else None)
                    or f"Live AVE-ranked token in {topic_names[topic_id]}."
                )
                normalized_tokens.append(
                    NormalizedAVETokenInput(
                        id=token.token_id,
                        narrativeId=topic_id,
                        symbol=token_symbol,
                        name=token_name,
                        leadership=leadership,
                        liquidity=liquidity,
                        routeStability=route_stability,
                        riskCoverage=risk_coverage,
                        smartFlowAlignment=smart_flow_alignment,
                        toxicity=toxicity,
                        scoutSizePct=_scout_size_pct(leadership, liquidity, route_stability, risk_coverage),
                        overlapNarratives=overlap_topics,
                        priceExpansionPct=round(price_expansion_pct, 2),
                        breadthContribution=(
                            f'{topic_names[topic_id]} has {narrative_records[topic_id].breadthTokens} active names; '
                            f'{token_symbol} is one of the live ranked expressions.'
                        ),
                        thesisBreak=(
                            f'{token_symbol} loses route adequacy, or {topic_names[topic_id]} breadth falls below '
                            f'{max(2, narrative_records[topic_id].breadthTokens - 2)} names.'
                        ),
                        hardStopPct=hard_stop_pct,
                        timeStopHours=time_stop_hours,
                        routeProvider=route_provider,
                        signalConfirmations=signal_confirmations.get(token.token, 0),
                        trendingOnAVE=token.token in trending_token_addresses,
                        topHolderPct=top_holder_pct_by_token_id.get(token.token_id),
                        logoUrl=token.logo_url or (detail.logo_url if detail else None),
                        klineTrend=kline_trend_by_token_id.get(token.token_id, "flat"),
                        note=note,
                    )
                )

        return list(narrative_records.values()), normalized_tokens


def get_ave_client() -> AVEClient:
    settings = get_settings()
    if settings.app_mode == "LIVE_MODE":
        return LiveAVEClient()
    return DemoAVEClient()
