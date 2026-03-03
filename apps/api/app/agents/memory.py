from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.feedback import Feedback


class MemoryAgent:
    def fetch_preference_notes(self, db: Session, user_id: UUID, profile_id: UUID) -> list[str]:
        rows = db.scalars(
            select(Feedback)
            .where(Feedback.user_id == user_id)
            .where(Feedback.profile_id == profile_id)
            .order_by(Feedback.created_at.desc())
            .limit(20)
        ).all()
        notes: list[str] = []
        for row in rows:
            if row.note:
                notes.append(row.note)
            if row.feedback_type == "not_interested" and row.product_provider:
                notes.append(f"avoid_provider:{row.product_provider}")
        return notes
