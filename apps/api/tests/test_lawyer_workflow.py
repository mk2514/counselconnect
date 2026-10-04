"""
Acceptance test for the comprehensive Lawyer Workflow.
"""

from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestLawyerWorkflow:

    def test_lawyer_full_workflow(self, client):
        """Test lawyer fetching cases, requesting absence, and retiring from a case."""
        mock_session = AsyncMock()
        
        case_id = uuid.uuid4()
        hearing_id = uuid.uuid4()
        party_id = uuid.uuid4()
        lawyer_assignment_id = uuid.uuid4()
        lawyer_id = uuid.uuid4()
        
        from app.database import get_db
        from app.dependencies import get_current_user
        from app.models.case import Case, Party
        from app.models.hearing import Hearing
        from app.models.legal import LawyerAssignment
        
        async def override_get_db():
            yield mock_session
            
        async def mock_refresh(instance):
            if not getattr(instance, "id", None):
                instance.id = uuid.uuid4()
            if hasattr(instance, "created_at"):
                instance.created_at = datetime.utcnow()
            if hasattr(instance, "recorded_at"):
                instance.recorded_at = datetime.utcnow()
            
        mock_session.refresh.side_effect = mock_refresh
            
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = lambda: {"id": str(lawyer_id), "role": "LAWYER", "identifier": "LWYR01"}

        # 1. Get Cases
        mock_result = MagicMock()
        mock_case = Case(
            id=case_id, 
            csr_number="CSR/PS01/2026/0101", 
            case_type="CRIMINAL", 
            case_status="REGISTERED", 
            created_by=uuid.uuid4(),
            parties=[]
        )
        mock_result.scalars().all.return_value = [mock_case]
        mock_result.scalar_one_or_none.return_value = mock_case
        mock_session.execute.return_value = mock_result
        
        resp = client.get("/api/lawyer/cases")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        
        # 2. Get Case Details
        resp = client.get(f"/api/lawyer/cases/{case_id}")
        assert resp.status_code == 200
        
        # 3. Mark Attendance
        resp = client.post(
            f"/api/lawyer/hearings/{hearing_id}/attendance",
            json={"party_id": str(party_id), "attendance_status": "PRESENT"}
        )
        assert resp.status_code == 200
        
        # 4. Absence Request
        mock_hearing = Hearing(id=hearing_id, case_id=case_id, court_id=uuid.uuid4(), judge_name="J. Doe", hearing_date=datetime.utcnow().date())
        mock_result.scalar_one_or_none.return_value = mock_hearing
        
        resp = client.post(
            f"/api/lawyer/hearings/{hearing_id}/absence-requests",
            json={"party_id": str(party_id), "reason": "Medical emergency"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "PENDING_REVIEW"
        
        # 5. Retire Case
        resp = client.post(
            f"/api/lawyer/cases/{case_id}/retire",
            json={
                "lawyer_assignment_id": str(lawyer_assignment_id), 
                "request_type": "RETIRE_REPRESENTATION", 
                "reason": "Conflict of interest"
            }
        )
        assert resp.status_code == 200
        
        # 6. Withdraw Case
        resp = client.post(
            f"/api/lawyer/cases/{case_id}/withdraw",
            json={"reason": "Parties settled out of court"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "PENDING_REVIEW"

        app.dependency_overrides = {}
