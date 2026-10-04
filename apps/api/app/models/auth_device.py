"""
Authentication device models: NFC cards, registered devices, WebAuthn credentials, QR tokens.

Per project rules:
- NFC must NOT contain password, JWT, access/refresh tokens, personal case data.
- QR must NOT contain sensitive case details directly.
- QR and NFC are NOT authentication bypasses.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, LargeBinary, String, text
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin


class NFCCard(UUIDPrimaryKeyMixin, Base):
    """
    NFC card registration for lawyers.

    The card contains an opaque HTTPS URL. The server stores only
    the secure hash required to resolve the card, never raw credentials.
    """

    __tablename__ = "nfc_cards"

    lawyer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        comment="Hash of the opaque NFC token, never the raw token",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="ACTIVE",
    )
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    lawyer: Mapped["User"] = relationship(foreign_keys=[lawyer_id])  # noqa: F821

    __table_args__ = (
        Index("ix_nfc_cards_token_hash", "token_hash", unique=True),
        Index("ix_nfc_cards_lawyer_id", "lawyer_id"),
    )


class RegisteredDevice(UUIDPrimaryKeyMixin, Base):
    """Registered device for a user (phone, laptop, etc.)."""

    __tablename__ = "registered_devices"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    device_label: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="ACTIVE",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship(foreign_keys=[user_id])  # noqa: F821
    webauthn_credentials: Mapped[list["WebAuthnCredential"]] = relationship(
        back_populates="device"
    )

    __table_args__ = (
        Index("ix_registered_devices_user_id", "user_id"),
    )


class WebAuthnCredential(UUIDPrimaryKeyMixin, Base):
    """
    WebAuthn / Passkey credential.

    The backend must verify the WebAuthn assertion.
    Frontend biometric dialogs alone are not authentication.
    """

    __tablename__ = "webauthn_credentials"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    device_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("registered_devices.id", ondelete="SET NULL"),
        nullable=True,
    )
    credential_id: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    public_key: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    sign_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship(foreign_keys=[user_id])  # noqa: F821
    device: Mapped["RegisteredDevice | None"] = relationship(
        back_populates="webauthn_credentials"
    )

    __table_args__ = (
        Index("ix_webauthn_credentials_user_id", "user_id"),
        Index("ix_webauthn_credentials_credential_id", "credential_id", unique=True),
    )


class CaseQRToken(UUIDPrimaryKeyMixin, Base):
    """
    QR token for secure case access.

    QR contains an opaque token or HTTPS resolver URL.
    Never contains sensitive case details directly.
    """

    __tablename__ = "case_qr_tokens"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="RESTRICT"),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="ACTIVE",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    case: Mapped["Case"] = relationship(foreign_keys=[case_id])  # noqa: F821

    __table_args__ = (
        Index("ix_case_qr_tokens_token_hash", "token_hash", unique=True),
        Index("ix_case_qr_tokens_case_id", "case_id"),
    )
