"""
Case and party models.

Per project rules:
- ONE CSR = ONE CONTINUOUS DIGITAL CASE LIFECYCLE.
- CSR must be unique.
- Support multiple parties of the same type per case.
- Do not falsely require every case to follow the same procedural branch.
"""

import uuid
from datetime import date, time, datetime

from sqlalchemy import text, Date, DateTime, ForeignKey, Index, String, Text, Time
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Case(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Central case record (CSR).

    The CSR is the parent entity to which everything connects:
    FIR, parties, investigations, evidence, documents, hearings,
    lawyer assignments, proceedings, judgments, audit history.
    """

    __tablename__ = "cases"

    csr_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="Human-readable unique CSR identifier",
    )
    fir_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    case_type: Mapped[str] = mapped_column(String(100), nullable=False)
    offence_category: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cognizable_status: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="COGNIZABLE or NON_COGNIZABLE",
    )
    incident_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    incident_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    incident_location: Mapped[str | None] = mapped_column(Text, nullable=True)
    case_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="REGISTERED",
    )
    procedural_stage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Relationships
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])  # noqa: F821
    parties: Mapped[list["Party"]] = relationship(back_populates="case")
    investigations: Mapped[list["Investigation"]] = relationship(  # noqa: F821
        back_populates="case"
    )
    documents: Mapped[list["Document"]] = relationship(back_populates="case")  # noqa: F821
    evidence_records: Mapped[list["EvidenceRecord"]] = relationship(  # noqa: F821
        back_populates="case"
    )
    lawyer_assignments: Mapped[list["LawyerAssignment"]] = relationship(  # noqa: F821
        back_populates="case"
    )
    hearings: Mapped[list["Hearing"]] = relationship(back_populates="case")  # noqa: F821
    absence_requests: Mapped[list["AbsenceRequest"]] = relationship(  # noqa: F821
        back_populates="case"
    )
    proceedings: Mapped[list["Proceeding"]] = relationship(back_populates="case")  # noqa: F821
    judgments: Mapped[list["Judgment"]] = relationship(back_populates="case")  # noqa: F821
    withdrawal_requests: Mapped[list["WithdrawalRequest"]] = relationship(  # noqa: F821
        back_populates="case"
    )
    representation_change_requests: Mapped[list["RepresentationChangeRequest"]] = relationship(  # noqa: F821
        back_populates="case"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="case")  # noqa: F821

    __table_args__ = (
        Index("ix_cases_csr_number", "csr_number", unique=True),
        Index("ix_cases_case_status", "case_status"),
        Index("ix_cases_created_by", "created_by"),
        Index("ix_cases_fir_number", "fir_number"),
    )


class Party(UUIDPrimaryKeyMixin, Base):
    """
    Party involved in a case.

    Supports COMPLAINANT, ACCUSED, WITNESS, OTHER.
    Multiple parties of the same type per case are allowed.
    """

    __tablename__ = "parties"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="RESTRICT"),
        nullable=False,
    )
    party_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="COMPLAINANT, ACCUSED, WITNESS, OTHER",
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    age: Mapped[int | None] = mapped_column(nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    id_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    id_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    case: Mapped["Case"] = relationship(back_populates="parties")
    lawyer_assignments: Mapped[list["LawyerAssignment"]] = relationship(  # noqa: F821
        back_populates="party"
    )
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(  # noqa: F821
        back_populates="party"
    )
    absence_requests: Mapped[list["AbsenceRequest"]] = relationship(  # noqa: F821
        back_populates="party"
    )

    __table_args__ = (
        Index("ix_parties_case_id", "case_id"),
        Index("ix_parties_party_type", "party_type"),
    )
