from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.models.base import Base, TimestampMixin, generate_uuid


class Exercise(Base, TimestampMixin):
    """Master exercise library."""

    __tablename__ = "exercises"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100))  # strength, cardio, flexibility
    muscle_groups: Mapped[list[str] | None] = mapped_column(JSON)
    equipment: Mapped[str | None] = mapped_column(String(100))
    instructions: Mapped[str | None] = mapped_column(Text)
    video_url: Mapped[str | None] = mapped_column(String(500))
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL")
    )


class WorkoutPlan(Base, TimestampMixin):
    __tablename__ = "workout_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    goal: Mapped[str | None] = mapped_column(String(100))
    duration_weeks: Mapped[int | None] = mapped_column(Integer)
    days_per_week: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_plan_data: Mapped[dict | None] = mapped_column(JSON)

    days: Mapped[list[WorkoutPlanDay]] = relationship(
        "WorkoutPlanDay", back_populates="plan", cascade="all, delete-orphan", order_by="WorkoutPlanDay.day_number"
    )


class WorkoutPlanDay(Base):
    __tablename__ = "workout_plan_days"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workout_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str | None] = mapped_column(String(100))  # e.g., "Push Day", "Leg Day"
    focus: Mapped[str | None] = mapped_column(String(100))

    plan: Mapped[WorkoutPlan] = relationship("WorkoutPlan", back_populates="days")
    exercises: Mapped[list[WorkoutPlanExercise]] = relationship(
        "WorkoutPlanExercise", back_populates="day", cascade="all, delete-orphan", order_by="WorkoutPlanExercise.order"
    )


class WorkoutPlanExercise(Base):
    __tablename__ = "workout_plan_exercises"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    day_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workout_plan_days.id", ondelete="CASCADE"), nullable=False, index=True
    )
    exercise_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, default=0)
    sets: Mapped[int | None] = mapped_column(Integer)
    reps: Mapped[str | None] = mapped_column(String(50))  # "8-12" or "10"
    rest_seconds: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)

    day: Mapped[WorkoutPlanDay] = relationship("WorkoutPlanDay", back_populates="exercises")
    exercise: Mapped[Exercise] = relationship("Exercise")


class WorkoutSession(Base, TimestampMixin):
    __tablename__ = "workout_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("workout_plans.id", ondelete="SET NULL")
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    total_volume_kg: Mapped[float | None] = mapped_column(Float)

    sets: Mapped[list[SessionSet]] = relationship(
        "SessionSet", back_populates="session", cascade="all, delete-orphan"
    )


class SessionSet(Base):
    __tablename__ = "session_sets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    exercise_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float | None] = mapped_column(Float)
    reps: Mapped[int | None] = mapped_column(Integer)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)  # for time-based exercises
    rpe: Mapped[float | None] = mapped_column(Float)  # rate of perceived exertion 1-10
    is_pr: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(String(500))

    session: Mapped[WorkoutSession] = relationship("WorkoutSession", back_populates="sets")
    exercise: Mapped[Exercise] = relationship("Exercise")
