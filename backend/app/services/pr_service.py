from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession


async def check_and_create_pr(
    db: AsyncSession,
    user_id: str,
    exercise_id: str,
    weight_kg: float,
    reps: int,
    set_id: str,
) -> bool:
    """Check if the logged set is a PR and create a PersonalRecord if so.

    Stub implementation — replace with real PR detection logic.
    """
    raise NotImplementedError("check_and_create_pr not yet implemented")
