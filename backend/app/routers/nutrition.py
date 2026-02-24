from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_current_user, get_db
from app.models.nutrition import FoodItem, MealEntry, NutritionLog
from app.models.user import User
from app.schemas.nutrition import FoodItemCreate, MealEntryCreate, NutritionLogResponse

router = APIRouter()


@router.get("/foods/search")
async def search_foods(
    q: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(FoodItem).where(FoodItem.name.ilike(f"%{q}%")).limit(20)
    )
    foods = result.scalars().all()
    return {"data": [
        {"id": f.id, "name": f.name, "brand": f.brand, "calories_per_100g": f.calories_per_100g,
         "protein_per_100g": f.protein_per_100g, "carbs_per_100g": f.carbs_per_100g, "fat_per_100g": f.fat_per_100g}
        for f in foods
    ]}


@router.get("/log", response_model=NutritionLogResponse)
async def get_log(
    log_date: date | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    target_date = log_date or date.today()
    result = await db.execute(
        select(NutritionLog)
        .where(NutritionLog.user_id == current_user.id, NutritionLog.log_date == target_date)
        .options(selectinload(NutritionLog.meals))
    )
    log = result.scalar_one_or_none()
    if not log:
        log = NutritionLog(user_id=current_user.id, log_date=target_date)
        db.add(log)
        await db.flush()
        await db.refresh(log)
    return log


@router.post("/meals")
async def log_meal(
    data: MealEntryCreate,
    log_date: date | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    target_date = log_date or date.today()

    result = await db.execute(
        select(NutritionLog).where(
            NutritionLog.user_id == current_user.id, NutritionLog.log_date == target_date
        )
    )
    log = result.scalar_one_or_none()
    if not log:
        log = NutritionLog(user_id=current_user.id, log_date=target_date)
        db.add(log)
        await db.flush()

    food_result = await db.execute(select(FoodItem).where(FoodItem.id == data.food_item_id))
    food = food_result.scalar_one_or_none()
    if not food:
        raise HTTPException(status_code=404, detail="Food item not found")

    ratio = data.amount_g / 100.0
    entry = MealEntry(
        log_id=log.id,
        food_item_id=data.food_item_id,
        meal_type=data.meal_type,
        amount_g=data.amount_g,
        calories=(food.calories_per_100g or 0) * ratio,
        protein_g=(food.protein_per_100g or 0) * ratio,
        carbs_g=(food.carbs_per_100g or 0) * ratio,
        fat_g=(food.fat_per_100g or 0) * ratio,
    )
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return entry


@router.get("/tdee")
async def get_tdee(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.services.nutrition_service import calculate_user_tdee
    return await calculate_user_tdee(db, current_user.id)


@router.post("/foods", status_code=201)
async def create_food(
    data: FoodItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    food = FoodItem(created_by=current_user.id, **data.model_dump())
    db.add(food)
    await db.flush()
    await db.refresh(food)
    return {
        "id": food.id,
        "name": food.name,
        "brand": food.brand,
        "calories_per_100g": food.calories_per_100g,
        "protein_per_100g": food.protein_per_100g,
        "carbs_per_100g": food.carbs_per_100g,
        "fat_per_100g": food.fat_per_100g,
    }
