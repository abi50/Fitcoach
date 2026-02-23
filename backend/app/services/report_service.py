from __future__ import annotations

import datetime

from sqlalchemy.ext.asyncio import AsyncSession


async def generate_weekly_report(
    db: AsyncSession,
    user_id: str,
    week_start: datetime.date,
) -> dict:
    """Generate a weekly fitness summary report.

    Stub implementation — replace with real aggregation queries.
    """
    raise NotImplementedError("generate_weekly_report not yet implemented")


async def generate_monthly_report(
    db: AsyncSession,
    user_id: str,
    month: int,
    year: int,
) -> dict:
    """Generate a monthly fitness summary report.

    Stub implementation — replace with real aggregation queries.
    """
    raise NotImplementedError("generate_monthly_report not yet implemented")
