"""
Document model.

Per project rules:
- PostgreSQL stores file metadata. MinIO stores actual file objects.
- Validate MIME type, extension, size. Generate safe filenames. Prevent path traversal.
- SHA-256 for integrity verification (not encryption).
"""

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, text
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin


class Document(UUIDPrimaryKeyMixin, Base):
    """
    Document metadata record.

    Actual file content is stored in MinIO (object storage).
    This table stores the metadata, storage key, and integrity hash.
    """

    __tablename__ = "documents"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="RESTRICT"),
        nullable=False,
    )
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    storage_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="MinIO object key",
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    safe_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="SHA-256 digest for integrity verification",
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    processing_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="PENDING",
    )
    verification_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="UNVERIFIED",
    )

    # Relationships
    case: Mapped["Case"] = relationship(back_populates="documents")  # noqa: F821
    uploader: Mapped["User"] = relationship(foreign_keys=[uploaded_by])  # noqa: F821

    __table_args__ = (
        Index("ix_documents_case_id", "case_id"),
        Index("ix_documents_uploaded_by", "uploaded_by"),
        Index("ix_documents_processing_status", "processing_status"),
    )
