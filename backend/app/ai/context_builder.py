from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserProfile


async def build_user_context(db: AsyncSession, user_id: str | None) -> dict:
    """Build a context dict for AI prompts from the user's stored profile.

    Returns an empty dict for guest users (user_id is None).
    Profile data is used to personalise AI prompts when available.
    """
    if user_id is None:
        return {}

    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        return {}

    return {
        "weight_kg": profile.weight_kg,
        "height_cm": profile.height_cm,
        "fitness_goal": profile.fitness_goal,
        "activity_level": profile.activity_level,
        "experience_level": profile.experience_level,
        "available_equipment": profile.available_equipment or [],
        "dietary_restrictions": profile.dietary_restrictions or [],
        "units": profile.units,
    }
