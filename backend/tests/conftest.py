from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.dependencies import get_db
from app.main import app as fastapi_app

# Pre-import all models so Base.metadata is fully populated before any fixture runs.
# These must come after app import but use explicit module imports to avoid
# shadowing the `fastapi_app` name.
from app.models.base import Base  # noqa: F401
from app.models import user as _m_user  # noqa: F401
from app.models import workout as _m_workout  # noqa: F401
from app.models import nutrition as _m_nutrition  # noqa: F401
from app.models import body_stats as _m_body_stats  # noqa: F401
from app.models import personal_record as _m_personal_record  # noqa: F401
from app.models import hydration as _m_hydration  # noqa: F401
from app.models import recovery as _m_recovery  # noqa: F401


@pytest.fixture
async def client():
    """Async test client backed by a fresh in-memory SQLite database per test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    fastapi_app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        yield ac

    fastapi_app.dependency_overrides.clear()
    await engine.dispose()
