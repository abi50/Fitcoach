from __future__ import annotations
from datetime import date, datetime
from pydantic import BaseModel


class FoodItemResponse(BaseModel):
    id: str
    name: str
    brand: str | None
    calories_per_100g: float | None
    protein_per_100g: float | None
    carbs_per_100g: float | None
    fat_per_100g: float | None
    serving_size_g: float | None
    serving_name: str | None

    class Config:
        from_attributes = True


class MealEntryCreate(BaseModel):
    food_item_id: str
    meal_type: str | None = None
    amount_g: float


class MealEntryResponse(BaseModel):
    id: str
    food_item_id: str
    meal_type: str | None
    amount_g: float
    calories: float | None
    protein_g: float | None
    carbs_g: float | None
    fat_g: float | None
    logged_at: datetime

    class Config:
        from_attributes = True


class NutritionLogResponse(BaseModel):
    id: str
    log_date: date
    target_calories: float | None
    target_protein_g: float | None
    target_carbs_g: float | None
    target_fat_g: float | None
    meals: list[MealEntryResponse]

    class Config:
        from_attributes = True


class FoodItemCreate(BaseModel):
    name: str
    brand: str | None = None
    calories_per_100g: float | None = None
    protein_per_100g: float | None = None
    carbs_per_100g: float | None = None
    fat_per_100g: float | None = None
    serving_size_g: float | None = None
    serving_name: str | None = None
