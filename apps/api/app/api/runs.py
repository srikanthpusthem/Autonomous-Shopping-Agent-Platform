from __future__ import annotations

from uuid import UUID

import asyncio
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import SessionLocal, get_db_session
from app.models.run import Run
from app.models.run_event import RunEvent
from app.models.user import User
from app.schemas import AgentEventPayload, RunCreateRequest, RunResponse
from app.services.event_stream import run_event_manager
from app.services.orchestrator import orchestrator
from app.services.rate_limit import runs_rate_limiter

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=RunResponse)
def create_run(
    payload: RunCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> RunResponse:
    runs_rate_limiter.check(str(current_user.id))
    run = Run(
        user_id=current_user.id,
        profile_id=payload.profile_id,
        user_query=payload.prompt,
        status="created",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    background_tasks.add_task(_execute_run_task, run.id)
    return run


def _execute_run_task(run_id: UUID) -> None:
    asyncio.run(orchestrator.execute_run(run_id))


@router.get("/{run_id}", response_model=RunResponse)
def get_run(
    run_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> RunResponse:
    run = db.scalar(select(Run).where(Run.id == run_id).where(Run.user_id == current_user.id))
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return run


@router.websocket("/{run_id}/events")
async def run_events_websocket(websocket: WebSocket, run_id: UUID) -> None:
    await run_event_manager.connect(run_id, websocket)
    db = SessionLocal()
    try:
        history = db.scalars(select(RunEvent).where(RunEvent.run_id == run_id).order_by(RunEvent.id.asc())).all()
        for event in history:
            payload = AgentEventPayload(
                run_id=run_id,
                event_type=event.event_type,
                agent_name=event.agent_name,
                message=event.message,
                payload=event.payload,
                timestamp=event.created_at,
            )
            await websocket.send_json(payload.model_dump(mode="json"))

        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await run_event_manager.disconnect(run_id, websocket)
    finally:
        db.close()
