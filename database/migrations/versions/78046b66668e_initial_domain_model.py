"""Initial domain model - core tables.

Revision ID: 78046b66668e
Revises:
Create Date: 2026-10-02

Creates all core domain tables:
- courts, users, police_profiles, lawyer_profiles, court_authority_profiles
- cases, parties, investigations, documents, evidence_records
- lawyer_assignments, representation_change_requests, withdrawal_requests
- hearings, attendance_records, absence_requests
- court_agendas, agenda_items, proceedings, judgments
- nfc_cards, registered_devices, webauthn_credentials, case_qr_tokens
- ai_jobs, ai_outputs, audit_logs
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "78046b66668e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # --- Reference Tables ---

    op.create_table(
        "courts",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("court_name", sa.String(255), nullable=False),
        sa.Column("court_type", sa.String(100), nullable=False),
        sa.Column("jurisdiction", sa.String(255), nullable=True),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- Users ---

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, comment="POLICE, LAWYER, or COURT_AUTHORITY"),
        sa.Column("status", sa.String(30), server_default="PENDING_VERIFICATION", nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_status", "users", ["status"])

    op.create_table(
        "police_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("station_code", sa.String(50), nullable=False),
        sa.Column("officer_name", sa.String(255), nullable=False),
        sa.Column("station_name", sa.String(255), nullable=False),
        sa.Column("jurisdiction", sa.String(255), nullable=True),
        sa.Column("verification_status", sa.String(20), server_default="UNVERIFIED", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id"),
        sa.UniqueConstraint("station_code"),
    )
    op.create_index("ix_police_profiles_station_code", "police_profiles", ["station_code"], unique=True)

    op.create_table(
        "lawyer_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("bar_registration_id", sa.String(100), nullable=False),
        sa.Column("verification_status", sa.String(20), server_default="UNVERIFIED", nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id"),
        sa.UniqueConstraint("bar_registration_id"),
    )
    op.create_index("ix_lawyer_profiles_bar_registration_id", "lawyer_profiles", ["bar_registration_id"], unique=True)

    op.create_table(
        "court_authority_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("jo_code", sa.String(50), nullable=False),
        sa.Column("court_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("verification_status", sa.String(20), server_default="UNVERIFIED", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["court_id"], ["courts.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("user_id"),
        sa.UniqueConstraint("jo_code"),
    )
    op.create_index("ix_court_authority_profiles_jo_code", "court_authority_profiles", ["jo_code"], unique=True)

    # --- Cases ---

    op.create_table(
        "cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("csr_number", sa.String(50), nullable=False, comment="Human-readable unique CSR identifier"),
        sa.Column("fir_number", sa.String(100), nullable=True),
        sa.Column("case_type", sa.String(100), nullable=False),
        sa.Column("offence_category", sa.String(200), nullable=True),
        sa.Column("cognizable_status", sa.String(20), nullable=True, comment="COGNIZABLE or NON_COGNIZABLE"),
        sa.Column("incident_date", sa.Date, nullable=True),
        sa.Column("incident_time", sa.Time, nullable=True),
        sa.Column("incident_location", sa.Text, nullable=True),
        sa.Column("case_status", sa.String(30), server_default="REGISTERED", nullable=False),
        sa.Column("procedural_stage", sa.String(100), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("csr_number"),
    )
    op.create_index("ix_cases_csr_number", "cases", ["csr_number"], unique=True)
    op.create_index("ix_cases_case_status", "cases", ["case_status"])
    op.create_index("ix_cases_created_by", "cases", ["created_by"])
    op.create_index("ix_cases_fir_number", "cases", ["fir_number"])

    op.create_table(
        "parties",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_type", sa.String(20), nullable=False, comment="COMPLAINANT, ACCUSED, WITNESS, OTHER"),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("age", sa.Integer, nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("contact_number", sa.String(20), nullable=True),
        sa.Column("id_type", sa.String(50), nullable=True),
        sa.Column("id_number", sa.String(100), nullable=True),
        sa.Column("created_at", sa.Date, server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_parties_case_id", "parties", ["case_id"])
    op.create_index("ix_parties_party_type", "parties", ["party_type"])

    # --- Documents ---

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_type", sa.String(100), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False, comment="MinIO object key"),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("safe_filename", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("file_size", sa.BigInteger, nullable=False),
        sa.Column("sha256_hash", sa.String(64), nullable=False, comment="SHA-256 digest for integrity verification"),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("processing_status", sa.String(20), server_default="PENDING", nullable=False),
        sa.Column("verification_status", sa.String(20), server_default="UNVERIFIED", nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_documents_case_id", "documents", ["case_id"])
    op.create_index("ix_documents_uploaded_by", "documents", ["uploaded_by"])
    op.create_index("ix_documents_processing_status", "documents", ["processing_status"])

    # --- Investigations and Evidence ---

    op.create_table(
        "investigations",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("note", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_investigations_case_id", "investigations", ["case_id"])

    op.create_table(
        "evidence_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evidence_number", sa.String(100), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("source", sa.String(200), nullable=True),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_evidence_records_case_id", "evidence_records", ["case_id"])

    # --- Lawyer Assignments ---

    op.create_table(
        "lawyer_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lawyer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(20), server_default="ACTIVE", nullable=False),
        sa.Column("assigned_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_reason", sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["party_id"], ["parties.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["lawyer_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["assigned_by"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_lawyer_assignments_case_id", "lawyer_assignments", ["case_id"])
    op.create_index("ix_lawyer_assignments_lawyer_id", "lawyer_assignments", ["lawyer_id"])
    op.create_index("ix_lawyer_assignments_status", "lawyer_assignments", ["status"])

    op.create_table(
        "representation_change_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lawyer_assignment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_type", sa.String(50), nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("status", sa.String(20), server_default="PENDING", nullable=False),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["lawyer_assignment_id"], ["lawyer_assignments.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_representation_change_requests_case_id", "representation_change_requests", ["case_id"])

    op.create_table(
        "withdrawal_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("submitted_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("status", sa.String(30), server_default="PENDING_REVIEW", nullable=False),
        sa.Column("ai_summary", sa.Text, nullable=True),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decision_note", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["submitted_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_withdrawal_requests_case_id", "withdrawal_requests", ["case_id"])
    op.create_index("ix_withdrawal_requests_status", "withdrawal_requests", ["status"])

    # --- Hearings ---

    op.create_table(
        "hearings",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("court_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("judge_name", sa.String(255), nullable=False),
        sa.Column("hearing_date", sa.Date, nullable=False),
        sa.Column("hearing_time", sa.Time, nullable=True),
        sa.Column("status", sa.String(20), server_default="SCHEDULED", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("confirmed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["court_id"], ["courts.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["confirmed_by"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_hearings_case_id", "hearings", ["case_id"])
    op.create_index("ix_hearings_court_id", "hearings", ["court_id"])
    op.create_index("ix_hearings_hearing_date", "hearings", ["hearing_date"])
    op.create_index("ix_hearings_status", "hearings", ["status"])

    op.create_table(
        "attendance_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("hearing_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recorded_by_lawyer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attendance_status", sa.String(10), nullable=False, comment="PRESENT or ABSENT"),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["hearing_id"], ["hearings.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["party_id"], ["parties.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["recorded_by_lawyer_id"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_attendance_records_hearing_id", "attendance_records", ["hearing_id"])

    op.create_table(
        "absence_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hearing_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("submitted_by_lawyer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("status", sa.String(30), server_default="PENDING_REVIEW", nullable=False),
        sa.Column("ai_summary", sa.Text, nullable=True),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decision_note", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["hearing_id"], ["hearings.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["party_id"], ["parties.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["submitted_by_lawyer_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_absence_requests_case_id", "absence_requests", ["case_id"])
    op.create_index("ix_absence_requests_hearing_id", "absence_requests", ["hearing_id"])
    op.create_index("ix_absence_requests_status", "absence_requests", ["status"])

    # --- Court Agenda ---

    op.create_table(
        "court_agendas",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("court_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agenda_date", sa.Date, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["court_id"], ["courts.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_court_agendas_court_date", "court_agendas", ["court_id", "agenda_date"], unique=True)

    op.create_table(
        "agenda_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("agenda_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hearing_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ai_proposed_order", sa.Integer, nullable=True, comment="AI-recommended hearing order, immutable after creation"),
        sa.Column("final_order", sa.Integer, nullable=True, comment="Court Authority confirmed hearing order"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["agenda_id"], ["court_agendas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["hearing_id"], ["hearings.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_agenda_items_agenda_id", "agenda_items", ["agenda_id"])

    # --- Proceedings ---

    op.create_table(
        "proceedings",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hearing_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("source", sa.String(20), nullable=False, comment="MANUAL or SPEECH_TO_TEXT"),
        sa.Column("verified_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["hearing_id"], ["hearings.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["verified_by"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_proceedings_case_id", "proceedings", ["case_id"])
    op.create_index("ix_proceedings_hearing_id", "proceedings", ["hearing_id"])

    # --- Judgments ---

    op.create_table(
        "judgments",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("judgment_date", sa.Date, nullable=False),
        sa.Column("metadata_json", postgresql.JSONB, nullable=True, comment="AI-extracted metadata only"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_judgments_case_id", "judgments", ["case_id"])

    # --- Auth Devices ---

    op.create_table(
        "nfc_cards",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("lawyer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False),
        sa.Column("status", sa.String(20), server_default="ACTIVE", nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["lawyer_id"], ["users.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_nfc_cards_token_hash", "nfc_cards", ["token_hash"], unique=True)
    op.create_index("ix_nfc_cards_lawyer_id", "nfc_cards", ["lawyer_id"])

    op.create_table(
        "registered_devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("device_label", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), server_default="ACTIVE", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_registered_devices_user_id", "registered_devices", ["user_id"])

    op.create_table(
        "webauthn_credentials",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("credential_id", sa.String(500), nullable=False),
        sa.Column("public_key", sa.LargeBinary, nullable=False),
        sa.Column("sign_count", sa.Integer, server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["device_id"], ["registered_devices.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("credential_id"),
    )
    op.create_index("ix_webauthn_credentials_user_id", "webauthn_credentials", ["user_id"])
    op.create_index("ix_webauthn_credentials_credential_id", "webauthn_credentials", ["credential_id"], unique=True)

    op.create_table(
        "case_qr_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False),
        sa.Column("status", sa.String(20), server_default="ACTIVE", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_case_qr_tokens_token_hash", "case_qr_tokens", ["token_hash"], unique=True)
    op.create_index("ix_case_qr_tokens_case_id", "case_qr_tokens", ["case_id"])

    # --- AI ---

    op.create_table(
        "ai_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("job_type", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), server_default="PENDING", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_ai_jobs_case_id", "ai_jobs", ["case_id"])
    op.create_index("ix_ai_jobs_status", "ai_jobs", ["status"])

    op.create_table(
        "ai_outputs",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("ai_job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("output_type", sa.String(100), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("model_metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("verified_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["ai_job_id"], ["ai_jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["verified_by"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_ai_outputs_ai_job_id", "ai_outputs", ["ai_job_id"])

    # --- Audit Log ---

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_role", sa.String(20), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("old_state", postgresql.JSONB, nullable=True),
        sa.Column("new_state", postgresql.JSONB, nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("request_metadata", postgresql.JSONB, nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_audit_logs_case_id", "audit_logs", ["case_id"])
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])
    op.create_index("ix_audit_logs_entity_type_entity_id", "audit_logs", ["entity_type", "entity_id"])
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("ai_outputs")
    op.drop_table("ai_jobs")
    op.drop_table("case_qr_tokens")
    op.drop_table("webauthn_credentials")
    op.drop_table("registered_devices")
    op.drop_table("nfc_cards")
    op.drop_table("judgments")
    op.drop_table("proceedings")
    op.drop_table("agenda_items")
    op.drop_table("court_agendas")
    op.drop_table("absence_requests")
    op.drop_table("attendance_records")
    op.drop_table("hearings")
    op.drop_table("withdrawal_requests")
    op.drop_table("representation_change_requests")
    op.drop_table("lawyer_assignments")
    op.drop_table("evidence_records")
    op.drop_table("investigations")
    op.drop_table("documents")
    op.drop_table("parties")
    op.drop_table("cases")
    op.drop_table("court_authority_profiles")
    op.drop_table("lawyer_profiles")
    op.drop_table("police_profiles")
    op.drop_table("users")
    op.drop_table("courts")
    op.execute("DROP EXTENSION IF EXISTS vector")
