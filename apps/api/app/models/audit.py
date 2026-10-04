"""
Audit log model.

Per project rules:
- Every consequential action creates an audit record.
- Append-oriented. Normal users cannot edit audit events.
- Historical audit events must not be editable through ordinary application APIs.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, text
from sqlalchemy import JSON as JSONB, Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin


class AuditLog(UUIDPrimaryKeyMixin, Base):
    """
    Append-only audit log.

    Records every consequential action with: actor, target entity,
    old state, new state, and request metadata.
    """

    __tablename__ = "audit_logs"

    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="SET NULL"),
        nullable=True,
    )
    actor_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    actor_role: Mapped[str] = mapped_column(String(20), nullable=False)
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="e.g., created, updated, deleted, approved, rejected, assigned",
    )
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="e.g., case, document, hearing, lawyer_assignment",
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    old_state: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    new_state: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    request_metadata: Mapped[dict[str, object] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="IP address, user agent, request ID",
    )

    # Relationships
    case: Mapped["Case | None"] = relationship(back_populates="audit_logs")  # noqa: F821
    actor: Mapped["User"] = relationship(foreign_keys=[actor_user_id])  # noqa: F821

    __table_args__ = (
        Index("ix_audit_logs_case_id", "case_id"),
        Index("ix_audit_logs_actor_user_id", "actor_user_id"),
        Index("ix_audit_logs_entity_type_entity_id", "entity_type", "entity_id"),
        Index("ix_audit_logs_timestamp", "timestamp"),
        Index("ix_audit_logs_action", "action"),
    )
