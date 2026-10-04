"""
Error handling for the FastAPI application.

Per project rules:
- Return HTTP 401 for unauthenticated access
- Return HTTP 403 for authenticated but unauthorized actions
- Error messages must state what failed, why, and what to correct
- Do not use vague errors
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.logging_config import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    """Base application error."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found.") -> None:
        super().__init__(message=message, status_code=404)


class AuthenticationError(AppError):
    """Request is not authenticated (401)."""

    def __init__(self, message: str = "Authentication required.") -> None:
        super().__init__(message=message, status_code=401)


class AuthorizationError(AppError):
    """Request is authenticated but not authorized (403)."""

    def __init__(self, message: str = "You do not have permission to perform this action.") -> None:
        super().__init__(message=message, status_code=403)


class ConflictError(AppError):
    """Conflict with current state (409)."""

    def __init__(self, message: str = "Operation conflicts with current state.") -> None:
        super().__init__(message=message, status_code=409)


def register_error_handlers(app: FastAPI) -> None:
    """Register global error handlers on the FastAPI app."""

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        logger.warning("app_error", message=exc.message, status_code=exc.status_code)
        body: dict[str, str | None] = {"message": exc.message}
        if exc.detail:
            body["detail"] = exc.detail
        return JSONResponse(status_code=exc.status_code, content=body)

    @app.exception_handler(ValidationError)
    async def validation_error_handler(_request: Request, exc: ValidationError) -> JSONResponse:
        logger.warning("validation_error", errors=exc.error_count())
        errors: dict[str, list[str]] = {}
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.setdefault(field, []).append(error["msg"])
        return JSONResponse(
            status_code=422,
            content={
                "message": "Validation failed.",
                "errors": errors,
            },
        )

    from sqlalchemy.exc import SQLAlchemyError
    import uuid

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(_request: Request, exc: SQLAlchemyError) -> JSONResponse:
        trace_id = str(uuid.uuid4())
        logger.error("database_error", error=str(exc), trace_id=trace_id, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": "An internal database error occurred.", "trace_id": trace_id},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
        trace_id = str(uuid.uuid4())
        logger.error("unhandled_error", error=str(exc), trace_id=trace_id, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": "An internal error occurred. Please try again later.", "trace_id": trace_id},
        )
