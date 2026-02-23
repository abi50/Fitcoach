from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class ExerciseResponse(BaseModel):
    id: str
    name: str
    category: str | None
    muscle_groups: list[str] | None
    equipment: str | None
    instructions: str | None

    class Config:
        from_attributes = True


class WorkoutPlanCreate(BaseModel):
    name: str
    description: str | None = None
    goal: str | None = None
    duration_weeks: int | None = None
    days_per_week: int | None = None


class WorkoutPlanUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    goal: str | None = None
    is_active: bool | None = None


class WorkoutPlanDayCreate(BaseModel):
    day_number: int
    name: str | None = None
    focus: str | None = None


class WorkoutPlanExerciseCreate(BaseModel):
    exercise_id: str
    order: int = 0
    sets: int | None = None
    reps: str | None = None
    rest_seconds: int | None = None
    notes: str | None = None


class WorkoutPlanResponse(BaseModel):
    id: str
    name: str
    description: str | None
    goal: str | None
    duration_weeks: int | None
    days_per_week: int | None
    is_active: bool
    is_ai_generated: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SessionSetCreate(BaseModel):
    exercise_id: str
    set_number: int
    weight_kg: float | None = None
    reps: int | None = None
    rpe: float | None = None
    notes: str | None = None


class SessionSetResponse(BaseModel):
    id: str
    exercise_id: str
    set_number: int
    weight_kg: float | None
    reps: int | None
    rpe: float | None
    is_pr: bool
    notes: str | None

    class Config:
        from_attributes = True


class WorkoutSessionCreate(BaseModel):
    plan_id: str | None = None
    started_at: datetime
    notes: str | None = None


class WorkoutSessionResponse(BaseModel):
    id: str
    plan_id: str | None
    started_at: datetime
    completed_at: datetime | None
    duration_minutes: int | None
    total_volume_kg: float | None
    notes: str | None

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    data: list
    total: int
    page: int
    page_size: int
    pages: int
