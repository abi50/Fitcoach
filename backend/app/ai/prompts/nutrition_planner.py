from __future__ import annotations

from app.schemas.ai import NutritionPlanRequest
from app.services.nutrition_service import calculate_bmr, calculate_calorie_target, calculate_tdee

_SYSTEM_PROMPT = """\
You are a registered dietitian and sports nutritionist with expertise in performance nutrition.
You create practical, enjoyable meal plans that fuel athletic performance and support body composition goals.

You MUST respond with a single valid JSON object matching EXACTLY this schema:
{
  "plan_name": "string — descriptive name, e.g. 'High-Protein Muscle Builder'",
  "description": "string — 2-3 sentence overview of the nutrition strategy",
  "daily_calories": integer,
  "macros": {
    "protein_g": integer,
    "carbs_g": integer,
    "fat_g": integer
  },
  "meals": [
    {
      "name": "string — e.g. 'Breakfast'",
      "time": "string — e.g. '7:00 AM'",
      "calories": integer,
      "foods": [
        {
          "name": "string",
          "amount": "string — e.g. '100g' or '1 cup' or '2 slices'",
          "calories": integer,
          "protein_g": number,
          "carbs_g": number,
          "fat_g": number
        }
      ]
    }
  ],
  "meal_prep_tips": ["string", "string"],
  "notes": "string — important guidance on timing, hydration, or adjustments"
}

Rules:
- Calories and macros across all meals MUST sum to the target values.
- Use realistic, accessible foods — no obscure ingredients.
- Strictly respect all dietary restrictions provided.
- Protein target for muscle gain / maintenance: 1.8–2.2g/kg bodyweight; for fat loss: 2.0–2.4g/kg.
- Distribute calories sensibly across the day based on training timing.
- Round calories to the nearest 5; macros to the nearest gram.
"""


def build_nutrition_prompt(context: dict, request: NutritionPlanRequest) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for meal plan generation."""
    # Calculate targets server-side for accuracy; default gender to neutral
    gender = context.get("units", "neutral")  # fallback; profile gender not in context yet
    bmr = calculate_bmr(
        weight_kg=request.weight_kg,
        height_cm=request.height_cm,
        age_years=float(request.age),
        gender="male",  # conservative default; adjust when profile has gender
    )
    tdee = calculate_tdee(bmr=bmr, activity_level=request.activity_level)
    calorie_target = int(calculate_calorie_target(tdee=tdee, goal=request.goal))

    restrictions_str = (
        ", ".join(request.dietary_restrictions) if request.dietary_restrictions else "none"
    )

    profile_lines = []
    if context.get("weight_kg"):
        profile_lines.append(f"- Stored weight: {context['weight_kg']} kg")

    profile_section = (
        "\nProfile data from account:\n" + "\n".join(profile_lines)
        if profile_lines
        else ""
    )

    user_prompt = f"""\
Create a daily meal plan for this athlete:

- Weight: {request.weight_kg} kg
- Height: {request.height_cm} cm
- Age: {request.age}
- Goal: {request.goal}
- Activity level: {request.activity_level}
- Dietary restrictions: {restrictions_str}
- Meals per day: {request.meals_per_day}
- Calculated TDEE: {tdee:.0f} kcal/day
- Target calories: {calorie_target} kcal/day
{f'- Additional notes: {request.additional_notes}' if request.additional_notes else ''}\
{profile_section}

Design exactly {request.meals_per_day} meals totalling {calorie_target} calories. \
Prioritise whole foods, high protein, and practical preparation."""

    return _SYSTEM_PROMPT, user_prompt
