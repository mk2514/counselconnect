"""
CounselConnect API - Application Factory

Creates and configures the FastAPI application with:
- CORS middleware
- Structured logging
- Error handlers
- Health/readiness routes
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.errors import register_error_handlers
from app.logging_config import configure_logging
from app.models.base import Base
from app.routers import auth, health, police, court, lawyer, ai, nfc_auth


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: startup and shutdown."""
    configure_logging()

    # Create tables if they don't exist (for prototype/demo deployment without alembic)
    import app.models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Startup: verify connections are possible
    # Actual connection pool is lazy; health/ready endpoints verify state.
    yield

    await engine.dispose()


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title="CounselConnect API",
        description="Judicial Case Management Platform API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.python_env == "development" else None,
        redoc_url="/redoc" if settings.python_env == "development" else None,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            settings.app_origin,
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Error handlers
    register_error_handlers(app)

    # Routers
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(police.router)
    app.include_router(court.router)
    app.include_router(lawyer.router)
    app.include_router(ai.router)
    app.include_router(nfc_auth.router)
    app.include_router(nfc_auth.qr_router)

    return app


app = create_app()
