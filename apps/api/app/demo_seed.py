from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.services.ave_contracts import NormalizedAVENarrativeInput, NormalizedAVETokenInput


STAGE_ORDER = [
    "WATCH",
    "SCOUT",
    "CONFIRM",
    "ADD",
    "TRIM",
    "EXIT",
    "COOLDOWN",
]
WORKSPACE_DEMO_FILE = Path(__file__).resolve().parents[2] / "web" / "lib" / "demo" / "avert-demo.json"
CONTAINER_DEMO_FILE = Path(__file__).resolve().parents[1] / "shared" / "avert-demo.json"
DEMO_FILE = WORKSPACE_DEMO_FILE if WORKSPACE_DEMO_FILE.exists() else CONTAINER_DEMO_FILE
AVE_INTEGRATION_ENDPOINTS = [
    "GET /ranks/topics",
    "GET /ranks?topic={topic}",
    "GET /contracts/{token_id}",
    "GET /signals/public/list",
    "GET /address/smart_wallet/list",
    "GET /tokens/trending",
    "GET /tokens/holders/{token_id}",
    "GET /tokens/{token_id}",
    "GET /supported_chains",
    "GET /klines/token/{token_id}",
    "POST /wallet/swap/quote",
    "WSS price subscription",
    "WSS heartbeat",
]
AVE_INTEGRATION_TRACKS = ["Monitoring Skill", "Trading Skill", "Complete Application"]


def _normalize_live_price_token_id(token_id: str) -> str:
    if "-" not in token_id:
        return token_id
    address, chain = token_id.rsplit("-", 1)
    normalized_address = address.lower() if address.startswith("0x") else address
    return f"{normalized_address}-{chain.lower()}"


def _lookup_live_price(
    live_prices: dict[str, dict[str, Any]],
    token_id: str,
) -> float | None:
    direct = live_prices.get(token_id, {}).get("price_usd")
    if direct is not None:
        return direct
    return live_prices.get(_normalize_live_price_token_id(token_id), {}).get("price_usd")


def clamp(value: float, minimum: int = 0, maximum: int = 100) -> int:
    return max(minimum, min(maximum, round(value)))


def format_signed_percent(value: float) -> str:
    return f"{value:+.1f}%"


def format_stop(value: float | None) -> str:
    return "N/A" if value is None else f"-{value:.1f}%"


def format_hours(value: int | None) -> str:
    return "Blocked" if value is None else f"{value}h review window"


def build_stage_progress(stage: str) -> list[dict[str, Any]]:
    reached_index = STAGE_ORDER.index(stage)
    return [{"stage": item, "reached": index <= reached_index} for index, item in enumerate(STAGE_ORDER)]


def compute_narrative_strength(narrative: dict[str, Any]) -> int:
    return clamp(
        narrative["flowScore"] * 0.22
        + narrative["accelerationScore"] * 0.26
        + narrative["breadthScore"] * 0.20
        + narrative["priceExpansionScore"] * 0.16
        + narrative["persistenceScore"] * 0.16
    )


def compute_flow_acceleration(narrative: dict[str, Any]) -> int:
    return clamp(
        narrative["accelerationScore"] * 0.40
        + narrative["flowScore"] * 0.24
        + narrative["priceExpansionScore"] * 0.16
        + narrative["breadthScore"] * 0.10
        + narrative["aveRankDelta"] * 6
    )


def compute_deterioration_risk(narrative: dict[str, Any]) -> int:
    return clamp(
        narrative["deteriorationBase"] * 0.45
        + narrative["crowdingScore"] * 0.35
        + narrative["leaderConcentration"] * 0.20
    )


def compute_velocity(narrative: dict[str, Any], flow_acceleration: int) -> int:
    return clamp(
        flow_acceleration * 0.38
        + narrative["breadthScore"] * 0.24
        + narrative["priceExpansionScore"] * 0.18
        + narrative["persistenceScore"] * 0.12
        + narrative["flowScore"] * 0.08
    )


