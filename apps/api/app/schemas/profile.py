from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ShippingSpeedPreference


class ProfileCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    budget_min: float | None = None
    budget_max: float | None = None
    preferred_brands: list[str] = Field(default_factory=list)
    avoid_brands: list[str] = Field(default_factory=list)
    shipping_speed_preference: ShippingSpeedPreference = ShippingSpeedPreference.BALANCED
    use_case_tags: list[str] = Field(default_factory=list)


class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    budget_min: float | None
    budget_max: float | None
    preferred_brands: list[str]
    avoid_brands: list[str]
    shipping_speed_preference: str
    use_case_tags: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}
