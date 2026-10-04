"""
CounselConnect domain models.

Import all models here so that:
1. SQLAlchemy's Base.metadata discovers all tables.
2. Alembic autogenerate can detect schema changes.
3. Other modules can import from app.models directly.
"""

# Base
from app.models.ai import AIJob, AIOutput  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401
from app.models.auth_device import (  # noqa: F401
    CaseQRToken,
    NFCCard,
    RegisteredDevice,
    WebAuthnCredential,
)
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin  # noqa: F401
from app.models.case import Case, Party  # noqa: F401

# Domain models - import order matters for relationship resolution
from app.models.court import Court  # noqa: F401
from app.models.document import Document  # noqa: F401

# Enums
from app.models.enums import (  # noqa: F401
    AbsenceRequestStatus,
    AIJobStatus,
    AssignmentStatus,
    AttendanceStatus,
    CaseStatus,
    CognizableStatus,
    DeviceStatus,
    DocumentProcessingStatus,
    DocumentVerificationStatus,
    HearingStatus,
    NFCCardStatus,
    PartyType,
    ProceedingSource,
    RequestStatus,
    TokenStatus,
    UserRole,
    UserStatus,
    VerificationStatus,
    WithdrawalRequestStatus,
)
from app.models.hearing import (  # noqa: F401
    AbsenceRequest,
    AgendaItem,
    AttendanceRecord,
    CourtAgenda,
    Hearing,
    Proceeding,
)
from app.models.investigation import EvidenceRecord, Investigation  # noqa: F401
from app.models.judgment import Judgment  # noqa: F401
from app.models.legal import (  # noqa: F401
    LawyerAssignment,
    RepresentationChangeRequest,
    WithdrawalRequest,
)
from app.models.user import (  # noqa: F401
    CourtAuthorityProfile,
    LawyerProfile,
    PoliceProfile,
    User,
)
