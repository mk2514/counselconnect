"""
Hearing, attendance, absence, court agenda, and proceeding models.

Per project rules:
- Court agenda must maintain both AI proposed order and final authorized order.
- Do not overwrite the original AI proposal when Court Authority modifies it.
- An unreviewed transcript must never automatically become official proceeding text.
"""

import uuid
from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, Text, Time
from sqlalchemy import text as sa_text
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Hearing(UUIDPrimaryKeyMixin, Base):
    """Scheduled hearing for a case at a court."""

    __tablename__ = "hearings"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="RESTRICT"),
        nullable=False,
    )
    court_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    judge_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hearing_date: Mapped[date] = mapped_column(Date, nullable=False)
    hearing_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="SCHEDULED",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa_text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    confirmed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    case: Mapped["Case"] = relationship(back_populates="hearings")  # noqa: F821
    court: Mapped["Court"] = relationship(back_populates="hearings")  # noqa: F821
    confirmer: Mapped["User | None"] = relationship(foreign_keys=[confirmed_by])  # noqa: F821
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(
        back_populates="hearing"
    )
    absence_requests: Mapped[list["AbsenceRequest"]] = relationship(
        back_populates="hearing"
    )
    proceedings: Mapped[list["Proceeding"]] = relationship(back_populates="hearing")
    agenda_items: Mapped[list["AgendaItem"]] = relationship(back_populates="hearing")

    __table_args__ = (
        Index("ix_hearings_case_id", "case_id"),
        Index("ix_hearings_court_id", "court_id"),
        Index("ix_hearings_hearing_date", "hearing_date"),
        Index("ix_hearings_status", "status"),
    )


class AttendanceRecord(UUIDPrimaryKeyMixin, Base):
    """Attendance record for a party at a hearing."""

    __tablename__ = "attendance_records"

    hearing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hearings.id", ondelete="RESTRICT"),
        nullable=False,
    )
    party_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("parties.id", ondelete="RESTRICT"),
        nullable=False,
    )
    recorded_by_lawyer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    attendance_status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="PRESENT or ABSENT",
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa_text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    hearing: Mapped["Hearing"] = relationship(back_populates="attendance_records")
    party: Mapped["Party"] = relationship(back_populates="attendance_records")  # noqa: F821
    recorder: Mapped["User"] = relationship(  # noqa: F821
        foreign_keys=[recorded_by_lawyer_id]
    )

    __table_args__ = (
        Index("ix_attendance_records_hearing_id", "hearing_id"),
    )


class AbsenceRequest(UUIDPrimaryKeyMixin, Base):
    """Request for absence from a hearing."""

    __tablename__ = "absence_requests"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="RESTRICT"),
        nullable=False,
    )
    hearing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hearings.id", ondelete="RESTRICT"),
        nullable=False,
    )
    party_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("parties.id", ondelete="RESTRICT"),
        nullable=False,
    )
    submitted_by_lawyer_id: Mapped[uuid.UUID] = mapped_column(
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
        server_default=sa_text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    case: Mapped["Case"] = relationship(back_populates="absence_requests")  # noqa: F821
    hearing: Mapped["Hearing"] = relationship(back_populates="absence_requests")
    party: Mapped["Party"] = relationship(back_populates="absence_requests")  # noqa: F821
    submitter: Mapped["User"] = relationship(  # noqa: F821
        foreign_keys=[submitted_by_lawyer_id]
    )
    reviewer: Mapped["User | None"] = relationship(  # noqa: F821
        foreign_keys=[reviewed_by]
    )

    __table_args__ = (
        Index("ix_absence_requests_case_id", "case_id"),
        Index("ix_absence_requests_hearing_id", "hearing_id"),
        Index("ix_absence_requests_status", "status"),
    )


class CourtAgenda(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Court agenda for a specific date."""

    __tablename__ = "court_agendas"

    court_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    agenda_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    court: Mapped["Court"] = relationship(back_populates="agendas")  # noqa: F821
    items: Mapped[list["AgendaItem"]] = relationship(
        back_populates="agenda", order_by="AgendaItem.final_order"
    )

    __table_args__ = (
        Index("ix_court_agendas_court_date", "court_id", "agenda_date", unique=True),
    )


class AgendaItem(UUIDPrimaryKeyMixin, Base):
    """
    Individual item on a court agenda.

    Preserves both the AI proposed order and the final authorized order.
    The original AI proposal is never overwritten.
    """

    __tablename__ = "agenda_items"

    agenda_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("court_agendas.id", ondelete="CASCADE"),
        nullable=False,
    )
    hearing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hearings.id", ondelete="RESTRICT"),
        nullable=False,
    )
    ai_proposed_order: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="AI-recommended hearing order, immutable after creation",
    )
    final_order: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Court Authority confirmed hearing order",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    agenda: Mapped["CourtAgenda"] = relationship(back_populates="items")
    hearing: Mapped["Hearing"] = relationship(back_populates="agenda_items")

    __table_args__ = (
        Index("ix_agenda_items_agenda_id", "agenda_id"),
    )


class Proceeding(UUIDPrimaryKeyMixin, Base):
    """
    Proceeding record for a hearing.

    Source can be MANUAL or SPEECH_TO_TEXT.
    Unreviewed transcripts must not automatically become official text.
    """

    __tablename__ = "proceedings"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="RESTRICT"),
        nullable=False,
    )
    hearing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hearings.id", ondelete="RESTRICT"),
        nullable=False,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="MANUAL or SPEECH_TO_TEXT",
    )
    verified_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa_text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    case: Mapped["Case"] = relationship(back_populates="proceedings")  # noqa: F821
    hearing: Mapped["Hearing"] = relationship(back_populates="proceedings")
    verifier: Mapped["User | None"] = relationship(foreign_keys=[verified_by])  # noqa: F821

    __table_args__ = (
        Index("ix_proceedings_case_id", "case_id"),
        Index("ix_proceedings_hearing_id", "hearing_id"),
    )


class ScheduleDecision(UUIDPrimaryKeyMixin, Base):
    """
    AI recommendation for scheduling, explicitly confirmed by a human.
    All scheduling rationale and factors are stored here.
    """

    __tablename__ = "schedule_decisions"

    hearing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hearings.id", ondelete="CASCADE"),
        nullable=False,
    )
    recommended_date: Mapped[date] = mapped_column(Date, nullable=False)
    recommended_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    reasoning_factors: Mapped[str] = mapped_column(Text, nullable=False)
    
    confirmed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    confirmed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa_text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    hearing: Mapped["Hearing"] = relationship()
    confirmer: Mapped["User"] = relationship(foreign_keys=[confirmed_by])  # noqa: F821

    __table_args__ = (
        Index("ix_schedule_decisions_hearing_id", "hearing_id"),
    )
