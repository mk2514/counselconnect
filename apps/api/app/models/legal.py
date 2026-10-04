"""
Lawyer assignment, representation change, and withdrawal request models.

Per project rules:
- Preserve historical assignments. Do not delete old assignments when representation changes.
- Changing lawyers must not create a new CSR.
- Withdrawal/disposal must not delete historical records.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin


class LawyerAssignment(UUIDPrimaryKeyMixin, Base):
    """
    Lawyer assignment to a party in a case.

    Historical assignments are preserved. When a lawyer is replaced,
    the old assignment is marked as REPLACED with ended_at and end_reason set.
    """

    __tablename__ = "lawyer_assignments"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="RESTRICT"),
        nullable=False,
    )
    party_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("parties.id", ondelete="RESTRICT"),
        nullable=False,
    )
    lawyer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Must be a user with LAWYER role",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="ACTIVE",
        comment="ACTIVE, RETIRED, REPLACED, ENDED",
    )
    assigned_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    case: Mapped["Case"] = relationship(back_populates="lawyer_assignments")  # noqa: F821
    party: Mapped["Party"] = relationship(back_populates="lawyer_assignments")  # noqa: F821
    lawyer: Mapped["User"] = relationship(foreign_keys=[lawyer_id])  # noqa: F821
    assigner: Mapped["User"] = relationship(foreign_keys=[assigned_by])  # noqa: F821
    representation_changes: Mapped[list["RepresentationChangeRequest"]] = relationship(
        back_populates="lawyer_assignment"
    )

    __table_args__ = (
        Index("ix_lawyer_assignments_case_id", "case_id"),
        Index("ix_lawyer_assignments_lawyer_id", "lawyer_id"),
        Index("ix_lawyer_assignments_status", "status"),
    )


class RepresentationChangeRequest(UUIDPrimaryKeyMixin, Base):
    """Request to change representation for a lawyer assignment."""

    __tablename__ = "representation_change_requests"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="RESTRICT"),
        nullable=False,
    )
    lawyer_assignment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lawyer_assignments.id", ondelete="RESTRICT"),
        nullable=False,
    )
    requested_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    request_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="PENDING",
    )
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    case: Mapped["Case"] = relationship(  # noqa: F821
        back_populates="representation_change_requests"
    )
    lawyer_assignment: Mapped["LawyerAssignment"] = relationship(
        back_populates="representation_changes"
    )
    requester: Mapped["User"] = relationship(foreign_keys=[requested_by])  # noqa: F821
    reviewer: Mapped["User | None"] = relationship(foreign_keys=[reviewed_by])  # noqa: F821

    __table_args__ = (
        Index("ix_representation_change_requests_case_id", "case_id"),
    )


class WithdrawalRequest(UUIDPrimaryKeyMixin, Base):
    """
    Request to withdraw or dispose of a case.

    Withdrawal/disposal must not delete historical records.
    """

    __tablename__ = "withdrawal_requests"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="RESTRICT"),
        nullable=False,
    )
    submitted_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="PENDING_REVIEW",
    )
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    decision_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    case: Mapped["Case"] = relationship(back_populates="withdrawal_requests")  # noqa: F821
    submitter: Mapped["User"] = relationship(foreign_keys=[submitted_by])  # noqa: F821
    reviewer: Mapped["User | None"] = relationship(foreign_keys=[reviewed_by])  # noqa: F821

    __table_args__ = (
        Index("ix_withdrawal_requests_case_id", "case_id"),
        Index("ix_withdrawal_requests_status", "status"),
    )
