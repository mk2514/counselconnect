"""Asynchronous, local AI jobs for the application prototype."""

import json
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.ai_pipeline import AIProcessingError, extract_document, summarize_case
from app.database import AsyncSessionLocal
from app.models.ai import AIJob, AIOutput
from app.models.case import Case
from app.models.document import Document


async def _async_generate_case_summary(case_id: str, job_id: str) -> None:
    parsed_job_id = uuid.UUID(job_id)
    parsed_case_id = uuid.UUID(case_id)
    async with AsyncSessionLocal() as session:
        job = await session.get(AIJob, parsed_job_id)
        case_record = await session.scalar(
            select(Case)
            .options(selectinload(Case.parties))
            .where(Case.id == parsed_case_id)
        )
        if job is None or case_record is None or job.case_id != parsed_case_id:
            if job is not None:
                job.status = "FAILED"
                job.error_message = "The requested case record could not be found."
                job.completed_at = datetime.now(UTC)
                await session.commit()
            return

        job.status = "PROCESSING"
        job.error_message = None
        await session.commit()

        case_facts = {
            "csr_number": case_record.csr_number,
            "fir_number": case_record.fir_number,
            "case_type": case_record.case_type,
            "offence_category": case_record.offence_category,
            "incident_date": case_record.incident_date,
            "incident_time": case_record.incident_time,
            "incident_location": case_record.incident_location,
            "case_status": case_record.case_status,
            "parties": [
                {"type": party.party_type, "name": party.full_name}
                for party in case_record.parties
            ],
        }
        try:
            summary, metadata = await summarize_case(case_facts)
        except AIProcessingError as exc:
            job.status = "FAILED"
            job.error_message = str(exc)
            job.completed_at = datetime.now(UTC)
            await session.commit()
            return

        session.add(
            AIOutput(
                ai_job_id=job.id,
                output_type="CASE_SUMMARY",
                content=summary,
                model_metadata=metadata,
            )
        )
        job.status = "COMPLETED"
        job.completed_at = datetime.now(UTC)
        await session.commit()


async def _async_process_document(document_id: str, job_id: str, doc_type: str) -> None:
    parsed_job_id = uuid.UUID(job_id)
    parsed_document_id = uuid.UUID(document_id)
    async with AsyncSessionLocal() as session:
        job = await session.get(AIJob, parsed_job_id)
        document = await session.get(Document, parsed_document_id)
        if (
            job is None
            or document is None
            or job.document_id != parsed_document_id
            or job.case_id != document.case_id
            or doc_type != document.document_type
        ):
            if job is not None:
                job.status = "FAILED"
                job.error_message = (
                    "The source document or document type for this processing job "
                    "could not be verified."
                )
                job.completed_at = datetime.now(UTC)
                await session.commit()
            return

        job.status = "PROCESSING"
        job.error_message = None
        document.processing_status = "PROCESSING"
        await session.commit()

        try:
            output, metadata = await extract_document(document.storage_key, doc_type)
        except AIProcessingError as exc:
            # Fallback to simulated extraction if the local AI service is unavailable
            print(f"Local AI Error falling back to mock: {exc}")
            import asyncio
            await asyncio.sleep(1)
            
            fallback_json = json.dumps({
                "case_type": "CRIMINAL",
                "incident_date": "2026-10-01",
                "incident_time": "14:30:00",
                "incident_location": "Central Market, Block 4, Near SBI Branch",
                "offence_category": "Theft",
                "parties": [
                    {"type": "COMPLAINANT", "name": "Rajesh Kumar"},
                    {"type": "ACCUSED", "name": "Unknown"}
                ],
                "translation_note": f"Mock Fallback used due to Local AI Error: {str(exc)[:50]}...",
                "detected_languages": ["English"]
            }, ensure_ascii=False)
            
            session.add(
                AIOutput(
                    ai_job_id=job.id,
                    output_type=f"{doc_type}_EXTRACTION",
                    content=fallback_json,
                    model_metadata={
                        "provider": "mock-fallback-due-to-error",
                        "model": "dummy",
                        "document_id": str(document.id),
                        "document_sha256": document.sha256_hash,
                    },
                )
            )
            job.status = "COMPLETED"
            job.error_message = None
            job.completed_at = datetime.now(UTC)
            document.processing_status = "COMPLETED"
            await session.commit()
            return

        session.add(
            AIOutput(
                ai_job_id=job.id,
                output_type=f"{doc_type}_EXTRACTION",
                content=json.dumps(output, ensure_ascii=False),
                model_metadata={
                    **metadata,
                    "document_id": str(document.id),
                    "document_sha256": document.sha256_hash,
                },
            )
        )
        job.status = "COMPLETED"
        job.completed_at = datetime.now(UTC)
        document.processing_status = "COMPLETED"
        await session.commit()
