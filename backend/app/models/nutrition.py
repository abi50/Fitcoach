from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.models.base import Base, TimestampMixin, generate_uuid


class FoodItem(Base, TimestampMixin):
    __tablename__ = "food_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    brand: Mapped[str | None] = mapped_column(String(200))
    calories_per_100g: Mapped[float | None] = mapped_column(Float)
    protein_per_100g: Mapped[float | None] = mapped_column(Float)
    carbs_per_100g: Mapped[float | None] = mapped_column(Float)
    fat_per_100g: Mapped[float | None] = mapped_column(Float)
    fiber_per_100g: Mapped[float | None] = mapped_column(Float)
    serving_size_g: Mapped[float | None] = mapped_column(Float)
    serving_name: Mapped[str | None] = mapped_column(String(100))
    usda_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL")
    )


class NutritionLog(Base, TimestampMixin):
    """Daily nutrition log for a user."""

    __tablename__ = "nutrition_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    target_calories: Mapped[float | None] = mapped_column(Float)
    target_protein_g: Mapped[float | None] = mapped_column(Float)
    target_carbs_g: Mapped[float | None] = mapped_column(Float)
    target_fat_g: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)

    meals: Mapped[list[MealEntry]] = relationship(
        "MealEntry", back_populates="log", cascade="all, delete-orphan"
    )


class MealEntry(Base, TimestampMixin):
    __tablename__ = "meal_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("nutrition_logs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    food_item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("food_items.id", ondelete="CASCADE"), nullable=False
    )
    meal_type: Mapped[str | None] = mapped_column(String(50))  # breakfast, lunch, dinner, snack
    amount_g: Mapped[float] = mapped_column(Float, nullable=False)
    calories: Mapped[float | None] = mapped_column(Float)
    protein_g: Mapped[float | None] = mapped_column(Float)
    carbs_g: Mapped[float | None] = mapped_column(Float)
    fat_g: Mapped[float | None] = mapped_column(Float)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    log: Mapped[NutritionLog] = relationship("NutritionLog", back_populates="meals")
    food_item: Mapped[FoodItem] = relationship("FoodItem")


class NutritionPlan(Base, TimestampMixin):
    __tablename__ = "nutrition_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    total_calories: Mapped[float | None] = mapped_column(Float)
    protein_g: Mapped[float | None] = mapped_column(Float)
    carbs_g: Mapped[float | None] = mapped_column(Float)
    fat_g: Mapped[float | None] = mapped_column(Float)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    plan_data: Mapped[dict | None] = mapped_column(JSON)  # full AI-generated meal plan
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