def compute_capital_demand(
    narrative: dict[str, Any],
    narrative_strength: int,
    flow_acceleration: int,
) -> int:
    return clamp(
        narrative["capitalDemandScore"] * 0.46
        + flow_acceleration * 0.18
        + narrative["breadthScore"] * 0.12
        + narrative["priceExpansionScore"] * 0.10
        + max(0, narrative["aveRankDelta"]) * 5
        + narrative_strength * 0.14
    )


def compute_allocation_pressure(
    narrative: dict[str, Any],
    capital_demand: int,
    deterioration_risk: int,
) -> int:
    return clamp(
        capital_demand * 0.44
        + narrative["crowdingScore"] * 0.30
        + narrative["leaderConcentration"] * 0.16
        + deterioration_risk * 0.10
    )


def compute_narrative_state(strength: int, risk: int, acceleration: int) -> str:
    if risk >= 82:
        return "invalidated"
    if strength >= 80 and risk < 62:
        return "strengthening"
    if strength >= 66 and acceleration >= 64 and risk < 72:
        return "emerging"
    if risk >= 64 and strength >= 62:
        return "crowded"
    return "fading"


def compute_stage_bias(strength: int, risk: int, hint: str) -> str:
    if risk >= 78:
        return "EXIT"
    if risk >= 68 and strength >= 66:
        return "TRIM"
    if strength >= 84 and risk < 58:
        return "ADD"
    if strength >= 74 and risk < 64:
        return "CONFIRM"
    if strength >= 64:
        return "SCOUT"
    return hint


def compute_investability(token: dict[str, Any]) -> int:
    overlap_penalty = len(token["overlapNarratives"]) * 5
    return clamp(
        token["leadership"] * 0.24
        + token["liquidity"] * 0.24
        + token["routeStability"] * 0.18
        + token["riskCoverage"] * 0.16
        + token["smartFlowAlignment"] * 0.18
        - token["toxicity"] * 0.18
        - overlap_penalty
    )


def compute_readiness_stage(token: dict[str, Any], narrative_strength: int) -> str:
    score = compute_investability(token) * 0.6 + narrative_strength * 0.4 - token["toxicity"] * 0.15
    if token["hardStopPct"] is None:
        return "WATCH"
    if score >= 82:
        return "ADD"
    if score >= 72:
        return "CONFIRM"
    if score >= 60:
        return "SCOUT"
    return "WATCH"


def create_narrative_evidence(
    narrative: dict[str, Any],
    risk: int,
    flow_acceleration: int,
) -> list[dict[str, Any]]:
    notes = narrative["notes"]
    return [
        {
            "label": "Velocity impulse",
            "detail": notes[0],
            "delta": str(flow_acceleration),
            "tone": "up" if flow_acceleration >= 70 else "watch",
        },
        {
            "label": "Breadth quality",
            "detail": notes[1] if len(notes) > 1 else "Breadth participation is still developing.",
            "delta": f'{narrative["breadthTokens"]} tokens',
            "tone": "up" if narrative["breadthScore"] >= 68 else "watch",
        },
        {
            "label": "Deterioration risk",
            "detail": notes[2] if len(notes) > 2 else "Deterioration risk is elevated and needs monitoring.",
            "delta": str(risk),
            "tone": "down" if risk >= 68 else "watch",
        },
    ]


