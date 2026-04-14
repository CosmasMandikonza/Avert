from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NarrativeModel(Base):
    __tablename__ = "narratives"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    state: Mapped[str] = mapped_column(String(32))
    thesis: Mapped[str] = mapped_column(Text)
    topic_rank: Mapped[int] = mapped_column(Integer)
    rank_delta: Mapped[int] = mapped_column(Integer)
    internal_velocity: Mapped[int] = mapped_column(Integer)
    flow_acceleration: Mapped[int] = mapped_column(Integer)
    breadth: Mapped[int] = mapped_column(Integer)
    price_expansion: Mapped[int] = mapped_column(Integer)
    persistence: Mapped[int] = mapped_column(Integer)
    risk_heat: Mapped[int] = mapped_column(Integer)
    capital_demand: Mapped[int] = mapped_column(Integer)
    token_strip: Mapped[list[str]] = mapped_column(JSON)
    stage_bias: Mapped[str] = mapped_column(String(24))
    evidence: Mapped[list[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CandidateTokenModel(Base):
    __tablename__ = "candidate_tokens"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    narrative_id: Mapped[str] = mapped_column(String(64), index=True)
    symbol: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(255))
    investability_score: Mapped[int] = mapped_column(Integer)
    leadership_score: Mapped[int] = mapped_column(Integer)
    liquidity_score: Mapped[int] = mapped_column(Integer)
    toxicity_penalty: Mapped[int] = mapped_column(Integer)
    scout_size: Mapped[str] = mapped_column(String(32))
    overlap_narratives: Mapped[list[str]] = mapped_column(JSON)
    price_expansion_5m: Mapped[str] = mapped_column(String(32))
    breadth_signal: Mapped[str] = mapped_column(Text)
    protected_exit: Mapped[dict] = mapped_column(JSON)
    note: Mapped[str] = mapped_column(Text)


class AllocationPlanModel(Base):
    __tablename__ = "allocation_plans"

    narrative_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    budget: Mapped[dict] = mapped_column(JSON)
    gates: Mapped[list[dict]] = mapped_column(JSON)
    protected_exit: Mapped[dict] = mapped_column(JSON)


class PositionModel(Base):
    __tablename__ = "positions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    narrative_id: Mapped[str] = mapped_column(String(64), index=True)
    symbol: Mapped[str] = mapped_column(String(32))
    stage: Mapped[str] = mapped_column(String(24))
    size: Mapped[str] = mapped_column(String(32))
    average_basis: Mapped[str] = mapped_column(String(32))
    pnl: Mapped[str] = mapped_column(String(32))
    status_note: Mapped[str] = mapped_column(Text)
    next_action: Mapped[str] = mapped_column(Text)
    stage_progress: Mapped[list[dict]] = mapped_column(JSON)
    protected_exit: Mapped[dict] = mapped_column(JSON)


class PolicyEvaluationModel(Base):
    __tablename__ = "policy_evaluations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    narrative_id: Mapped[str] = mapped_column(String(64), index=True)
    candidate_id: Mapped[str] = mapped_column(String(64), index=True)
    target_stage: Mapped[str] = mapped_column(String(24))
    allowed: Mapped[str] = mapped_column(String(8))
    gates: Mapped[list[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ExecutionIntentModel(Base):
    __tablename__ = "execution_intents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    candidate_id: Mapped[str] = mapped_column(String(64), index=True)
    mode: Mapped[str] = mapped_column(String(16))
    provider: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(24))
    protected_exit: Mapped[dict] = mapped_column(JSON)
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ExecutionRequestModel(Base):
    __tablename__ = "execution_requests"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    app_mode: Mapped[str] = mapped_column(String(16))
    narrative_id: Mapped[str] = mapped_column(String(64), index=True)
    candidate_id: Mapped[str] = mapped_column(String(64), index=True)
    target_stage: Mapped[str] = mapped_column(String(24))
    decision: Mapped[str] = mapped_column(String(255))
    execution_mode: Mapped[str] = mapped_column(String(32))
    lifecycle_phase: Mapped[str] = mapped_column(String(24))
    lifecycle_status: Mapped[str] = mapped_column(String(24))
    provider: Mapped[str] = mapped_column(String(64))
    route: Mapped[str] = mapped_column(String(64))
    slippage: Mapped[str] = mapped_column(String(32))
    protected_exit: Mapped[dict] = mapped_column(JSON)
    message: Mapped[str] = mapped_column(Text)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_payload: Mapped[dict] = mapped_column(JSON)
    response_payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ExecutionEventModel(Base):
    __tablename__ = "execution_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    execution_request_id: Mapped[str] = mapped_column(String(64), index=True)
    lifecycle_phase: Mapped[str] = mapped_column(String(24))
    lifecycle_status: Mapped[str] = mapped_column(String(24))
    message: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class JournalEntryModel(Base):
    __tablename__ = "journal_entries"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    timestamp: Mapped[str] = mapped_column(String(32))
    narrative_id: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(255))
    stage: Mapped[str] = mapped_column(String(24))
    verdict: Mapped[str] = mapped_column(String(16))
    summary: Mapped[str] = mapped_column(Text)
    evidence: Mapped[list[str]] = mapped_column(JSON)


class ReplaySessionModel(Base):
    __tablename__ = "replay_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    narrative_id: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(255))
    result: Mapped[str] = mapped_column(String(255))
    snapshots: Mapped[list[dict]] = mapped_column(JSON)
