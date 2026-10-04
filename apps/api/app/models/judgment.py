"""
Judgment model.

Per project rules:
- Official judgment content comes from the uploaded official document, not AI generation.
- metadata_json is only for extracted metadata that is genuinely variable.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, text
from sqlalchemy import JSON as JSONB, Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin


class Judgment(UUIDPrimaryKeyMixin, Base):
    """Judgment record linked to an official uploaded document."""

    __tablename__ = "judgments"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="RESTRICT"),
        nullable=False,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="RESTRICT"),
        nullable=False,
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    judgment_date: Mapped[date] = mapped_column(Date, nullable=False)
    metadata_json: Mapped[dict[str, object] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="AI-extracted metadata only. Not authoritative case data.",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    case: Mapped["Case"] = relationship(back_populates="judgments")  # noqa: F821
    document: Mapped["Document"] = relationship()  # noqa: F821
    uploader: Mapped["User"] = relationship(foreign_keys=[uploaded_by])  # noqa: F821

    __table_args__ = (
        Index("ix_judgments_case_id", "case_id"),
    )
