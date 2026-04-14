from app.domain.state_machine import STAGE_THRESHOLDS, can_transition


def parse_percent(value: str) -> float:
    if value in {"N/A", "Blocked"}:
        return -1.0

    cleaned = value.replace("%", "").replace("+", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return -1.0


class PolicyEngine:
    def evaluate(
        self,
        narrative: dict,
        candidate: dict,
        current_stage: str,
        target_stage: str,
    ) -> dict:
        thresholds = STAGE_THRESHOLDS[target_stage]
        overlap_count = len(candidate["overlap_narratives"])
        price_expansion = parse_percent(candidate["price_expansion_5m"])
        hard_stop_defined = candidate["protected_exit"]["hardStop"] != "N/A"
        time_stop_defined = candidate["protected_exit"]["timeStop"] != "Blocked"

        narrative_ready = (
            narrative["narrative_strength"] >= thresholds["min_strength"]
            and narrative["internal_velocity"] >= thresholds["min_velocity"]
            and narrative["breadth"] >= thresholds["min_breadth"]
        )
        deterioration_ok = narrative["deterioration_risk"] <= thresholds["max_risk"]
        risk_sufficient = candidate["risk_coverage"] >= thresholds["min_risk_coverage"] and hard_stop_defined
        route_ready = (
            candidate["route_readiness"] >= thresholds["min_route_readiness"]
            and candidate["liquidity_score"] >= thresholds["min_route_readiness"]
        )
        scout_momentum_ready = price_expansion >= 0.8 or target_stage not in {"SCOUT", "CONFIRM", "ADD"}
        confirm_breadth_ready = (
            narrative["breadth_tokens"] >= 6 if target_stage in {"CONFIRM", "ADD"} else True
        )
        add_pressure_ok = (
            narrative["allocation_pressure"] < 82 if target_stage == "ADD" else True
        )
        trim_condition = (
            narrative["allocation_pressure"] >= 76
            or narrative["deterioration_risk"] >= 66
            or price_expansion <= 1.4
        )
        exit_condition = (
            narrative["deterioration_risk"] >= 78
            or candidate["route_readiness"] < 50
            or candidate["risk_coverage"] < 55
        )

        overlap_verdict = "pass"
        if overlap_count >= 2 and target_stage in {"CONFIRM", "ADD"}:
            overlap_verdict = "block"
        elif overlap_count >= 1:
            overlap_verdict = "watch"

        toxicity_verdict = "pass"
        if candidate["toxicity_penalty"] >= 26:
            toxicity_verdict = "block"
        elif candidate["toxicity_penalty"] >= 16:
            toxicity_verdict = "watch"

        gates = [
            {
                "title": "Valid state transition",
                "verdict": "pass" if can_transition(current_stage, target_stage) else "block",
                "detail": f"{current_stage} -> {target_stage} must follow the staged capital state machine.",
            },
            {
                "title": "Narrative strength and breadth",
                "verdict": "pass" if narrative_ready else "block",
                "detail": (
                    f'Narrative strength {narrative["narrative_strength"]}, velocity '
                    f'{narrative["internal_velocity"]}, breadth {narrative["breadth"]}, and '
                    f'{narrative["breadth_tokens"]} breadth names must clear the {target_stage} floor.'
                ),
            },
            {
                "title": "Deterioration containment",
                "verdict": "pass" if deterioration_ok else "block",
                "detail": (
                    f'Deterioration risk is {narrative["deterioration_risk"]}; '
                    f'{target_stage} requires risk at or below {thresholds["max_risk"]}.'
                ),
            },
            {
                "title": "Risk sufficiency and protected exits",
                "verdict": "pass" if risk_sufficient and time_stop_defined else "block",
                "detail": (
                    f'Risk coverage {candidate["risk_coverage"]}, hard stop '
                    f'{candidate["protected_exit"]["hardStop"]}, and time stop '
                    f'{candidate["protected_exit"]["timeStop"]} must all exist before promotion.'
                ),
            },
            {
                "title": "Execution readiness",
                "verdict": "pass" if route_ready else "block",
                "detail": (
                    f'Route readiness {candidate["route_readiness"]} and liquidity '
                    f'{candidate["liquidity_score"]} must remain inside the slippage budget.'
                ),
            },
            {
                "title": "Scout momentum quality",
                "verdict": "pass" if scout_momentum_ready else "watch",
                "detail": (
                    f'Price expansion is {candidate["price_expansion_5m"]}; scouts and confirms need '
                    "real expansion, not only narrative headlines."
                ),
            },
            {
                "title": "Confirmation breadth",
                "verdict": "pass" if confirm_breadth_ready else "watch",
                "detail": (
                    f'{narrative["breadth_tokens"]} participating names are live. CONFIRM and ADD '
                    "need real participation, not a single leading token."
                ),
            },
            {
                "title": "Allocation pressure discipline",
                "verdict": "pass" if add_pressure_ok else "block",
                "detail": (
                    f'Allocation pressure is {narrative["allocation_pressure"]}; ADD is blocked once '
                    "pressure exceeds the narrative rotation budget."
                ),
            },
            {
                "title": "Duplicate exposure",
                "verdict": overlap_verdict,
                "detail": (
                    f'{overlap_count} overlap memberships were detected across narratives.'
                    if overlap_count
                    else "No duplicate narrative membership detected."
                ),
            },
            {
                "title": "Toxicity filter",
                "verdict": toxicity_verdict,
                "detail": (
                    f'Toxicity penalty is {candidate["toxicity_penalty"]}; toxic leaders cannot anchor deployment.'
                ),
            },
        ]

        if target_stage == "TRIM":
            gates.append(
                {
                    "title": "Trim trigger is active",
                    "verdict": "pass" if trim_condition else "watch",
                    "detail": (
                        "TRIM becomes eligible when pressure, deterioration, or asymmetry compression "
                        f"shows up. Allocation pressure {narrative['allocation_pressure']}, "
                        f"deterioration {narrative['deterioration_risk']}, price expansion {candidate['price_expansion_5m']}."
                    ),
                }
            )

        if target_stage == "EXIT":
            gates.append(
                {
                    "title": "Exit condition is active",
                    "verdict": "pass" if exit_condition else "watch",
                    "detail": (
                        "EXIT becomes mandatory when deterioration, route quality, or risk sufficiency breaks. "
                        f"Deterioration {narrative['deterioration_risk']}, route readiness "
                        f"{candidate['route_readiness']}, risk coverage {candidate['risk_coverage']}."
                    ),
                }
            )

        blocked = [gate for gate in gates if gate["verdict"] == "block"]
        allowed = not blocked

        return {
            "allowed": allowed,
            "current_stage": current_stage,
            "target_stage": target_stage,
            "gates": gates,
            "reason": (
                f"{target_stage} promotion cleared with deterministic gates and protected exits attached."
                if allowed
                else "One or more deterministic gates blocked promotion or forced discipline."
            ),
        }
