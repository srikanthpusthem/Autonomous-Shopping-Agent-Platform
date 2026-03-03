from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ShippingSpeedPreference


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    budget_min: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    budget_max: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    preferred_brands: Mapped[list[str]] = mapped_column(JSONB, default=list)
    avoid_brands: Mapped[list[str]] = mapped_column(JSONB, default=list)
    shipping_speed_preference: Mapped[str] = mapped_column(
        String(32), default=ShippingSpeedPreference.BALANCED.value
    )
    use_case_tags: Mapped[list[str]] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    user = relationship("User", back_populates="profiles")
    runs = relationship("Run", back_populates="profile", cascade="all, delete-orphan")
