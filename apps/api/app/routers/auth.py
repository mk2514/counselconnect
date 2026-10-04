"""
Authentication router.

Handles registration, login, logout, and session management.

Per project rules:
- A user must be registered before first login.
- Do not create accounts automatically on login.
- Derive role from server-side identity, do not trust frontend role claims.
- Logout must invalidate session server-side.
"""

import uuid

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.errors import AuthenticationError, ConflictError
from app.models.court import Court
from app.models.audit import AuditLog
from app.models.user import CourtAuthorityProfile, LawyerProfile, PoliceProfile, User
from app.schemas.auth import (
    AuthResponse,
    CourtAuthorityRegisterRequest,
    LawyerRegisterRequest,
    LoginRequest,
    MessageResponse,
    PoliceRegisterRequest,
    UserResponse,
)
from app.security.password import hash_password, needs_rehash, verify_password
from app.security.session import create_session, delete_session, get_session

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Cookie settings
_COOKIE_NAME = "session_token"
_COOKIE_MAX_AGE = 86400  # 24 hours


def _set_session_cookie(response: Response, token: str) -> None:
    """Set the session cookie on the response."""
    from app.config import settings
    
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.python_env == "production",
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
        path="/",
        domain=settings.cookie_domain,
    )


def _clear_session_cookie(response: Response) -> None:
    """Clear the session cookie."""
    from app.config import settings
    response.delete_cookie(
        key=_COOKIE_NAME, 
        path="/",
        domain=settings.cookie_domain
    )


# --- Registration Endpoints ---


