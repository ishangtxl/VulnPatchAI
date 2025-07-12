"""
Multi-Factor Authentication endpoints
"""
import base64
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from app.core.database import get_db
from app.services.mfa_service import MFAService
from app.services.auth_service import AuthService
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.mfa import (
    MFASetupResponse, 
    MFAVerifyRequest, 
    MFAStatusResponse,
    MFADisableRequest,
    BackupCodesResponse,
    QRCodeResponse
)

router = APIRouter()


@router.get("/status", response_model=MFAStatusResponse)
async def get_mfa_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get MFA status for current user"""
    mfa_service = MFAService(db)
    status_info = mfa_service.get_mfa_status(current_user)
    
    return MFAStatusResponse(**status_info)


@router.post("/setup", response_model=MFASetupResponse)
async def setup_mfa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initialize MFA setup for current user"""
    try:
        # Check if MFA is already enabled
        if current_user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is already enabled. Disable it first to reconfigure."
            )
        
        mfa_service = MFAService(db)
        secret_key, qr_url, backup_codes = mfa_service.setup_mfa(current_user)
        
        return MFASetupResponse(
            secret_key=secret_key,
            qr_code_url=qr_url,
            backup_codes=backup_codes
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting up MFA: {str(e)}"
        )


@router.get("/qr-code")
async def get_qr_code_image(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get QR code image for MFA setup"""
    try:
        if not current_user.mfa_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA setup not initiated. Call /setup first."
            )
        
        mfa_service = MFAService(db)
        
        # Recreate QR URL
        import pyotp
        totp = pyotp.TOTP(current_user.mfa_secret)
        qr_url = totp.provisioning_uri(
            name=current_user.email,
            issuer_name="VulnPatch AI"
        )
        
        # Generate QR code image
        qr_image_bytes = mfa_service.generate_qr_code_image(qr_url)
        
        # Return as image response
        return StreamingResponse(
            BytesIO(qr_image_bytes),
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=mfa_qr_code.png"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating QR code: {str(e)}"
        )


@router.get("/qr-code/base64", response_model=QRCodeResponse)
async def get_qr_code_base64(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get QR code as base64 encoded image"""
    try:
        if not current_user.mfa_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA setup not initiated. Call /setup first."
            )
        
        mfa_service = MFAService(db)
        
        # Recreate QR URL
        import pyotp
        totp = pyotp.TOTP(current_user.mfa_secret)
        qr_url = totp.provisioning_uri(
            name=current_user.email,
            issuer_name="VulnPatch AI"
        )
        
        # Generate QR code image
        qr_image_bytes = mfa_service.generate_qr_code_image(qr_url)
        
        # Encode as base64
        qr_base64 = base64.b64encode(qr_image_bytes).decode('utf-8')
        
        return QRCodeResponse(qr_code_data=qr_base64)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating QR code: {str(e)}"
        )


@router.post("/verify")
async def verify_mfa_setup(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify MFA setup with TOTP code"""
    try:
        if current_user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is already enabled"
            )
        
        if not current_user.mfa_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA setup not initiated. Call /setup first."
            )
        
        mfa_service = MFAService(db)
        
        # Verify the TOTP code
        if not mfa_service.verify_totp_code(current_user, request.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid MFA code"
            )
        
        # Enable MFA
        if not mfa_service.enable_mfa(current_user):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error enabling MFA"
            )
        
        return {
            "message": "MFA enabled successfully",
            "status": "enabled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying MFA: {str(e)}"
        )


@router.post("/disable")
async def disable_mfa(
    request: MFADisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disable MFA for current user"""
    try:
        # Verify password
        auth_service = AuthService(db)
        if not auth_service.verify_password(request.password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password"
            )
        
        mfa_service = MFAService(db)
        
        # If MFA is enabled, require MFA code
        if current_user.mfa_enabled:
            if not request.code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="MFA code required to disable MFA"
                )
            
            # Verify MFA code
            if not (mfa_service.verify_totp_code(current_user, request.code) or 
                   mfa_service.verify_backup_code(current_user, request.code)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid MFA code"
                )
        
        # Disable MFA
        if not mfa_service.disable_mfa(current_user):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error disabling MFA"
            )
        
        return {
            "message": "MFA disabled successfully",
            "status": "disabled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error disabling MFA: {str(e)}"
        )


@router.post("/backup-codes/regenerate", response_model=BackupCodesResponse)
async def regenerate_backup_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate backup codes for current user"""
    try:
        if not current_user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is not enabled"
            )
        
        mfa_service = MFAService(db)
        backup_codes = mfa_service.regenerate_backup_codes(current_user)
        
        return BackupCodesResponse(backup_codes=backup_codes)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error regenerating backup codes: {str(e)}"
        )


@router.post("/test")
async def test_mfa_code(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test MFA code without any side effects"""
    try:
        if not current_user.mfa_enabled and not current_user.mfa_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is not configured"
            )
        
        mfa_service = MFAService(db)
        
        # Check if it's a TOTP code
        is_totp_valid = mfa_service.verify_totp_code(current_user, request.code)
        
        # Check if it's a backup code (without consuming it)
        is_backup_code = False
        if current_user.mfa_backup_codes:
            import json
            backup_codes = json.loads(current_user.mfa_backup_codes)
            code = request.code.replace(" ", "").upper()
            if len(code) == 8 and "-" not in code:
                code = f"{code[:4]}-{code[4:]}"
            is_backup_code = code in backup_codes
        
        return {
            "valid": is_totp_valid or is_backup_code,
            "code_type": "totp" if is_totp_valid else ("backup" if is_backup_code else "invalid"),
            "message": "Code is valid" if (is_totp_valid or is_backup_code) else "Invalid code"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing MFA code: {str(e)}"
        )


@router.get("/health")
async def mfa_service_health():
    """MFA service health check"""
    return {
        "status": "healthy",
        "service": "MFA Service",
        "version": "1.0.0",
        "features": {
            "totp_authentication": True,
            "backup_codes": True,
            "qr_code_generation": True,
            "setup_verification": True
        },
        "supported_authenticators": [
            "Google Authenticator",
            "Microsoft Authenticator", 
            "Authy",
            "1Password",
            "Any TOTP-compatible app"
        ]
    }