"""
MFA (Multi-Factor Authentication) schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class MFASetupResponse(BaseModel):
    """Response for MFA setup initiation"""
    secret_key: str = Field(..., description="TOTP secret key")
    qr_code_url: str = Field(..., description="QR code URL for authenticator apps")
    backup_codes: List[str] = Field(..., description="Backup codes for recovery")
    instructions: str = Field(default="Scan the QR code with your authenticator app, then verify with a TOTP code")


class MFAVerifyRequest(BaseModel):
    """Request to verify MFA code"""
    code: str = Field(..., description="6-digit TOTP code or backup code", min_length=6, max_length=10)


class MFAStatusResponse(BaseModel):
    """MFA status response"""
    enabled: bool = Field(..., description="Whether MFA is enabled")
    secret_configured: bool = Field(..., description="Whether secret key is configured")
    backup_codes_remaining: int = Field(..., description="Number of backup codes remaining")
    setup_required: bool = Field(..., description="Whether setup verification is required")


class MFADisableRequest(BaseModel):
    """Request to disable MFA"""
    password: str = Field(..., description="Current password for verification")
    code: Optional[str] = Field(None, description="TOTP code or backup code (if MFA is enabled)")


class BackupCodesResponse(BaseModel):
    """Response with new backup codes"""
    backup_codes: List[str] = Field(..., description="New backup codes")
    message: str = Field(default="New backup codes generated. Store these securely!")


class MFALoginRequest(BaseModel):
    """Request for MFA verification during login"""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")
    mfa_code: Optional[str] = Field(None, description="MFA code (required if MFA is enabled)")


class MFALoginResponse(BaseModel):
    """Response for MFA login"""
    access_token: Optional[str] = Field(None, description="JWT access token")
    token_type: str = Field(default="bearer")
    mfa_required: bool = Field(default=False, description="Whether MFA code is required")
    message: str = Field(..., description="Status message")


class QRCodeResponse(BaseModel):
    """Response containing QR code image"""
    qr_code_data: str = Field(..., description="Base64 encoded QR code image")
    format: str = Field(default="PNG", description="Image format")