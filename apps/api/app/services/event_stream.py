from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import UTC, datetime
from uuid import UUID

from fastapi import WebSocket
from sqlalchemy.orm import Session

from app.models.run_event import RunEvent
from app.schemas import AgentEventPayload


class RunEventManager:
    def __init__(self) -> None:
        self._connections: dict[UUID, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, run_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[run_id].add(websocket)

    async def disconnect(self, run_id: UUID, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections[run_id].discard(websocket)
            if not self._connections[run_id]:
                self._connections.pop(run_id, None)

    async def broadcast(self, run_id: UUID, event: AgentEventPayload) -> None:
        for socket in list(self._connections.get(run_id, set())):
            try:
                await socket.send_json(event.model_dump(mode="json"))
            except Exception:
                await self.disconnect(run_id, socket)


run_event_manager = RunEventManager()


async def persist_and_publish_event(
    db: Session,
    run_id: UUID,
    event_type: str,
    agent_name: str,
    message: str,
    payload: dict | None = None,
) -> AgentEventPayload:
    data = payload or {}
    event = RunEvent(
        run_id=run_id,
        event_type=event_type,
        agent_name=agent_name,
        message=message,
        payload=data,
    )
    db.add(event)
    db.commit()

    ws_payload = AgentEventPayload(
        run_id=run_id,
        event_type=event_type,
        agent_name=agent_name,
        message=message,
        payload=data,
        timestamp=datetime.now(UTC),
    )
    await run_event_manager.broadcast(run_id, ws_payload)
    return ws_payload
