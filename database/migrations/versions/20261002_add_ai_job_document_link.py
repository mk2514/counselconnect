"""Link AI jobs to their source documents.

Revision ID: 20261002_ai_document
Revises: 78046b66668e
Create Date: 2026-10-02
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20261002_ai_document"
down_revision = "78046b66668e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ai_jobs",
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_ai_jobs_document_id_documents",
        "ai_jobs",
        "documents",
        ["document_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_ai_jobs_document_id", "ai_jobs", ["document_id"])


def downgrade() -> None:
    op.drop_index("ix_ai_jobs_document_id", table_name="ai_jobs")
    op.drop_constraint("fk_ai_jobs_document_id_documents", "ai_jobs", type_="foreignkey")
    op.drop_column("ai_jobs", "document_id")
