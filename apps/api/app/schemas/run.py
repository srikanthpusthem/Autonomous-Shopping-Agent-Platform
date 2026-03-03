from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RunCreateRequest(BaseModel):
    profile_id: UUID
    prompt: str = Field(min_length=3, max_length=1000)


class RunResponse(BaseModel):
    id: UUID
    user_id: UUID
    profile_id: UUID
    user_query: str
    status: str
    final_output: dict | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentEventPayload(BaseModel):
    run_id: UUID
    event_type: str
    agent_name: str
    message: str
    payload: dict = Field(default_factory=dict)
    timestamp: datetime
