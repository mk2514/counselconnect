from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class NFCEnrolRequest(BaseModel):
    device_id: UUID
    passkey_credential_id: str


class NFCEnrolResponse(BaseModel):
    card_id: UUID
    opaque_token: str
    activation_url: str


class NFCTapRequest(BaseModel):
    opaque_token: str
    device_id: UUID
    passkey_assertion: str  # Simulated WebAuthn assertion


class NFCTapResponse(BaseModel):
    access_token: str
    lawyer_id: UUID


class NFCCardStatusUpdate(BaseModel):
    status: str  # ACTIVE, LOST, REVOKED, REPLACED


class CaseQRResolveResponse(BaseModel):
    case_id: UUID
    csr_number: str
    status: str
    redirect_url: str
