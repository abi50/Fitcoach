from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.personal_record import PersonalRecord
from app.models.workout import SessionSet  # noqa: F401 — available for callers


async def check_and_create_pr(
    db: AsyncSession,
    user_id: str,
    exercise_id: str,
    weight_kg: float | None,
    reps: int | None,
    set_id: str,
) -> bool:
    """Check if the logged set is a PR and create PersonalRecord(s) if so.

    Logic:
    1. Query max weight_kg ever recorded for this user+exercise (pr_type='weight')
    2. If weight_kg is provided AND (no previous record OR weight_kg > previous max) -> create weight PR
    3. Query max reps for this user+exercise at same weight (pr_type='reps')
    4. If reps provided AND (no previous record OR reps > max reps at this weight) -> create reps PR
    5. Return True if any PR was created
    """
    pr_created = False
    now = datetime.now(UTC)

    # --- Weight PR check ---
    if weight_kg is not None:
        # Find the max weight_kg ever recorded for this user+exercise
        max_weight_result = await db.execute(
            select(func.max(PersonalRecord.weight_kg)).where(
                PersonalRecord.user_id == user_id,
                PersonalRecord.exercise_id == exercise_id,
                PersonalRecord.pr_type == "weight",
            )
        )
        previous_max_weight = max_weight_result.scalar()  # None if no records

        if previous_max_weight is None or weight_kg > previous_max_weight:
            pr = PersonalRecord(
                user_id=user_id,
                exercise_id=exercise_id,
                session_set_id=set_id,
                weight_kg=weight_kg,
                reps=reps,
                achieved_at=now,
                pr_type="weight",
                previous_best=previous_max_weight,
                celebrated=False,
            )
            db.add(pr)
            pr_created = True

    # --- Reps PR check (at the same weight) ---
    if reps is not None and weight_kg is not None:
        # Find max reps recorded for this user+exercise at the same weight
        max_reps_result = await db.execute(
            select(func.max(PersonalRecord.reps)).where(
                PersonalRecord.user_id == user_id,
                PersonalRecord.exercise_id == exercise_id,
                PersonalRecord.pr_type == "reps",
                PersonalRecord.weight_kg == weight_kg,
            )
        )
        previous_max_reps = max_reps_result.scalar()  # None if no records

        if previous_max_reps is None or reps > previous_max_reps:
            pr = PersonalRecord(
                user_id=user_id,
                exercise_id=exercise_id,
                session_set_id=set_id,
                weight_kg=weight_kg,
                reps=reps,
                achieved_at=now,
                pr_type="reps",
                previous_best=float(previous_max_reps) if previous_max_reps is not None else None,
                celebrated=False,
            )
            db.add(pr)
            pr_created = True

    if pr_created:
        await db.flush()

    return pr_created


async def get_pending_celebrations(db: AsyncSession, user_id: str) -> list[PersonalRecord]:
    """Query PersonalRecord where user_id=? AND celebrated=False."""
    result = await db.execute(
        select(PersonalRecord).where(
            PersonalRecord.user_id == user_id,
            PersonalRecord.celebrated == False,  # noqa: E712
        ).order_by(PersonalRecord.achieved_at.desc())
    )
    return list(result.scalars().all())


async def mark_celebrated(db: AsyncSession, user_id: str, pr_id: str) -> PersonalRecord | None:
    """Mark a PR as celebrated and return it."""
    result = await db.execute(
        select(PersonalRecord).where(
            PersonalRecord.id == pr_id,
            PersonalRecord.user_id == user_id,
        )
    )
    pr = result.scalar_one_or_none()
    if pr:
        pr.celebrated = True
        await db.flush()
    return pr
