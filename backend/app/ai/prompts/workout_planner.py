from __future__ import annotations

from app.schemas.ai import WorkoutPlanRequest


def build_workout_prompt(context: dict, request: WorkoutPlanRequest) -> str:
    """Build the system + user prompt for workout plan generation.

    Stub implementation — replace with real prompt engineering.
    """
    raise NotImplementedError("build_workout_prompt not yet implemented")
