from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_current_user, get_db
from app.models.hydration import HydrationEntry, HydrationLog
from app.models.user import User
from app.schemas.hydration import HydrationEntryCreate, HydrationTargetUpdate

router = APIRouter()


@router.get("/entries")
async def get_hydration(
    log_date: date | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    target_date = log_date or date.today()
    result = await db.execute(
        select(HydrationLog)
        .where(HydrationLog.user_id == current_user.id, HydrationLog.log_date == target_date)
        .options(selectinload(HydrationLog.entries))
    )
    log = result.scalar_one_or_none()
    if not log:
        log = HydrationLog(user_id=current_user.id, log_date=target_date)
        db.add(log)
        await db.flush()
        await db.refresh(log)

    return {
        "id": log.id,
        "log_date": log.log_date,
        "target_ml": log.target_ml,
        "total_ml": log.total_ml,
        "percentage": (log.total_ml / log.target_ml * 100) if log.target_ml else 0,
        "entries": [{"id": e.id, "amount_ml": e.amount_ml, "beverage_type": e.beverage_type, "logged_at": e.logged_at} for e in (log.entries or [])],
    }


@router.post("/entries", status_code=201)
async def add_entry(
    data: HydrationEntryCreate,
    log_date: date | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    target_date = log_date or date.today()
    result = await db.execute(
        select(HydrationLog).where(
            HydrationLog.user_id == current_user.id, HydrationLog.log_date == target_date
        )
    )
    log = result.scalar_one_or_none()
    if not log:
        log = HydrationLog(user_id=current_user.id, log_date=target_date)
        db.add(log)
        await db.flush()

    entry = HydrationEntry(log_id=log.id, **data.model_dump())
    db.add(entry)
    log.total_ml += data.amount_ml
    await db.flush()
    return {"id": entry.id, "amount_ml": entry.amount_ml, "beverage_type": entry.beverage_type, "logged_at": entry.logged_at}


@router.patch("/target", status_code=204)
async def update_target(
    data: HydrationTargetUpdate,
    log_date: date | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    target_date = log_date or date.today()
    result = await db.execute(
        select(HydrationLog).where(
            HydrationLog.user_id == current_user.id, HydrationLog.log_date == target_date
        )
    )
    log = result.scalar_one_or_none()
    if not log:
        log = HydrationLog(user_id=current_user.id, log_date=target_date, target_ml=data.target_ml)
        db.add(log)
    else:
        log.target_ml = data.target_ml
