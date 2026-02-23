from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession


async def build_user_context(db: AsyncSession, user_id: str) -> dict:
    """Build a context dict for AI prompts from the user's stored data.

    Stub implementation — replace with real profile/history queries.
    """
    raise NotImplementedError("build_user_context not yet implemented")
