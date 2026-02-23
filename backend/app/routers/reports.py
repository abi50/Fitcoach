from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.workout import WorkoutSession
from app.models.personal_record import PersonalRecord
from app.services.report_service import generate_weekly_report, generate_monthly_report

router = APIRouter()


@router.get("/weekly")
async def weekly_report(
    week_start: date | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not week_start:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
    return await generate_weekly_report(db=db, user_id=current_user.id, week_start=week_start)


@router.get("/monthly")
async def monthly_report(
    month: int | None = None,
    year: int | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()
    return await generate_monthly_report(
        db=db,
        user_id=current_user.id,
        month=month or today.month,
        year=year or today.year,
    )
