from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.nutrition import NutritionLog, MealEntry
from app.models.user import UserProfile


ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

GOAL_ADJUSTMENTS = {
    "lose_weight": -500,
    "maintain": 0,
    "build_muscle": 300,
}


def calculate_bmr(weight_kg: float, height_cm: float, age_years: float, gender: str) -> float:
    """Mifflin-St Jeor BMR formula.

    Male:   10*weight + 6.25*height - 5*age + 5
    Female: 10*weight + 6.25*height - 5*age - 161
    Other:  average of male and female
    """
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age_years
    if gender == "male":
        return base + 5
    elif gender == "female":
        return base - 161
    else:
        # average
        return base - 78.0


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Apply activity multiplier to BMR."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    return bmr * multiplier


def calculate_calorie_target(tdee: float, goal: str) -> float:
    """Apply goal-based calorie adjustment."""
    adjustment = GOAL_ADJUSTMENTS.get(goal, 0)
    return tdee + adjustment


async def calculate_user_tdee(db: AsyncSession, user_id: str) -> dict:
    """Fetch UserProfile, compute BMR -> TDEE -> calorie target, return all values.

    Raises 422 if profile missing or incomplete (missing weight, height, dob, gender, activity_level).
    """
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=422,
            detail={"code": "INCOMPLETE_PROFILE", "message": "User profile not found. Please complete your profile first."}
        )

    missing = []
    if profile.weight_kg is None:
        missing.append("weight_kg")
    if profile.height_cm is None:
        missing.append("height_cm")
    if profile.date_of_birth is None:
        missing.append("date_of_birth")
    if not profile.gender:
        missing.append("gender")
    if not profile.activity_level:
        missing.append("activity_level")

    if missing:
        raise HTTPException(
            status_code=422,
            detail={"code": "INCOMPLETE_PROFILE", "message": f"Profile is missing required fields: {', '.join(missing)}"}
        )

    # Calculate age
    now = datetime.now(UTC)
    dob = profile.date_of_birth
    # Handle both timezone-aware and naive datetimes
    if dob.tzinfo is None:
        dob = dob.replace(tzinfo=UTC)
    age_years = (now - dob).days / 365.25

    bmr = calculate_bmr(profile.weight_kg, profile.height_cm, age_years, profile.gender)
    tdee = calculate_tdee(bmr, profile.activity_level)
    goal = profile.fitness_goal or "maintain"
    target = calculate_calorie_target(tdee, goal)

    return {
        "bmr": round(bmr, 1),
        "tdee": round(tdee, 1),
        "calorie_target": round(target, 1),
        "activity_level": profile.activity_level,
        "goal": goal,
    }
