from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.workout import (
    Exercise,
    SessionSet,
    WorkoutPlan,
    WorkoutSession,
)
from app.schemas.workout import (
    ExerciseCreate,
    SessionSetCreate,
    SessionSetResponse,
    WorkoutPlanCreate,
    WorkoutPlanResponse,
    WorkoutPlanUpdate,
    WorkoutSessionCreate,
    WorkoutSessionResponse,
)
from app.services.pr_service import check_and_create_pr
from app.services.workout_service import calculate_session_volume

router = APIRouter()


@router.get("/exercises")
async def list_exercises(
    q: str | None = None,
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Exercise)
    if q:
        query = query.where(Exercise.name.ilike(f"%{q}%"))
    if category:
        query = query.where(Exercise.category == category)
    result = await db.execute(query.limit(50))
    exercises = result.scalars().all()
    return {"data": [{"id": e.id, "name": e.name, "category": e.category, "muscle_groups": e.muscle_groups, "equipment": e.equipment} for e in exercises]}


@router.post("/exercises", status_code=status.HTTP_201_CREATED)
async def create_exercise(
    data: ExerciseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    exercise = Exercise(
        is_custom=True,
        created_by=current_user.id,
        **data.model_dump(),
    )
    db.add(exercise)
    await db.flush()
    await db.refresh(exercise)
    return {
        "id": exercise.id,
        "name": exercise.name,
        "category": exercise.category,
        "muscle_groups": exercise.muscle_groups,
        "equipment": exercise.equipment,
    }


@router.get("/plans", response_model=list[WorkoutPlanResponse])
async def list_plans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkoutPlan).where(WorkoutPlan.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/plans", response_model=WorkoutPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    data: WorkoutPlanCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    plan = WorkoutPlan(user_id=current_user.id, **data.model_dump())
    db.add(plan)
    await db.flush()
    await db.refresh(plan)
    return plan


@router.put("/plans/{plan_id}", response_model=WorkoutPlanResponse)
async def update_plan(
    plan_id: str,
    data: WorkoutPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkoutPlan).where(
            WorkoutPlan.id == plan_id, WorkoutPlan.user_id == current_user.id
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(plan, field, value)
    await db.flush()
    await db.refresh(plan)
    return plan


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkoutPlan).where(
            WorkoutPlan.id == plan_id, WorkoutPlan.user_id == current_user.id
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    await db.delete(plan)


@router.post("/sessions", response_model=WorkoutSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    data: WorkoutSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = WorkoutSession(
        user_id=current_user.id,
        **data.model_dump(),
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)
    return session


@router.post("/sessions/{session_id}/complete", response_model=WorkoutSessionResponse)
async def complete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.id == session_id, WorkoutSession.user_id == current_user.id)
        .options(selectinload(WorkoutSession.sets))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.completed_at = datetime.now(UTC)
    if session.started_at:
        started = session.started_at
        if started.tzinfo is None:
            started = started.replace(tzinfo=UTC)
        delta = session.completed_at - started
        session.duration_minutes = int(delta.total_seconds() / 60)
    session.total_volume_kg = calculate_session_volume(session.sets)

    await db.flush()
    await db.refresh(session)
    return session


@router.post(
    "/sessions/{session_id}/sets",
    response_model=SessionSetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def log_set(
    session_id: str,
    data: SessionSetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session_result = await db.execute(
        select(WorkoutSession).where(
            WorkoutSession.id == session_id, WorkoutSession.user_id == current_user.id
        )
    )
    if not session_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Session not found")

    set_obj = SessionSet(session_id=session_id, **data.model_dump())
    db.add(set_obj)
    await db.flush()

    # PR detection
    is_pr = await check_and_create_pr(
        db=db,
        user_id=current_user.id,
        exercise_id=data.exercise_id,
        weight_kg=data.weight_kg,
        reps=data.reps,
        set_id=set_obj.id,
    )
    set_obj.is_pr = is_pr

    await db.flush()
    await db.refresh(set_obj)
    return set_obj


@router.get("/sessions", response_model=list[WorkoutSessionResponse])
async def list_sessions(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.user_id == current_user.id)
        .order_by(WorkoutSession.started_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return result.scalars().all()
