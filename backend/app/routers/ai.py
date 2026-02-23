from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.ai import NutritionPlanRequest, RecoveryAdviceRequest, WorkoutPlanRequest
from app.ai.client import get_ai_client
from app.ai.context_builder import build_user_context
from app.ai.token_budget import check_and_consume_budget

router = APIRouter()


@router.post("/workout-plan")
async def generate_workout_plan(
    request: WorkoutPlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_and_consume_budget(user_id=current_user.id, estimated_tokens=5000)
    context = await build_user_context(db=db, user_id=current_user.id)
    client = get_ai_client()

    async def stream_plan():
        from app.ai.prompts.workout_planner import build_workout_prompt
        prompt = build_workout_prompt(context=context, request=request)
        async for chunk in client.stream_message(prompt=prompt):
            yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(stream_plan(), media_type="text/event-stream")


@router.post("/nutrition-plan")
async def generate_nutrition_plan(
    request: NutritionPlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_and_consume_budget(user_id=current_user.id, estimated_tokens=4000)
    context = await build_user_context(db=db, user_id=current_user.id)
    client = get_ai_client()

    async def stream_plan():
        from app.ai.prompts.nutrition_planner import build_nutrition_prompt
        prompt = build_nutrition_prompt(context=context, request=request)
        async for chunk in client.stream_message(prompt=prompt):
            yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(stream_plan(), media_type="text/event-stream")


@router.post("/recovery-advice")
async def get_recovery_advice(
    request: RecoveryAdviceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_and_consume_budget(user_id=current_user.id, estimated_tokens=2000)
    context = await build_user_context(db=db, user_id=current_user.id)
    client = get_ai_client()

    from app.ai.prompts.recovery_advisor import build_recovery_prompt
    prompt = build_recovery_prompt(context=context, request=request)
    response = await client.complete_message(prompt=prompt)
    return {"advice": response}
