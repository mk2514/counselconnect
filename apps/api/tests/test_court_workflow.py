"""
Acceptance test for the comprehensive Court Authority Workflow.
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


class TestCourtWorkflow:

    def test_court_full_workflow(self, client):
        """Test court fetching cases, reviewing absence, and updating agenda."""
        mock_session = AsyncMock()
        
        court_id = uuid.uuid4()
        agenda_id = uuid.uuid4()
        absence_req_id = uuid.uuid4()
        rep_req_id = uuid.uuid4()
        auth_id = uuid.uuid4()
        
        from app.database import get_db
        from app.dependencies import get_current_user
        from app.models.hearing import Hearing, CourtAgenda, AbsenceRequest
        from app.models.legal import LawyerAssignment, RepresentationChangeRequest
        
        async def override_get_db():
            yield mock_session
            
        async def mock_refresh(instance):
            if not getattr(instance, "id", None):
                instance.id = uuid.uuid4()
            if hasattr(instance, "created_at"):
                instance.created_at = datetime.utcnow()
            
        mock_session.refresh.side_effect = mock_refresh
            
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = lambda: {"id": str(auth_id), "role": "COURT_AUTHORITY", "identifier": "JUDGE01"}

        # 1. Get Today's Cases
        mock_result = MagicMock()
        mock_hearing = Hearing(
            id=uuid.uuid4(), 
            case_id=uuid.uuid4(), 
            court_id=court_id, 
            judge_name="Hon. J. Smith", 
            hearing_date=datetime.utcnow().date(),
            status="SCHEDULED",
            created_at=datetime.utcnow()
        )
        mock_result.scalars().all.return_value = [mock_hearing]
        mock_result.scalar_one_or_none.return_value = mock_hearing
        mock_session.execute.return_value = mock_result
        
        resp = client.get("/api/court/hearings/today")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        
        # 2. Get Agenda Today
        mock_agenda = CourtAgenda(id=agenda_id, court_id=court_id, agenda_date=datetime.utcnow().date())
        mock_agenda.items = []
        mock_result.scalar_one_or_none.return_value = mock_agenda
        resp = client.get("/api/court/agenda/today")
        assert resp.status_code == 200
        
        # 3. Update Agenda
        resp = client.put(
            f"/api/court/agenda/{agenda_id}",
            json={"items": []}
        )
        assert resp.status_code == 200
        
        # 4. List Absence Requests
        mock_absence = AbsenceRequest(
            id=absence_req_id,
            case_id=uuid.uuid4(),
            hearing_id=uuid.uuid4(),
            party_id=uuid.uuid4(),
            submitted_by_lawyer_id=uuid.uuid4(),
            reason="Medical",
            status="PENDING_REVIEW",
            created_at=datetime.utcnow()
        )
        mock_result.scalars().all.return_value = [mock_absence]
        resp = client.get("/api/court/absence-requests")
        assert resp.status_code == 200
        
        # 5. Review Absence
        mock_result.scalar_one_or_none.return_value = mock_absence
        resp = client.put(
            f"/api/court/absence-requests/{absence_req_id}",
            json={"action": "APPROVE"}
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "APPROVED"
        
        # 6. Review Representation Request
        mock_rep = RepresentationChangeRequest(
            id=rep_req_id,
            case_id=uuid.uuid4(),
            lawyer_assignment_id=uuid.uuid4(),
            requested_by=uuid.uuid4(),
            request_type="RETIRE_REPRESENTATION",
            reason="Conflict",
            status="PENDING",
            created_at=datetime.utcnow()
        )
        mock_assignment = LawyerAssignment(
            id=uuid.uuid4(),
            case_id=uuid.uuid4(),
            party_id=uuid.uuid4(),
            lawyer_id=uuid.uuid4(),
            assigned_by=uuid.uuid4(),
            status="ACTIVE"
        )
        mock_result.scalar_one_or_none.side_effect = [mock_rep, mock_assignment]
        
        resp = client.put(
            f"/api/court/representation-requests/{rep_req_id}",
            json={"action": "APPROVE"}
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "APPROVED"

    def test_create_schedule_decision_transaction(self, client):
        mock_session = AsyncMock()
        hearing_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        from app.database import get_db
        from app.dependencies import get_current_user
        
        async def override_get_db():
            yield mock_session
            
        async def mock_refresh(instance):
            pass
            
        mock_session.refresh.side_effect = mock_refresh
            
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = lambda: {"id": str(user_id), "role": "COURT_AUTHORITY"}
        
        from app.models.hearing import Hearing
        from datetime import date
        fake_hearing = Hearing(
            id=hearing_id,
            case_id=uuid.uuid4(),
            court_id=uuid.uuid4(),
            judge_name="Judge",
            hearing_date=date.today(),
            status="SCHEDULED"
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = fake_hearing
        mock_session.execute.return_value = mock_result
        
        resp = client.post(
            f"/api/court/hearings/{hearing_id}/schedule-decision",
            json={
                "recommended_date": "2026-12-15",
                "recommended_time": "10:30:00",
                "reasoning_factors": "Low workload."
            }
        )
        
        assert resp.status_code == 201
        
        # Verify transaction (add decision, add hearing, add audit)
        assert mock_session.add.call_count == 3
        assert mock_session.commit.called

        app.dependency_overrides = {}
