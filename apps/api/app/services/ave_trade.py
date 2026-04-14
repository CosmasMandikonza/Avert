from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from functools import lru_cache
from typing import Any

import httpx

from app.config import Settings, get_settings


_SUCCESS_CODES = {0, 200}
_EVM_NATIVE = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
_SUPPORTED_CHAINS = {"solana", "bsc", "eth", "base"}
_CHAIN_DECIMALS = {
    "solana": 9,
    "bsc": 18,
    "eth": 18,
    "base": 18,
}


def _format_amount(raw_amount: str, decimals: int | None) -> str | None:
    if decimals is None:
        return None
    try:
        value = Decimal(raw_amount)
    except (InvalidOperation, TypeError):
        return None
    scaled = value / (Decimal(10) ** decimals)
    normalized = format(scaled.normalize(), "f")
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")
    return normalized or "0"


def _to_smallest_unit(amount: str, decimals: int) -> str:
    try:
        value = Decimal(amount)
    except (InvalidOperation, TypeError):
        value = Decimal("0.001")
    scaled = (value * (Decimal(10) ** decimals)).quantize(Decimal("1"), rounding=ROUND_DOWN)
    return str(int(scaled))


def _native_input_token(chain: str) -> str | None:
    normalized = chain.lower()
    if normalized == "solana":
        return "sol"
    if normalized in {"bsc", "eth", "base"}:
        return _EVM_NATIVE
    return None


def _parse_token_id(token_id: str) -> tuple[str, str] | None:
    if not token_id or "-" not in token_id:
        return None
    address, chain = token_id.rsplit("-", 1)
    normalized_chain = chain.lower().strip()
    if not address or normalized_chain not in _SUPPORTED_CHAINS:
        return None
    return address.strip(), normalized_chain


def _extract_route(data: dict[str, Any], fallback_route: str | None) -> str | None:
    amms = data.get("amms")
    if isinstance(amms, list):
        labels = [str(item).strip() for item in amms if str(item).strip()]
        if labels:
            return " -> ".join(labels[:3])
    for key in ("route", "dex", "amm"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    if fallback_route and fallback_route != "none":
        return fallback_route
    return None


def _extract_price_impact(data: dict[str, Any]) -> str | None:
    for key in ("priceImpact", "priceImpactPct", "price_impact", "price_impact_pct"):
        value = data.get(key)
        if value is None or value == "":
            continue
        text = str(value).strip()
        return text if text.endswith("%") else f"{text}%"
    return None


def _extract_gas_estimate(data: dict[str, Any]) -> str | None:
    gas_limit = data.get("gasLimit")
    if gas_limit not in {None, ""}:
        return f"gas {gas_limit}"

    priority_fee = data.get("priorityFee")
    bundle_tip = data.get("bundleTip")
    parts = []
    if priority_fee not in {None, ""}:
        parts.append(f"priority {priority_fee}")
    if bundle_tip not in {None, ""}:
        parts.append(f"bundle {bundle_tip}")
    if parts:
        return " / ".join(parts)
    return None


@dataclass
class AVESwapQuote:
    estimated_output: str
    estimated_output_display: str | None
    output_decimals: int | None
    route: str | None
    price_impact: str | None
    gas_estimate: str | None
    spender: str | None
    source_endpoint: str
    availability_note: str | None = None

    def to_record(self) -> dict[str, Any]:
        return {
            "estimated_output": self.estimated_output,
            "estimated_output_display": self.estimated_output_display,
            "output_decimals": self.output_decimals,
            "route": self.route,
            "price_impact": self.price_impact,
            "gas_estimate": self.gas_estimate,
            "spender": self.spender,
            "source_endpoint": self.source_endpoint,
            "availability_note": self.availability_note,
        }


class AVETradeClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.base_url = self.settings.ave_trade_api_base_url.rstrip("/")
        self.api_key = self.settings.ave_api_key
        self.timeout = self.settings.ave_trade_request_timeout_seconds

    def fetch_swap_quote(
        self,
        *,
        token_id: str,
        fallback_route: str | None = None,
    ) -> dict[str, Any] | None:
        if not self.api_key:
            return None

        parsed = _parse_token_id(token_id)
        if parsed is None:
            return None
        token_address, chain = parsed
        native_input = _native_input_token(chain)
        decimals = _CHAIN_DECIMALS.get(chain)
        if native_input is None or decimals is None:
            return None

        payload = {
            "chain": chain,
            "inAmount": _to_smallest_unit(self.settings.ave_trade_preview_amount, decimals),
            "inTokenAddress": native_input,
            "outTokenAddress": token_address,
            "swapType": "buy",
        }
        headers = {
            "AVE-ACCESS-KEY": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            response = httpx.post(
                f"{self.base_url}/v1/thirdParty/chainWallet/getAmountOut",
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            body = response.json() if response.content else {}
        except (httpx.HTTPError, ValueError):
            return None

        if not isinstance(body, dict):
            return None
        status = body.get("status")
        if status not in _SUCCESS_CODES:
            return None
        data = body.get("data")
        if not isinstance(data, dict):
            return None

        estimate_out = str(data.get("estimateOut") or "").strip()
        if not estimate_out:
            return None

        output_decimals = data.get("decimals")
        try:
            decimals_value = int(output_decimals) if output_decimals not in {None, ""} else None
        except (TypeError, ValueError):
            decimals_value = None

        route = _extract_route(data, fallback_route)
        price_impact = _extract_price_impact(data)
        gas_estimate = _extract_gas_estimate(data)
        availability_note = None
        if not price_impact or not gas_estimate:
            availability_note = (
                "AVE quote preview is live. This endpoint returns amount-out truth; "
                "route/gas fields stay best-effort unless AVE includes them in the response."
            )

        quote = AVESwapQuote(
            estimated_output=estimate_out,
            estimated_output_display=_format_amount(estimate_out, decimals_value),
            output_decimals=decimals_value,
            route=route,
            price_impact=price_impact,
            gas_estimate=gas_estimate,
            spender=str(data.get("spender")).strip() or None,
            source_endpoint="/v1/thirdParty/chainWallet/getAmountOut",
            availability_note=availability_note,
        )
        return quote.to_record()


@lru_cache
def get_ave_trade_client() -> AVETradeClient:
    return AVETradeClient()
