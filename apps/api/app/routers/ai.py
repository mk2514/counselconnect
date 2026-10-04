"""Case-scoped AI processing routes."""

import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import CurrentUser, RequireCourtAuthority, RequirePolice, require_case_access
from app.document_upload import store_case_document
from app.errors import AuthorizationError
from app.models.ai import AIJob
from app.models.case import Case
from app.models.document import Document
from app.schemas.ai import AIJobResponse, SummarizeRequest
from app.worker import _async_generate_case_summary, _async_process_document

router = APIRouter(prefix="/api/ai", tags=["ai"])


async def _require_case_access(case_id: uuid.UUID, user: dict[str, str], db: AsyncSession) -> None:
    await require_case_access(case_id, user, db)
    case_record = await db.get(Case, case_id)
    if case_record is None:
        raise HTTPException(status_code=404, detail="Case not found.")
    if user["role"] == "POLICE" and case_record.created_by != uuid.UUID(user["id"]):
        raise AuthorizationError("Police users may access AI records only for cases they filed.")


@router.post(
    "/jobs/summarize",
    response_model=AIJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireCourtAuthority],
)
async def request_case_summary(
    request: SummarizeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> AIJob:
    case_record = await db.get(Case, request.case_id)
    if case_record is None:
        raise HTTPException(status_code=404, detail="Case not found.")

    job = AIJob(case_id=request.case_id, job_type="CASE_SUMMARY", status="PENDING")
    db.add(job)
    await db.commit()
    await db.refresh(job)
    created_job_id = job.id
    loaded_job = await db.scalar(
        select(AIJob).options(selectinload(AIJob.outputs)).where(AIJob.id == job.id)
    )
    if loaded_job is None:
        raise HTTPException(status_code=500, detail="Could not load the created AI job.")
    background_tasks.add_task(
        _async_generate_case_summary,
        str(request.case_id),
        str(created_job_id),
    )
    return loaded_job


@router.get("/jobs/{job_id}", response_model=AIJobResponse)
async def get_job_status(
    job_id: uuid.UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> AIJob:
    result = await db.execute(
        select(AIJob).options(selectinload(AIJob.outputs)).where(AIJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    if job is None or job.case_id is None:
        raise HTTPException(status_code=404, detail="AI job not found.")
    await _require_case_access(job.case_id, user, db)
    return job


@router.get("/cases/{case_id}/jobs", response_model=list[AIJobResponse])
async def list_case_ai_jobs(
    case_id: uuid.UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> list[AIJob]:
    await _require_case_access(case_id, user, db)
    result = await db.execute(
        select(AIJob)
        .options(selectinload(AIJob.outputs))
        .where(AIJob.case_id == case_id)
        .order_by(AIJob.created_at.desc())
    )
    return list(result.scalars().all())


@router.post(
    "/documents/process",
    response_model=AIJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequirePolice],
)
async def process_case_document(
    user: CurrentUser,
    background_tasks: BackgroundTasks,
    case_id: Annotated[uuid.UUID, Form()],
    document_type: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
    db: AsyncSession = Depends(get_db),
) -> AIJob:
    document, job = await store_case_document(
        case_id=case_id,
        document_type=document_type,
        file=file,
        user=user,
        db=db,
    )
    background_tasks.add_task(_async_process_document, str(document.id), str(job.id), document_type)
    return job


@router.post(
    "/jobs/{job_id}/retry",
    response_model=AIJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def retry_document_processing(
    job_id: uuid.UUID,
    user: CurrentUser,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> AIJob:
    result = await db.execute(
        select(AIJob)
        .options(selectinload(AIJob.outputs))
        .where(AIJob.id == job_id)
        .with_for_update()
    )
    job = result.scalar_one_or_none()
    if job is None or job.case_id is None:
        raise HTTPException(status_code=404, detail="AI job not found.")
    await _require_case_access(job.case_id, user, db)
    if user["role"] not in {"POLICE", "COURT_AUTHORITY"}:
        raise AuthorizationError("Only Police or Court Authority may retry document processing.")
    if job.status != "FAILED" or job.document_id is None:
        raise HTTPException(status_code=409, detail="Only failed document jobs can be retried.")
    document = await db.get(Document, job.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="The source document is no longer available.")

    document.processing_status = "PENDING"
    job.status = "PENDING"
    job.completed_at = None
    job.error_message = None
    await db.commit()
    background_tasks.add_task(
        _async_process_document,
        str(document.id),
        str(job.id),
        document.document_type,
    )
    return job


@router.post("/speech-to-text", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def speech_to_text_not_configured() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "Speech transcription is not configured yet. "
            "Enter and review the transcript manually."
        ),
    )
