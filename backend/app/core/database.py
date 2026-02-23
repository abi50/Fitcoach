from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_tables() -> None:
    from app.models.base import Base  # noqa: F401
    import app.models.user  # noqa: F401
    import app.models.workout  # noqa: F401
    import app.models.nutrition  # noqa: F401
    import app.models.body_stats  # noqa: F401
    import app.models.personal_record  # noqa: F401
    import app.models.hydration  # noqa: F401
    import app.models.recovery  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
