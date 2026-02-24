from __future__ import annotations

from app.schemas.ai import RecoveryAdviceRequest

_SYSTEM_PROMPT = """\
You are a sports medicine specialist and recovery coach.
You provide personalised, science-backed recovery recommendations.

Respond with a single valid JSON object:
{
  "overall_status": "string — e.g. 'Good', 'Moderate', 'High Fatigue'",
  "recovery_score": integer (0-100),
  "recommendations": ["string", "string", "string"],
  "today_suggestion": "string — train, active recovery, or full rest, with reasoning",
  "notes": "string — any specific concerns or focus areas"
}
"""


def build_recovery_prompt(context: dict, request: RecoveryAdviceRequest) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for recovery advice."""
    soreness_str = (
        ", ".join(request.current_soreness) if request.current_soreness else "none reported"
    )

    user_prompt = f"""\
Assess recovery and provide recommendations for this athlete:

- Recent workouts in past week: {request.recent_workouts}
- Current muscle soreness: {soreness_str}
- Last night's sleep: {f'{request.sleep_hours} hours' if request.sleep_hours else 'not reported'}
{f'- Additional notes: {request.additional_notes}' if request.additional_notes else ''}

Provide actionable recovery guidance."""

    return _SYSTEM_PROMPT, user_prompt
