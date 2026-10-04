from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AbsenceReviewRequest(BaseModel):
    action: str  # APPROVE, REJECT, REQUEST_MORE_INFO
    decision_note: Optional[str] = None


class RepresentationReviewRequest(BaseModel):
    action: str  # APPROVE, REJECT
    decision_note: Optional[str] = None


class WithdrawalReviewRequest(BaseModel):
    action: str  # APPROVE, REJECT
    decision_note: Optional[str] = None


class AgendaItemUpdate(BaseModel):
    agenda_item_id: UUID
    final_order: int
    notes: Optional[str] = None


class CourtAgendaUpdateRequest(BaseModel):
    items: List[AgendaItemUpdate]


class CategorizationPriorityResponse(BaseModel):
    case_id: UUID
    csr_number: str
    ai_category: str
    needs_human_verification: bool
    priority_label: str  # HIGH, MEDIUM, LOW
    contributing_factors: List[str]
    ai_recommendation: str
    human_review_status: str

    model_config = ConfigDict(from_attributes=True)


class ScheduleRecommendationResponse(BaseModel):
    hearing_id: UUID
    recommended_date: date
    recommended_time: Optional[str] = None
    reasoning_factors: str
    conflicts_checked: bool


class ScheduleDecisionCreate(BaseModel):
    recommended_date: date
    recommended_time: Optional[str] = None
    reasoning_factors: str

