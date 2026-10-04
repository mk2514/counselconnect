"""
Authentication and registration schemas.

Pydantic models for request/response validation.
"""

import re

from pydantic import BaseModel, field_validator

# --- Password validation ---

_PASSWORD_MIN_LENGTH = 8
_PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]).+$"
)


def _validate_password(v: str) -> str:
    """Shared password validation logic."""
    if len(v) < _PASSWORD_MIN_LENGTH:
        msg = f"Password must be at least {_PASSWORD_MIN_LENGTH} characters."
        raise ValueError(msg)
    if not _PASSWORD_PATTERN.match(v):
        msg = (
            "Password must contain at least one uppercase letter, "
            "one lowercase letter, one digit, and one special character."
        )
        raise ValueError(msg)
    return v


# --- Registration schemas ---


class PoliceRegisterRequest(BaseModel):
    """Police officer registration."""

    station_code: str
    officer_name: str
    station_name: str
    jurisdiction: str = ""
    password: str
    confirm_password: str

    @field_validator("station_code")
    @classmethod
    def validate_station_code(cls, v: str) -> str:
        v = v.strip()
        if not v:
            msg = "Police Station Code is required."
            raise ValueError(msg)
        if len(v) < 3 or len(v) > 50:
            msg = "Police Station Code must be between 3 and 50 characters."
            raise ValueError(msg)
        return v

    @field_validator("officer_name")
    @classmethod
    def validate_officer_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            msg = "Officer name is required."
            raise ValueError(msg)
        return v

    @field_validator("station_name")
    @classmethod
    def validate_station_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            msg = "Station name is required."
            raise ValueError(msg)
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password(v)

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, v: str, info: object) -> str:
        # Access the already-validated data
        data = getattr(info, "data", {})
        password = data.get("password")
        if password and v != password:
            msg = "Passwords do not match."
            raise ValueError(msg)
        return v


class LawyerRegisterRequest(BaseModel):
    """Lawyer registration."""

    full_name: str
    bar_registration_id: str
    phone: str
    address: str = ""
    password: str
    confirm_password: str

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            msg = "Full name is required."
            raise ValueError(msg)
        if len(v) < 2:
            msg = "Full name must be at least 2 characters."
            raise ValueError(msg)
        return v

    @field_validator("bar_registration_id")
    @classmethod
    def validate_bar_id(cls, v: str) -> str:
        v = v.strip()
        if not v:
            msg = "Bar Registration ID is required."
            raise ValueError(msg)
        if len(v) < 3 or len(v) > 100:
            msg = "Bar Registration ID must be between 3 and 100 characters."
            raise ValueError(msg)
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not v:
            msg = "Phone number is required."
            raise ValueError(msg)
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password(v)

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, v: str, info: object) -> str:
        data = getattr(info, "data", {})
        password = data.get("password")
        if password and v != password:
            msg = "Passwords do not match."
            raise ValueError(msg)
        return v


class CourtAuthorityRegisterRequest(BaseModel):
    """Court Authority registration."""

    full_name: str
    jo_code: str
    court_id: str  # UUID string of the court
    password: str
    confirm_password: str

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            msg = "Full name is required."
            raise ValueError(msg)
        if len(v) < 2:
            msg = "Full name must be at least 2 characters."
            raise ValueError(msg)
        return v

    @field_validator("jo_code")
    @classmethod
    def validate_jo_code(cls, v: str) -> str:
        v = v.strip()
        if not v:
            msg = "JO Code is required."
            raise ValueError(msg)
        if len(v) < 2 or len(v) > 50:
            msg = "JO Code must be between 2 and 50 characters."
            raise ValueError(msg)
        return v

    @field_validator("court_id")
    @classmethod
    def validate_court_id(cls, v: str) -> str:
        v = v.strip()
        if not v:
            msg = "Court selection is required."
            raise ValueError(msg)
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password(v)

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, v: str, info: object) -> str:
        data = getattr(info, "data", {})
        password = data.get("password")
        if password and v != password:
            msg = "Passwords do not match."
            raise ValueError(msg)
        return v


# --- Login schema ---


class LoginRequest(BaseModel):
    """Universal login request. Role determines which identifier is used."""

    role: str
    identifier: str
    password: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in ("POLICE", "LAWYER", "COURT_AUTHORITY"):
            msg = "Invalid role. Must be POLICE, LAWYER, or COURT_AUTHORITY."
            raise ValueError(msg)
        return v

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        v = v.strip()
        if not v:
            msg = "Identifier is required."
            raise ValueError(msg)
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v:
            msg = "Password is required."
            raise ValueError(msg)
        return v


# --- Response schemas ---


class UserResponse(BaseModel):
    """Public user info returned after authentication."""

    id: str
    role: str
    identifier: str
    display_name: str
    status: str


class AuthResponse(BaseModel):
    """Response after successful login or registration."""

    message: str
    user: UserResponse


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str
