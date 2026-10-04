import uuid
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import RequireCourtAuthority, CurrentUser
from app.models.case import Case, Party
from app.models.user import User, LawyerProfile
from app.models.legal import LawyerAssignment, RepresentationChangeRequest, WithdrawalRequest
from app.models.hearing import CourtAgenda, AgendaItem, AbsenceRequest
from app.models.audit import AuditLog
from app.schemas.case import CaseResponse
from app.schemas.legal import (
    LawyerAssignmentCreate, LawyerAssignmentResponse,
    RepresentationChangeRequestResponse, WithdrawalRequestResponse
)
from app.schemas.hearing import CourtAgendaResponse, AbsenceRequestResponse
from app.schemas.court import (
    AbsenceReviewRequest,
    RepresentationReviewRequest,
    WithdrawalReviewRequest,
    CourtAgendaUpdateRequest,
    CategorizationPriorityResponse,
    ScheduleRecommendationResponse,
    ScheduleDecisionCreate
)

router = APIRouter(prefix="/api/court", tags=["court"])

@router.get("/cases", response_model=List[CaseResponse], dependencies=[RequireCourtAuthority])
async def list_court_cases(db: AsyncSession = Depends(get_db)) -> List[Case]:
    """List all registered cases for court view."""
    stmt = (
        select(Case)
        .options(selectinload(Case.parties))
        .order_by(Case.created_at.desc())
        .limit(100) # Simple limit for now
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.get("/cases/{case_id}", response_model=CaseResponse, dependencies=[RequireCourtAuthority])
async def get_court_case(case_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Case:
    """Get full details of a specific case."""
    stmt = (
        select(Case)
        .options(selectinload(Case.parties))
        .where(Case.id == case_id)
    )
    result = await db.execute(stmt)
    case_record = result.scalar_one_or_none()
    if not case_record:
        raise HTTPException(status_code=404, detail="Case not found")
    return case_record

@router.get("/lawyers", dependencies=[RequireCourtAuthority])
async def list_lawyers(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """List all registered lawyers so court can assign them."""
    stmt = (
        select(User, LawyerProfile)
        .join(LawyerProfile, User.id == LawyerProfile.user_id)
        .where(User.role == "LAWYER")
        .where(User.status == "ACTIVE")
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "id": row[0].id,
            "full_name": row[1].full_name,
            "bar_registration_id": row[1].bar_registration_id
        }
        for row in rows
    ]

@router.post(
    "/cases/{case_id}/assignments", 
    response_model=LawyerAssignmentResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireCourtAuthority]
)
async def assign_lawyer(
    case_id: uuid.UUID,
    assignment_in: LawyerAssignmentCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> LawyerAssignment:
    """
    Assign a lawyer to a party in a case.
    Validates that the case and party exist, and that the lawyer is valid.
    """
    # 1. Verify Case & Party
    stmt_party = select(Party).where(Party.id == assignment_in.party_id, Party.case_id == case_id)
    result_party = await db.execute(stmt_party)
    party = result_party.scalar_one_or_none()
    if not party:
        raise HTTPException(status_code=404, detail="Party not found in this case.")

    # 2. Verify Lawyer
    stmt_lawyer = select(User).where(User.id == assignment_in.lawyer_id, User.role == "LAWYER")
    result_lawyer = await db.execute(stmt_lawyer)
    lawyer = result_lawyer.scalar_one_or_none()
    if not lawyer:
        raise HTTPException(status_code=404, detail="Valid lawyer not found.")

    # 3. Create Assignment
    new_assignment = LawyerAssignment(
        case_id=case_id,
        party_id=assignment_in.party_id,
        lawyer_id=assignment_in.lawyer_id,
        status="ACTIVE",
        assigned_by=uuid.UUID(user["id"])
    )
    
    db.add(new_assignment)
    
    # 4. End any previous ACTIVE assignment for this specific party
    stmt_previous = select(LawyerAssignment).where(
        LawyerAssignment.party_id == assignment_in.party_id,
        LawyerAssignment.status == "ACTIVE",
        LawyerAssignment.id != new_assignment.id
    )
    result_prev = await db.execute(stmt_previous)
    prev_assignments = result_prev.scalars().all()
    for prev in prev_assignments:
        prev.status = "REPLACED"
        prev.end_reason = "Replaced by court authority"
        from datetime import datetime, timezone
        prev.ended_at = datetime.now(timezone.utc)
        db.add(prev)
        
    audit = AuditLog(
        case_id=case_id,
        actor_user_id=uuid.UUID(user["id"]),
        actor_role="COURT_AUTHORITY",
        action="LAWYER_ASSIGNED",
        entity_type="LAWYER_ASSIGNMENT",
        entity_id=new_assignment.id,
        new_state={"lawyer_id": str(assignment_in.lawyer_id), "party_id": str(assignment_in.party_id)}
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(new_assignment)
    return new_assignment


from app.models.hearing import Hearing, Proceeding, ScheduleDecision
from app.schemas.hearing import HearingCreate, HearingResponse, ProceedingCreate, ProceedingResponse
from app.models.court import Court

@router.post("/hearings", response_model=HearingResponse, status_code=status.HTTP_201_CREATED, dependencies=[RequireCourtAuthority])
async def schedule_hearing(
    hearing_in: HearingCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Hearing:
    """Schedule a new hearing for a case."""
    # Create Hearing
    new_hearing = Hearing(
        case_id=hearing_in.case_id,
        court_id=hearing_in.court_id,
        judge_name=hearing_in.judge_name,
        hearing_date=hearing_in.hearing_date,
        hearing_time=hearing_in.hearing_time,
        status="SCHEDULED",
        confirmed_by=uuid.UUID(user["id"])
    )
    
    db.add(new_hearing)
    
    audit = AuditLog(
        case_id=new_hearing.case_id,
        actor_user_id=uuid.UUID(user["id"]),
        actor_role="COURT_AUTHORITY",
        action="HEARING_SCHEDULED",
        entity_type="HEARING",
        entity_id=new_hearing.id,
        new_state={"hearing_date": str(new_hearing.hearing_date), "status": new_hearing.status}
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(new_hearing)
    return new_hearing

@router.post("/hearings/{hearing_id}/proceedings", response_model=ProceedingResponse, status_code=status.HTTP_201_CREATED, dependencies=[RequireCourtAuthority])
async def log_proceeding(
    hearing_id: uuid.UUID,
    proceeding_in: ProceedingCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Proceeding:
    """Log proceeding notes/transcripts for a hearing."""
    # Find hearing to get case_id
    stmt = select(Hearing).where(Hearing.id == hearing_id)
    result = await db.execute(stmt)
    hearing = result.scalar_one_or_none()
    
    if not hearing:
        raise HTTPException(status_code=404, detail="Hearing not found")
        
    new_proceeding = Proceeding(
        hearing_id=hearing_id,
        case_id=hearing.case_id,
        text=proceeding_in.text,
        source=proceeding_in.source,
        verified_by=uuid.UUID(user["id"])
    )
    
    db.add(new_proceeding)
    
    # Update hearing status
    hearing.status = "CONCLUDED"
    db.add(hearing)
    
    audit = AuditLog(
        case_id=hearing.case_id,
        actor_user_id=uuid.UUID(user["id"]),
        actor_role="COURT_AUTHORITY",
        action="PROCEEDING_LOGGED",
        entity_type="PROCEEDING",
        entity_id=new_proceeding.id,
        new_state={"hearing_status": "CONCLUDED"}
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(new_proceeding)
    return new_proceeding

@router.get("/hearings/{hearing_id}/schedule-recommendation", response_model=ScheduleRecommendationResponse, dependencies=[RequireCourtAuthority])
async def get_schedule_recommendation(
    hearing_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    AI recommendation for scheduling a hearing.
    Output: recommendations only, with reasoning factors.
    """
    stmt = select(Hearing).where(Hearing.id == hearing_id)
    result = await db.execute(stmt)
    hearing = result.scalar_one_or_none()
    
    if not hearing:
        raise HTTPException(status_code=404, detail="Hearing not found")
        
    # Simulated AI Scheduling Engine Logic
    from datetime import date, timedelta
    recommended_date = date.today() + timedelta(days=14)
    
    return {
        "hearing_id": hearing_id,
        "recommended_date": recommended_date,
        "recommended_time": "10:30:00",
        "reasoning_factors": "Case priority is HIGH. Court workload is low on this date. Judge availability confirmed.",
        "conflicts_checked": True
    }

@router.post("/hearings/{hearing_id}/schedule-decision", status_code=status.HTTP_201_CREATED, dependencies=[RequireCourtAuthority])
async def create_schedule_decision(
    hearing_id: uuid.UUID,
    decision_in: ScheduleDecisionCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> Hearing:
    """
    Final confirmation of scheduling recommendation.
    Database transaction: create schedule decision -> update hearing -> create audit log.
    """
    stmt = select(Hearing).where(Hearing.id == hearing_id)
    result = await db.execute(stmt)
    hearing = result.scalar_one_or_none()
    
    if not hearing:
        raise HTTPException(status_code=404, detail="Hearing not found")
        
    from datetime import datetime
    
    # 1. Create schedule decision
    decision = ScheduleDecision(
        hearing_id=hearing_id,
        recommended_date=decision_in.recommended_date,
        reasoning_factors=decision_in.reasoning_factors,
        confirmed_by=uuid.UUID(user["id"])
    )
    if decision_in.recommended_time:
        from datetime import datetime as dt
        decision.recommended_time = dt.strptime(decision_in.recommended_time, "%H:%M:%S").time()
        
    db.add(decision)
    
    # 2. Update hearing
    hearing.hearing_date = decision.recommended_date
    hearing.hearing_time = decision.recommended_time
    hearing.status = "RESCHEDULED"
    db.add(hearing)
    
    # 3. Create audit log
    audit = AuditLog(
        case_id=hearing.case_id,
        actor_user_id=uuid.UUID(user["id"]),
        actor_role=user["role"],
        action="RESCHEDULED",
        entity_type="HEARING",
        entity_id=hearing_id,
        new_state={"hearing_date": str(hearing.hearing_date), "status": hearing.status}
    )
    db.add(audit)
    
    # All succeed or all roll back
    await db.commit()
    await db.refresh(hearing)
    return hearing

@router.get("/hearings", response_model=List[HearingResponse], dependencies=[RequireCourtAuthority])
async def list_court_hearings(db: AsyncSession = Depends(get_db)) -> List[Hearing]:
    """List all scheduled hearings."""
    stmt = (
        select(Hearing)
        .order_by(Hearing.hearing_date.asc(), Hearing.hearing_time.asc())
        .limit(100)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.get("/courts")
async def list_courts(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """List all courts for selection."""
    stmt = select(Court).order_by(Court.court_name.asc())
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [{"id": c.id, "court_name": c.court_name, "court_type": c.court_type} for c in rows]

@router.get("/hearings/today", response_model=List[HearingResponse], dependencies=[RequireCourtAuthority])
async def get_todays_cases(db: AsyncSession = Depends(get_db)) -> List[Hearing]:
    """Fetch real scheduled hearings for the current date."""
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).date()
    stmt = select(Hearing).where(Hearing.hearing_date == today).order_by(Hearing.hearing_time)
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.get("/agenda/today", response_model=CourtAgendaResponse, dependencies=[RequireCourtAuthority])
async def get_todays_agenda(db: AsyncSession = Depends(get_db)) -> CourtAgenda:
    """Get the Court Agenda for today (proposed or final)."""
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).date()
    stmt = (
        select(CourtAgenda)
        .where(CourtAgenda.agenda_date == today)
        .options(selectinload(CourtAgenda.items))
    )
    result = await db.execute(stmt)
    agenda = result.scalar_one_or_none()
    if not agenda:
        raise HTTPException(status_code=404, detail="Agenda not published for today")
    return agenda

@router.put("/agenda/{agenda_id}", response_model=CourtAgendaResponse, dependencies=[RequireCourtAuthority])
async def update_agenda(
    agenda_id: uuid.UUID,
    payload: CourtAgendaUpdateRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> CourtAgenda:
    """Update final order of agenda items."""
    stmt = select(CourtAgenda).where(CourtAgenda.id == agenda_id).options(selectinload(CourtAgenda.items))
    res = await db.execute(stmt)
    agenda = res.scalar_one_or_none()
    
    if not agenda:
        raise HTTPException(status_code=404, detail="Agenda not found")
        
    item_map = {item.id: item for item in agenda.items}
    for update_item in payload.items:
        if update_item.agenda_item_id in item_map:
            db_item = item_map[update_item.agenda_item_id]
            db_item.final_order = update_item.final_order
            if update_item.notes:
                db_item.notes = update_item.notes
                
    audit = AuditLog(
        case_id=agenda.items[0].hearing.case_id if agenda.items else None,
        actor_user_id=uuid.UUID(user["id"]),
        actor_role=user["role"],
        action="UPDATED",
        entity_type="COURT_AGENDA",
        entity_id=agenda_id,
        new_state={"items_updated": len(payload.items)}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(agenda)
    return agenda

@router.get("/absence-requests", response_model=List[AbsenceRequestResponse], dependencies=[RequireCourtAuthority])
async def list_absence_requests(db: AsyncSession = Depends(get_db)) -> List[AbsenceRequest]:
    """List pending absence requests."""
    stmt = select(AbsenceRequest).where(AbsenceRequest.status == "PENDING_REVIEW")
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.put("/absence-requests/{request_id}", response_model=AbsenceRequestResponse, dependencies=[RequireCourtAuthority])
async def review_absence(
    request_id: uuid.UUID,
    payload: AbsenceReviewRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> AbsenceRequest:
    """Approve/Reject absence request."""
    from datetime import datetime, timezone
    stmt = select(AbsenceRequest).where(AbsenceRequest.id == request_id)
    res = await db.execute(stmt)
    req = res.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    status_map = {
        "APPROVE": "APPROVED",
        "REJECT": "REJECTED",
        "REQUEST_MORE_INFO": "MORE_INFO_NEEDED"
    }
    req.status = status_map.get(payload.action, req.status)
    req.reviewed_by = uuid.UUID(user["id"])
    req.reviewed_at = datetime.now(timezone.utc)
    if payload.decision_note:
        req.decision_note = payload.decision_note
        
    audit = AuditLog(
        case_id=req.case_id,
        actor_user_id=uuid.UUID(user["id"]),
        actor_role="COURT_AUTHORITY",
        action="ABSENCE_REVIEWED",
        entity_type="ABSENCE",
        entity_id=req.id,
        new_state={"status": req.status}
    )
    db.add(audit)
        
    await db.commit()
    await db.refresh(req)
    return req

@router.get("/representation-requests", response_model=List[RepresentationChangeRequestResponse], dependencies=[RequireCourtAuthority])
async def list_representation_requests(db: AsyncSession = Depends(get_db)) -> List[RepresentationChangeRequest]:
    """List pending representation change requests."""
    stmt = select(RepresentationChangeRequest).where(RepresentationChangeRequest.status == "PENDING")
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.put("/representation-requests/{request_id}", response_model=RepresentationChangeRequestResponse, dependencies=[RequireCourtAuthority])
async def review_representation_request(
    request_id: uuid.UUID,
    payload: RepresentationReviewRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> RepresentationChangeRequest:
    """Approve/Reject lawyer retirement/change."""
    from datetime import datetime, timezone
    stmt = select(RepresentationChangeRequest).where(RepresentationChangeRequest.id == request_id)
    res = await db.execute(stmt)
    req = res.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if payload.action == "APPROVE":
        req.status = "APPROVED"
        assign_stmt = select(LawyerAssignment).where(LawyerAssignment.id == req.lawyer_assignment_id)
        assign_res = await db.execute(assign_stmt)
        assignment = assign_res.scalar_one_or_none()
        if assignment:
            assignment.status = "RETIRE"
            assignment.ended_at = datetime.now(timezone.utc)
            assignment.end_reason = "Court Approved Retirement"
    else:
        req.status = "REJECTED"
        
    req.reviewed_by = uuid.UUID(user["id"])
    req.reviewed_at = datetime.now(timezone.utc)
    
    audit = AuditLog(
        case_id=req.case_id,
        actor_user_id=uuid.UUID(user["id"]),
        actor_role="COURT_AUTHORITY",
        action="REPRESENTATION_REVIEWED",
        entity_type="REPRESENTATION",
        entity_id=req.id,
        new_state={"status": req.status}
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(req)
    return req

@router.get("/withdrawals", response_model=List[WithdrawalRequestResponse], dependencies=[RequireCourtAuthority])
async def list_withdrawals(db: AsyncSession = Depends(get_db)) -> List[WithdrawalRequest]:
    """List pending withdrawal requests."""
    stmt = select(WithdrawalRequest).where(WithdrawalRequest.status == "PENDING_REVIEW")
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.put("/withdrawals/{request_id}", response_model=WithdrawalRequestResponse, dependencies=[RequireCourtAuthority])
async def review_withdrawal(
    request_id: uuid.UUID,
    payload: WithdrawalReviewRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> WithdrawalRequest:
    """Approve/Reject withdrawal requests."""
    from datetime import datetime, timezone
    stmt = select(WithdrawalRequest).where(WithdrawalRequest.id == request_id)
    res = await db.execute(stmt)
    req = res.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    req.status = "APPROVED" if payload.action == "APPROVE" else "REJECTED"
    req.reviewed_by = uuid.UUID(user["id"])
    req.reviewed_at = datetime.now(timezone.utc)
    if payload.decision_note:
        req.decision_note = payload.decision_note
        
    audit = AuditLog(
        case_id=req.case_id,
        actor_user_id=uuid.UUID(user["id"]),
        actor_role="COURT_AUTHORITY",
        action="WITHDRAWAL_REVIEWED",
        entity_type="WITHDRAWAL",
        entity_id=req.id,
        new_state={"status": req.status}
    )
    db.add(audit)
        
    await db.commit()
    await db.refresh(req)
    return req

@router.get("/categorization", response_model=List[CategorizationPriorityResponse], dependencies=[RequireCourtAuthority])
async def list_categorization(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Mock endpoint returning AI categorization and prioritization."""
    return []
