"""Tests for local AI extraction and honest processing failures."""

import json
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from pypdf import PdfWriter

from app.ai_pipeline import AIProcessingError, _generate, _read_document, extract_document
from app.models.ai import AIJob
from app.models.document import Document
from app.worker import _async_generate_case_summary, _async_process_document


def _create_text_pdf(path) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with path.open("wb") as pdf_file:
        writer.write(pdf_file)


def test_read_document_extracts_pdf_text(tmp_path):
    path = tmp_path / "fir.pdf"
    _create_text_pdf(path)

    fake_page = SimpleNamespace(extract_text=lambda: "FIR incident at River Road")
    with patch("app.ai_pipeline.PdfReader", return_value=SimpleNamespace(pages=[fake_page])):
        text, images, engine = _read_document(str(path))

    assert "River Road" in text
    assert images == []
    assert engine == "pypdf-text"


def test_read_document_marks_scanned_pdf_for_local_vision_ocr(tmp_path):
    path = tmp_path / "scanned.pdf"
    _create_text_pdf(path)

    text, images, engine = _read_document(str(path))

    assert text == ""
    assert len(images) == 1
    assert engine == "ollama-vision"


@pytest.mark.asyncio
async def test_extract_document_returns_candidate_and_local_provenance(tmp_path):
    path = tmp_path / "fir.pdf"
    _create_text_pdf(path)
    candidate = {
        "case_type": "CRIMINAL",
        "incident_date": "2026-09-12",
        "incident_time": "14:30:00",
        "incident_location": "River Road",
        "offence_category": "Theft",
        "parties": [{"type": "COMPLAINANT", "name": "A. Kumar"}],
        "detected_languages": ["English"],
        "translation_note": None,
    }
    fake_page = SimpleNamespace(extract_text=lambda: "FIR incident at River Road on 2026-09-12")
    with (
        patch("app.ai_pipeline.PdfReader", return_value=SimpleNamespace(pages=[fake_page])),
        patch(
            "app.ai_pipeline._generate",
            new=AsyncMock(return_value=(json.dumps(candidate), "test-local-model")),
        ) as generate,
    ):
        output, metadata = await extract_document(str(path), "FIR")

    assert output["incident_date"] == "2026-09-12"
    assert output["incident_time"] == "14:30"
    assert output["incident_location"] == "River Road"
    assert output["parties"][0]["name"] == "A. Kumar"
    assert "River Road" in output["extracted_text"]
    assert metadata == {
        "provider": "ollama-local",
        "model": "test-local-model",
        "ocr_engine": "pypdf-text",
    }
    assert "Do not infer facts" in generate.await_args.args[0]


@pytest.mark.asyncio
async def test_generate_reports_local_model_unavailable_without_fabricating_output():
    class OfflineClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def post(self, *_args, **_kwargs):
            raise httpx.ConnectError("connection refused")

    with patch("app.ai_pipeline.httpx.AsyncClient", return_value=OfflineClient()):
        with pytest.raises(AIProcessingError, match="Local AI processing is unavailable"):
            await _generate("summarize")


@pytest.mark.asyncio
async def test_failed_case_summary_records_failure_without_output():
    case_id = uuid.uuid4()
    job = SimpleNamespace(
        id=uuid.uuid4(),
        case_id=case_id,
        status="PENDING",
        error_message=None,
        completed_at=None,
    )
    case = SimpleNamespace(
        id=case_id,
        csr_number="CSR/TEST/2026/001",
        fir_number="FIR-1",
        case_type="CRIMINAL",
        offence_category="Theft",
        incident_date=None,
        incident_time=None,
        incident_location="River Road",
        case_status="REGISTERED",
        parties=[],
    )

    class FakeSession:
        def __init__(self):
            self.added = []
            self.commits = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def get(self, model, _identifier):
            return job if model is AIJob else None

        async def scalar(self, _statement):
            return case

        async def commit(self):
            self.commits += 1

        def add(self, value):
            self.added.append(value)

    session = FakeSession()
    with (
        patch("app.worker.AsyncSessionLocal", return_value=session),
        patch(
            "app.worker.summarize_case",
            new=AsyncMock(side_effect=AIProcessingError("Local model unavailable.")),
        ),
    ):
        await _async_generate_case_summary(str(case_id), str(job.id))

    assert job.status == "FAILED"
    assert job.error_message == "Local model unavailable."
    assert job.completed_at is not None
    assert session.added == []
    assert session.commits == 2


@pytest.mark.asyncio
async def test_unavailable_document_ai_marks_job_and_document_failed():
    job_id = uuid.uuid4()
    document_id = uuid.uuid4()
    case_id = uuid.uuid4()
    job = SimpleNamespace(
        id=job_id,
        case_id=case_id,
        document_id=document_id,
        status="PENDING",
        error_message=None,
        completed_at=None,
    )
    source_document = SimpleNamespace(
        id=document_id,
        case_id=case_id,
        document_type="FIR",
        storage_key="missing.pdf",
        sha256_hash="sha256",
        processing_status="PENDING",
    )

    class FakeSession:
        def __init__(self):
            self.added = []
            self.commits = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def get(self, model, _identifier):
            return job if model is AIJob else source_document if model is Document else None

        async def commit(self):
            self.commits += 1

        def add(self, value):
            self.added.append(value)

    session = FakeSession()
    with (
        patch("app.worker.AsyncSessionLocal", return_value=session),
        patch(
            "app.worker.extract_document",
            new=AsyncMock(side_effect=AIProcessingError("Local AI processing is unavailable.")),
        ),
    ):
        await _async_process_document(str(document_id), str(job_id), "FIR")

    assert job.status == "FAILED"
    assert source_document.processing_status == "FAILED"
    assert job.error_message == "Local AI processing is unavailable."
    assert job.completed_at is not None
    assert session.added == []
    assert session.commits == 2
