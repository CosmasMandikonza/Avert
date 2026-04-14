from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


ExecutionMode = Literal["PAPER", "LIVE_CHAIN_WALLET", "LIVE_PROXY_WALLET"]
ExecutionPhase = Literal["preview", "submitted"]
ExecutionStatus = Literal["ready", "blocked", "unavailable", "pending", "success", "failed", "skipped"]


class AppStatusSchema(BaseModel):
    mode: Literal["DEMO_MODE", "LIVE_MODE"]
    posture: str
    allocated_capital: str
    dry_powder: str
    open_risk: str


class NarrativeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    state: str
    thesis: str
    topic_rank: int
    rank_delta: int
    narrative_strength: int
    internal_velocity: int
    flow_acceleration: int
    breadth: int
    breadth_tokens: int
    price_expansion: int
    persistence: int
    risk_heat: int
    deterioration_risk: int
    capital_demand: int
    allocation_pressure: int
    leader_concentration: int
    smart_money: str = "unavailable"
    token_strip: list[str]
    competing_narratives: list[str]
    stage_bias: str
    evidence: list[dict]


class CandidateTokenSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    narrative_id: str
    symbol: str
    name: str
    investability_score: int
    leadership_score: int
    liquidity_score: int
    route_readiness: int
    risk_coverage: int
    smart_flow_alignment: int
    toxicity_penalty: int
    scout_size: str
    readiness_stage: str
    overlap_narratives: list[str]
    price_expansion_5m: str
    breadth_signal: str
    signal_confirmations: int = 0
    trending_on_ave: bool = False
    top_holder_pct: float | None = None
    logo_url: str | None = None
    price_trend_24h: str = "flat"
    live_price_usd: float | None = None
    protected_exit: dict
    note: str


class AVEIntegrationSchema(BaseModel):
    endpoints_used: list[str]
    total_endpoints: int = 0
    narratives_ingested: int
    tokens_scored: int
    skills_version: str
    mode: Literal["DEMO_MODE", "LIVE_MODE"]
    tracks: list[str] = Field(default_factory=list)
    supported_chains: list[str] = Field(default_factory=list)


class AllocationPlanSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    narrative_id: str
    budget: dict
    gates: list[dict]
    protected_exit: dict


class PositionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    narrative_id: str
    candidate_id: str
    symbol: str
    stage: str
    size: str
    average_basis: str
    pnl: str
    status_note: str
    next_action: str
    stage_progress: list[dict]
    protected_exit: dict
    ave_quote: dict | None = None


class AVEQuoteSchema(BaseModel):
    estimated_output: str
    estimated_output_display: str | None = None
    output_decimals: int | None = None
    route: str | None = None
    price_impact: str | None = None
    gas_estimate: str | None = None
    spender: str | None = None
    source_endpoint: str | None = None
    availability_note: str | None = None


class ExecutionStateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    app_mode: Literal["DEMO_MODE", "LIVE_MODE"] | None = None
    decision: str | None = None
    mode: ExecutionMode | None = None
    phase: ExecutionPhase | None = None
    status: str
    route: str
    provider: str | None = None
    slippage: str
    note: str
    failure_reason: str | None = None
    request_id: str | None = None
    ave_quote: AVEQuoteSchema | None = None


class JournalCasefileSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    timestamp: str
    narrative_id: str
    candidate_id: str
    title: str
    stage_from: str
    stage_to: str
    verdict: str
    summary: str
    rule_trace: list[dict]
    evidence_stack: list[dict]
    narrative_snapshot: dict
    token_snapshot: dict
    execution_outcome: ExecutionStateSchema


class ReplaySnapshotSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    timestamp: str
    stage: str
    label: str
    narrative_signal: str
    decision: str
    why_now: str
    change_set: list[str]
    gate_delta: list[str]
    execution: ExecutionStateSchema
    outcome: str


class ReplaySessionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    narrative_id: str
    title: str
    result: str
    snapshots: list[ReplaySnapshotSchema]


class SnapshotResponse(BaseModel):
    status: AppStatusSchema
    ave_integration: AVEIntegrationSchema
    narratives: list[NarrativeSchema]
    candidates: list[CandidateTokenSchema]
    allocations: list[AllocationPlanSchema]
    positions: list[PositionSchema]
    journal: list[JournalCasefileSchema]
    replay_sessions: list[ReplaySessionSchema]


class PolicyEvaluationRequest(BaseModel):
    narrative_id: str
    candidate_id: str
    target_stage: str


class PolicyEvaluationResponse(BaseModel):
    allowed: bool
    current_stage: str
    target_stage: str
    gates: list[dict]
    reason: str


class ExecutionPreviewRequest(BaseModel):
    narrative_id: str
    candidate_id: str
    target_stage: str
    mode: ExecutionMode = "PAPER"


class ExecutionSubmitRequest(BaseModel):
    narrative_id: str
    candidate_id: str
    target_stage: str
    mode: ExecutionMode = "PAPER"


class ExecutionEventSchema(BaseModel):
    id: str
    phase: ExecutionPhase
    status: str
    message: str
    created_at: str
    payload: dict[str, Any] = Field(default_factory=dict)


class ExecutionLifecycleResponse(BaseModel):
    request_id: str
    app_mode: Literal["DEMO_MODE", "LIVE_MODE"]
    narrative_id: str
    candidate_id: str
    target_stage: str
    decision: str
    mode: ExecutionMode
    phase: ExecutionPhase
    status: ExecutionStatus
    available: bool
    provider: str
    route: str
    slippage: str
    protected_exit: dict
    message: str
    failure_reason: str | None = None
    created_at: str
    updated_at: str
    events: list[ExecutionEventSchema]
    ave_quote: AVEQuoteSchema | None = None


class ExecutionPreviewResponse(ExecutionLifecycleResponse):
    pass


class ExecutionSubmitResponse(ExecutionLifecycleResponse):
    pass


class ExecutionStatusResponse(ExecutionLifecycleResponse):
    pass