@router.post("/register/police", response_model=AuthResponse, status_code=201)
async def register_police(
    body: PoliceRegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Register a new police officer."""
    # Check for duplicate station_code
    stmt = select(PoliceProfile).where(
        PoliceProfile.station_code == body.station_code.strip()
    )
    existing = await db.execute(stmt)
    if existing.scalar_one_or_none():
        raise ConflictError(
            f"Police Station Code '{body.station_code.strip()}' is already registered."
        )

    # Create user
    user = User(
        role="POLICE",
        status="ACTIVE",  # For prototype; production would use PENDING_VERIFICATION
        password_hash=hash_password(body.password),
    )
    db.add(user)
    await db.flush()  # Get user.id

    # Create profile
    profile = PoliceProfile(
        user_id=user.id,
        station_code=body.station_code.strip(),
        officer_name=body.officer_name.strip(),
        station_name=body.station_name.strip(),
        jurisdiction=body.jurisdiction.strip() if body.jurisdiction else "",
        verification_status="VERIFIED",  # For prototype
    )
    db.add(profile)
    await db.flush()

    audit = AuditLog(
        actor_user_id=user.id,
        actor_role="POLICE",
        action="REGISTER",
        entity_type="USER",
        entity_id=user.id,
        new_state={"station_code": body.station_code.strip()}
    )
    db.add(audit)
    await db.commit()

    # Create session
    token = await create_session(
        user_id=user.id,
        role="POLICE",
        identifier=body.station_code.strip(),
        display_name=body.officer_name.strip(),
    )
    _set_session_cookie(response, token)

    return AuthResponse(
        message="Registration successful.",
        user=UserResponse(
            id=str(user.id),
            role="POLICE",
            identifier=body.station_code.strip(),
            display_name=body.officer_name.strip(),
            status=user.status,
        ),
    )


@router.post("/register/lawyer", response_model=AuthResponse, status_code=201)
async def register_lawyer(
    body: LawyerRegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Register a new lawyer."""
    # Check for duplicate bar_registration_id
    stmt = select(LawyerProfile).where(
        LawyerProfile.bar_registration_id == body.bar_registration_id.strip()
    )
    existing = await db.execute(stmt)
    if existing.scalar_one_or_none():
        raise ConflictError(
            f"Bar Registration ID '{body.bar_registration_id.strip()}' is already registered."
        )

    user = User(
        role="LAWYER",
        status="ACTIVE",
        password_hash=hash_password(body.password),
    )
    db.add(user)
    await db.flush()

    profile = LawyerProfile(
        user_id=user.id,
        full_name=body.full_name.strip(),
        bar_registration_id=body.bar_registration_id.strip(),
        phone=body.phone.strip(),
        address=body.address.strip() if body.address else "",
        verification_status="VERIFIED",
    )
    db.add(profile)
    await db.flush()

    audit = AuditLog(
        actor_user_id=user.id,
        actor_role="LAWYER",
        action="REGISTER",
        entity_type="USER",
        entity_id=user.id,
        new_state={"bar_registration_id": body.bar_registration_id.strip()}
    )
    db.add(audit)
    await db.commit()

    token = await create_session(
        user_id=user.id,
        role="LAWYER",
        identifier=body.bar_registration_id.strip(),
        display_name=body.full_name.strip(),
    )
    _set_session_cookie(response, token)

    return AuthResponse(
        message="Registration successful.",
        user=UserResponse(
            id=str(user.id),
            role="LAWYER",
            identifier=body.bar_registration_id.strip(),
            display_name=body.full_name.strip(),
            status=user.status,
        ),
    )


@router.post("/register/court-authority", response_model=AuthResponse, status_code=201)
async def register_court_authority(
    body: CourtAuthorityRegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Register a new court authority."""
    # Check for duplicate JO code
    stmt = select(CourtAuthorityProfile).where(
        CourtAuthorityProfile.jo_code == body.jo_code.strip()
    )
    existing = await db.execute(stmt)
    if existing.scalar_one_or_none():
        raise ConflictError(
            f"JO Code '{body.jo_code.strip()}' is already registered."
        )

    # Validate court_id exists
    court_uuid = uuid.UUID(body.court_id.strip())
    court_stmt = select(Court).where(Court.id == court_uuid)
    court = (await db.execute(court_stmt)).scalar_one_or_none()
    if not court:
        raise ConflictError("Selected court does not exist.")

    user = User(
        role="COURT_AUTHORITY",
        status="ACTIVE",
        password_hash=hash_password(body.password),
    )
    db.add(user)
    await db.flush()

    profile = CourtAuthorityProfile(
        user_id=user.id,
        full_name=body.full_name.strip(),
        jo_code=body.jo_code.strip(),
        court_id=court_uuid,
        verification_status="VERIFIED",
    )
    db.add(profile)
    await db.flush()

    audit = AuditLog(
        actor_user_id=user.id,
        actor_role="COURT_AUTHORITY",
        action="REGISTER",
        entity_type="USER",
        entity_id=user.id,
        new_state={"jo_code": body.jo_code.strip(), "court_id": str(court_uuid)}
    )
    db.add(audit)
    await db.commit()

    token = await create_session(
        user_id=user.id,
        role="COURT_AUTHORITY",
        identifier=body.jo_code.strip(),
        display_name=body.full_name.strip(),
    )
    _set_session_cookie(response, token)

    return AuthResponse(
        message="Registration successful.",
        user=UserResponse(
            id=str(user.id),
            role="COURT_AUTHORITY",
            identifier=body.jo_code.strip(),
            display_name=body.full_name.strip(),
            status=user.status,
        ),
    )


# --- Login Endpoint ---


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """
    Authenticate a user.

    Role determines which identifier type is used:
    - POLICE: Police Station Code
    - LAWYER: Bar Registration ID
    - COURT_AUTHORITY: JO Code

    After authentication, role is derived from the server-side user record.
    The frontend-submitted role is only used to look up the correct identifier.
    """
    user: User | None = None
    identifier = body.identifier.strip()
    display_name = ""

    if body.role == "POLICE":
        stmt = (
            select(PoliceProfile)
            .where(PoliceProfile.station_code == identifier)
        )
        profile = (await db.execute(stmt)).scalar_one_or_none()
        if not profile:
            raise AuthenticationError(
                "Account not registered. Complete registration before signing in."
            )
        user_stmt = select(User).where(User.id == profile.user_id)
        user = (await db.execute(user_stmt)).scalar_one_or_none()
        display_name = profile.officer_name

    elif body.role == "LAWYER":
        stmt = (
            select(LawyerProfile)
            .where(LawyerProfile.bar_registration_id == identifier)
        )
        profile = (await db.execute(stmt)).scalar_one_or_none()
        if not profile:
            raise AuthenticationError(
                "Account not registered. Complete registration before signing in."
            )
        user_stmt = select(User).where(User.id == profile.user_id)
        user = (await db.execute(user_stmt)).scalar_one_or_none()
        display_name = profile.full_name

    elif body.role == "COURT_AUTHORITY":
        stmt = (
            select(CourtAuthorityProfile)
            .where(CourtAuthorityProfile.jo_code == identifier)
        )
        profile = (await db.execute(stmt)).scalar_one_or_none()
        if not profile:
            raise AuthenticationError(
                "Account not registered. Complete registration before signing in."
            )
        user_stmt = select(User).where(User.id == profile.user_id)
        user = (await db.execute(user_stmt)).scalar_one_or_none()
        display_name = profile.full_name

    if not user:
        raise AuthenticationError(
            "Account not registered. Complete registration before signing in."
        )

    # Verify password
    if not verify_password(body.password, user.password_hash):
        audit = AuditLog(
            actor_user_id=user.id,
            actor_role=user.role,
            action="LOGIN_FAILURE",
            entity_type="USER",
            entity_id=user.id,
            new_state={"reason": "Invalid credentials"}
        )
        db.add(audit)
        await db.commit()
        raise AuthenticationError("Invalid credentials. Please check your password.")

    # Check user status
    if user.status != "ACTIVE":
        audit = AuditLog(
            actor_user_id=user.id,
            actor_role=user.role,
            action="LOGIN_FAILURE",
            entity_type="USER",
            entity_id=user.id,
            new_state={"reason": "Account inactive"}
        )
        db.add(audit)
        await db.commit()
        raise AuthenticationError(
            "Account is not active. Please contact an administrator."
        )

    # Rehash if needed (parameter migration)
    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(body.password)
        db.add(user)

    audit = AuditLog(
        actor_user_id=user.id,
        actor_role=user.role,
        action="LOGIN",
        entity_type="USER",
        entity_id=user.id
    )
    db.add(audit)
    await db.commit()

    # Create session — role is derived from the SERVER record
    token = await create_session(
        user_id=user.id,
        role=user.role,  # Server-side role, not from the request
        identifier=identifier,
        display_name=display_name,
    )
    _set_session_cookie(response, token)

    return AuthResponse(
        message="Login successful.",
        user=UserResponse(
            id=str(user.id),
            role=user.role,
            identifier=identifier,
            display_name=display_name,
            status=user.status,
        ),
    )


# --- Logout Endpoint ---


@router.post("/logout", response_model=MessageResponse)
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db)) -> MessageResponse:
    """Invalidate the session and clear the cookie."""
    token = request.cookies.get(_COOKIE_NAME)
    if token:
        session = await get_session(token)
        if session:
            audit = AuditLog(
                actor_user_id=uuid.UUID(session["user_id"]),
                actor_role=session["role"],
                action="LOGOUT",
                entity_type="USER",
                entity_id=uuid.UUID(session["user_id"])
            )
            db.add(audit)
            await db.commit()
        await delete_session(token)
    _clear_session_cookie(response)
    return MessageResponse(message="Logged out successfully.")


# --- Session Endpoint ---


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(request: Request) -> UserResponse:
    """Return the current authenticated user's info."""
    token = request.cookies.get(_COOKIE_NAME)
    if not token:
        raise AuthenticationError("Authentication required. Please sign in.")

    session = await get_session(token)
    if not session:
        raise AuthenticationError("Session expired. Please sign in again.")

    return UserResponse(
        id=session["user_id"],
        role=session["role"],
        identifier=session["identifier"],
        display_name=session["display_name"],
        status="ACTIVE",
    )


# --- Courts list for registration ---


@router.get("/courts")
async def list_courts(
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, str]]:
    """List courts for the registration dropdown."""
    stmt = select(Court).order_by(Court.court_name)
    result = await db.execute(stmt)
    courts = result.scalars().all()
    return [
        {"id": str(c.id), "name": c.court_name, "type": c.court_type}
        for c in courts
    ]
