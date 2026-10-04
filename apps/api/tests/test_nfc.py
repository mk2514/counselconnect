"""
Tests for NFC, Passkey, and QR Layer.
"""

from unittest.mock import AsyncMock, patch, MagicMock
import uuid
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.auth_device import NFCCard, RegisteredDevice, WebAuthnCredential, CaseQRToken
from app.models.legal import LawyerAssignment
from app.models.case import Case

@pytest.fixture
def client():
    return TestClient(app)

class TestNFCAuth:
    def test_nfc_tap_valid_card(self, client):
        mock_session = AsyncMock()
        lawyer_id = uuid.uuid4()
        device_id = uuid.uuid4()
        
        # Fake active card
        fake_card = NFCCard(lawyer_id=lawyer_id, token_hash="dummy_hash", status="ACTIVE")
        # Fake active primary device
        fake_device = RegisteredDevice(id=device_id, user_id=lawyer_id, status="ACTIVE")
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = fake_card
        mock_result.scalars().first.return_value = fake_device
        
        mock_session.execute.side_effect = [mock_result, mock_result]
        
        from app.database import get_db
        app.dependency_overrides[get_db] = lambda: mock_session
        
        with patch("app.routers.nfc_auth._hash_token", return_value="dummy_hash"):
            resp = client.post(
                "/api/nfc/tap",
                json={
                    "opaque_token": "some_token",
                    "device_id": str(device_id),
                    "passkey_assertion": "VALID_ASSERTION"
                }
            )
            
        assert resp.status_code == 200
        data = resp.json()
        assert data["access_token"] == "simulated_jwt_token_for_nfc_session"
        assert data["lawyer_id"] == str(lawyer_id)
        assert mock_session.commit.called

    def test_nfc_tap_unknown_card(self, client):
        mock_session = AsyncMock()
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        from app.database import get_db
        app.dependency_overrides[get_db] = lambda: mock_session
        
        resp = client.post(
            "/api/nfc/tap",
            json={
                "opaque_token": "unknown_token",
                "device_id": str(uuid.uuid4()),
                "passkey_assertion": "VALID_ASSERTION"
            }
        )
        assert resp.status_code == 401
        assert "Unknown or invalid" in resp.json()["detail"]

    def test_nfc_tap_revoked_card(self, client):
        mock_session = AsyncMock()
        
        fake_card = NFCCard(lawyer_id=uuid.uuid4(), token_hash="dummy_hash", status="REVOKED")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = fake_card
        mock_session.execute.return_value = mock_result
        
        from app.database import get_db
        app.dependency_overrides[get_db] = lambda: mock_session
        
        resp = client.post(
            "/api/nfc/tap",
            json={
                "opaque_token": "revoked_token",
                "device_id": str(uuid.uuid4()),
                "passkey_assertion": "VALID_ASSERTION"
            }
        )
        assert resp.status_code == 403
        assert "not active" in resp.json()["detail"]

    def test_nfc_tap_wrong_device(self, client):
        mock_session = AsyncMock()
        lawyer_id = uuid.uuid4()
        
        fake_card = NFCCard(lawyer_id=lawyer_id, token_hash="dummy_hash", status="ACTIVE")
        fake_primary_device = RegisteredDevice(id=uuid.uuid4(), user_id=lawyer_id, status="ACTIVE")
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = fake_card
        mock_result.scalars().first.return_value = fake_primary_device
        mock_session.execute.side_effect = [mock_result, mock_result]
        
        from app.database import get_db
        app.dependency_overrides[get_db] = lambda: mock_session
        
        resp = client.post(
            "/api/nfc/tap",
            json={
                "opaque_token": "some_token",
                "device_id": str(uuid.uuid4()), # Different from primary device
                "passkey_assertion": "VALID_ASSERTION"
            }
        )
        assert resp.status_code == 403
        assert "Unauthorized device detected" in resp.json()["detail"]

    def test_nfc_tap_failed_passkey(self, client):
        mock_session = AsyncMock()
        lawyer_id = uuid.uuid4()
        device_id = uuid.uuid4()
        
        fake_card = NFCCard(lawyer_id=lawyer_id, token_hash="dummy_hash", status="ACTIVE")
        fake_device = RegisteredDevice(id=device_id, user_id=lawyer_id, status="ACTIVE")
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = fake_card
        mock_result.scalars().first.return_value = fake_device
        mock_session.execute.side_effect = [mock_result, mock_result]
        
        from app.database import get_db
        app.dependency_overrides[get_db] = lambda: mock_session
        
        resp = client.post(
            "/api/nfc/tap",
            json={
                "opaque_token": "some_token",
                "device_id": str(device_id),
                "passkey_assertion": "INVALID"
            }
        )
        assert resp.status_code == 401
        assert "WebAuthn assertion failed" in resp.json()["detail"]

    def test_qr_resolve_unauthorized_lawyer(self, client):
        mock_session = AsyncMock()
        case_id = uuid.uuid4()
        
        fake_qr = CaseQRToken(case_id=case_id, token_hash="qr_hash", status="ACTIVE")
        mock_result = MagicMock()
        # QR exists, but Lawyer Assignment check returns None (no active assignment)
        mock_result.scalar_one_or_none.side_effect = [fake_qr, None]
        mock_session.execute.return_value = mock_result
        
        from app.database import get_db
        from app.dependencies import get_current_user
        app.dependency_overrides[get_db] = lambda: mock_session
        app.dependency_overrides[get_current_user] = lambda: {"id": str(uuid.uuid4()), "role": "LAWYER"}
        
        with patch("app.routers.nfc_auth._hash_token", return_value="qr_hash"):
            resp = client.get("/api/qr/case/some_qr_token")
            
        assert resp.status_code == 403
        assert "Not authorized" in resp.json()["detail"]

    def test_qr_resolve_authorized_police(self, client):
        mock_session = AsyncMock()
        case_id = uuid.uuid4()
        
        fake_qr = CaseQRToken(case_id=case_id, token_hash="qr_hash", status="ACTIVE")
        fake_case = Case(id=case_id, csr_number="CSR/TEST/123", case_status="REGISTERED")
        
        mock_result = MagicMock()
        # QR exists, Role check skips assignment check, Case fetch returns fake_case
        mock_result.scalar_one_or_none.side_effect = [fake_qr, fake_case]
        mock_session.execute.return_value = mock_result
        
        from app.database import get_db
        from app.dependencies import get_current_user
        app.dependency_overrides[get_db] = lambda: mock_session
        app.dependency_overrides[get_current_user] = lambda: {"id": str(uuid.uuid4()), "role": "POLICE"}
        
        with patch("app.routers.nfc_auth._hash_token", return_value="qr_hash"):
            resp = client.get("/api/qr/case/some_qr_token")
            
        assert resp.status_code == 200
        assert resp.json()["csr_number"] == "CSR/TEST/123"

    def teardown_method(self):
        app.dependency_overrides = {}
