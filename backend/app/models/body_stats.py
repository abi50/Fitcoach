from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class BodyMeasurement(Base, TimestampMixin):
    __tablename__ = "body_measurements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), index=True
    )
    weight_kg: Mapped[float | None] = mapped_column(Float)
    body_fat_pct: Mapped[float | None] = mapped_column(Float)
    waist_cm: Mapped[float | None] = mapped_column(Float)
    chest_cm: Mapped[float | None] = mapped_column(Float)
    hips_cm: Mapped[float | None] = mapped_column(Float)
    neck_cm: Mapped[float | None] = mapped_column(Float)
    left_arm_cm: Mapped[float | None] = mapped_column(Float)
    right_arm_cm: Mapped[float | None] = mapped_column(Float)
    left_thigh_cm: Mapped[float | None] = mapped_column(Float)
    right_thigh_cm: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)


class ProgressPhoto(Base, TimestampMixin):
    __tablename__ = "progress_photos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    taken_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), index=True
    )
    s3_url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))
    angle: Mapped[str | None] = mapped_column(String(50))  # front, back, side
    notes: Mapped[str | None] = mapped_column(Text)
