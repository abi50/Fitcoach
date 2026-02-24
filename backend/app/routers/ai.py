from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.client import get_ai_client
from app.ai.context_builder import build_user_context
from app.ai.token_budget import check_and_consume_budget
from app.dependencies import get_current_user, get_db, get_optional_user
from app.models.base import generate_uuid
from app.models.nutrition import NutritionPlan
from app.models.user import User
from app.models.workout import WorkoutPlan
from app.schemas.ai import (
    NutritionPlanRequest,
    RecoveryAdviceRequest,
    SavedPlanResponse,
    SaveMealPlanRequest,
    SaveWorkoutPlanRequest,
    WorkoutPlanRequest,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Generation endpoints — guest-accessible (no auth required)
# ---------------------------------------------------------------------------


@router.post("/workout-plan")
async def generate_workout_plan(
    request: WorkoutPlanRequest,
    current_user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Stream a GPT-4o workout plan. Guests can generate; auth required to save."""
    user_id = current_user.id if current_user else None
    await check_and_consume_budget(user_id=user_id, estimated_tokens=5000)
    context = await build_user_context(db=db, user_id=user_id)
    client = get_ai_client()

    async def _stream() -> Any:
        try:
            from app.ai.prompts.workout_planner import build_workout_prompt

            system_prompt, user_prompt = build_workout_prompt(
                context=context, request=request
            )
            async for chunk in client.stream_json(
                system_prompt=system_prompt, user_prompt=user_prompt
            ):
                yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as exc:  # noqa: BLE001
            yield f"data: {json.dumps({'type': 'error', 'error': str(exc)})}\n\n"

    return StreamingResponse(_stream(), media_type="text/event-stream")


@router.post("/meal-plan")
async def generate_meal_plan(
    request: NutritionPlanRequest,
    current_user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Stream a GPT-4o meal plan. Guests can generate; auth required to save."""
    user_id = current_user.id if current_user else None
    await check_and_consume_budget(user_id=user_id, estimated_tokens=4000)
    context = await build_user_context(db=db, user_id=user_id)
    client = get_ai_client()

    async def _stream() -> Any:
        try:
            from app.ai.prompts.nutrition_planner import build_nutrition_prompt

            system_prompt, user_prompt = build_nutrition_prompt(
                context=context, request=request
            )
            async for chunk in client.stream_json(
                system_prompt=system_prompt, user_prompt=user_prompt
            ):
                yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as exc:  # noqa: BLE001
            yield f"data: {json.dumps({'type': 'error', 'error': str(exc)})}\n\n"

    return StreamingResponse(_stream(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# Save endpoints — auth required
# ---------------------------------------------------------------------------


@router.post(
    "/save-workout-plan",
    response_model=SavedPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_workout_plan(
    request: SaveWorkoutPlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SavedPlanResponse:
    """Persist a generated workout plan to the user's profile."""
    plan_data = request.plan_data
    plan_name = request.name or plan_data.get("plan_name", "My AI Workout Plan")

    plan = WorkoutPlan(
        id=generate_uuid(),
        user_id=current_user.id,
        name=plan_name,
        description=plan_data.get("description"),
        goal=plan_data.get("goal"),
        days_per_week=plan_data.get("days_per_week"),
        duration_weeks=plan_data.get("weeks"),
        is_active=True,
        is_ai_generated=True,
        ai_plan_data=plan_data,
    )
    db.add(plan)
    await db.flush()

    return SavedPlanResponse(id=plan.id, name=plan.name, is_ai_generated=True)


@router.post(
    "/save-meal-plan",
    response_model=SavedPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_meal_plan(
    request: SaveMealPlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SavedPlanResponse:
    """Persist a generated meal plan to the user's profile."""
    plan_data = request.plan_data
    plan_name = request.name or plan_data.get("plan_name", "My AI Meal Plan")
    macros = plan_data.get("macros", {})

    nutrition_plan = NutritionPlan(
        id=generate_uuid(),
        user_id=current_user.id,
        name=plan_name,
        description=plan_data.get("description"),
        total_calories=plan_data.get("daily_calories"),
        protein_g=macros.get("protein_g"),
        carbs_g=macros.get("carbs_g"),
        fat_g=macros.get("fat_g"),
        is_ai_generated=True,
        plan_data=plan_data,
        is_active=True,
    )
    db.add(nutrition_plan)
    await db.flush()

    return SavedPlanResponse(
        id=nutrition_plan.id, name=nutrition_plan.name, is_ai_generated=True
    )


# ---------------------------------------------------------------------------
# Recovery advice — auth required
# ---------------------------------------------------------------------------


@router.post("/recovery-advice")
async def get_recovery_advice(
    request: RecoveryAdviceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    await check_and_consume_budget(user_id=current_user.id, estimated_tokens=2000)
    context = await build_user_context(db=db, user_id=current_user.id)
    client = get_ai_client()

    from app.ai.prompts.recovery_advisor import build_recovery_prompt

    system_prompt, user_prompt = build_recovery_prompt(context=context, request=request)
    advice_json = await client.complete_json(
        system_prompt=system_prompt, user_prompt=user_prompt
    )
    return {"advice": advice_json}
