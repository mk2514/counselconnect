import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import CurrentUser, RequirePolice
from app.document_upload import store_case_document
from app.models.ai import AIJob
from app.models.audit import AuditLog
from app.models.case import Case, Party
from app.models.investigation import EvidenceRecord, Investigation
from app.schemas.ai import AIJobResponse
from app.schemas.case import (
    CaseCreate,
    CaseResponse,
    EvidenceCreate,
    EvidenceResponse,
    InvestigationCreate,
    InvestigationResponse,
)
from app.worker import _async_process_document

router = APIRouter(prefix="/api/police", tags=["police"])

def _generate_csr_number(station_code: str) -> str:
    """Generate a unique CSR number based on station code and current year/time."""
    now = datetime.now()
    year = now.strftime("%Y")
    unique_id = now.strftime("%m%d%H%M%S")
    return f"CSR/{station_code}/{year}/{unique_id}"

@router.post(
    "/cases",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequirePolice]
)
async def create_fir(
    case_in: CaseCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    File an FIR and create the central CSR Case record.
    Requires POLICE role.
    """
    # In a real app, you'd fetch the station_code from PoliceProfile.
    # We assume 'identifier' in CurrentUser points to station_code for police.
    csr_number = _generate_csr_number(user["identifier"])

    # Create Case
    new_case = Case(
        csr_number=csr_number,
        fir_number=case_in.fir_number,
        case_type=case_in.case_type,
        offence_category=case_in.offence_category,
        cognizable_status=case_in.cognizable_status,
        incident_date=case_in.incident_date,
        incident_time=case_in.incident_time,
        incident_location=case_in.incident_location,
        case_status="REGISTERED",
        created_by=uuid.UUID(user["id"])
    )
    db.add(new_case)
    await db.flush()  # To get new_case.id

    # Create Parties
    parties = []

    for comp in case_in.complainants:
        parties.append(Party(**comp.model_dump(), party_type="COMPLAINANT", case_id=new_case.id))

    for accused in case_in.accused_persons:
        parties.append(Party(**accused.model_dump(), party_type="ACCUSED", case_id=new_case.id))

    for witness in case_in.witnesses:
        parties.append(Party(**witness.model_dump(), party_type="WITNESS", case_id=new_case.id))

    db.add_all(parties)
    await db.commit()

    # Reload with parties to return full response
    stmt = (
        select(Case)
        .options(selectinload(Case.parties))
        .where(Case.id == new_case.id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()

@router.get(
    "/cases",
    response_model=list[CaseResponse],
    dependencies=[RequirePolice]
)
async def list_police_cases(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List cases created by this police station."""
    stmt = (
        select(Case)
        .options(selectinload(Case.parties))
        .where(Case.created_by == uuid.UUID(user["id"]))
        .order_by(Case.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.get(
    "/cases/{case_id}",
    response_model=CaseResponse,
    dependencies=[RequirePolice]
)
async def get_police_case(
    case_id: uuid.UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get a single case details."""
    stmt = (
        select(Case)
        .options(selectinload(Case.parties))
        .where(Case.id == case_id)
    )
    result = await db.execute(stmt)
    case_obj = result.scalar_one_or_none()

    if not case_obj:
        raise HTTPException(status_code=404, detail="Case not found")
    return case_obj

@router.post(
    "/cases/draft",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequirePolice]
)
async def create_draft_case(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Initialize a DRAFT case with a server-generated CSR."""
    csr_number = _generate_csr_number(user["identifier"])
    new_case = Case(
        csr_number=csr_number,
        case_type="TBD",
        case_status="DRAFT",
        created_by=uuid.UUID(user["id"])
    )
    db.add(new_case)
    await db.commit()
    await db.refresh(new_case)

    audit = AuditLog(
        case_id=new_case.id,
        actor_user_id=uuid.UUID(user["id"]),
        actor_role="POLICE",
        action="CSR_CREATED",
        entity_type="CASE",
        entity_id=new_case.id,
        new_state={"csr_number": new_case.csr_number, "status": "DRAFT"}
    )
    db.add(audit)
    await db.commit()

    stmt = select(Case).options(selectinload(Case.parties)).where(Case.id == new_case.id)
    res = await db.execute(stmt)
    return res.scalar_one()

@router.post(
    "/cases/{case_id}/documents/fir",
    response_model=AIJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequirePolice]
)
async def upload_fir_document(
    case_id: uuid.UUID,
    user: CurrentUser,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> AIJob:
    """Store an FIR and queue local, review-only document extraction."""
    doc, job = await store_case_document(
        case_id=case_id,
        document_type="FIR",
        file=file,
        user=user,
        db=db,
    )
    audit = AuditLog(
        case_id=case_id,
        actor_user_id=uuid.UUID(user["id"]),
        actor_role="POLICE",
        action="FIR_UPLOADED",
        entity_type="DOCUMENT",
        entity_id=doc.id,
        new_state={"document_type": "FIR", "processing_status": "PENDING"}
    )
    db.add(audit)
    await db.commit()
    background_tasks.add_task(_async_process_document, str(doc.id), str(job.id), "FIR")
    return job

@router.put(
    "/cases/{case_id}",
    response_model=CaseResponse,
    dependencies=[RequirePolice]
)
async def finalize_case(
    case_id: uuid.UUID,
    case_in: CaseCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> CaseResponse:
    """Update case with human-verified structured data and finalize registration."""
    stmt = select(Case).options(selectinload(Case.parties)).where(Case.id == case_id)
    result = await db.execute(stmt)
    case_obj = result.scalar_one_or_none()

    if not case_obj:
        raise HTTPException(status_code=404, detail="Case not found")
    if case_obj.created_by != uuid.UUID(user["id"]):
        raise HTTPException(
            status_code=403,
            detail="Police users may update only cases they filed.",
        )

    reviewed_job = None
    if case_in.source_ai_job_id:
        job_result = await db.execute(
            select(AIJob)
            .options(selectinload(AIJob.outputs))
            .where(
                AIJob.id == case_in.source_ai_job_id,
                AIJob.case_id == case_id,
                AIJob.status == "COMPLETED",
            )
        )
        reviewed_job = job_result.scalar_one_or_none()
        if reviewed_job is None or not reviewed_job.outputs:
            raise HTTPException(
                status_code=409,
                detail="The selected AI extraction is not available for human review.",
            )

    case_obj.case_type = case_in.case_type
    case_obj.offence_category = case_in.offence_category
    case_obj.incident_date = case_in.incident_date
    case_obj.incident_time = case_in.incident_time
    case_obj.incident_location = case_in.incident_location
    case_obj.case_status = "REGISTERED"

    # Clear old parties if any
    for p in case_obj.parties:
        await db.delete(p)

    for p_in in case_in.complainants:
        db.add(
            Party(
                case_id=case_id,
                party_type="COMPLAINANT",
                full_name=p_in.full_name,
                contact_number=p_in.contact_number,
            )
        )

    for p_in in case_in.accused_persons:
        db.add(
            Party(
                case_id=case_id,
                party_type="ACCUSED",
                full_name=p_in.full_name,
                contact_number=p_in.contact_number,
            )
        )

    for p_in in case_in.witnesses:
        db.add(
            Party(
                case_id=case_id,
                party_type="WITNESS",
                full_name=p_in.full_name,
                contact_number=p_in.contact_number,
            )
        )

    audit = AuditLog(
        case_id=case_id,
        actor_user_id=uuid.UUID(user["id"]),
        actor_role="POLICE",
        action="CASE_REGISTERED",
        entity_type="CASE",
        entity_id=case_id,
        new_state={
            "case_status": "REGISTERED",
            "case_type": case_in.case_type,
            "source_ai_job_id": str(reviewed_job.id) if reviewed_job else None,
        }
    )
    db.add(audit)
    if reviewed_job:
        reviewed_job.status = "REVIEWED"
        for output in reviewed_job.outputs:
            output.verified_by = uuid.UUID(user["id"])
            output.verified_at = datetime.now(UTC)
    await db.commit()

    stmt = select(Case).options(selectinload(Case.parties)).where(Case.id == case_id)
    res = await db.execute(stmt)
    return res.scalar_one()

@router.post(
    "/cases/{case_id}/investigations",
    response_model=InvestigationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequirePolice]
)
async def add_investigation_note(
    case_id: uuid.UUID,
    payload: InvestigationCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Add a structured investigation note."""
    note = Investigation(
        case_id=case_id,
        created_by=uuid.UUID(user["id"]),
        note=payload.note
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note

@router.get(
    "/cases/{case_id}/investigations",
    response_model=list[InvestigationResponse],
    dependencies=[RequirePolice]
)
async def list_investigations(
    case_id: uuid.UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Investigation)
        .where(Investigation.case_id == case_id)
        .order_by(Investigation.created_at.desc())
    )
    res = await db.execute(stmt)
    return list(res.scalars().all())

@router.post(
    "/cases/{case_id}/evidence",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequirePolice]
)
async def add_evidence_record(
    case_id: uuid.UUID,
    payload: EvidenceCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Add a structured evidence record."""
    evidence = EvidenceRecord(
        case_id=case_id,
        evidence_number=payload.evidence_number,
        category=payload.category,
        description=payload.description,
        source=payload.source,
        document_id=payload.document_id,
        uploaded_by=uuid.UUID(user["id"])
    )
    db.add(evidence)

    audit = AuditLog(
        case_id=case_id,
        actor_user_id=uuid.UUID(user["id"]),
        actor_role="POLICE",
        action="EVIDENCE_UPLOADED",
        entity_type="EVIDENCE",
        entity_id=evidence.id,
        new_state={"category": payload.category}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(evidence)
    return evidence

@router.get(
    "/cases/{case_id}/evidence",
    response_model=list[EvidenceResponse],
    dependencies=[RequirePolice]
)
async def list_evidence(
    case_id: uuid.UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(EvidenceRecord)
        .where(EvidenceRecord.case_id == case_id)
        .order_by(EvidenceRecord.created_at.desc())
    )
    res = await db.execute(stmt)
    return list(res.scalars().all())
