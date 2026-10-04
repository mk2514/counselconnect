"""
AI job and output models.

Per project rules:
- AI output must be separated from official verified data.
- AI proposes → human reviews → authorized human confirms → database changes.
- Explicit states: PENDING, PROCESSING, COMPLETED, FAILED, REVIEWED.
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON as JSONB
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin


class AIJob(UUIDPrimaryKeyMixin, Base):
    """
    AI processing job (OCR, extraction, summarization, etc.).

    Processed asynchronously by the application worker. Frontend polls for state.
    """

    __tablename__ = "ai_jobs"

    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="SET NULL"),
        nullable=True,
    )
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    job_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="PENDING",
        comment="PENDING, PROCESSING, COMPLETED, FAILED, REVIEWED",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    case: Mapped["Case | None"] = relationship(foreign_keys=[case_id])  # noqa: F821
    document: Mapped["Document | None"] = relationship(foreign_keys=[document_id])  # noqa: F821
    outputs: Mapped[list["AIOutput"]] = relationship(back_populates="job")

    __table_args__ = (
        Index("ix_ai_jobs_case_id", "case_id"),
        Index("ix_ai_jobs_document_id", "document_id"),
        Index("ix_ai_jobs_status", "status"),
    )


class AIOutput(UUIDPrimaryKeyMixin, Base):
    """
    AI-generated output associated with a job.

    This is candidate information only. It must not automatically become
    authoritative judicial data without human verification.
    """

    __tablename__ = "ai_outputs"

    ai_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    output_type: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    model_metadata: Mapped[dict[str, object] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Model identifier, version, parameters",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    verified_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    job: Mapped["AIJob"] = relationship(back_populates="outputs")
    verifier: Mapped["User | None"] = relationship(foreign_keys=[verified_by])  # noqa: F821

    __table_args__ = (
        Index("ix_ai_outputs_ai_job_id", "ai_job_id"),
    )
