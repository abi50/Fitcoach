from __future__ import annotations
from pydantic import BaseModel


class WorkoutPlanRequest(BaseModel):
    goal: str
    duration_weeks: int = 8
    days_per_week: int = 4
    focus_areas: list[str] = []
    additional_notes: str | None = None


class NutritionPlanRequest(BaseModel):
    goal: str
    dietary_restrictions: list[str] = []
    meals_per_day: int = 3
    additional_notes: str | None = None


class RecoveryAdviceRequest(BaseModel):
    recent_workouts: int = 3
    current_soreness: list[str] = []
    sleep_hours: float | None = None
    additional_notes: str | None = None


class AIStreamChunk(BaseModel):
    type: str  # "content", "done", "error"
    content: str | None = None
    error: str | None = None
