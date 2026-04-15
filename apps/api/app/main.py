from __future__ import annotations

from contextlib import asynccontextmanager
import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal, get_db
from app.domain.policy import PolicyEngine
from app.migrations import upgrade_database
from app.schemas import (
    ExecutionPreviewRequest,
    ExecutionPreviewResponse,
    ExecutionStatusResponse,
    ExecutionSubmitRequest,
    ExecutionSubmitResponse,
    PolicyEvaluationRequest,
    PolicyEvaluationResponse,
    SnapshotResponse,
)
from app.services.ave import AVEUnavailableError, get_ave_client
from app.services.ave_contracts import AVEContractError
from app.services.execution import ExecutionService
from app.services.repository import SnapshotRepository, SnapshotUnavailableError
from app.services.ave_wss import get_ave_wss_monitor

settings = get_settings()
policy_engine = PolicyEngine()
execution_service = ExecutionService(settings)
live_price_monitor = get_ave_wss_monitor()
logger = logging.getLogger(__name__)


def _execution_response(record: dict) -> dict:
    response_payload = record.get("response_payload", {})
    return {
        "request_id": record["id"],
        "app_mode": record["app_mode"],
        "narrative_id": record["narrative_id"],
        "candidate_id": record["candidate_id"],
        "target_stage": record["target_stage"],
        "decision": record["decision"],
        "mode": record["execution_mode"],
        "phase": record["lifecycle_phase"],
        "status": record["lifecycle_status"],
        "available": record["lifecycle_status"] in {"ready", "pending", "success", "skipped"},
        "provider": record["provider"],
        "route": record["route"],
        "slippage": record["slippage"],
        "protected_exit": record["protected_exit"],
        "message": record["message"],
        "failure_reason": record.get("failure_reason"),
        "created_at": record["created_at"],
        "updated_at": record["updated_at"],
        "events": record["events"],
        "ave_quote": response_payload.get("ave_quote"),
    }


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.auto_run_migrations:
        try:
            upgrade_database()
        except Exception:
            pass
    if settings.auto_seed_demo:
        try:
            with SessionLocal() as db:
                SnapshotRepository(db).seed_demo()
        except Exception:
            pass
    try:
        await live_price_monitor.start()
    except Exception as exc:
        logger.warning("AVE WSS monitor failed to start: %s", exc)
    yield
    try:
        await live_price_monitor.stop()
    except Exception as exc:
        logger.warning("AVE WSS monitor failed to stop cleanly: %s", exc)


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "mode": settings.app_mode}


@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/api/v1/snapshot", response_model=SnapshotResponse)
def snapshot(db: Session = Depends(get_db)) -> dict:
    try:
        return SnapshotRepository(db).get_snapshot()
    except SnapshotUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/v1/policy/evaluate", response_model=PolicyEvaluationResponse)
def evaluate_policy(
    payload: PolicyEvaluationRequest,
    db: Session = Depends(get_db),
) -> dict:
    repository = SnapshotRepository(db)
    try:
        snapshot = repository.get_snapshot()
    except SnapshotUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    narrative = next((item for item in snapshot["narratives"] if item["id"] == payload.narrative_id), None)
    candidate = next((item for item in snapshot["candidates"] if item["id"] == payload.candidate_id), None)

    if narrative is None or candidate is None:
        raise HTTPException(status_code=404, detail="Narrative or candidate not found")

    current_stage = repository.current_stage_for_candidate(candidate["id"])
    return policy_engine.evaluate(
        narrative=narrative,
        candidate=candidate,
        current_stage=current_stage,
        target_stage=payload.target_stage,
    )


@app.post("/api/v1/execution/preview", response_model=ExecutionPreviewResponse)
def preview_execution(
    payload: ExecutionPreviewRequest,
    db: Session = Depends(get_db),
) -> dict:
    repository = SnapshotRepository(db)
    try:
        snapshot = repository.get_snapshot()
    except SnapshotUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    narrative = next((item for item in snapshot["narratives"] if item["id"] == payload.narrative_id), None)
    candidate = next((item for item in snapshot["candidates"] if item["id"] == payload.candidate_id), None)
    if narrative is None or candidate is None:
        raise HTTPException(status_code=404, detail="Narrative or candidate not found")
    if candidate["narrative_id"] != payload.narrative_id:
        raise HTTPException(status_code=400, detail="Candidate does not belong to the selected narrative")

    preview_record = execution_service.preview(
        candidate=candidate,
        target_stage=payload.target_stage,
        mode=payload.mode,
    )
    persisted = repository.create_execution_request(
        narrative_id=payload.narrative_id,
        candidate_id=payload.candidate_id,
        record=preview_record,
    )
    return _execution_response(persisted)


@app.post("/api/v1/execution/submit", response_model=ExecutionSubmitResponse)
def submit_execution(
    payload: ExecutionSubmitRequest,
    db: Session = Depends(get_db),
) -> dict:
    repository = SnapshotRepository(db)
    try:
        snapshot = repository.get_snapshot()
    except SnapshotUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    narrative = next((item for item in snapshot["narratives"] if item["id"] == payload.narrative_id), None)
    candidate = next((item for item in snapshot["candidates"] if item["id"] == payload.candidate_id), None)
    if narrative is None or candidate is None:
        raise HTTPException(status_code=404, detail="Narrative or candidate not found")
    if candidate["narrative_id"] != payload.narrative_id:
        raise HTTPException(status_code=400, detail="Candidate does not belong to the selected narrative")

    submit_record = execution_service.submit(
        candidate=candidate,
        target_stage=payload.target_stage,
        mode=payload.mode,
    )
    persisted = repository.create_execution_request(
        narrative_id=payload.narrative_id,
        candidate_id=payload.candidate_id,
        record=submit_record,
    )
    return _execution_response(persisted)


@app.get("/api/v1/execution/{request_id}", response_model=ExecutionStatusResponse)
def execution_status(
    request_id: str,
    db: Session = Depends(get_db),
) -> dict:
    repository = SnapshotRepository(db)
    current = repository.get_execution_request(request_id)
    if current is None:
        raise HTTPException(status_code=404, detail="Execution request not found")

    refreshed = execution_service.refresh_status(current)
    updated = repository.update_execution_request(request_id, refreshed)
    if updated is None:
        raise HTTPException(status_code=404, detail="Execution request not found")
    return _execution_response(updated)


@app.get("/api/v1/ave/topics")
def ave_topics() -> list[dict]:
    try:
        return get_ave_client().fetch_topic_ranks()
    except (AVEUnavailableError, AVEContractError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/v1/prices/live")
def live_prices() -> dict[str, dict]:
    return live_price_monitor.get_prices()
