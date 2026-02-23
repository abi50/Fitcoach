from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.database import create_tables
from app.routers import (
    auth,
    users,
    workouts,
    nutrition,
    body_stats,
    personal_records,
    hydration,
    recovery,
    reports,
    ai,
)

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    logger.info("Starting FitCoach AI API...")
    await create_tables()
    yield
    logger.info("Shutting down FitCoach AI API...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="FitCoach AI API",
        description="AI-powered fitness coaching platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    prefix = "/api/v1"
    app.include_router(auth.router, prefix=f"{prefix}/auth", tags=["auth"])
    app.include_router(users.router, prefix=f"{prefix}/users", tags=["users"])
    app.include_router(workouts.router, prefix=f"{prefix}/workouts", tags=["workouts"])
    app.include_router(nutrition.router, prefix=f"{prefix}/nutrition", tags=["nutrition"])
    app.include_router(body_stats.router, prefix=f"{prefix}/body-stats", tags=["body-stats"])
    app.include_router(
        personal_records.router, prefix=f"{prefix}/personal-records", tags=["personal-records"]
    )
    app.include_router(hydration.router, prefix=f"{prefix}/hydration", tags=["hydration"])
    app.include_router(recovery.router, prefix=f"{prefix}/recovery", tags=["recovery"])
    app.include_router(reports.router, prefix=f"{prefix}/reports", tags=["reports"])
    app.include_router(ai.router, prefix=f"{prefix}/ai", tags=["ai"])

    @app.get("/api/v1/health")
    async def health_check():
        return {"status": "healthy", "environment": settings.ENVIRONMENT}

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL_ERROR", "message": "Internal server error"}},
        )

    return app


app = create_app()
