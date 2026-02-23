from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession


async def calculate_dashboard(db: AsyncSession, user_id: str) -> dict:
    """Return body stats dashboard data for the given user.

    Stub implementation — replace with real aggregation queries.
    """
    raise NotImplementedError("calculate_dashboard not yet implemented")
