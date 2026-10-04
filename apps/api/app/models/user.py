"""
User and profile models.

Per project rules:
- Roles: POLICE, LAWYER, COURT_AUTHORITY. No CLIENT role.
- Identity types: Police Station Code, Bar Registration ID, JO Code.
- Password hashing uses Argon2id (per 12-tech-stack-lock.md).
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import UserStatus, VerificationStatus


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Platform user account.

    The user table stores authentication credentials and role.
    Role-specific profile data is stored in the corresponding profile table.
    """

    __tablename__ = "users"

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="POLICE, LAWYER, or COURT_AUTHORITY",
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=UserStatus.PENDING_VERIFICATION.value,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    police_profile: Mapped["PoliceProfile | None"] = relationship(
        back_populates="user", uselist=False
    )
    lawyer_profile: Mapped["LawyerProfile | None"] = relationship(
        back_populates="user", uselist=False
    )
    court_authority_profile: Mapped["CourtAuthorityProfile | None"] = relationship(
        back_populates="user", uselist=False
    )

    __table_args__ = (
        Index("ix_users_role", "role"),
        Index("ix_users_status", "status"),
    )


class PoliceProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Police officer profile linked to a user account."""

    __tablename__ = "police_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    station_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    officer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    station_name: Mapped[str] = mapped_column(String(255), nullable=False)
    jurisdiction: Mapped[str | None] = mapped_column(String(255), nullable=True)
    verification_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=VerificationStatus.UNVERIFIED.value,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="police_profile")

    __table_args__ = (
        Index("ix_police_profiles_station_code", "station_code", unique=True),
    )


class LawyerProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Lawyer profile linked to a user account."""

    __tablename__ = "lawyer_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bar_registration_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    verification_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=VerificationStatus.UNVERIFIED.value,
    )
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="lawyer_profile")

    __table_args__ = (
        Index("ix_lawyer_profiles_bar_registration_id", "bar_registration_id", unique=True),
    )


class CourtAuthorityProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Court authority profile linked to a user account."""

    __tablename__ = "court_authority_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    jo_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    court_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courts.id", ondelete="SET NULL"),
        nullable=True,
    )
    verification_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=VerificationStatus.UNVERIFIED.value,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="court_authority_profile")
    court: Mapped["Court | None"] = relationship(back_populates="authority_profiles")  # noqa: F821

    __table_args__ = (
        Index("ix_court_authority_profiles_jo_code", "jo_code", unique=True),
    )
