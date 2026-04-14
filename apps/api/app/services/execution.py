from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.services.ave_trade import get_ave_trade_client


ORDER_STAGES = {"SCOUT", "ADD", "TRIM", "EXIT"}
VALIDATED_EXECUTION_MODE = "PAPER"


def _parse_percent(value: str) -> float:
    if value in {"N/A", "Blocked"}:
        return -1.0
    cleaned = value.replace("%", "").replace("+", "").replace("-", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return -1.0


def _slippage_budget(candidate: dict[str, Any]) -> str:
    liquidity = candidate.get("liquidity_score", 0)
    route = candidate.get("route_readiness", 0)
    budget = max(0.18, round(((100 - liquidity) * 0.014) + ((100 - route) * 0.009), 2))
    return f"{budget:.2f}%"


def _trade_required(target_stage: str) -> bool:
    return target_stage in ORDER_STAGES


def _decision_for_stage(target_stage: str, symbol: str) -> str:
    decisions = {
        "WATCH": f"Recorded WATCH discipline for {symbol}.",
        "SCOUT": f"Open SCOUT sizing in {symbol}.",
        "CONFIRM": f"Promote {symbol} thesis to CONFIRM without new size.",
        "ADD": f"Add capital to {symbol}.",
        "TRIM": f"Trim active {symbol} exposure.",
        "EXIT": f"Exit {symbol} and move to cooldown.",
        "COOLDOWN": f"Record cooldown state for {symbol}.",
    }
    return decisions.get(target_stage, f"Review {symbol} execution path.")


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class ExecutionResolution:
    mode: str
    phase: str
    status: str
    available: bool
    provider: str
    route: str
    slippage: str
    protected_exit: dict[str, Any]
    message: str
    failure_reason: str | None = None
    external_id: str | None = None
    response_payload: dict[str, Any] | None = None


class ExecutionAdapter(ABC):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    @abstractmethod
    def mode(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    def _preflight(self, candidate: dict[str, Any], target_stage: str) -> tuple[bool, str | None]:
        route_provider = candidate.get("route_provider", "none")
        route_ready = candidate.get("route_readiness", 0)
        liquidity = candidate.get("liquidity_score", 0)
        risk_coverage = candidate.get("risk_coverage", 0)
        hard_stop_defined = candidate["protected_exit"]["hardStop"] != "N/A"
        time_stop_defined = candidate["protected_exit"]["timeStop"] != "Blocked"

        if route_provider == "none":
            return False, "No execution route is available for this token."
        if target_stage in {"SCOUT", "ADD"} and (not hard_stop_defined or not time_stop_defined):
            return False, "Protected exits are incomplete for a capital-increasing trade."
        if target_stage in {"SCOUT", "ADD"} and risk_coverage < 65:
            return False, "Risk coverage is below the live execution floor."
        if target_stage in {"SCOUT", "ADD"} and (route_ready < 62 or liquidity < 62):
            return False, "Route readiness or liquidity is outside the allowed slippage budget."
        if target_stage in {"TRIM", "EXIT"} and (route_ready < 48 or liquidity < 45):
            return False, "Exit route quality is too weak to claim clean execution."
        return True, None

    def preview(self, candidate: dict[str, Any], target_stage: str) -> ExecutionResolution:
        available, failure_reason = self._preflight(candidate, target_stage)
        trade_required = _trade_required(target_stage)
        provider = self.provider_name if available else candidate.get("route_provider", "none")
        route = candidate.get("route_provider", "none")
        slippage = _slippage_budget(candidate) if trade_required else "0.00%"

        if not trade_required:
            return ExecutionResolution(
                mode=self.mode,
                phase="preview",
                status="ready",
                available=True,
                provider=provider,
                route=route,
                slippage=slippage,
                protected_exit=candidate["protected_exit"],
                message="The next step is a state transition only. No fill will be sent if submitted.",
            )

        if available:
            return ExecutionResolution(
                mode=self.mode,
                phase="preview",
                status="ready",
                available=True,
                provider=provider,
                route=route,
                slippage=slippage,
                protected_exit=candidate["protected_exit"],
                message="Execution path is available within the current slippage and risk budget.",
            )

        return ExecutionResolution(
            mode=self.mode,
            phase="preview",
            status="blocked" if route != "none" else "unavailable",
            available=False,
            provider=provider,
            route=route,
            slippage=slippage if route != "none" else "N/A",
            protected_exit=candidate["protected_exit"],
            message="Execution preview did not clear the deterministic route and risk checks.",
            failure_reason=failure_reason,
        )

    @abstractmethod
    def submit(self, candidate: dict[str, Any], target_stage: str) -> ExecutionResolution:
        raise NotImplementedError

    def status(self, request: dict[str, Any]) -> ExecutionResolution:
        return ExecutionResolution(
            mode=request["execution_mode"],
            phase=request["lifecycle_phase"],
            status=request["lifecycle_status"],
            available=request["lifecycle_status"] in {"ready", "pending", "success", "skipped"},
            provider=request["provider"],
            route=request["route"],
            slippage=request["slippage"],
            protected_exit=request["protected_exit"],
            message=request["message"],
            failure_reason=request.get("failure_reason"),
            external_id=request.get("response_payload", {}).get("external_id"),
            response_payload=request.get("response_payload", {}),
        )


class PaperExecutionAdapter(ExecutionAdapter):
    @property
    def mode(self) -> str:
        return "PAPER"

    @property
    def provider_name(self) -> str:
        return "paper-ledger"

    def submit(self, candidate: dict[str, Any], target_stage: str) -> ExecutionResolution:
        preview = self.preview(candidate, target_stage)
        if preview.status != "ready":
            return ExecutionResolution(
                mode=self.mode,
                phase="submitted",
                status=preview.status,
                available=False,
                provider=preview.provider,
                route=preview.route,
                slippage=preview.slippage,
                protected_exit=preview.protected_exit,
                message="Paper submission was not created because the deterministic preview checks did not pass.",
                failure_reason=preview.failure_reason,
                response_payload={"validated_mode": self.mode, "submitted": False},
            )

        if not _trade_required(target_stage):
            return ExecutionResolution(
                mode=self.mode,
                phase="submitted",
                status="skipped",
                available=True,
                provider=self.provider_name,
                route=preview.route,
                slippage="0.00%",
                protected_exit=preview.protected_exit,
                message="State transition recorded on the validated PAPER path without a simulated fill.",
                response_payload={"validated_mode": self.mode, "submitted": False, "skipped_fill": True},
            )

        return ExecutionResolution(
            mode=self.mode,
            phase="submitted",
            status="success",
            available=True,
            provider=self.provider_name,
            route=preview.route,
            slippage=preview.slippage,
            protected_exit=preview.protected_exit,
            message="Paper execution completed on the validated PAPER path and the request lifecycle is now closed.",
            response_payload={"validated_mode": self.mode, "submitted": True, "ledger": "paper"},
        )

    def preview(self, candidate: dict[str, Any], target_stage: str) -> ExecutionResolution:
        preview = super().preview(candidate, target_stage)
        trade_required = _trade_required(target_stage)
        if preview.status != "ready":
            return ExecutionResolution(
                mode=self.mode,
                phase="preview",
                status=preview.status,
                available=False,
                provider=preview.provider,
                route=preview.route,
                slippage=preview.slippage,
                protected_exit=preview.protected_exit,
                message="PAPER is the validated path, but this trade is blocked by deterministic route or risk checks.",
                failure_reason=preview.failure_reason,
                response_payload={"validated_mode": self.mode, "trade_required": trade_required},
            )

        message = (
            "No order will be sent. The transition will be journaled on the validated PAPER path."
            if not trade_required
            else "PAPER is the validated end-to-end execution path in this repo, and the deterministic checks passed."
        )
        return ExecutionResolution(
            mode=self.mode,
            phase=preview.phase,
            status=preview.status,
            available=preview.available,
            provider=preview.provider,
            route=preview.route,
            slippage=preview.slippage,
            protected_exit=preview.protected_exit,
            message=message,
            failure_reason=preview.failure_reason,
            response_payload={"validated_mode": self.mode, "trade_required": trade_required},
        )


class RemoteExecutionAdapter(ExecutionAdapter):
    base_url_setting_name: str
    api_key_setting_name: str

    def _credential_error(self) -> str | None:
        raise NotImplementedError

    def _resolve_remote_config(self) -> tuple[str | None, dict[str, str], str | None]:
        base_url = getattr(self.settings, self.base_url_setting_name)
        api_key = getattr(self.settings, self.api_key_setting_name)
        headers: dict[str, str] = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return base_url, headers, self._credential_error()

    def preview(self, candidate: dict[str, Any], target_stage: str) -> ExecutionResolution:
        base_preview = super().preview(candidate, target_stage)
        if base_preview.status != "ready":
            return base_preview
        if not _trade_required(target_stage):
            return ExecutionResolution(
                mode=self.mode,
                phase="preview",
                status="ready",
                available=True,
                provider=self.provider_name,
                route=base_preview.route,
                slippage="0.00%",
                protected_exit=base_preview.protected_exit,
                message="No live order will be sent for this stage. The transition can be journaled without wallet credentials.",
                response_payload={"trade_required": False},
            )
        if self.settings.app_mode != "LIVE_MODE":
            return ExecutionResolution(
                mode=self.mode,
                phase="preview",
                status="unavailable",
                available=False,
                provider=self.provider_name,
                route=base_preview.route,
                slippage=base_preview.slippage,
                protected_exit=base_preview.protected_exit,
                message=(
                    f"{self.mode} is only a truthful execution path in LIVE_MODE. "
                    f"{VALIDATED_EXECUTION_MODE} remains the validated end-to-end mode in this repo."
                ),
                failure_reason="live_mode_required_for_live_wallet",
                response_payload={"trade_required": True, "validated_mode": VALIDATED_EXECUTION_MODE},
            )
        if not self.settings.live_execution_enabled:
            return ExecutionResolution(
                mode=self.mode,
                phase="preview",
                status="unavailable",
                available=False,
                provider=self.provider_name,
                route=base_preview.route,
                slippage=base_preview.slippage,
                protected_exit=base_preview.protected_exit,
                message="Live execution is disabled in this deployment.",
                failure_reason="live_execution_disabled",
                response_payload={"trade_required": True},
            )

        base_url, _, credential_error = self._resolve_remote_config()
        if credential_error:
            return ExecutionResolution(
                mode=self.mode,
                phase="preview",
                status="unavailable",
                available=False,
                provider=self.provider_name,
                route=base_preview.route,
                slippage=base_preview.slippage,
                protected_exit=base_preview.protected_exit,
                message="Execution credentials are unavailable for this wallet mode.",
                failure_reason=credential_error,
                response_payload={"trade_required": True},
            )
        if not base_url:
            return ExecutionResolution(
                mode=self.mode,
                phase="preview",
                status="unavailable",
                available=False,
                provider=self.provider_name,
                route=base_preview.route,
                slippage=base_preview.slippage,
                protected_exit=base_preview.protected_exit,
                message="Execution adapter endpoint is not configured for this wallet mode.",
                failure_reason="execution_adapter_unconfigured",
                response_payload={"trade_required": True},
            )
        return ExecutionResolution(
            mode=self.mode,
            phase="preview",
            status="ready",
            available=True,
            provider=self.provider_name,
            route=base_preview.route,
            slippage=base_preview.slippage,
            protected_exit=base_preview.protected_exit,
            message="Live execution preview is ready and the remote wallet adapter is reachable.",
            response_payload={"trade_required": True},
        )

    def submit(self, candidate: dict[str, Any], target_stage: str) -> ExecutionResolution:
        preview = self.preview(candidate, target_stage)
        if preview.status != "ready":
            return ExecutionResolution(
                mode=self.mode,
                phase="submitted",
                status=preview.status,
                available=False,
                provider=preview.provider,
                route=preview.route,
                slippage=preview.slippage,
                protected_exit=preview.protected_exit,
                message="Live submission was not attempted because the preview path is unavailable.",
                failure_reason=preview.failure_reason,
                response_payload=preview.response_payload or {"submitted": False},
            )

        if not _trade_required(target_stage):
            return ExecutionResolution(
                mode=self.mode,
                phase="submitted",
                status="skipped",
                available=True,
                provider=self.provider_name,
                route=preview.route,
                slippage="0.00%",
                protected_exit=preview.protected_exit,
                message="No order was sent because this stage change does not require execution.",
                response_payload={"submitted": False, "skipped_fill": True},
            )

        base_url, headers, _ = self._resolve_remote_config()
        payload = {
            "symbol": candidate["symbol"],
            "candidate_id": candidate["id"],
            "target_stage": target_stage,
            "route": candidate.get("route_provider", "unknown"),
            "slippage_budget": preview.slippage,
            "protected_exit": candidate["protected_exit"],
        }
        try:
            response = httpx.post(f"{base_url}/execute", json=payload, headers=headers, timeout=10.0)
            response.raise_for_status()
            body = response.json() if response.content else {}
        except ValueError as exc:
            return ExecutionResolution(
                mode=self.mode,
                phase="submitted",
                status="failed",
                available=False,
                provider=self.provider_name,
                route=preview.route,
                slippage=preview.slippage,
                protected_exit=preview.protected_exit,
                message="Remote execution adapter returned a non-JSON submit response.",
                failure_reason=f"execution_adapter_invalid_json: {exc}",
                response_payload={"submitted": True},
            )
        except httpx.HTTPError as exc:
            return ExecutionResolution(
                mode=self.mode,
                phase="submitted",
                status="failed",
                available=False,
                provider=self.provider_name,
                route=preview.route,
                slippage=preview.slippage,
                protected_exit=preview.protected_exit,
                message="Remote execution adapter rejected or failed the order request.",
                failure_reason=f"execution_adapter_request_failed: {exc}",
                response_payload={"submitted": True},
            )

        response_payload = body if isinstance(body, dict) else {"raw_response": body}
        external_id = str(response_payload.get("execution_id") or response_payload.get("id") or "")
        remote_status = str(response_payload.get("status") or "pending").lower()
        if remote_status not in {"pending", "success", "failed"}:
            remote_status = "pending"
        if remote_status == "pending" and not external_id:
            return ExecutionResolution(
                mode=self.mode,
                phase="submitted",
                status="failed",
                available=False,
                provider=self.provider_name,
                route=preview.route,
                slippage=preview.slippage,
                protected_exit=preview.protected_exit,
                message="Remote execution returned a pending state without a trackable execution identifier.",
                failure_reason="missing_remote_execution_id",
                response_payload=response_payload,
            )

        return ExecutionResolution(
            mode=self.mode,
            phase="submitted",
            status=remote_status,
            available=remote_status in {"pending", "success"},
            provider=self.provider_name,
            route=preview.route,
            slippage=preview.slippage,
            protected_exit=preview.protected_exit,
            message="Remote execution adapter accepted the order request."
            if remote_status in {"pending", "success"}
            else "Remote execution adapter returned a failed execution state.",
            failure_reason=None
            if remote_status in {"pending", "success"}
            else str(response_payload.get("error") or "remote_execution_failed"),
            external_id=external_id or None,
            response_payload=response_payload,
        )

    def status(self, request: dict[str, Any]) -> ExecutionResolution:
        response_payload = request.get("response_payload", {})
        external_id = response_payload.get("external_id")
        if not external_id:
            if request["lifecycle_status"] == "pending":
                return ExecutionResolution(
                    mode=request["execution_mode"],
                    phase="submitted",
                    status="failed",
                    available=False,
                    provider=request["provider"],
                    route=request["route"],
                    slippage=request["slippage"],
                    protected_exit=request["protected_exit"],
                    message="Pending execution cannot be refreshed because the remote adapter did not return a trackable execution identifier.",
                    failure_reason="missing_remote_execution_id",
                    response_payload=response_payload,
                )
            return super().status(request)

        base_url, headers, credential_error = self._resolve_remote_config()
        if credential_error or not base_url:
            return super().status(request)

        try:
            response = httpx.get(f"{base_url}/executions/{external_id}", headers=headers, timeout=10.0)
            response.raise_for_status()
            body = response.json() if response.content else {}
        except ValueError:
            return super().status(request)
        except httpx.HTTPError:
            return super().status(request)

        payload = body if isinstance(body, dict) else response_payload
        remote_status = str(payload.get("status") or request["lifecycle_status"]).lower()
        if remote_status not in {"pending", "success", "failed"}:
            remote_status = request["lifecycle_status"]

        return ExecutionResolution(
            mode=request["execution_mode"],
            phase="submitted",
            status=remote_status,
            available=remote_status in {"pending", "success"},
            provider=request["provider"],
            route=request["route"],
            slippage=request["slippage"],
            protected_exit=request["protected_exit"],
            message=str(payload.get("message") or request["message"]),
            failure_reason=str(payload.get("error")) if remote_status == "failed" and payload.get("error") else request.get("failure_reason"),
            external_id=external_id,
            response_payload=payload,
        )


class LiveChainWalletExecutionAdapter(RemoteExecutionAdapter):
    base_url_setting_name = "chain_executor_base_url"
    api_key_setting_name = "chain_executor_api_key"

    @property
    def mode(self) -> str:
        return "LIVE_CHAIN_WALLET"

    @property
    def provider_name(self) -> str:
        return "chain-wallet-adapter"

    def _credential_error(self) -> str | None:
        if not self.settings.chain_wallet_address:
            return "missing_chain_wallet_address"
        if not self.settings.chain_wallet_private_key:
            return "missing_chain_wallet_private_key"
        return None


class LiveProxyWalletExecutionAdapter(RemoteExecutionAdapter):
    base_url_setting_name = "proxy_executor_base_url"
    api_key_setting_name = "proxy_executor_api_key"

    @property
    def mode(self) -> str:
        return "LIVE_PROXY_WALLET"

    @property
    def provider_name(self) -> str:
        return "proxy-wallet-adapter"

    def _credential_error(self) -> str | None:
        if not self.settings.proxy_wallet_id:
            return "missing_proxy_wallet_id"
        return None


class ExecutionService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.adapters: dict[str, ExecutionAdapter] = {
            "PAPER": PaperExecutionAdapter(self.settings),
            "LIVE_CHAIN_WALLET": LiveChainWalletExecutionAdapter(self.settings),
            "LIVE_PROXY_WALLET": LiveProxyWalletExecutionAdapter(self.settings),
        }

    def _adapter(self, mode: str) -> ExecutionAdapter:
        adapter = self.adapters.get(mode)
        if adapter is None:
            raise ValueError(f"Unsupported execution mode: {mode}")
        return adapter

    def preview(self, candidate: dict[str, Any], target_stage: str, mode: str) -> dict[str, Any]:
        record = self._resolution_to_record(
            candidate=candidate,
            target_stage=target_stage,
            resolution=self._adapter(mode).preview(candidate, target_stage),
        )
        return self._attach_ave_quote(record=record, candidate=candidate, mode=mode)

    def submit(self, candidate: dict[str, Any], target_stage: str, mode: str) -> dict[str, Any]:
        record = self._resolution_to_record(
            candidate=candidate,
            target_stage=target_stage,
            resolution=self._adapter(mode).submit(candidate, target_stage),
        )
        return self._attach_ave_quote(record=record, candidate=candidate, mode=mode)

    def refresh_status(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._resolution_to_record(
            candidate={
                "id": request["candidate_id"],
                "symbol": request["request_payload"].get("symbol", request["candidate_id"]),
                "protected_exit": request["protected_exit"],
            },
            target_stage=request["target_stage"],
            resolution=self._adapter(request["execution_mode"]).status(request),
        )

    def _resolution_to_record(
        self,
        *,
        candidate: dict[str, Any],
        target_stage: str,
        resolution: ExecutionResolution,
    ) -> dict[str, Any]:
        now = _timestamp()
        return {
            "app_mode": self.settings.app_mode,
            "candidate_id": candidate["id"],
            "target_stage": target_stage,
            "decision": _decision_for_stage(target_stage, candidate["symbol"]),
            "execution_mode": resolution.mode,
            "lifecycle_phase": resolution.phase,
            "lifecycle_status": resolution.status,
            "available": resolution.available,
            "provider": resolution.provider,
            "route": resolution.route,
            "slippage": resolution.slippage,
            "protected_exit": resolution.protected_exit,
            "message": resolution.message,
            "failure_reason": resolution.failure_reason,
            "response_payload": {
                **(resolution.response_payload or {}),
                **({"external_id": resolution.external_id} if resolution.external_id else {}),
            },
            "request_payload": {
                "symbol": candidate["symbol"],
                "target_stage": target_stage,
                "trade_required": _trade_required(target_stage),
                "route": candidate.get("route_provider", "none"),
                "protected_exit": candidate["protected_exit"],
            },
            "created_at": now,
            "updated_at": now,
        }

    def _attach_ave_quote(
        self,
        *,
        record: dict[str, Any],
        candidate: dict[str, Any],
        mode: str,
    ) -> dict[str, Any]:
        if mode != "PAPER" or not record["request_payload"]["trade_required"]:
            return record

        try:
            quote = get_ave_trade_client().fetch_swap_quote(
                token_id=candidate["id"],
                fallback_route=candidate.get("route_provider"),
            )
        except Exception:
            quote = None

        if quote is None:
            return record

        response_payload = dict(record.get("response_payload") or {})
        response_payload["ave_quote"] = quote
        record["response_payload"] = response_payload
        return record
