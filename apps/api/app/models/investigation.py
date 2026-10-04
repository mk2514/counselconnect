"""
Investigation and evidence models.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Investigation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Investigation note record.

    Uses separate structured records instead of one endlessly overwritten text field.
    Each entry is an append to the investigation history.
    """

    __tablename__ = "investigations"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    note: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    case: Mapped["Case"] = relationship(back_populates="investigations")  # noqa: F821
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])  # noqa: F821

    __table_args__ = (
        Index("ix_investigations_case_id", "case_id"),
    )


class EvidenceRecord(UUIDPrimaryKeyMixin, Base):
    """Evidence record linked to a case, optionally linked to a document."""

    __tablename__ = "evidence_records"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="RESTRICT"),
        nullable=False,
    )
    evidence_number: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(200), nullable=True)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    case: Mapped["Case"] = relationship(back_populates="evidence_records")  # noqa: F821
    uploader: Mapped["User"] = relationship(foreign_keys=[uploaded_by])  # noqa: F821
    document: Mapped["Document | None"] = relationship()  # noqa: F821

    __table_args__ = (
        Index("ix_evidence_records_case_id", "case_id"),
    )
