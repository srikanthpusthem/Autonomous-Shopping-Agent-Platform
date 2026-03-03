from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import FeedbackType


class FeedbackCreateRequest(BaseModel):
    profile_id: UUID
    run_id: UUID | None = None
    feedback_type: FeedbackType
    product_provider: str | None = None
    product_id: str | None = None
    note: str | None = None
    metadata: dict = Field(default_factory=dict)
