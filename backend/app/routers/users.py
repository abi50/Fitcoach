from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User, UserProfile
from app.schemas.user import UserProfileUpdate, UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me/profile", response_model=UserResponse)
async def update_profile(
    update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    for field, value in update.model_dump(exclude_none=True).items():
        setattr(profile, field, value)

    await db.flush()
    await db.refresh(current_user)
    return current_user
