from __future__ import annotations

from copy import deepcopy
from collections import defaultdict
from datetime import UTC, datetime
from threading import Event, Lock
from time import monotonic
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.demo_seed import (
    build_live_raw_data,
    build_snapshot_from_raw,
    build_stage_progress,
    get_demo_snapshot,
)
from app.models import ExecutionEventModel, ExecutionRequestModel
from app.services.ave import AVEUnavailableError, get_ave_client
from app.services.ave_contracts import AVEContractError
from app.services.ave_wss import get_ave_wss_monitor


class SnapshotUnavailableError(Exception):
    """Raised when a truthful snapshot cannot be assembled."""


_FALLBACK_EXECUTION_REQUESTS: dict[str, dict] = {}
_LIVE_BASE_SNAPSHOT_CACHE: dict[str, object] = {"snapshot": None, "fetched_at": 0.0}
_LAST_GOOD_LIVE_SNAPSHOT: dict[str, object] = {"snapshot": None, "fetched_at": 0.0}
_LIVE_BASE_SNAPSHOT_LOCK = Lock()
_LIVE_BASE_SNAPSHOT_BUILD_EVENT: Event | None = None


def _has_live_snapshot(snapshot: object) -> bool:
    return isinstance(snapshot, dict) and bool(snapshot.get("narratives"))


def _isoformat(value) -> str:
    if value is None:
        return ""
    if hasattr(value, "astimezone"):
        if getattr(value, "tzinfo", None) is None:
            return value.replace(tzinfo=UTC).isoformat()
        return value.astimezone(UTC).isoformat()
    return str(value)


def _format_timestamp(value) -> str:
    if value is None or not hasattr(value, "astimezone"):
        return str(value)
    if getattr(value, "tzinfo", None) is None:
        return value.replace(tzinfo=UTC).strftime("%Y-%m-%d %H:%M UTC")
    return value.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")


def _verdict_for_status(status: str) -> str:
    if status in {"success", "ready", "skipped"}:
        return "pass"
    if status in {"pending"}:
        return "watch"
    return "block"


def _execution_outcome(record: dict) -> dict:
    return {
        "app_mode": record["app_mode"],
        "decision": record["decision"],
        "mode": record["execution_mode"],
        "phase": record["lifecycle_phase"],
        "status": record["lifecycle_status"],
        "route": record["route"],
        "provider": record["provider"],
        "slippage": record["slippage"],
        "note": record["message"],
        "failure_reason": record.get("failure_reason"),
        "request_id": record["id"],
        "ave_quote": (record.get("response_payload") or {}).get("ave_quote"),
    }


class SnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def seed_demo(self) -> None:
        return None

    def _rollback_quietly(self) -> None:
        try:
            self.db.rollback()
        except Exception:
            return None

    def _build_fallback_execution_record(
        self,
        *,
        narrative_id: str,
        candidate_id: str,
        record: dict,
        request_id: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
        events: list[dict] | None = None,
    ) -> dict:
        created = created_at or record.get("created_at") or datetime.now(UTC).isoformat()
        updated = updated_at or record.get("updated_at") or created
        fallback_id = request_id or record.get("id") or f"exec-{uuid4().hex[:12]}"
        event_list = events if events is not None else []
        return {
            "id": fallback_id,
            "app_mode": record["app_mode"],
            "narrative_id": narrative_id,
            "candidate_id": candidate_id,
            "target_stage": record["target_stage"],
            "decision": record["decision"],
            "execution_mode": record["execution_mode"],
            "lifecycle_phase": record["lifecycle_phase"],
            "lifecycle_status": record["lifecycle_status"],
            "provider": record["provider"],
            "route": record["route"],
            "slippage": record["slippage"],
            "protected_exit": record["protected_exit"],
            "message": record["message"],
            "failure_reason": record.get("failure_reason"),
            "request_payload": record["request_payload"],
            "response_payload": record.get("response_payload", {}),
            "created_at": created,
            "updated_at": updated,
            "events": event_list,
        }

    def _fallback_add_event(
        self,
        *,
        request_id: str,
        phase: str,
        status: str,
        message: str,
        payload: dict | None = None,
    ) -> dict:
        event = {
            "id": f"event-{uuid4().hex[:12]}",
            "phase": phase,
            "status": status,
            "message": message,
            "created_at": datetime.now(UTC).isoformat(),
            "payload": payload or {},
        }
        record = _FALLBACK_EXECUTION_REQUESTS.get(request_id)
        if record is not None:
            record.setdefault("events", []).append(event)
            record["updated_at"] = event["created_at"]
        return event

    def get_snapshot(self) -> dict:
        base_snapshot = self._get_base_snapshot()
        return self._merge_execution_truth(base_snapshot)

    def _get_base_snapshot(self) -> dict:
        global _LIVE_BASE_SNAPSHOT_BUILD_EVENT

        if self.settings.app_mode != "LIVE_MODE":
            return self._build_base_snapshot()

        cache_ttl = max(self.settings.live_snapshot_cache_seconds, 0)
        now = monotonic()
        build_event: Event | None = None
        should_build = False

        with _LIVE_BASE_SNAPSHOT_LOCK:
            cached_snapshot = _LIVE_BASE_SNAPSHOT_CACHE.get("snapshot")
            fetched_at = float(_LIVE_BASE_SNAPSHOT_CACHE.get("fetched_at") or 0.0)
            if cached_snapshot is not None and now - fetched_at < cache_ttl:
                return deepcopy(cached_snapshot)

            if _LIVE_BASE_SNAPSHOT_BUILD_EVENT is not None:
                build_event = _LIVE_BASE_SNAPSHOT_BUILD_EVENT
            else:
                build_event = Event()
                _LIVE_BASE_SNAPSHOT_BUILD_EVENT = build_event
                should_build = True

        if not should_build:
            assert build_event is not None
            build_event.wait(timeout=max(self.settings.ave_request_timeout_seconds * 2, 30.0))
            with _LIVE_BASE_SNAPSHOT_LOCK:
                refreshed_snapshot = _LIVE_BASE_SNAPSHOT_CACHE.get("snapshot")
                if refreshed_snapshot is not None:
                    return deepcopy(refreshed_snapshot)

                stale_snapshot = _LAST_GOOD_LIVE_SNAPSHOT.get("snapshot")
                if stale_snapshot is not None:
                    return deepcopy(stale_snapshot)

            raise SnapshotUnavailableError(
                "Live snapshot build did not complete successfully and no cached snapshot is available."
            )

        try:
            snapshot = self._build_base_snapshot()
        except SnapshotUnavailableError:
            with _LIVE_BASE_SNAPSHOT_LOCK:
                stale_snapshot = _LAST_GOOD_LIVE_SNAPSHOT.get("snapshot")
                build_event = _LIVE_BASE_SNAPSHOT_BUILD_EVENT
                _LIVE_BASE_SNAPSHOT_BUILD_EVENT = None
                if build_event is not None:
                    build_event.set()

            if stale_snapshot is not None:
                return deepcopy(stale_snapshot)
            raise
        except Exception:
            with _LIVE_BASE_SNAPSHOT_LOCK:
                stale_snapshot = _LAST_GOOD_LIVE_SNAPSHOT.get("snapshot")
                build_event = _LIVE_BASE_SNAPSHOT_BUILD_EVENT
                _LIVE_BASE_SNAPSHOT_BUILD_EVENT = None
                if build_event is not None:
                    build_event.set()

            if stale_snapshot is not None:
                return deepcopy(stale_snapshot)
            raise
        else:
            with _LIVE_BASE_SNAPSHOT_LOCK:
                snapshot_copy = deepcopy(snapshot)
                _LIVE_BASE_SNAPSHOT_CACHE["snapshot"] = snapshot_copy
                _LIVE_BASE_SNAPSHOT_CACHE["fetched_at"] = monotonic()
                if _has_live_snapshot(snapshot_copy):
                    _LAST_GOOD_LIVE_SNAPSHOT["snapshot"] = deepcopy(snapshot_copy)
                    _LAST_GOOD_LIVE_SNAPSHOT["fetched_at"] = _LIVE_BASE_SNAPSHOT_CACHE["fetched_at"]
                build_event = _LIVE_BASE_SNAPSHOT_BUILD_EVENT
                _LIVE_BASE_SNAPSHOT_BUILD_EVENT = None
                if build_event is not None:
                    build_event.set()
            return snapshot

    def _build_base_snapshot(self) -> dict:
        if self.settings.app_mode != "LIVE_MODE":
            return get_demo_snapshot()

        try:
            ave_client = get_ave_client()
            narratives, tokens = ave_client.build_normalized_inputs()
            raw = build_live_raw_data(
                narratives,
                tokens,
                mode="LIVE_MODE",
                live_prices=get_ave_wss_monitor().get_prices(),
                supported_chains=ave_client.get_supported_chains(),
            )
            return build_snapshot_from_raw(raw)
        except (AVEUnavailableError, AVEContractError) as exc:
            raise SnapshotUnavailableError(str(exc)) from exc

    def get_narrative(self, narrative_id: str) -> dict | None:
        return next(
            (
                narrative
                for narrative in self.get_snapshot()["narratives"]
                if narrative["id"] == narrative_id
            ),
            None,
        )

    def get_candidate(self, candidate_id: str) -> dict | None:
        return next(
            (
                candidate
                for candidate in self.get_snapshot()["candidates"]
                if candidate["id"] == candidate_id
            ),
            None,
        )

    def current_stage_for_candidate(self, candidate_id: str) -> str:
        position = None
        if self.settings.app_mode != "LIVE_MODE":
            position = next(
                (item for item in get_demo_snapshot()["positions"] if item["candidate_id"] == candidate_id),
                None,
            )
        if position is not None:
            return position["stage"]

        try:
            stmt = (
                select(ExecutionRequestModel)
                .where(ExecutionRequestModel.candidate_id == candidate_id)
                .where(ExecutionRequestModel.lifecycle_phase == "submitted")
                .where(ExecutionRequestModel.lifecycle_status.in_(["pending", "success", "skipped"]))
                .order_by(ExecutionRequestModel.created_at.desc())
            )
            record = self.db.execute(stmt).scalars().first()
            return record.target_stage if record is not None else "WATCH"
        except Exception:
            matching = [
                request
                for request in _FALLBACK_EXECUTION_REQUESTS.values()
                if request["candidate_id"] == candidate_id
                and request["lifecycle_phase"] == "submitted"
                and request["lifecycle_status"] in {"pending", "success", "skipped"}
            ]
            if not matching:
                return "WATCH"
            matching.sort(key=lambda item: item["created_at"], reverse=True)
            return matching[0]["target_stage"]

    def create_execution_request(
        self,
        *,
        narrative_id: str,
        candidate_id: str,
        record: dict,
    ) -> dict:
        fallback_record = self._build_fallback_execution_record(
            narrative_id=narrative_id,
            candidate_id=candidate_id,
            record=record,
        )
        try:
            execution_request = ExecutionRequestModel(
                id=fallback_record["id"],
                app_mode=record["app_mode"],
                narrative_id=narrative_id,
                candidate_id=candidate_id,
                target_stage=record["target_stage"],
                decision=record["decision"],
                execution_mode=record["execution_mode"],
                lifecycle_phase=record["lifecycle_phase"],
                lifecycle_status=record["lifecycle_status"],
                provider=record["provider"],
                route=record["route"],
                slippage=record["slippage"],
                protected_exit=record["protected_exit"],
                message=record["message"],
                failure_reason=record.get("failure_reason"),
                request_payload=record["request_payload"],
                response_payload=record.get("response_payload", {}),
            )
            self.db.add(execution_request)
            self.db.flush()
            self.add_execution_event(
                request_id=execution_request.id,
                phase=execution_request.lifecycle_phase,
                status=execution_request.lifecycle_status,
                message=execution_request.message,
                payload=execution_request.response_payload or {},
            )
            self.db.commit()
            self.db.refresh(execution_request)
            return self.get_execution_request(execution_request.id) or fallback_record
        except Exception:
            self._rollback_quietly()
            initial_event = self._fallback_add_event(
                request_id=fallback_record["id"],
                phase=fallback_record["lifecycle_phase"],
                status=fallback_record["lifecycle_status"],
                message=fallback_record["message"],
                payload=fallback_record["response_payload"] or {},
            )
            fallback_record["events"] = [initial_event]
            fallback_record["updated_at"] = initial_event["created_at"]
            _FALLBACK_EXECUTION_REQUESTS[fallback_record["id"]] = fallback_record
            return fallback_record

    def add_execution_event(
        self,
        *,
        request_id: str,
        phase: str,
        status: str,
        message: str,
        payload: dict | None = None,
    ) -> dict:
        try:
            event = ExecutionEventModel(
                id=f"event-{uuid4().hex[:12]}",
                execution_request_id=request_id,
                lifecycle_phase=phase,
                lifecycle_status=status,
                message=message,
                payload=payload or {},
            )
            self.db.add(event)
            self.db.flush()
            return {
                "id": event.id,
                "phase": event.lifecycle_phase,
                "status": event.lifecycle_status,
                "message": event.message,
                "created_at": _isoformat(event.created_at),
                "payload": event.payload,
            }
        except Exception:
            self._rollback_quietly()
            return self._fallback_add_event(
                request_id=request_id,
                phase=phase,
                status=status,
                message=message,
                payload=payload,
            )

    def update_execution_request(self, request_id: str, record: dict) -> dict | None:
        try:
            request = self.db.get(ExecutionRequestModel, request_id)
            if request is None:
                return None

            request.lifecycle_phase = record["lifecycle_phase"]
            request.lifecycle_status = record["lifecycle_status"]
            request.provider = record["provider"]
            request.route = record["route"]
            request.slippage = record["slippage"]
            request.protected_exit = record["protected_exit"]
            request.message = record["message"]
            request.failure_reason = record.get("failure_reason")
            request.request_payload = record["request_payload"]
            request.response_payload = record.get("response_payload", {})
            self.add_execution_event(
                request_id=request.id,
                phase=request.lifecycle_phase,
                status=request.lifecycle_status,
                message=request.message,
                payload=request.response_payload or {},
            )
            self.db.commit()
            self.db.refresh(request)
            return self.get_execution_request(request_id)
        except Exception:
            self._rollback_quietly()
            request = _FALLBACK_EXECUTION_REQUESTS.get(request_id)
            if request is None:
                return None
            request.update(
                {
                    "app_mode": record["app_mode"],
                    "target_stage": record["target_stage"],
                    "decision": record["decision"],
                    "execution_mode": record["execution_mode"],
                    "lifecycle_phase": record["lifecycle_phase"],
                    "lifecycle_status": record["lifecycle_status"],
                    "provider": record["provider"],
                    "route": record["route"],
                    "slippage": record["slippage"],
                    "protected_exit": record["protected_exit"],
                    "message": record["message"],
                    "failure_reason": record.get("failure_reason"),
                    "request_payload": record["request_payload"],
                    "response_payload": record.get("response_payload", {}),
                    "updated_at": record.get("updated_at") or datetime.now(UTC).isoformat(),
                }
            )
            self._fallback_add_event(
                request_id=request_id,
                phase=request["lifecycle_phase"],
                status=request["lifecycle_status"],
                message=request["message"],
                payload=request["response_payload"] or {},
            )
            return request

    def get_execution_request(self, request_id: str) -> dict | None:
        try:
            request = self.db.get(ExecutionRequestModel, request_id)
            if request is None:
                return _FALLBACK_EXECUTION_REQUESTS.get(request_id)

            stmt = (
                select(ExecutionEventModel)
                .where(ExecutionEventModel.execution_request_id == request_id)
                .order_by(ExecutionEventModel.created_at.asc())
            )
            events = self.db.execute(stmt).scalars().all()
            return {
                "id": request.id,
                "app_mode": request.app_mode,
                "narrative_id": request.narrative_id,
                "candidate_id": request.candidate_id,
                "target_stage": request.target_stage,
                "decision": request.decision,
                "execution_mode": request.execution_mode,
                "lifecycle_phase": request.lifecycle_phase,
                "lifecycle_status": request.lifecycle_status,
                "provider": request.provider,
                "route": request.route,
                "slippage": request.slippage,
                "protected_exit": request.protected_exit,
                "message": request.message,
                "failure_reason": request.failure_reason,
                "request_payload": request.request_payload,
                "response_payload": request.response_payload,
                "created_at": _isoformat(request.created_at),
                "updated_at": _isoformat(request.updated_at),
                "events": [
                    {
                        "id": event.id,
                        "phase": event.lifecycle_phase,
                        "status": event.lifecycle_status,
                        "message": event.message,
                        "created_at": _isoformat(event.created_at),
                        "payload": event.payload,
                    }
                    for event in events
                ],
            }
        except Exception:
            self._rollback_quietly()
            return _FALLBACK_EXECUTION_REQUESTS.get(request_id)

    def list_execution_requests(self) -> list[dict]:
        try:
            stmt = select(ExecutionRequestModel).order_by(ExecutionRequestModel.created_at.asc())
            requests = self.db.execute(stmt).scalars().all()
            return [item for item in (self.get_execution_request(request.id) for request in requests) if item]
        except Exception:
            self._rollback_quietly()
            return sorted(
                _FALLBACK_EXECUTION_REQUESTS.values(),
                key=lambda item: item["created_at"],
            )

    def _merge_execution_truth(self, snapshot):
        try:
            requests = self.list_execution_requests()
        except Exception:
            return snapshot

        candidate_map = {candidate["id"]: candidate for candidate in snapshot["candidates"]}
        narrative_map = {narrative["id"]: narrative for narrative in snapshot["narratives"]}
        position_map = {position["candidate_id"]: position for position in snapshot["positions"]}
        replay_map = {session["narrative_id"]: session for session in snapshot["replay_sessions"]}
        stage_by_candidate = {
            candidate_id: position["stage"] for candidate_id, position in position_map.items()
        }

        for request in requests:
            candidate = candidate_map.get(request["candidate_id"])
            narrative = narrative_map.get(request["narrative_id"])
            if candidate is None or narrative is None:
                continue

            stage_from = stage_by_candidate.get(request["candidate_id"], "WATCH")
            stage_to = (
                request["target_stage"]
                if request["lifecycle_phase"] == "submitted"
                and request["lifecycle_status"] in {"pending", "success", "skipped"}
                else stage_from
            )

            snapshot["journal"].insert(
                0,
                {
                    "id": f'journal-{request["id"]}',
                    "timestamp": _format_timestamp(request["created_at"]),
                    "narrative_id": request["narrative_id"],
                    "candidate_id": request["candidate_id"],
                    "title": request["decision"],
                    "stage_from": stage_from,
                    "stage_to": stage_to,
                    "verdict": _verdict_for_status(request["lifecycle_status"]),
                    "summary": request["message"],
                    "rule_trace": [
                        {
                            "title": "Execution mode",
                            "verdict": "pass" if request["execution_mode"] == "PAPER" else "watch",
                            "detail": (
                                f'{request["execution_mode"]} was selected in {request["app_mode"]}. '
                                "PAPER is the validated end-to-end path in this repo; live wallet modes stay explicit about availability."
                            ),
                        },
                        {
                            "title": "Lifecycle phase",
                            "verdict": _verdict_for_status(request["lifecycle_status"]),
                            "detail": (
                                f'{request["lifecycle_phase"]} phase reported '
                                f'{request["lifecycle_status"]}.'
                            ),
                        },
                        {
                            "title": "Operating mode",
                            "verdict": "pass" if request["app_mode"] == "LIVE_MODE" else "watch",
                            "detail": (
                                "LIVE_MODE uses normalized AVE inputs as the source of truth."
                                if request["app_mode"] == "LIVE_MODE"
                                else "DEMO_MODE is a backend-owned replay surface and does not claim live wallet execution."
                            ),
                        },
                        {
                            "title": "Failure guard",
                            "verdict": "block" if request.get("failure_reason") else "pass",
                            "detail": request.get("failure_reason")
                            or "No adapter failure was reported.",
                        },
                    ],
                    "evidence_stack": [
                        {
                            "label": "Execution mode",
                            "reading": request["execution_mode"],
                            "delta": request["lifecycle_phase"],
                            "note": "Preview and submitted paths are journaled independently.",
                        },
                        {
                            "label": "Operating mode",
                            "reading": request["app_mode"],
                            "delta": request["execution_mode"],
                            "note": "Every execution record now captures both environment mode and wallet mode.",
                        },
                        {
                            "label": "Route",
                            "reading": request["route"],
                            "delta": request["slippage"],
                            "note": "Route and slippage come from the adapter-backed execution review.",
                        },
                        {
                            "label": "Lifecycle",
                            "reading": request["lifecycle_status"],
                            "delta": request["provider"],
                            "note": request.get("failure_reason")
                            or "Execution lifecycle remained inside the supported adapter path.",
                        },
                    ],
                    "narrative_snapshot": {
                        "strength": narrative["narrative_strength"],
                        "velocity": narrative["internal_velocity"],
                        "breadth": narrative["breadth_tokens"],
                        "pressure": narrative["allocation_pressure"],
                        "deteriorationRisk": narrative["deterioration_risk"],
                    },
                    "token_snapshot": {
                        "symbol": candidate["symbol"],
                        "investability": candidate["investability_score"],
                        "liquidity": candidate["liquidity_score"],
                        "overlap": candidate["overlap_narratives"],
                        "routeReadiness": candidate["route_readiness"],
                        "protectedExit": (
                            f'{candidate["protected_exit"]["hardStop"]} / '
                            f'{candidate["protected_exit"]["timeStop"]}'
                        ),
                    },
                    "execution_outcome": _execution_outcome(request),
                },
            )

            replay_session = replay_map.get(request["narrative_id"])
            if replay_session is None:
                replay_session = {
                    "id": f'replay-{request["narrative_id"]}',
                    "narrative_id": request["narrative_id"],
                    "title": f'{narrative["name"]} operating history',
                    "result": "Execution lifecycle journal is active.",
                    "snapshots": [],
                }
                snapshot["replay_sessions"].append(replay_session)
                replay_map[request["narrative_id"]] = replay_session

            replay_session["snapshots"].append(
                {
                    "id": f'step-{request["id"]}',
                    "timestamp": _format_timestamp(request["created_at"]),
                    "stage": stage_to,
                    "label": request["decision"],
                    "narrative_signal": (
                        f'{narrative["name"]} live metrics: strength {narrative["narrative_strength"]}, '
                        f'velocity {narrative["internal_velocity"]}, pressure {narrative["allocation_pressure"]}.'
                    ),
                    "decision": request["decision"],
                    "why_now": request["message"],
                    "change_set": [
                        f'App mode {request["app_mode"]}',
                        f'Execution mode {request["execution_mode"]}',
                        f'Phase {request["lifecycle_phase"]}',
                        f'Status {request["lifecycle_status"]}',
                    ],
                    "gate_delta": [
                        f'Route {request["route"]}',
                        f'Provider {request["provider"]}',
                        request.get("failure_reason") or "No adapter failure reported.",
                    ],
                    "execution": _execution_outcome(request),
                    "outcome": request["message"],
                }
            )

            if request["lifecycle_phase"] == "submitted" and request["lifecycle_status"] in {"pending", "success", "skipped"}:
                stage_by_candidate[request["candidate_id"]] = request["target_stage"]
                size = position_map.get(request["candidate_id"], {}).get("size", candidate["scout_size"])
                if request["target_stage"] in {"EXIT", "COOLDOWN"}:
                    size = "0.0%"
                position_map[request["candidate_id"]] = {
                    "id": f'position-{request["candidate_id"]}',
                    "narrative_id": request["narrative_id"],
                    "candidate_id": request["candidate_id"],
                    "symbol": candidate["symbol"],
                    "stage": request["target_stage"],
                    "size": size,
                    "average_basis": position_map.get(request["candidate_id"], {}).get(
                        "average_basis", "Execution-tracked"
                    ),
                    "pnl": position_map.get(request["candidate_id"], {}).get("pnl", "+0.0%"),
                    "status_note": request["message"],
                    "next_action": (
                        "Monitor live execution settlement."
                        if request["lifecycle_status"] == "pending"
                        else "Advance into cooldown discipline."
                        if request["target_stage"] in {"EXIT", "COOLDOWN"}
                        else "Review next deterministic transition."
                    ),
                    "stage_progress": build_stage_progress(request["target_stage"]),
                    "protected_exit": {
                        "hardStop": candidate["protected_exit"]["hardStop"],
                        "thesisBreak": candidate["protected_exit"]["thesisBreak"],
                        "cooldown": "24h if exited",
                    },
                    "ave_quote": (request.get("response_payload") or {}).get("ave_quote")
                    or position_map.get(request["candidate_id"], {}).get("ave_quote"),
                }

        snapshot["positions"] = sorted(position_map.values(), key=lambda item: item["symbol"])
        snapshot["replay_sessions"] = sorted(
            snapshot["replay_sessions"],
            key=lambda item: item["narrative_id"],
        )
        return snapshot
