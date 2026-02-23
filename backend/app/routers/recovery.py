from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_current_user, get_db
from app.models.recovery import MuscleSorenessEntry, RecoveryLog
from app.models.user import User
from app.schemas.recovery import RecoveryCheckinCreate
from app.services.recovery_service import calculate_recovery_score

router = APIRouter()


@router.post("/checkin", status_code=201)
async def recovery_checkin(
    data: RecoveryCheckinCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    target_date = data.log_date or date.today()

    existing = await db.execute(
        select(RecoveryLog).where(
            RecoveryLog.user_id == current_user.id, RecoveryLog.log_date == target_date
        )
    )
    log = existing.scalar_one_or_none()
    if not log:
        log = RecoveryLog(user_id=current_user.id, log_date=target_date)
        db.add(log)

    for field in ["sleep_hours", "sleep_quality", "fatigue_level", "stress_level", "mood", "notes"]:
        val = getattr(data, field, None)
        if val is not None:
            setattr(log, field, val)

    log.recovery_score = calculate_recovery_score(
        sleep_hours=log.sleep_hours,
        sleep_quality=log.sleep_quality,
        fatigue_level=log.fatigue_level,
    )

    await db.flush()

    for s in data.soreness:
        entry = MuscleSorenessEntry(log_id=log.id, muscle_group=s.muscle_group, soreness_level=s.soreness_level)
        db.add(entry)

    await db.flush()
    await db.refresh(log)
    return {
        "id": log.id,
        "log_date": log.log_date,
        "recovery_score": log.recovery_score,
        "sleep_hours": log.sleep_hours,
        "sleep_quality": log.sleep_quality,
        "fatigue_level": log.fatigue_level,
    }


@router.get("/recommendations")
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RecoveryLog)
        .where(RecoveryLog.user_id == current_user.id)
        .order_by(RecoveryLog.log_date.desc())
        .limit(7)
    )
    logs = result.scalars().all()

    if not logs:
        return {"recommendation": "Start logging your recovery to get personalized recommendations.", "should_rest": False}

    latest = logs[0]
    avg_score = sum(l.recovery_score or 50 for l in logs) / len(logs)

    if (latest.recovery_score or 50) < 40:
        return {"recommendation": "Your recovery score is low. Consider a rest day or light activity.", "should_rest": True, "score": latest.recovery_score}

    return {"recommendation": "Recovery looks good. You're ready to train.", "should_rest": False, "score": latest.recovery_score}
