from __future__ import annotations

from collections import defaultdict
from datetime import date

from fastapi import HTTPException, status

from app.config import get_settings

# In-memory daily usage counter: {(user_id, "YYYY-MM-DD") -> tokens_used}
# For production, replace with Redis-backed atomic counter.
_daily_usage: dict[tuple[str, str], int] = defaultdict(int)


async def check_and_consume_budget(user_id: str | None, estimated_tokens: int) -> None:
    """Check and deduct from the user's daily token budget.

    Guests (user_id=None) are not checked here — apply rate limiting at
    infra level (e.g. nginx or Cloudflare) for guest endpoints.
    """
    if user_id is None:
        return

    settings = get_settings()
    today = str(date.today())
    key = (user_id, today)

    current = _daily_usage[key]
    if current + estimated_tokens > settings.DAILY_TOKEN_BUDGET:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily AI token budget exceeded. Try again tomorrow.",
        )

    _daily_usage[key] += estimated_tokens
