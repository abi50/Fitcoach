from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class PersonalRecord(Base, TimestampMixin):
    __tablename__ = "personal_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    exercise_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False, index=True
    )
    session_set_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("session_sets.id", ondelete="SET NULL")
    )
    weight_kg: Mapped[float | None] = mapped_column(Float)
    reps: Mapped[int | None] = mapped_column(Integer)
    achieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), index=True
    )
    pr_type: Mapped[str] = mapped_column(String(50), nullable=False)  # weight, reps, weight_x_reps
    previous_best: Mapped[float | None] = mapped_column(Float)  # previous value for comparison
    celebrated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    exercise: Mapped["Exercise"] = relationship("Exercise")
