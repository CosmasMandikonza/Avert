from collections.abc import Iterable


TRANSITIONS: dict[str, tuple[str, ...]] = {
    "WATCH": ("SCOUT",),
    "SCOUT": ("CONFIRM", "EXIT", "COOLDOWN"),
    "CONFIRM": ("ADD", "EXIT", "COOLDOWN"),
    "ADD": ("TRIM", "EXIT"),
    "TRIM": ("ADD", "EXIT", "COOLDOWN"),
    "EXIT": ("COOLDOWN",),
    "COOLDOWN": ("WATCH",),
}

STAGE_THRESHOLDS = {
    "WATCH": {
        "min_strength": 0,
        "min_velocity": 0,
        "min_breadth": 0,
        "max_risk": 100,
        "min_route_readiness": 0,
        "min_risk_coverage": 0,
    },
    "SCOUT": {
        "min_strength": 60,
        "min_velocity": 68,
        "min_breadth": 55,
        "max_risk": 72,
        "min_route_readiness": 58,
        "min_risk_coverage": 60,
    },
    "CONFIRM": {
        "min_strength": 72,
        "min_velocity": 75,
        "min_breadth": 62,
        "max_risk": 66,
        "min_route_readiness": 66,
        "min_risk_coverage": 68,
    },
    "ADD": {
        "min_strength": 82,
        "min_velocity": 80,
        "min_breadth": 70,
        "max_risk": 58,
        "min_route_readiness": 72,
        "min_risk_coverage": 74,
    },
    "TRIM": {
        "min_strength": 0,
        "min_velocity": 0,
        "min_breadth": 0,
        "max_risk": 100,
        "min_route_readiness": 0,
        "min_risk_coverage": 0,
    },
    "EXIT": {
        "min_strength": 0,
        "min_velocity": 0,
        "min_breadth": 0,
        "max_risk": 100,
        "min_route_readiness": 0,
        "min_risk_coverage": 0,
    },
    "COOLDOWN": {
        "min_strength": 0,
        "min_velocity": 0,
        "min_breadth": 0,
        "max_risk": 100,
        "min_route_readiness": 0,
        "min_risk_coverage": 0,
    },
}


def allowed_transitions(stage: str) -> Iterable[str]:
    return TRANSITIONS.get(stage, tuple())


def can_transition(current_stage: str, target_stage: str) -> bool:
    return target_stage in TRANSITIONS.get(current_stage, tuple())