def create_allocation_gates(narrative: dict[str, Any], candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    top_candidate = candidates[0] if candidates else None
    return [
        {
            "title": "Narrative strength is above deployment threshold",
            "verdict": "pass" if narrative["narrative_strength"] >= 72 else "block",
            "detail": (
                f'Narrative strength {narrative["narrative_strength"]} '
                f'with velocity {narrative["internal_velocity"]}.'
            ),
        },
        {
            "title": "Allocation pressure remains within the rotation budget",
            "verdict": "watch" if narrative["allocation_pressure"] >= 80 else "pass",
            "detail": (
                f'Allocation pressure {narrative["allocation_pressure"]}; '
                f'competing narratives {", ".join(narrative["competing_narratives"])}.'
            ),
        },
        {
            "title": "Deterioration risk stays contained",
            "verdict": "watch" if narrative["deterioration_risk"] >= 72 else "pass",
            "detail": (
                f'Deterioration risk {narrative["deterioration_risk"]} driven by '
                f'leader concentration {narrative["leader_concentration"]}.'
            ),
        },
        {
            "title": "Protected exits exist on the lead expression",
            "verdict": "pass"
            if top_candidate and top_candidate["protected_exit"]["hardStop"] != "N/A"
            else "block",
            "detail": (
                f'{top_candidate["symbol"]} carries a hard stop '
                f'{top_candidate["protected_exit"]["hardStop"]} and '
                f'{top_candidate["protected_exit"]["timeStop"]}.'
                if top_candidate
                else "No lead candidate available."
            ),
        },
    ]


def build_default_budget(narrative: NormalizedAVENarrativeInput) -> dict[str, str]:
    scout = clamp(narrative.flowScore * 0.012, minimum=0, maximum=20) / 10
    confirm = clamp(narrative.breadthScore * 0.026, minimum=0, maximum=35) / 10
    add = clamp(narrative.accelerationScore * 0.046, minimum=0, maximum=55) / 10
    cooldown_hours = max(18, 42 - round(narrative.accelerationScore / 4))
    return {
        "watch": "0%",
        "scout": f"{max(0.2, scout):.1f}%",
        "confirm": f"{max(0.6, confirm):.1f}%",
        "add": f"{max(1.1, add):.1f}%",
        "trim": "Harvest 25%" if narrative.crowdingScore < 68 else "Harvest 35%",
        "cooldown": f"{cooldown_hours}h",
    }


def build_live_raw_data(
    narratives: list[NormalizedAVENarrativeInput],
    tokens: list[NormalizedAVETokenInput],
    *,
    mode: str = "LIVE_MODE",
    live_prices: dict[str, dict[str, Any]] | None = None,
    supported_chains: list[str] | None = None,
) -> dict[str, Any]:
    live_prices = live_prices or {}
    supported_chains = supported_chains or []
    return {
        "status": {
            "mode": mode,
            "posture": "Live AVE ingestion is active. Snapshot truth comes from normalized AVE payloads and persisted execution state.",
            "allocatedCapital": "$0K",
            "dryPowder": "$400K",
            "openRisk": "0.0R",
        },
        "ave_integration": {
            "endpoints_used": AVE_INTEGRATION_ENDPOINTS,
            "total_endpoints": len(AVE_INTEGRATION_ENDPOINTS),
            "narratives_ingested": len(narratives),
            "tokens_scored": len(tokens),
            "skills_version": "v2.4.0",
            "mode": mode,
            "tracks": AVE_INTEGRATION_TRACKS,
            "supported_chains": supported_chains,
        },
        "narratives": [
            {
                "id": item.id,
                "name": item.name,
                "thesis": item.thesis,
                "aveTopicRank": item.aveTopicRank,
                "aveRankDelta": item.aveRankDelta,
                "flowScore": item.flowScore,
                "accelerationScore": item.accelerationScore,
                "breadthScore": item.breadthScore,
                "breadthTokens": item.breadthTokens,
                "priceExpansionScore": item.priceExpansionScore,
                "persistenceScore": item.persistenceScore,
                "capitalDemandScore": item.capitalDemandScore,
                "crowdingScore": item.crowdingScore,
                "leaderConcentration": item.leaderConcentration,
                "deteriorationBase": item.deteriorationBase,
                "stageBiasHint": item.stageBiasHint,
                "competingNarratives": item.competingNarratives,
                "notes": item.notes,
                "tokenIds": item.tokenIds,
                "budget": item.budget,
                "smartMoneySignal": item.smartMoneySignal,
            }
            for item in narratives
        ],
        "tokens": [
            {
                "id": item.id,
                "narrativeId": item.narrativeId,
                "symbol": item.symbol,
                "name": item.name,
                "leadership": item.leadership,
                "liquidity": item.liquidity,
                "routeStability": item.routeStability,
                "riskCoverage": item.riskCoverage,
                "smartFlowAlignment": item.smartFlowAlignment,
                "toxicity": item.toxicity,
                "scoutSizePct": item.scoutSizePct,
                "overlapNarratives": item.overlapNarratives,
                "priceExpansionPct": item.priceExpansionPct,
                "breadthContribution": item.breadthContribution,
                "thesisBreak": item.thesisBreak,
                "hardStopPct": item.hardStopPct,
                "timeStopHours": item.timeStopHours,
                "routeProvider": item.routeProvider,
                "signalConfirmations": item.signalConfirmations,
                "trendingOnAVE": item.trendingOnAVE,
                "topHolderPct": item.topHolderPct,
                "logoUrl": item.logoUrl,
                "klineTrend": item.klineTrend,
                "livePriceUsd": _lookup_live_price(live_prices, item.id),
                "note": item.note,
            }
            for item in tokens
        ],
        "positions": [],
        "journal": [],
        "replaySessions": [],
    }


def build_snapshot_from_raw(raw: dict[str, Any]) -> dict[str, Any]:
    raw_tokens = raw["tokens"]

    narratives: list[dict[str, Any]] = []
    for item in raw["narratives"]:
        narrative_strength = compute_narrative_strength(item)
        flow_acceleration = compute_flow_acceleration(item)
        internal_velocity = compute_velocity(item, flow_acceleration)
        deterioration_risk = compute_deterioration_risk(item)
        capital_demand = compute_capital_demand(
            item,
            narrative_strength,
            flow_acceleration,
        )
        allocation_pressure = compute_allocation_pressure(
            item,
            capital_demand,
            deterioration_risk,
        )
        narratives.append(
            {
                "id": item["id"],
                "name": item["name"],
                "state": compute_narrative_state(
                    narrative_strength,
                    deterioration_risk,
                    item["accelerationScore"],
                ),
                "thesis": item["thesis"],
                "topic_rank": item["aveTopicRank"],
                "rank_delta": item["aveRankDelta"],
                "narrative_strength": narrative_strength,
                "internal_velocity": internal_velocity,
                "flow_acceleration": flow_acceleration,
                "breadth": item["breadthScore"],
                "breadth_tokens": item["breadthTokens"],
                "price_expansion": item["priceExpansionScore"],
                "persistence": item["persistenceScore"],
                "risk_heat": item["crowdingScore"],
                "deterioration_risk": deterioration_risk,
                "capital_demand": capital_demand,
                "allocation_pressure": allocation_pressure,
                "leader_concentration": item["leaderConcentration"],
                "smart_money": item.get("smartMoneySignal", "unavailable"),
                "token_strip": [
                    token["symbol"] for token in raw_tokens if token["id"] in item["tokenIds"]
                ],
                "competing_narratives": item["competingNarratives"],
                "stage_bias": compute_stage_bias(
                    narrative_strength,
                    deterioration_risk,
                    item["stageBiasHint"],
                ),
                "evidence": create_narrative_evidence(
                    item,
                    deterioration_risk,
                    flow_acceleration,
                ),
            }
        )

    narrative_map = {narrative["id"]: narrative for narrative in narratives}

    candidates = [
        {
            "id": token["id"],
            "narrative_id": token["narrativeId"],
            "symbol": token["symbol"],
            "name": token["name"],
            "investability_score": compute_investability(token),
            "leadership_score": token["leadership"],
            "liquidity_score": token["liquidity"],
            "route_readiness": token["routeStability"],
            "risk_coverage": token["riskCoverage"],
            "smart_flow_alignment": token["smartFlowAlignment"],
            "toxicity_penalty": token["toxicity"],
            "scout_size": f'{token["scoutSizePct"]:.2f}%',
            "readiness_stage": compute_readiness_stage(
                token,
                narrative_map[token["narrativeId"]]["narrative_strength"],
            ),
            "overlap_narratives": token["overlapNarratives"],
            "price_expansion_5m": format_signed_percent(token["priceExpansionPct"]),
            "breadth_signal": token["breadthContribution"],
            "signal_confirmations": token.get("signalConfirmations", 0),
            "trending_on_ave": token.get("trendingOnAVE", False),
            "top_holder_pct": token.get("topHolderPct"),
            "logo_url": token.get("logoUrl"),
            "price_trend_24h": token.get("klineTrend", "flat"),
            "live_price_usd": token.get("livePriceUsd"),
            "protected_exit": {
                "hardStop": format_stop(token["hardStopPct"]),
                "thesisBreak": token["thesisBreak"],
                "timeStop": format_hours(token["timeStopHours"]),
            },
            "route_provider": token["routeProvider"],
            "note": token["note"],
        }
        for token in raw_tokens
    ]
    candidates.sort(key=lambda item: item["investability_score"], reverse=True)
    candidate_map = {candidate["id"]: candidate for candidate in candidates}

    allocations = []
    for item in raw["narratives"]:
        narrative = narrative_map[item["id"]]
        narrative_candidates = [
            candidate for candidate in candidates if candidate["narrative_id"] == item["id"]
        ]
        allocations.append(
            {
                "narrative_id": item["id"],
                "budget": item["budget"],
                "gates": create_allocation_gates(narrative, narrative_candidates),
                "protected_exit": {
                    "hardStop": f'Basket stop {format_stop((100 - narrative["narrative_strength"]) * 0.08 + 4.1)}',
                    "thesisBreak": (
                        f'Velocity below {max(58, narrative["internal_velocity"] - 12)} '
                        f'or breadth tokens below {max(4, narrative["breadth_tokens"] - 3)}'
                    ),
                    "timeStop": f'{max(8, 18 - round(narrative["internal_velocity"] / 18))}h re-check',
                    "invalidation": (
                        f'Leader concentration above '
                        f'{min(88, narrative["leader_concentration"] + 10)} '
                        "with weakening breadth"
                    ),
                },
            }
        )

    positions = []
    for item in raw.get("positions", []):
        candidate = candidate_map.get(item["candidateId"])
        if candidate is None:
            continue
        positions.append(
            {
                "id": item["id"],
                "narrative_id": item["narrativeId"],
                "candidate_id": item["candidateId"],
                "symbol": item["symbol"],
                "stage": item["stage"],
                "size": f'{item["sizePct"]:.1f}%',
                "average_basis": item["averageBasis"],
                "pnl": format_signed_percent(item["pnlPct"]),
                "status_note": item["note"],
                "next_action": item["nextAction"],
                "stage_progress": item["stageProgress"] or build_stage_progress(item["stage"]),
                "protected_exit": {
                    "hardStop": candidate["protected_exit"]["hardStop"],
                    "thesisBreak": candidate["protected_exit"]["thesisBreak"],
                    "cooldown": "36h lockout" if item["stage"] == "EXIT" else "24h if exited",
                },
            }
        )

    journal = []
    for item in raw.get("journal", []):
        narrative = narrative_map[item["narrativeId"]]
        candidate = candidate_map[item["candidateId"]]
        journal.append(
            {
                "id": item["id"],
                "timestamp": item["timestamp"],
                "narrative_id": item["narrativeId"],
                "candidate_id": item["candidateId"],
                "title": item["title"],
                "stage_from": item["stageFrom"],
                "stage_to": item["stageTo"],
                "verdict": item["verdict"],
                "summary": item["summary"],
                "rule_trace": item["ruleTrace"],
                "evidence_stack": item["evidenceStack"],
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
                "execution_outcome": item["executionOutcome"],
            }
        )

    replay_sessions = []
    for session in raw.get("replaySessions", []):
        replay_sessions.append(
            {
                "id": session["id"],
                "narrative_id": session["narrativeId"],
                "title": session["title"],
                "result": session["result"],
                "snapshots": [
                    {
                        "id": snapshot["id"],
                        "timestamp": snapshot["timestamp"],
                        "stage": snapshot["stage"],
                        "label": snapshot["label"],
                        "narrative_signal": snapshot["narrativeSignal"],
                        "decision": snapshot["decision"],
                        "why_now": snapshot["whyNow"],
                        "change_set": snapshot["changeSet"],
                        "gate_delta": snapshot["gateDelta"],
                        "execution": snapshot["execution"],
                        "outcome": snapshot["outcome"],
                    }
                    for snapshot in session["snapshots"]
                ],
            }
        )

    return {
        "status": {
            "mode": raw["status"]["mode"],
            "posture": raw["status"]["posture"],
            "allocated_capital": raw["status"]["allocatedCapital"],
            "dry_powder": raw["status"]["dryPowder"],
            "open_risk": raw["status"]["openRisk"],
        },
        "ave_integration": raw.get(
            "ave_integration",
            {
                "endpoints_used": [],
                "total_endpoints": 0,
                "narratives_ingested": len(narratives),
                "tokens_scored": len(candidates),
                "skills_version": "v2.4.0",
                "mode": raw["status"]["mode"],
                "tracks": [],
                "supported_chains": [],
            },
        ),
        "narratives": narratives,
        "candidates": candidates,
        "allocations": allocations,
        "positions": positions,
        "journal": journal,
        "replay_sessions": replay_sessions,
    }


@lru_cache
def load_raw_demo() -> dict[str, Any]:
    return json.loads(DEMO_FILE.read_text(encoding="utf-8"))


@lru_cache
def get_demo_snapshot() -> dict[str, Any]:
    return build_snapshot_from_raw(load_raw_demo())


def get_demo_narrative(narrative_id: str) -> dict[str, Any] | None:
    return next(
        (
            narrative
            for narrative in get_demo_snapshot()["narratives"]
            if narrative["id"] == narrative_id
        ),
        None,
    )


def get_demo_candidate(candidate_id: str) -> dict[str, Any] | None:
    return next(
        (
            candidate
            for candidate in get_demo_snapshot()["candidates"]
            if candidate["id"] == candidate_id
        ),
        None,
    )


def get_demo_current_stage(candidate_symbol: str) -> str:
    position = next(
        (
            position
            for position in get_demo_snapshot()["positions"]
            if position["symbol"] == candidate_symbol
        ),
        None,
    )
    return position["stage"] if position else "WATCH"


def get_demo_topic_ranks() -> list[dict[str, Any]]:
    snapshot = get_demo_snapshot()
    return sorted(
        [
            {
                "id": narrative["id"],
                "name": narrative["name"],
                "topic_rank": narrative["topic_rank"],
                "rank_delta": narrative["rank_delta"],
                "flow_acceleration": narrative["flow_acceleration"],
                "internal_velocity": narrative["internal_velocity"],
                "breadth_score": narrative["breadth"],
                "capital_demand_score": narrative["capital_demand"],
                "allocation_pressure": narrative["allocation_pressure"],
                "deterioration_risk": narrative["deterioration_risk"],
                "stage_bias": narrative["stage_bias"],
            }
            for narrative in snapshot["narratives"]
        ],
        key=lambda item: item["topic_rank"],
    )


def get_demo_topic_tokens(topic: str) -> list[dict[str, Any]]:
    return [
        candidate
        for candidate in get_demo_snapshot()["candidates"]
        if candidate["narrative_id"] == topic
    ]


def get_demo_contract_risk(token_id: str) -> dict[str, Any]:
    candidate = get_demo_candidate(token_id)
    if candidate is None:
        return {"available": False, "risk": "unknown", "route_provider": "none"}

    risk = "low"
    if candidate["risk_coverage"] < 60 or candidate["toxicity_penalty"] >= 22:
        risk = "high"
    elif candidate["risk_coverage"] < 72 or candidate["toxicity_penalty"] >= 14:
        risk = "medium"

    return {
        "available": candidate["protected_exit"]["hardStop"] != "N/A",
        "risk": risk,
        "route_provider": candidate["route_provider"],
        "risk_coverage": candidate["risk_coverage"],
        "route_readiness": candidate["route_readiness"],
        "hard_stop": candidate["protected_exit"]["hardStop"],
        "time_stop": candidate["protected_exit"]["timeStop"],
    }
