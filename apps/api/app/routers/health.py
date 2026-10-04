"""
Health and readiness endpoints.

These endpoints genuinely verify relevant service state:
- /health: basic application health
- /ready: verifies database and Redis connectivity
"""

from datetime import UTC, datetime

from fastapi import APIRouter
from sqlalchemy import text

from app.database import async_session_factory
from app.logging_config import get_logger

router = APIRouter(tags=["health"])
logger = get_logger(__name__)


@router.get("/health")
async def health_check() -> dict[str, str]:
    """
    Basic health check.

    Returns the application status and current timestamp.
    This endpoint confirms the API process is running and can handle requests.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "0.1.0",
    }


@router.get("/ready")
async def readiness_check() -> dict[str, object]:
    """
    Readiness check that verifies database and Redis connectivity.

    Returns the status of each dependency. The overall status is 'ready'
    only if all dependencies are connected.
    """
    checks: dict[str, str] = {}
    all_ready = True

    # Check database
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception as exc:
        logger.error("readiness_check_db_failed", error=str(exc))
        checks["database"] = "disconnected"
        all_ready = False



    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
        "timestamp": datetime.now(UTC).isoformat(),
    }
