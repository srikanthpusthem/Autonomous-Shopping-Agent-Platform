from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.profile import Profile
from app.models.user import User
from app.schemas import ProfileCreateRequest, ProfileResponse

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("", response_model=list[ProfileResponse])
def list_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> list[ProfileResponse]:
    return list(db.scalars(select(Profile).where(Profile.user_id == current_user.id)).all())


@router.post("", response_model=ProfileResponse)
def create_profile(
    payload: ProfileCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ProfileResponse:
    profile = Profile(
        user_id=current_user.id,
        name=payload.name,
        budget_min=payload.budget_min,
        budget_max=payload.budget_max,
        preferred_brands=payload.preferred_brands,
        avoid_brands=payload.avoid_brands,
        shipping_speed_preference=payload.shipping_speed_preference.value,
        use_case_tags=payload.use_case_tags,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile
