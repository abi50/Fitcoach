from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class RecoveryLog(Base, TimestampMixin):
    __tablename__ = "recovery_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    sleep_hours: Mapped[float | None] = mapped_column(Float)
    sleep_quality: Mapped[int | None] = mapped_column(Integer)  # 1-5
    fatigue_level: Mapped[int | None] = mapped_column(Integer)  # 1-10 (higher = more fatigued)
    stress_level: Mapped[int | None] = mapped_column(Integer)  # 1-10
    mood: Mapped[int | None] = mapped_column(Integer)  # 1-5
    recovery_score: Mapped[float | None] = mapped_column(Float)  # 0-100, calculated
    notes: Mapped[str | None] = mapped_column(Text)

    soreness_entries: Mapped[list[MuscleSorenessEntry]] = relationship(
        "MuscleSorenessEntry", back_populates="log", cascade="all, delete-orphan"
    )


class MuscleSorenessEntry(Base):
    __tablename__ = "muscle_soreness_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("recovery_logs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    muscle_group: Mapped[str] = mapped_column(String(100), nullable=False)
    soreness_level: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5

    log: Mapped[RecoveryLog] = relationship("RecoveryLog", back_populates="soreness_entries")
