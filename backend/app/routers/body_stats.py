from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.body_stats import BodyMeasurement
from app.models.user import User
from app.schemas.body_stats import BodyMeasurementCreate, BodyMeasurementResponse
from app.services.body_stats_service import calculate_dashboard

router = APIRouter()


@router.post("/measurements", response_model=BodyMeasurementResponse, status_code=201)
async def log_measurement(
    data: BodyMeasurementCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    measurement = BodyMeasurement(user_id=current_user.id, **data.model_dump(exclude_none=True))
    db.add(measurement)
    await db.flush()
    await db.refresh(measurement)
    return measurement


@router.get("/measurements", response_model=list[BodyMeasurementResponse])
async def list_measurements(
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BodyMeasurement)
        .where(BodyMeasurement.user_id == current_user.id)
        .order_by(BodyMeasurement.measured_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await calculate_dashboard(db=db, user_id=current_user.id)
