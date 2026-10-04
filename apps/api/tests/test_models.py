"""
Database model tests.

Tests for:
- Unique CSR
- Unique Bar Registration ID
- Unique JO Code
- Foreign-key enforcement
- Assignment relationships
- Audit creation capability
- Model import verification
"""



from app.models import (
    AbsenceRequest,
    AgendaItem,
    AIJob,
    AIOutput,
    AttendanceRecord,
    AuditLog,
    Base,
    Case,
    CaseQRToken,
    Court,
    CourtAgenda,
    CourtAuthorityProfile,
    Document,
    EvidenceRecord,
    Hearing,
    Investigation,
    Judgment,
    LawyerAssignment,
    LawyerProfile,
    NFCCard,
    Party,
    PoliceProfile,
    Proceeding,
    RegisteredDevice,
    RepresentationChangeRequest,
    User,
    WebAuthnCredential,
    WithdrawalRequest,
)
from app.models.enums import (
    AIJobStatus,
    AssignmentStatus,
    CaseStatus,
    PartyType,
    UserRole,
    UserStatus,
    VerificationStatus,
)


class TestModelImports:
    """Verify all models are importable and registered in metadata."""

    def test_all_models_importable(self) -> None:
        """Every model class should be importable from app.models."""
        models = [
            User, PoliceProfile, LawyerProfile, CourtAuthorityProfile,
            Court, Case, Party,
            Investigation, EvidenceRecord, Document,
            LawyerAssignment, RepresentationChangeRequest, WithdrawalRequest,
            Hearing, AttendanceRecord, AbsenceRequest,
            CourtAgenda, AgendaItem, Proceeding,
            Judgment,
            NFCCard, RegisteredDevice, WebAuthnCredential, CaseQRToken,
            AIJob, AIOutput,
            AuditLog,
        ]
        for model in models:
            assert hasattr(model, "__tablename__"), f"{model.__name__} missing __tablename__"

    def test_all_tables_in_metadata(self) -> None:
        """All tables should be registered in Base.metadata."""
        expected_tables = {
            "users", "police_profiles", "lawyer_profiles", "court_authority_profiles",
            "courts", "cases", "parties",
            "investigations", "evidence_records", "documents",
            "lawyer_assignments", "representation_change_requests", "withdrawal_requests",
            "hearings", "attendance_records", "absence_requests",
            "court_agendas", "agenda_items", "proceedings",
            "judgments",
            "nfc_cards", "registered_devices", "webauthn_credentials", "case_qr_tokens",
            "ai_jobs", "ai_outputs",
            "audit_logs",
        }
        actual_tables = set(Base.metadata.tables.keys())
        missing = expected_tables - actual_tables
        assert not missing, f"Missing tables in metadata: {missing}"


class TestEnums:
    """Verify enum values match requirements."""

    def test_user_roles_no_client(self) -> None:
        """CLIENT must not be an authenticated role per project rules."""
        role_values = {r.value for r in UserRole}
        assert "CLIENT" not in role_values
        assert role_values == {"POLICE", "LAWYER", "COURT_AUTHORITY"}

    def test_user_statuses(self) -> None:
        assert UserStatus.PENDING_VERIFICATION.value == "PENDING_VERIFICATION"
        assert UserStatus.ACTIVE.value == "ACTIVE"

    def test_case_statuses(self) -> None:
        assert CaseStatus.REGISTERED.value == "REGISTERED"
        assert CaseStatus.DISPOSED.value == "DISPOSED"
        assert CaseStatus.WITHDRAWN.value == "WITHDRAWN"

    def test_party_types(self) -> None:
        values = {p.value for p in PartyType}
        assert values == {"COMPLAINANT", "ACCUSED", "WITNESS", "OTHER"}

    def test_assignment_statuses(self) -> None:
        values = {s.value for s in AssignmentStatus}
        assert values == {"ACTIVE", "RETIRED", "REPLACED", "ENDED"}

    def test_ai_job_statuses(self) -> None:
        values = {s.value for s in AIJobStatus}
        assert values == {"PENDING", "PROCESSING", "COMPLETED", "FAILED", "REVIEWED"}

    def test_verification_statuses(self) -> None:
        values = {v.value for v in VerificationStatus}
        assert values == {"UNVERIFIED", "PENDING", "VERIFIED", "REJECTED"}


