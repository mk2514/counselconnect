"""
Acceptance test for the comprehensive Police Workflow.
"""

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestPoliceWorkflow:

    def test_police_full_workflow(self, client):
        """Test draft CSR, FIR upload, finalize, investigation, and evidence."""
        mock_session = MagicMock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.delete = AsyncMock()

        case_id = uuid.uuid4()
        user_id = uuid.uuid4()

        from app.database import get_db
        from app.dependencies import get_current_user
        from app.models.ai import AIJob, AIOutput
        from app.models.case import Case, Party

        async def override_get_db():
            yield mock_session

        async def mock_refresh(instance):
            if not getattr(instance, "id", None):
                instance.id = uuid.uuid4()
            if hasattr(instance, "created_at"):
                instance.created_at = datetime.now(UTC)

        mock_session.refresh.side_effect = mock_refresh

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = lambda: {
            "id": str(user_id),
            "role": "POLICE",
            "identifier": "PS01",
        }

        # 1. Draft Case
        mock_result = MagicMock()
        mock_case = Case(
            id=case_id,
            csr_number="CSR/PS01/2026/0101",
            case_type="TBD",
            case_status="DRAFT",
            created_by=user_id,
            parties=[]
        )
        mock_result.scalar_one.return_value = mock_case
        mock_result.scalar_one_or_none.return_value = mock_case
        mock_session.execute.return_value = mock_result

        resp = client.post("/api/police/cases/draft")
        assert resp.status_code == 201
        data = resp.json()
        assert data["csr_number"].startswith("CSR/PS01")
        assert data["case_status"] == "DRAFT"

        # 2. Upload FIR
        source_document = SimpleNamespace(id=uuid.uuid4())
        mock_job = AIJob(
            id=uuid.uuid4(),
            case_id=case_id,
            document_id=source_document.id,
            job_type="FIR_PROCESSING",
            status="PENDING",
            outputs=[],
            created_at=datetime.now(UTC),
        )
        with (
            patch(
                "app.routers.police.store_case_document",
                new=AsyncMock(return_value=(source_document, mock_job)),
            ) as mock_store,
            patch("app.routers.police._async_process_document", new=AsyncMock()) as mock_process,
        ):
            resp = client.post(
                f"/api/police/cases/{case_id}/documents/fir",
                files={"file": ("test_fir.pdf", b"dummy content", "application/pdf")}
            )
            assert resp.status_code == 202
            assert mock_store.called
            mock_process.assert_awaited_once_with(str(source_document.id), str(mock_job.id), "FIR")

        # 3. Finalize Case
        payload = {
            "source_ai_job_id": str(mock_job.id),
            "case_type": "CRIMINAL",
            "incident_date": "2026-10-01",
            "incident_location": "Central Park",
            "complainants": [
                {"full_name": "John Doe", "party_type": "COMPLAINANT"}
            ],
            "accused_persons": [],
            "witnesses": []
        }

        mock_case_final = Case(
            id=case_id,
            csr_number="CSR/PS01/2026/0101",
            case_type="CRIMINAL",
            case_status="REGISTERED",
            created_by=user_id,
            parties=[Party(id=uuid.uuid4(), full_name="John Doe", party_type="COMPLAINANT")]
        )
        case_result = MagicMock()
        case_result.scalar_one_or_none.return_value = mock_case
        output = AIOutput(
            id=uuid.uuid4(),
            ai_job_id=mock_job.id,
            output_type="FIR_EXTRACTION",
            content="{}",
        )
        reviewed_job = AIJob(
            id=mock_job.id,
            case_id=case_id,
            job_type="FIR_PROCESSING",
            status="COMPLETED",
            outputs=[output],
            created_at=datetime.now(UTC),
        )
        ai_job_result = MagicMock()
        ai_job_result.scalar_one_or_none.return_value = reviewed_job
        final_case_result = MagicMock()
        final_case_result.scalar_one.return_value = mock_case_final
        mock_session.execute.side_effect = [case_result, ai_job_result, final_case_result]

        resp = client.put(f"/api/police/cases/{case_id}", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["case_status"] == "REGISTERED"
        assert len(data["parties"]) == 1
        assert reviewed_job.status == "REVIEWED"
        assert output.verified_by == user_id
        assert output.verified_at is not None

        # 4. Add Investigation
        resp = client.post(
            f"/api/police/cases/{case_id}/investigations",
            json={"note": "Visited the crime scene. Secured perimeter."}
        )
        assert resp.status_code == 201

        # 5. Add Evidence
        resp = client.post(
            f"/api/police/cases/{case_id}/evidence",
            json={
                "evidence_number": "EV-001",
                "category": "PHYSICAL",
                "description": "Recovered weapon"
            }
        )
        assert resp.status_code == 201

        app.dependency_overrides = {}
