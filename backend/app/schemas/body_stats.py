from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class BodyMeasurementCreate(BaseModel):
    measured_at: datetime | None = None
    weight_kg: float | None = None
    body_fat_pct: float | None = None
    waist_cm: float | None = None
    chest_cm: float | None = None
    hips_cm: float | None = None
    neck_cm: float | None = None
    left_arm_cm: float | None = None
    right_arm_cm: float | None = None
    left_thigh_cm: float | None = None
    right_thigh_cm: float | None = None
    notes: str | None = None


class BodyMeasurementResponse(BaseModel):
    id: str
    measured_at: datetime
    weight_kg: float | None
    body_fat_pct: float | None
    waist_cm: float | None
    chest_cm: float | None
    hips_cm: float | None
    neck_cm: float | None
    left_arm_cm: float | None
    right_arm_cm: float | None
    notes: str | None

    class Config:
        from_attributes = True


class BodyStatsDashboard(BaseModel):
    latest_weight_kg: float | None
    bmi: float | None
    body_fat_pct: float | None
    strength_score: float | None
    weight_trend: list[dict]
    measurements_history: list[BodyMeasurementResponse]
