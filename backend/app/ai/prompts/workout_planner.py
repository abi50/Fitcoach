from __future__ import annotations

from app.schemas.ai import WorkoutPlanRequest

_SYSTEM_PROMPT = """\
You are an elite personal trainer and strength & conditioning coach with 20+ years of experience.
You create personalized, science-backed workout plans that are practical, progressive, and effective.

You MUST respond with a single valid JSON object matching EXACTLY this schema:
{
  "plan_name": "string — descriptive name, e.g. '4-Day Upper/Lower Split'",
  "description": "string — 2-3 sentence overview of the philosophy and approach",
  "weeks": integer — recommended duration (4–16),
  "days_per_week": integer,
  "weekly_schedule": [
    {
      "day": "string — e.g. 'Monday'",
      "name": "string — e.g. 'Push Day' or 'Rest Day'",
      "focus": "string — muscle groups, e.g. 'Chest, Shoulders, Triceps'",
      "exercises": [
        {
          "name": "string — exercise name",
          "sets": integer,
          "reps": "string — e.g. '8-10' or '5' or 'AMRAP' or '30s'",
          "rest_seconds": integer,
          "notes": "string — form cues, alternatives, or modifications"
        }
      ]
    }
  ],
  "progression_notes": "string — how to progress each week",
  "tips": ["string", "string", "string"]
}

Rules:
- Include ALL 7 days. Rest days have empty exercises array and focus: 'Recovery'.
- Only prescribe exercises achievable with the stated equipment.
- Scale intensity and volume to the athlete's level and experience.
- Be specific with reps ranges and rest periods.
- Provide at least 3 actionable tips.
"""


def build_workout_prompt(context: dict, request: WorkoutPlanRequest) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for workout plan generation."""
    equipment_str = ", ".join(request.equipment) if request.equipment else "bodyweight only"
    rest_days = 7 - request.days_per_week

    profile_lines = []
    if context.get("weight_kg"):
        profile_lines.append(f"- Bodyweight: {context['weight_kg']} kg")
    if context.get("units"):
        profile_lines.append(f"- Preferred units: {context['units']}")

    profile_section = (
        "\nProfile data from account:\n" + "\n".join(profile_lines)
        if profile_lines
        else ""
    )

    user_prompt = f"""\
Create a personalized workout plan for this athlete:

- Age: {request.age}
- Fitness level: {request.fitness_level}
- Training experience: {request.experience_years} year(s)
- Primary goal: {request.goal}
- Available equipment: {equipment_str}
- Training days per week: {request.days_per_week} (rest days: {rest_days})
{f'- Additional notes: {request.additional_notes}' if request.additional_notes else ''}\
{profile_section}

Design a complete 7-day weekly schedule with exactly {request.days_per_week} training days \
and {rest_days} rest/recovery days. Make it challenging but achievable, \
with built-in progressive overload."""

    return _SYSTEM_PROMPT, user_prompt
