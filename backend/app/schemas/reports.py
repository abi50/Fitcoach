from __future__ import annotations
from datetime import date
from pydantic import BaseModel


class WeeklyReportResponse(BaseModel):
    week_start: date
    week_end: date
    total_workouts: int
    total_volume_kg: float
    avg_recovery_score: float | None
    total_water_ml: int
    weight_change_kg: float | None
    new_prs: int
    workout_days: list[dict]
    top_exercises: list[dict]


class MonthlyReportResponse(BaseModel):
    month: int
    year: int
    total_workouts: int
    total_volume_kg: float
    avg_recovery_score: float | None
    weight_change_kg: float | None
    new_prs: int
    weekly_breakdown: list[dict]
