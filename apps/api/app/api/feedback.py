from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.feedback import Feedback
from app.models.user import User
from app.schemas import FeedbackCreateRequest, MessageResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=MessageResponse)
def create_feedback(
    payload: FeedbackCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> MessageResponse:
    feedback = Feedback(
        user_id=current_user.id,
        profile_id=payload.profile_id,
        run_id=payload.run_id,
        feedback_type=payload.feedback_type.value,
        product_provider=payload.product_provider,
        product_id=payload.product_id,
        note=payload.note,
        metadata_json=payload.metadata,
    )
    db.add(feedback)
    db.commit()
    return MessageResponse(message="Feedback stored")
