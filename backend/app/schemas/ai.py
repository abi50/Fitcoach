from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class WorkoutPlanRequest(BaseModel):
    age: int = Field(..., ge=13, le=100)
    fitness_level: str  # beginner, intermediate, advanced
    experience_years: float = Field(0.0, ge=0)
    goal: str  # strength, weight_loss, muscle_gain, endurance
    equipment: list[str] = []  # bodyweight, dumbbells, barbell, machines, cables, bands
    days_per_week: int = Field(4, ge=1, le=7)
    additional_notes: str | None = None


class NutritionPlanRequest(BaseModel):
    weight_kg: float = Field(..., gt=0)
    height_cm: float = Field(..., gt=0)
    age: int = Field(..., ge=13, le=100)
    goal: str  # lose_weight, build_muscle, maintain
    activity_level: str  # sedentary, light, moderate, active, very_active
    dietary_restrictions: list[str] = []
    meals_per_day: int = Field(3, ge=1, le=8)
    additional_notes: str | None = None


class RecoveryAdviceRequest(BaseModel):
    recent_workouts: int = 3
    current_soreness: list[str] = []
    sleep_hours: float | None = None
    additional_notes: str | None = None


class SaveWorkoutPlanRequest(BaseModel):
    plan_data: dict[str, Any]
    name: str | None = None


class SaveMealPlanRequest(BaseModel):
    plan_data: dict[str, Any]
    name: str | None = None


class SavedPlanResponse(BaseModel):
    id: str
    name: str
    is_ai_generated: bool = True


class AIStreamChunk(BaseModel):
    type: str  # "content", "done", "error"
    content: str | None = None
    error: str | None = None
