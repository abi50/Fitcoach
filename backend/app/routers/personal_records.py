from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_current_user, get_db
from app.models.personal_record import PersonalRecord
from app.models.user import User
from app.models.workout import Exercise

router = APIRouter()


@router.get("")
async def list_prs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PersonalRecord)
        .where(PersonalRecord.user_id == current_user.id)
        .options(selectinload(PersonalRecord.exercise))
        .order_by(PersonalRecord.achieved_at.desc())
        .limit(50)
    )
    prs = result.scalars().all()
    return {"data": [
        {
            "id": pr.id,
            "exercise_name": pr.exercise.name if pr.exercise else None,
            "weight_kg": pr.weight_kg,
            "reps": pr.reps,
            "achieved_at": pr.achieved_at,
            "pr_type": pr.pr_type,
            "previous_best": pr.previous_best,
            "celebrated": pr.celebrated,
        }
        for pr in prs
    ]}


@router.get("/pending-celebrations")
async def pending_celebrations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PersonalRecord)
        .where(
            PersonalRecord.user_id == current_user.id,
            PersonalRecord.celebrated == False,
        )
        .options(selectinload(PersonalRecord.exercise))
        .order_by(PersonalRecord.achieved_at.desc())
    )
    prs = result.scalars().all()
    return {"data": [
        {
            "id": pr.id,
            "exercise_name": pr.exercise.name if pr.exercise else None,
            "weight_kg": pr.weight_kg,
            "reps": pr.reps,
            "pr_type": pr.pr_type,
        }
        for pr in prs
    ]}


@router.post("/{pr_id}/celebrate", status_code=204)
async def mark_celebrated(
    pr_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PersonalRecord).where(
            PersonalRecord.id == pr_id,
            PersonalRecord.user_id == current_user.id,
        )
    )
    pr = result.scalar_one_or_none()
    if not pr:
        raise HTTPException(status_code=404, detail="Personal record not found")
    pr.celebrated = True