class TestTableSchema:
    """Verify table structure, constraints, and indexes."""

    def test_cases_csr_number_unique(self) -> None:
        """CSR must be unique."""
        table = Base.metadata.tables["cases"]
        csr_col = table.c.csr_number
        assert not csr_col.nullable
        # csr_number has unique=True on the column definition
        assert csr_col.unique, "csr_number column must have unique=True"

    def test_lawyer_profiles_bar_id_unique(self) -> None:
        """Bar Registration ID must be unique."""
        table = Base.metadata.tables["lawyer_profiles"]
        col = table.c.bar_registration_id
        assert col.unique, "bar_registration_id must be unique"
        assert not col.nullable

    def test_court_authority_jo_code_unique(self) -> None:
        """JO Code must be unique."""
        table = Base.metadata.tables["court_authority_profiles"]
        col = table.c.jo_code
        assert col.unique, "jo_code must be unique"
        assert not col.nullable

    def test_police_station_code_unique(self) -> None:
        """Station code must be unique."""
        table = Base.metadata.tables["police_profiles"]
        col = table.c.station_code
        assert col.unique, "station_code must be unique"
        assert not col.nullable

    def test_cases_foreign_keys(self) -> None:
        """Cases must have foreign key to users (created_by)."""
        table = Base.metadata.tables["cases"]
        fk_columns = {
            col.name
            for fk in table.foreign_keys
            for col in [fk.parent]
        }
        assert "created_by" in fk_columns

    def test_parties_foreign_keys(self) -> None:
        """Parties must have foreign key to cases."""
        table = Base.metadata.tables["parties"]
        fk_targets = {str(fk.column) for fk in table.foreign_keys}
        assert "cases.id" in fk_targets

    def test_lawyer_assignments_foreign_keys(self) -> None:
        """Assignments must reference case, party, lawyer, and assigner."""
        table = Base.metadata.tables["lawyer_assignments"]
        fk_columns = {
            col.name
            for fk in table.foreign_keys
            for col in [fk.parent]
        }
        assert {"case_id", "party_id", "lawyer_id", "assigned_by"}.issubset(fk_columns)

    def test_hearings_foreign_keys(self) -> None:
        """Hearings must reference case and court."""
        table = Base.metadata.tables["hearings"]
        fk_columns = {
            col.name
            for fk in table.foreign_keys
            for col in [fk.parent]
        }
        assert {"case_id", "court_id"}.issubset(fk_columns)

    def test_audit_logs_structure(self) -> None:
        """Audit log must have all required fields."""
        table = Base.metadata.tables["audit_logs"]
        required_cols = {
            "id", "case_id", "actor_user_id", "actor_role",
            "action", "entity_type", "entity_id",
            "old_state", "new_state", "timestamp", "request_metadata",
        }
        actual_cols = set(table.c.keys())
        missing = required_cols - actual_cols
        assert not missing, f"Audit log missing columns: {missing}"

    def test_documents_structure(self) -> None:
        """Documents must have all file metadata fields."""
        table = Base.metadata.tables["documents"]
        required_cols = {
            "id", "case_id", "document_type", "storage_key",
            "original_filename", "safe_filename", "mime_type",
            "file_size", "sha256_hash", "uploaded_by", "uploaded_at",
            "processing_status", "verification_status",
        }
        actual_cols = set(table.c.keys())
        missing = required_cols - actual_cols
        assert not missing, f"Documents missing columns: {missing}"

    def test_nfc_token_hash_unique(self) -> None:
        """NFC token_hash must be unique."""
        table = Base.metadata.tables["nfc_cards"]
        col = table.c.token_hash
        assert col.unique, "token_hash must be unique"

    def test_webauthn_credential_id_unique(self) -> None:
        """WebAuthn credential_id must be unique."""
        table = Base.metadata.tables["webauthn_credentials"]
        col = table.c.credential_id
        assert col.unique, "credential_id must be unique"

    def test_agenda_items_preserve_ai_and_final(self) -> None:
        """Agenda items must have both ai_proposed_order and final_order."""
        table = Base.metadata.tables["agenda_items"]
        assert "ai_proposed_order" in table.c.keys()
        assert "final_order" in table.c.keys()

    def test_proceedings_source_field(self) -> None:
        """Proceedings must have source field (MANUAL/SPEECH_TO_TEXT)."""
        table = Base.metadata.tables["proceedings"]
        assert "source" in table.c.keys()
        assert "verified_by" in table.c.keys()


class TestCascadeBehavior:
    """Verify cascade behavior is chosen carefully per project rules."""

    def test_case_delete_restricted(self) -> None:
        """Deleting a case must be restricted (not cascaded) for judicial records."""
        table = Base.metadata.tables["parties"]
        for fk in table.foreign_keys:
            if str(fk.column) == "cases.id":
                assert fk.ondelete == "RESTRICT", \
                    "Party FK to cases must use RESTRICT to prevent accidental deletion"

    def test_hearing_delete_restricted(self) -> None:
        """Deleting a hearing must be restricted for attendance/proceeding records."""
        table = Base.metadata.tables["attendance_records"]
        for fk in table.foreign_keys:
            if str(fk.column) == "hearings.id":
                assert fk.ondelete == "RESTRICT"

    def test_user_profile_cascade(self) -> None:
        """Deleting a user should cascade to their profile."""
        table = Base.metadata.tables["police_profiles"]
        for fk in table.foreign_keys:
            if str(fk.column) == "users.id":
                assert fk.ondelete == "CASCADE"
