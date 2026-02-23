from __future__ import annotations


async def check_and_consume_budget(user_id: str, estimated_tokens: int) -> None:
    """Verify the user has remaining daily token budget and deduct the estimate.

    Stub implementation — replace with Redis-backed tracking.
    """
    raise NotImplementedError("check_and_consume_budget not yet implemented")
