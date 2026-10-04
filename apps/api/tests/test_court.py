"""
Integration tests for Court Authority operations (Lawyer Assignment).
"""

from unittest.mock import AsyncMock, patch
import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.case import Case, Party
from app.models.legal import LawyerAssignment
from app.models.user import User, LawyerProfile


@pytest.fixture
def client():
    return TestClient(app)


class TestCourtLawyerAssignment:

    def test_non_court_cannot_assign_lawyer(self, client):
        """Only Court Authority can assign lawyers."""
        from app.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = lambda: {"id": str(uuid.uuid4()), "role": "POLICE"}
        
        resp = client.post(
            f"/api/court/cases/{uuid.uuid4()}/assignments", 
            json={"party_id": str(uuid.uuid4()), "lawyer_id": str(uuid.uuid4())}
        )
        assert resp.status_code == 403
        
        app.dependency_overrides = {}

    def test_court_assign_lawyer_success(self, client):
        """Court Authority successfully assigns a lawyer to a party."""
        mock_session = AsyncMock()
        
        case_id = uuid.uuid4()
        party_id = uuid.uuid4()
        lawyer_id = uuid.uuid4()
        
        # Mock finding party
        fake_party = Party(id=party_id, case_id=case_id, full_name="John Doe", party_type="ACCUSED")
        # Mock finding lawyer
        fake_lawyer = User(id=lawyer_id, role="LAWYER")
        
        from unittest.mock import MagicMock
        
        # We need the execute to return party, then lawyer, then previous assignments
        mock_party_result = MagicMock()
        mock_party_result.scalar_one_or_none.return_value = fake_party
        
        mock_lawyer_result = MagicMock()
        mock_lawyer_result.scalar_one_or_none.return_value = fake_lawyer
        
        mock_prev_result = MagicMock()
        mock_prev_result.scalars().all.return_value = []
        
        mock_session.execute.side_effect = [mock_party_result, mock_lawyer_result, mock_prev_result]
        
        from app.database import get_db
        from app.dependencies import get_current_user
        
        async def override_get_db():
            yield mock_session
            
        async def mock_refresh(instance):
            instance.id = uuid.uuid4()
            instance.assigned_at = datetime.utcnow()
            
        mock_session.refresh.side_effect = mock_refresh
            
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = lambda: {"id": str(uuid.uuid4()), "role": "COURT_AUTHORITY"}

        resp = client.post(
            f"/api/court/cases/{case_id}/assignments", 
            json={"party_id": str(party_id), "lawyer_id": str(lawyer_id)}
        )
        
        assert resp.status_code == 201
        data = resp.json()
        assert data["case_id"] == str(case_id)
        assert data["party_id"] == str(party_id)
        assert data["lawyer_id"] == str(lawyer_id)
        assert data["status"] == "ACTIVE"
        
        # Verify db.add was called to insert the new assignment
        assert mock_session.add.called
        assert mock_session.commit.called

        app.dependency_overrides = {}

    def test_court_replaces_lawyer_preserves_history(self, client):
        """Assigning a new lawyer to a party marks the previous assignment as REPLACED."""
        mock_session = AsyncMock()
        
        case_id = uuid.uuid4()
        party_id = uuid.uuid4()
        lawyer_id = uuid.uuid4()
        
        fake_party = Party(id=party_id, case_id=case_id, full_name="John Doe", party_type="ACCUSED")
        fake_lawyer = User(id=lawyer_id, role="LAWYER")
        
        old_assignment = LawyerAssignment(
            id=uuid.uuid4(),
            case_id=case_id,
            party_id=party_id,
            lawyer_id=uuid.uuid4(),
            status="ACTIVE",
            assigned_by=uuid.uuid4()
        )
        
        from unittest.mock import MagicMock
        
        mock_party_result = MagicMock()
        mock_party_result.scalar_one_or_none.return_value = fake_party
        
        mock_lawyer_result = MagicMock()
        mock_lawyer_result.scalar_one_or_none.return_value = fake_lawyer
        
        mock_prev_result = MagicMock()
        mock_prev_result.scalars().all.return_value = [old_assignment]
        
        mock_session.execute.side_effect = [mock_party_result, mock_lawyer_result, mock_prev_result]
        
        from app.database import get_db
        from app.dependencies import get_current_user
        
        async def override_get_db():
            yield mock_session
            
        async def mock_refresh(instance):
            instance.id = uuid.uuid4()
            instance.assigned_at = datetime.utcnow()
            
        mock_session.refresh.side_effect = mock_refresh
            
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = lambda: {"id": str(uuid.uuid4()), "role": "COURT_AUTHORITY"}

        resp = client.post(
            f"/api/court/cases/{case_id}/assignments", 
            json={"party_id": str(party_id), "lawyer_id": str(lawyer_id)}
        )
        
        assert resp.status_code == 201
        
        # The old assignment should have been updated to REPLACED
        assert old_assignment.status == "REPLACED"
        assert old_assignment.ended_at is not None
        assert old_assignment.end_reason == "Replaced by court authority"
        
        # Verify the new assignment, the old updated one, and audit log were added
        assert mock_session.add.call_count >= 2


class TestCourtHearings:

    def test_schedule_hearing_success(self, client):
        """Court Authority can schedule a hearing."""
        mock_session = AsyncMock()
        
        case_id = uuid.uuid4()
        court_id = uuid.uuid4()
        
        from app.database import get_db
        from app.dependencies import get_current_user
        
        async def override_get_db():
            yield mock_session
            
        async def mock_refresh(instance):
            instance.id = uuid.uuid4()
            from datetime import datetime
            instance.created_at = datetime.utcnow()
            
        mock_session.refresh.side_effect = mock_refresh
            
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = lambda: {"id": str(uuid.uuid4()), "role": "COURT_AUTHORITY"}

        payload = {
            "case_id": str(case_id),
            "court_id": str(court_id),
            "judge_name": "Honorable Judge Smith",
            "hearing_date": "2026-12-01",
            "hearing_time": "10:30:00"
        }
        
        resp = client.post("/api/court/hearings", json=payload)
        
        assert resp.status_code == 201
        data = resp.json()
        assert data["judge_name"] == "Honorable Judge Smith"
        assert data["status"] == "SCHEDULED"
        assert data["case_id"] == str(case_id)
        
        assert mock_session.add.called
        assert mock_session.commit.called

        app.dependency_overrides = {}
