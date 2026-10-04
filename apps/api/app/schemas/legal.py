from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LawyerAssignmentCreate(BaseModel):
    party_id: UUID
    lawyer_id: UUID


class LawyerAssignmentResponse(BaseModel):
    id: UUID
    case_id: UUID
    party_id: UUID
    lawyer_id: UUID
    status: str
    assigned_by: UUID
    assigned_at: datetime
    ended_at: Optional[datetime]
    end_reason: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class RepresentationChangeRequestCreate(BaseModel):
    lawyer_assignment_id: Optional[UUID] = None
    request_type: str
    reason: str


class RepresentationChangeRequestResponse(BaseModel):
    id: UUID
    case_id: UUID
    lawyer_assignment_id: Optional[UUID] = None
    requested_by: UUID
    request_type: str
    reason: str
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class WithdrawalRequestCreate(BaseModel):
    reason: str


class WithdrawalRequestResponse(BaseModel):
    id: UUID
    case_id: UUID
    submitted_by: UUID
    reason: str
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
