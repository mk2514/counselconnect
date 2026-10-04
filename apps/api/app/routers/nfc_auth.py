import hashlib
import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.models.auth_device import NFCCard, RegisteredDevice, WebAuthnCredential, CaseQRToken
from app.models.legal import LawyerAssignment
from app.models.audit import AuditLog
from app.models.case import Case
from app.schemas.nfc import (
    NFCEnrolRequest, NFCEnrolResponse, NFCTapRequest, NFCTapResponse,
    NFCCardStatusUpdate, CaseQRResolveResponse
)

router = APIRouter(prefix="/api/nfc", tags=["nfc"])

def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

@router.post("/enrol", response_model=NFCEnrolResponse, status_code=status.HTTP_201_CREATED)
async def enrol_nfc_card(
    user: CurrentUser,
    payload: NFCEnrolRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Lawyer account -> registered device -> passkey credential -> NFC card token association.
    """
    if user["role"] != "LAWYER":
        raise HTTPException(status_code=403, detail="Only verified lawyers can enrol NFC cards.")
        
    # Verify primary device
    stmt = select(RegisteredDevice).where(
        RegisteredDevice.id == payload.device_id,
        RegisteredDevice.user_id == uuid.UUID(user["id"]),
        RegisteredDevice.status == "ACTIVE"
    )
    res = await db.execute(stmt)
    device = res.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=400, detail="Invalid or unauthorized device.")
        
    # Verify WebAuthn Credential exists for this device
    stmt = select(WebAuthnCredential).where(
        WebAuthnCredential.credential_id == payload.passkey_credential_id,
        WebAuthnCredential.device_id == payload.device_id
    )
    res = await db.execute(stmt)
    cred = res.scalar_one_or_none()
    if not cred:
        raise HTTPException(status_code=400, detail="Passkey credential not linked to this device.")
        
    # Generate opaque token
    opaque_token = os.urandom(32).hex()
    token_hash = _hash_token(opaque_token)
    
    card = NFCCard(
        lawyer_id=uuid.UUID(user["id"]),
        token_hash=token_hash,
        status="ACTIVE"
    )
    db.add(card)
    
    audit = AuditLog(
        actor_user_id=uuid.UUID(user["id"]),
        actor_role=user["role"],
        action="NFC_ENROLLED",
        entity_type="NFC_CARD",
        entity_id=card.id,
        new_state={"status": "ACTIVE"}
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(card)
    
    return {
        "card_id": card.id,
        "opaque_token": opaque_token,
        "activation_url": f"https://app.example-domain.in/nfc/c/{opaque_token}"
    }

@router.post("/tap", response_model=NFCTapResponse)
async def tap_nfc_card(
    payload: NFCTapRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Tap NFC -> validate token -> determine linked lawyer -> verify card status -> 
    verify registered device -> request passkey -> authenticate.
    """
    token_hash = _hash_token(payload.opaque_token)
    
    stmt = select(NFCCard).where(NFCCard.token_hash == token_hash)
    res = await db.execute(stmt)
    card = res.scalar_one_or_none()
    
    if not card:
        raise HTTPException(status_code=401, detail="Unknown or invalid NFC card.")
        
    if card.status != "ACTIVE":
        raise HTTPException(status_code=403, detail="NFC Card is not active.")
        
    # Verify One Device Rule
    stmt = select(RegisteredDevice).where(
        RegisteredDevice.user_id == card.lawyer_id,
        RegisteredDevice.status == "ACTIVE"
    ).order_by(RegisteredDevice.created_at.desc())
    res = await db.execute(stmt)
    primary_device = res.scalars().first()
    
    if not primary_device or primary_device.id != payload.device_id:
        raise HTTPException(
            status_code=403, 
            detail="Unauthorized device detected. Please re-enrol or use your primary authorized device."
        )
        
    # Verify Passkey (Simulated WebAuthn Assertion)
    if not payload.passkey_assertion or payload.passkey_assertion == "INVALID":
        raise HTTPException(status_code=401, detail="WebAuthn assertion failed.")
        
    # Create Authenticated Session (Simulated JWT)
    card.last_used_at = datetime.utcnow()
    await db.commit()
    
    return {
        "access_token": "simulated_jwt_token_for_nfc_session",
        "lawyer_id": card.lawyer_id
    }

@router.put("/cards/{card_id}/status")
async def update_nfc_status(
    card_id: uuid.UUID,
    user: CurrentUser,
    payload: NFCCardStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Mark card: ACTIVE, LOST, REVOKED, REPLACED."""
    stmt = select(NFCCard).where(NFCCard.id == card_id)
    res = await db.execute(stmt)
    card = res.scalar_one_or_none()
    
    if not card:
        raise HTTPException(status_code=404, detail="Card not found.")
        
    if card.lawyer_id != uuid.UUID(user["id"]) and user["role"] != "COURT_AUTHORITY":
        raise HTTPException(status_code=403, detail="Not authorized to modify this card.")
        
    valid_statuses = ["ACTIVE", "LOST", "REVOKED", "REPLACED"]
    if payload.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status.")
        
    card.status = payload.status
    if payload.status in ["REVOKED", "LOST", "REPLACED"]:
        card.revoked_at = datetime.utcnow()
        
    audit = AuditLog(
        actor_user_id=uuid.UUID(user["id"]),
        actor_role=user["role"],
        action="NFC_STATUS_CHANGED",
        entity_type="NFC_CARD",
        entity_id=card.id,
        new_state={"status": payload.status}
    )
    db.add(audit)
        
    await db.commit()
    return {"status": card.status}

qr_router = APIRouter(prefix="/api/qr", tags=["qr"])

@qr_router.get("/case/{opaque_token}", response_model=CaseQRResolveResponse)
async def resolve_case_qr(
    opaque_token: str,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Scan -> case token resolver -> auth check -> role check -> case access check.
    Never unrestrained access.
    """
    token_hash = _hash_token(opaque_token)
    stmt = select(CaseQRToken).where(CaseQRToken.token_hash == token_hash)
    res = await db.execute(stmt)
    qr_record = res.scalar_one_or_none()
    
    if not qr_record or qr_record.status != "ACTIVE":
        raise HTTPException(status_code=404, detail="Invalid or inactive QR code.")
        
    # Access checks
    if user["role"] == "LAWYER":
        # Check active assignment
        stmt = select(LawyerAssignment).where(
            LawyerAssignment.lawyer_id == uuid.UUID(user["id"]),
            LawyerAssignment.case_id == qr_record.case_id,
            LawyerAssignment.status == "ACTIVE"
        )
        res = await db.execute(stmt)
        if not res.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized to access this case via QR.")
            
    # Allow Police and Court Authority unrestricted access to view the case if they have the valid QR
    stmt = select(Case).where(Case.id == qr_record.case_id)
    res = await db.execute(stmt)
    case_record = res.scalar_one_or_none()
    
    return {
        "case_id": case_record.id,
        "csr_number": case_record.csr_number,
        "status": case_record.case_status,
        "redirect_url": f"/cases/{case_record.id}"
    }
