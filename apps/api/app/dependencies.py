"""
Authentication and authorization dependencies.

Per project rules:
- Every protected endpoint must perform role authorization
- Hiding frontend menus is NOT authorization
- Verify: authenticated user, role, case authorization, action permission
- Return 401 for unauthenticated, 403 for unauthorized
"""

import uuid
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.errors import AuthenticationError, AuthorizationError
from app.models.legal import LawyerAssignment
from app.security.session import get_session


async def get_current_user(request: Request) -> dict[str, str]:
    """
    Dependency that extracts and validates the current user from the session.

    Returns session data dict with: user_id, role, identifier, display_name.
    """
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise AuthenticationError("Authentication required. Please sign in.")

    session = await get_session(session_token)
    if not session:
        raise AuthenticationError("Session expired. Please sign in again.")

    # Ensure backward compatibility with routers expecting 'id' instead of 'user_id'
    session["id"] = session["user_id"]
    return session


# Type alias for use in route dependencies
CurrentUser = Annotated[dict[str, str], Depends(get_current_user)]


def require_role(*roles: str):  # type: ignore[no-untyped-def]
    """
    Dependency factory that requires the current user to have one of the specified roles.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_role("COURT_AUTHORITY"))])
        async def admin_route():
            ...
    """

    async def role_checker(user: CurrentUser) -> dict[str, str]:
        user_role = user.get("role", "")
        if user_role not in roles:
            raise AuthorizationError(
                f"This action requires one of the following roles: {', '.join(roles)}."
            )
        return user

    return Depends(role_checker)


# Convenience dependencies for specific roles
RequirePolice = require_role("POLICE")
RequireLawyer = require_role("LAWYER")
RequireCourtAuthority = require_role("COURT_AUTHORITY")


async def require_case_access(
    case_id: uuid.UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """
    Dependency that verifies the current user has access to a specific case.

    - COURT_AUTHORITY and POLICE have broad access.
    - LAWYER must be assigned to the case.
    """
    role = user.get("role", "")

    # Court Authority and Police have broad case access
    if role in ("COURT_AUTHORITY", "POLICE"):
        return user

    # Lawyer must be assigned
    if role == "LAWYER":
        user_id = uuid.UUID(user["user_id"])
        stmt = select(LawyerAssignment).where(
            LawyerAssignment.case_id == case_id,
            LawyerAssignment.lawyer_id == user_id,
            LawyerAssignment.status == "ACTIVE",
        )
        result = await db.execute(stmt)
        assignment = result.scalar_one_or_none()
        if not assignment:
            raise AuthorizationError(
                "You are not assigned to this case."
            )
        return user

    raise AuthorizationError("Access denied.")
