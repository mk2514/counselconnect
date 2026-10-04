"""
PostgreSQL ENUM types for CounselConnect.

All enum values are defined as Python Enums and mapped to PostgreSQL
native ENUM types through SQLAlchemy.
"""

import enum


class UserRole(enum.StrEnum):
    """Platform user roles. CLIENT is intentionally excluded per project rules."""

    POLICE = "POLICE"
    LAWYER = "LAWYER"
    COURT_AUTHORITY = "COURT_AUTHORITY"


class UserStatus(enum.StrEnum):
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DEACTIVATED = "DEACTIVATED"


class VerificationStatus(enum.StrEnum):
    UNVERIFIED = "UNVERIFIED"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class CaseStatus(enum.StrEnum):
    REGISTERED = "REGISTERED"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    CHARGE_SHEETED = "CHARGE_SHEETED"
    TRIAL_IN_PROGRESS = "TRIAL_IN_PROGRESS"
    RESERVED_FOR_JUDGMENT = "RESERVED_FOR_JUDGMENT"
    JUDGMENT_DELIVERED = "JUDGMENT_DELIVERED"
    DISPOSED = "DISPOSED"
    WITHDRAWN = "WITHDRAWN"
    TRANSFERRED = "TRANSFERRED"


class PartyType(enum.StrEnum):
    COMPLAINANT = "COMPLAINANT"
    ACCUSED = "ACCUSED"
    WITNESS = "WITNESS"
    OTHER = "OTHER"


class AssignmentStatus(enum.StrEnum):
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"
    REPLACED = "REPLACED"
    ENDED = "ENDED"


class HearingStatus(enum.StrEnum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ADJOURNED = "ADJOURNED"
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"


class AttendanceStatus(enum.StrEnum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"


class AbsenceRequestStatus(enum.StrEnum):
    PENDING_REVIEW = "PENDING_REVIEW"
    MORE_INFORMATION_REQUIRED = "MORE_INFORMATION_REQUIRED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class DocumentProcessingStatus(enum.StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DocumentVerificationStatus(enum.StrEnum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class ProceedingSource(enum.StrEnum):
    MANUAL = "MANUAL"
    SPEECH_TO_TEXT = "SPEECH_TO_TEXT"


class RequestStatus(enum.StrEnum):
    """Shared status for representation change / withdrawal requests."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class WithdrawalRequestStatus(enum.StrEnum):
    PENDING_REVIEW = "PENDING_REVIEW"
    MORE_INFORMATION_REQUIRED = "MORE_INFORMATION_REQUIRED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class NFCCardStatus(enum.StrEnum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class DeviceStatus(enum.StrEnum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class TokenStatus(enum.StrEnum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class AIJobStatus(enum.StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVIEWED = "REVIEWED"


class CognizableStatus(enum.StrEnum):
    COGNIZABLE = "COGNIZABLE"
    NON_COGNIZABLE = "NON_COGNIZABLE"
