"""Validated case-document storage and AI job creation."""

import hashlib
import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.dependencies import require_case_access
from app.errors import AuthorizationError
from app.models.ai import AIJob
from app.models.case import Case
from app.models.document import Document

ALLOWED_DOCUMENT_TYPES = {"FIR", "ABSENCE_PROOF", "INVESTIGATION", "JUDGMENT", "WITHDRAWAL"}
ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png"}
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


async def store_case_document(
    *,
    case_id: uuid.UUID,
    document_type: str,
    file: UploadFile,
    user: dict[str, str],
    db: AsyncSession,
) -> tuple[Document, AIJob]:
    case_record = await db.get(Case, case_id)
    if case_record is None:
        raise HTTPException(status_code=404, detail="Case not found.")
    await require_case_access(case_id, user, db)
    if user["role"] == "POLICE" and case_record.created_by != uuid.UUID(user["id"]):
        raise AuthorizationError("Police users may upload documents only to cases they filed.")
    if document_type not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(status_code=422, detail="Unsupported document type.")
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Upload a PDF, JPEG, or PNG document.",
        )

    file_bytes = await file.read(settings.storage_max_file_size_mb * 1024 * 1024 + 1)
    if not file_bytes:
        raise HTTPException(status_code=400, detail="The uploaded document is empty.")
    if len(file_bytes) > settings.storage_max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"Document exceeds the {settings.storage_max_file_size_mb} MB upload limit.",
        )

    original_filename = (file.filename or "document").replace("\\", "/").split("/")[-1][:255]
    if Path(original_filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="The document filename must use PDF, JPG, or PNG.",
        )

    file_hash = hashlib.sha256(file_bytes).hexdigest()
    duplicate = await db.scalar(
        select(Document.id).where(
            Document.case_id == case_id,
            Document.sha256_hash == file_hash,
        )
    )
    if duplicate is not None:
        raise HTTPException(
            status_code=409,
            detail="This document has already been uploaded to the case.",
        )

    upload_dir = Path(os.getcwd()) / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_filename = f"{uuid.uuid4()}_{original_filename}"
    file_path = upload_dir / safe_filename
    file_path.write_bytes(file_bytes)

    document = Document(
        case_id=case_id,
        document_type=document_type,
        storage_key=str(file_path),
        original_filename=original_filename,
        safe_filename=safe_filename,
        mime_type=file.content_type,
        file_size=len(file_bytes),
        sha256_hash=file_hash,
        uploaded_by=uuid.UUID(user["id"]),
        processing_status="PENDING",
    )
    db.add(document)
    await db.flush()

    job = AIJob(
        case_id=case_id,
        document_id=document.id,
        job_type=f"{document_type}_PROCESSING",
        status="PENDING",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    job_with_outputs = await db.scalar(
        select(AIJob).options(selectinload(AIJob.outputs)).where(AIJob.id == job.id)
    )
    if job_with_outputs is None:
        raise HTTPException(status_code=500, detail="Could not load the created AI job.")
    return document, job_with_outputs
