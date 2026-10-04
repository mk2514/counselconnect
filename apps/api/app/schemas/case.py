from datetime import date, time
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PartyBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    gender: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    address: Optional[str] = None
    contact_number: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None


class PartyCreate(PartyBase):
    pass


class PartyResponse(PartyBase):
    id: UUID
    party_type: str

    model_config = ConfigDict(from_attributes=True)


class CaseCreate(BaseModel):
    source_ai_job_id: Optional[UUID] = None
    fir_number: Optional[str] = Field(None, max_length=100)
    case_type: str = Field(..., max_length=100)
    offence_category: Optional[str] = Field(None, max_length=200)
    cognizable_status: Optional[str] = Field(None, pattern="^(COGNIZABLE|NON_COGNIZABLE)$")
    incident_date: Optional[date] = None
    incident_time: Optional[time] = None
    incident_location: Optional[str] = None
    
    # Parties
    complainants: List[PartyCreate] = Field(default_factory=list, min_length=1)
    accused_persons: List[PartyCreate] = Field(default_factory=list)
    witnesses: List[PartyCreate] = Field(default_factory=list)


class CaseResponse(BaseModel):
    id: UUID
    csr_number: str
    fir_number: Optional[str]
    case_type: str
    offence_category: Optional[str]
    cognizable_status: Optional[str]
    incident_date: Optional[date]
    incident_time: Optional[time]
    incident_location: Optional[str]
    case_status: str
    procedural_stage: Optional[str]
    created_by: UUID
    
    parties: List[PartyResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class InvestigationCreate(BaseModel):
    note: str = Field(..., min_length=5)

class InvestigationResponse(BaseModel):
    id: UUID
    case_id: UUID
    note: str
    created_by: UUID
    
    model_config = ConfigDict(from_attributes=True)

class EvidenceCreate(BaseModel):
    evidence_number: str
    category: str
    description: Optional[str] = None
    source: Optional[str] = None
    document_id: Optional[UUID] = None

class EvidenceResponse(BaseModel):
    id: UUID
    case_id: UUID
    evidence_number: str
    category: str
    description: Optional[str]
    source: Optional[str]
    uploaded_by: UUID
    document_id: Optional[UUID]
    
    model_config = ConfigDict(from_attributes=True)
