import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import RequireLawyer, CurrentUser
from app.models.case import Case, Party
from app.models.legal import LawyerAssignment, RepresentationChangeRequest, WithdrawalRequest
from app.models.hearing import Hearing, AttendanceRecord, AbsenceRequest, CourtAgenda, AgendaItem
from app.models.audit import AuditLog
from app.models.judgment import Judgment

from app.schemas.case import CaseResponse
from app.schemas.legal import (
    LawyerAssignmentResponse, 
    RepresentationChangeRequestCreate, RepresentationChangeRequestResponse,
    WithdrawalRequestCreate, WithdrawalRequestResponse
)
from app.schemas.hearing import (
    AttendanceRecordCreate, AttendanceRecordResponse,
    AbsenceRequestCreate, AbsenceRequestResponse,
    CourtAgendaResponse, HearingResponse
)

router = APIRouter(prefix="/api/lawyer", tags=["lawyer"])

@router.get("/cases", response_model=List[CaseResponse], dependencies=[RequireLawyer])
async def list_lawyer_cases(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> List[Case]:
    """List all cases where the current lawyer is actively assigned to at least one party."""
    stmt = (
        select(Case)
        .join(LawyerAssignment, Case.id == LawyerAssignment.case_id)
        .options(selectinload(Case.parties))
        .where(
            LawyerAssignment.lawyer_id == uuid.UUID(user["id"]),
            LawyerAssignment.status == "ACTIVE"
        )
        .distinct()
        .order_by(Case.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.get(
    "/cases/{case_id}",
    response_model=CaseResponse,
    dependencies=[RequireLawyer]
)
async def get_case_details(
    case_id: uuid.UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> Case:
    """Get case details if lawyer has an ACTIVE assignment."""
    stmt = (
        select(Case)
        .join(LawyerAssignment, Case.id == LawyerAssignment.case_id)
        .where(LawyerAssignment.lawyer_id == uuid.UUID(user["id"]))
        .where(LawyerAssignment.status == "ACTIVE")
        .where(Case.id == case_id)
        .options(selectinload(Case.parties))
    )
    res = await db.execute(stmt)
    case_obj = res.scalar_one_or_none()
    if not case_obj:
        raise HTTPException(status_code=403, detail="Not authorized to access this case")
    return case_obj

@router.get(
    "/cases/{case_id}/hearings",
    response_model=List[HearingResponse],
    dependencies=[RequireLawyer]
)
async def list_case_hearings(
    case_id: uuid.UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> List[Hearing]:
    """List hearings for a case the lawyer is assigned to."""
    from app.schemas.hearing import HearingResponse
    from app.models.hearing import Hearing
    
    # First verify access
    stmt_check = select(LawyerAssignment).where(
        LawyerAssignment.case_id == case_id,
        LawyerAssignment.lawyer_id == uuid.UUID(user["id"]),
        LawyerAssignment.status == "ACTIVE"
    )
    if not (await db.execute(stmt_check)).scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized")
        
    stmt = select(Hearing).where(Hearing.case_id == case_id).order_by(Hearing.hearing_date.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.post(
    "/hearings/{hearing_id}/attendance",
    response_model=AttendanceRecordResponse,
    dependencies=[RequireLawyer]
)
async def mark_attendance(
    hearing_id: uuid.UUID,
    payload: AttendanceRecordCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> AttendanceRecord:
    """Record party attendance. If absent, must use absence request instead."""
    if payload.attendance_status != "PRESENT":
        raise HTTPException(status_code=400, detail="Use absence request for ABSENT status")
        
    record = AttendanceRecord(
        hearing_id=hearing_id,
        party_id=payload.party_id,
        recorded_by_lawyer_id=uuid.UUID(user["id"]),
        attendance_status=payload.attendance_status
    )
    db.add(record)
    
    audit = AuditLog(
        actor_user_id=uuid.UUID(user["id"]),
        actor_role="LAWYER",
        action="ATTENDANCE_RECORDED",
        entity_type="ATTENDANCE",
        entity_id=record.id,
        new_state={"status": payload.attendance_status}
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(record)
    return record

@router.post(
    "/hearings/{hearing_id}/absence-requests",
    response_model=AbsenceRequestResponse,
    dependencies=[RequireLawyer]
)
async def create_absence_request(
    hearing_id: uuid.UUID,
    payload: AbsenceRequestCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> AbsenceRequest:
    """Submit an absence request with mandatory reason."""
    stmt = select(Hearing).where(Hearing.id == hearing_id)
    res = await db.execute(stmt)
    hearing = res.scalar_one_or_none()
    if not hearing:
        raise HTTPException(status_code=404, detail="Hearing not found")
        
    req = AbsenceRequest(
        case_id=hearing.case_id,
        hearing_id=hearing_id,
        party_id=payload.party_id,
        submitted_by_lawyer_id=uuid.UUID(user["id"]),
        reason=payload.reason,
        status="PENDING_REVIEW"
    )
    db.add(req)
    
    audit = AuditLog(
        case_id=hearing.case_id,
        actor_user_id=uuid.UUID(user["id"]),
        actor_role="LAWYER",
        action="ABSENCE_REQUESTED",
        entity_type="ABSENCE",
        entity_id=req.id,
        new_state={"status": "PENDING_REVIEW", "hearing_id": str(hearing_id)}
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(req)
    return req

@router.post(
    "/cases/{case_id}/retire",
    response_model=RepresentationChangeRequestResponse,
    dependencies=[RequireLawyer]
)
async def retire_case(
    case_id: uuid.UUID,
    payload: RepresentationChangeRequestCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> RepresentationChangeRequest:
    """Submit representation change request."""
    assignment_id = payload.lawyer_assignment_id
    if not assignment_id:
        stmt = select(LawyerAssignment).where(
            LawyerAssignment.case_id == case_id,
            LawyerAssignment.lawyer_id == uuid.UUID(user["id"]),
            LawyerAssignment.status == "ACTIVE"
        )
        assignment = (await db.execute(stmt)).scalar_one_or_none()
        if not assignment:
            raise HTTPException(status_code=403, detail="No active assignment found")
        assignment_id = assignment.id

    req = RepresentationChangeRequest(
        case_id=case_id,
        lawyer_assignment_id=assignment_id,
        requested_by=uuid.UUID(user["id"]),
        request_type=payload.request_type,
        reason=payload.reason,
        status="PENDING"
    )
    db.add(req)
    
    audit = AuditLog(
        case_id=case_id,
        actor_user_id=uuid.UUID(user["id"]),
        actor_role="LAWYER",
        action="RETIREMENT_REQUESTED",
        entity_type="REPRESENTATION",
        entity_id=req.id,
        new_state={"status": "PENDING"}
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(req)
    return req

@router.post(
    "/cases/{case_id}/withdraw",
    response_model=WithdrawalRequestResponse,
    dependencies=[RequireLawyer]
)
async def request_withdrawal(
    case_id: uuid.UUID,
    payload: WithdrawalRequestCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> WithdrawalRequest:
    """Request withdrawal or disposal."""
    req = WithdrawalRequest(
        case_id=case_id,
        submitted_by=uuid.UUID(user["id"]),
        reason=payload.reason,
        status="PENDING_REVIEW"
    )
    db.add(req)
    
    audit = AuditLog(
        case_id=case_id,
        actor_user_id=uuid.UUID(user["id"]),
        actor_role="LAWYER",
        action="WITHDRAWAL_REQUESTED",
        entity_type="WITHDRAWAL",
        entity_id=req.id,
        new_state={"status": "PENDING_REVIEW"}
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(req)
    return req
