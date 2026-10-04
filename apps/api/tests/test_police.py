"""
Integration tests for the Police workflow (FIR to Case creation).
"""

from unittest.mock import AsyncMock, patch
import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.case import Case, Party


@pytest.fixture
def client():
    return TestClient(app)


def _valid_fir_data():
    return {
        "fir_number": "123/2026",
        "case_type": "CRIMINAL",
        "offence_category": "Theft",
        "cognizable_status": "COGNIZABLE",
        "incident_location": "Main Street, Block A",
        "complainants": [
            {
                "full_name": "Rahul Verma",
                "contact_number": "9876543210"
            }
        ],
        "accused_persons": [
            {
                "full_name": "Unknown Person"
            }
        ],
        "witnesses": []
    }


class TestPoliceCaseCreation:

    def test_unauthenticated_cannot_create_fir(self, client):
        """Unauthenticated user should be denied access."""
        resp = client.post("/api/police/cases", json=_valid_fir_data())
        assert resp.status_code == 401

    def test_non_police_cannot_create_fir(self, client):
        """Lawyers or Court Authorities should not be able to create FIRs."""
        from app.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = lambda: {"id": str(uuid.uuid4()), "role": "LAWYER"}
        
        resp = client.post("/api/police/cases", json=_valid_fir_data())
        assert resp.status_code == 403
        
        app.dependency_overrides = {}

    def test_police_create_fir_success(self, client):
        """Police officer should successfully create an FIR."""
        mock_session = AsyncMock()
        
        fake_case = Case(
            id=uuid.uuid4(),
            csr_number="CSR/PS001/2026/0101120000",
            fir_number="123/2026",
            case_type="CRIMINAL",
            case_status="REGISTERED",
            created_by=uuid.uuid4(),
            parties=[
                Party(id=uuid.uuid4(), full_name="Rahul Verma", party_type="COMPLAINANT")
            ]
        )
        
        from unittest.mock import MagicMock
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = fake_case
        mock_session.execute.return_value = mock_result
        
        from app.database import get_db
        from app.dependencies import get_current_user
        
        async def override_get_db():
            yield mock_session
            
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = lambda: {"id": str(uuid.uuid4()), "role": "POLICE", "identifier": "PS001"}

        resp = client.post("/api/police/cases", json=_valid_fir_data())
        
        assert resp.status_code == 201
        data = resp.json()
        assert data["csr_number"].startswith("CSR/PS001/")
        assert data["case_type"] == "CRIMINAL"
        assert len(data["parties"]) == 1
        assert data["parties"][0]["party_type"] == "COMPLAINANT"

        app.dependency_overrides = {}


class TestPoliceCaseList:

    def test_police_list_cases_success(self, client):
        """Police officer should be able to list their cases."""
        mock_session = AsyncMock()
        
        fake_case = Case(
            id=uuid.uuid4(),
            csr_number="CSR/PS001/2026/0101120000",
            case_type="CRIMINAL",
            case_status="REGISTERED",
            created_by=uuid.uuid4(),
            parties=[]
        )
        
        from unittest.mock import MagicMock
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [fake_case]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        from app.database import get_db
        from app.dependencies import get_current_user
        
        async def override_get_db():
            yield mock_session
            
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = lambda: {"id": str(uuid.uuid4()), "role": "POLICE"}

        resp = client.get("/api/police/cases")
        
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["csr_number"] == "CSR/PS001/2026/0101120000"

        app.dependency_overrides = {}
