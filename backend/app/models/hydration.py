from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class HydrationLog(Base, TimestampMixin):
    """Daily hydration tracking for a user."""

    __tablename__ = "hydration_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    target_ml: Mapped[int] = mapped_column(Integer, default=2500, nullable=False)
    total_ml: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    entries: Mapped[list[HydrationEntry]] = relationship(
        "HydrationEntry", back_populates="log", cascade="all, delete-orphan"
    )


class HydrationEntry(Base):
    __tablename__ = "hydration_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("hydration_logs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount_ml: Mapped[int] = mapped_column(Integer, nullable=False)
    beverage_type: Mapped[str | None] = mapped_column(String(100))  # water, coffee, juice, etc.
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    log: Mapped[HydrationLog] = relationship("HydrationLog", back_populates="entries")
