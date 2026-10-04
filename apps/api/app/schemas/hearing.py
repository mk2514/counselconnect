from datetime import date, datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HearingCreate(BaseModel):
    case_id: UUID
    court_id: UUID
    judge_name: str = Field(..., max_length=255)
    hearing_date: date
    hearing_time: Optional[time] = None


class HearingResponse(BaseModel):
    id: UUID
    case_id: UUID
    court_id: UUID
    judge_name: str
    hearing_date: date
    hearing_time: Optional[time]
    status: str
    created_at: datetime
    confirmed_by: Optional[UUID]
    confirmed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class ProceedingCreate(BaseModel):
    hearing_id: UUID
    text: str
    source: str = "MANUAL"


class ProceedingResponse(BaseModel):
    id: UUID
    hearing_id: UUID
    case_id: UUID
    text: str
    source: str
    created_at: datetime
    verified_by: Optional[UUID]

    model_config = ConfigDict(from_attributes=True)


class AttendanceRecordCreate(BaseModel):
    party_id: UUID
    attendance_status: str = Field(..., pattern="^(PRESENT|ABSENT)$")


class AttendanceRecordResponse(BaseModel):
    id: UUID
    hearing_id: UUID
    party_id: UUID
    recorded_by_lawyer_id: UUID
    attendance_status: str
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AbsenceRequestCreate(BaseModel):
    party_id: UUID
    reason: str


class AbsenceRequestResponse(BaseModel):
    id: UUID
    case_id: UUID
    hearing_id: UUID
    party_id: UUID
    submitted_by_lawyer_id: UUID
    reason: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgendaItemResponse(BaseModel):
    id: UUID
    agenda_id: UUID
    hearing_id: UUID
    ai_proposed_order: Optional[int]
    final_order: Optional[int]
    notes: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class CourtAgendaResponse(BaseModel):
    id: UUID
    court_id: UUID
    agenda_date: date
    items: list[AgendaItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
