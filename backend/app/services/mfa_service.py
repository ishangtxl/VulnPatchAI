"""
Multi-Factor Authentication service using TOTP
"""
import pyotp
import qrcode
import json
import secrets
import logging
from io import BytesIO
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session

from app.models.user import User

logger = logging.getLogger(__name__)


class MFAService:
    """Service for handling Multi-Factor Authentication operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_secret_key(self) -> str:
        """Generate a random secret key for TOTP"""
        return pyotp.random_base32()
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for MFA recovery"""
        codes = []
        for _ in range(count):
            # Generate 8-character backup codes
            code = secrets.token_hex(4).upper()
            codes.append(f"{code[:4]}-{code[4:]}")
        return codes
    
    def setup_mfa(self, user: User, app_name: str = "VulnPatch AI") -> Tuple[str, str, List[str]]:
        """
        Setup MFA for a user
        Returns: (secret_key, qr_code_url, backup_codes)
        """
        try:
            # Generate secret key
            secret_key = self.generate_secret_key()
            
            # Generate backup codes
            backup_codes = self.generate_backup_codes()
            
            # Create TOTP instance
            totp = pyotp.TOTP(secret_key)
            
            # Generate QR code URL
            qr_url = totp.provisioning_uri(
                name=user.email,
                issuer_name=app_name
            )
            
            # Store secret and backup codes in user record (not yet enabled)
            user.mfa_secret = secret_key
            user.mfa_backup_codes = json.dumps(backup_codes)
            user.mfa_enabled = False  # Will be enabled after verification
            
            self.db.commit()
            
            logger.info(f"MFA setup initiated for user {user.email}")
            return secret_key, qr_url, backup_codes
            
        except Exception as e:
            logger.error(f"Error setting up MFA for user {user.email}: {e}")
            self.db.rollback()
            raise
    
    def generate_qr_code_image(self, qr_url: str) -> bytes:
        """Generate QR code image as bytes"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to bytes
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes.getvalue()
            
        except Exception as e:
            logger.error(f"Error generating QR code image: {e}")
            raise
    
    def verify_totp_code(self, user: User, code: str) -> bool:
        """Verify TOTP code for a user"""
        try:
            if not user.mfa_secret:
                return False
            
            # Remove spaces and convert to uppercase
            code = code.replace(" ", "").strip()
            
            # Create TOTP instance
            totp = pyotp.TOTP(user.mfa_secret)
            
            # Verify code with some tolerance for time drift
            return totp.verify(code, valid_window=1)
            
        except Exception as e:
            logger.error(f"Error verifying TOTP code for user {user.email}: {e}")
            return False
    
    def verify_backup_code(self, user: User, code: str) -> bool:
        """Verify and consume a backup code"""
        try:
            if not user.mfa_backup_codes:
                return False
            
            # Parse backup codes
            backup_codes = json.loads(user.mfa_backup_codes)
            
            # Format input code
            code = code.replace(" ", "").upper()
            if len(code) == 8 and "-" not in code:
                code = f"{code[:4]}-{code[4:]}"
            
            # Check if code exists
            if code in backup_codes:
                # Remove used code
                backup_codes.remove(code)
                user.mfa_backup_codes = json.dumps(backup_codes)
                self.db.commit()
                
                logger.info(f"Backup code used for user {user.email}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying backup code for user {user.email}: {e}")
            return False
    
    def enable_mfa(self, user: User) -> bool:
        """Enable MFA for a user (after successful verification)"""
        try:
            if not user.mfa_secret:
                return False
            
            user.mfa_enabled = True
            self.db.commit()
            
            logger.info(f"MFA enabled for user {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enabling MFA for user {user.email}: {e}")
            self.db.rollback()
            return False
    
    def disable_mfa(self, user: User) -> bool:
        """Disable MFA for a user"""
        try:
            user.mfa_enabled = False
            user.mfa_secret = None
            user.mfa_backup_codes = None
            self.db.commit()
            
            logger.info(f"MFA disabled for user {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error disabling MFA for user {user.email}: {e}")
            self.db.rollback()
            return False
    
    def regenerate_backup_codes(self, user: User) -> List[str]:
        """Regenerate backup codes for a user"""
        try:
            if not user.mfa_enabled:
                raise ValueError("MFA is not enabled for this user")
            
            backup_codes = self.generate_backup_codes()
            user.mfa_backup_codes = json.dumps(backup_codes)
            self.db.commit()
            
            logger.info(f"Backup codes regenerated for user {user.email}")
            return backup_codes
            
        except Exception as e:
            logger.error(f"Error regenerating backup codes for user {user.email}: {e}")
            self.db.rollback()
            raise
    
    def get_mfa_status(self, user: User) -> dict:
        """Get MFA status for a user"""
        try:
            backup_codes_count = 0
            if user.mfa_backup_codes:
                backup_codes = json.loads(user.mfa_backup_codes)
                backup_codes_count = len(backup_codes)
            
            # Handle None values for new MFA fields
            mfa_enabled = user.mfa_enabled if user.mfa_enabled is not None else False
            mfa_secret = user.mfa_secret if user.mfa_secret is not None else ""
            
            return {
                "enabled": mfa_enabled,
                "secret_configured": bool(mfa_secret),
                "backup_codes_remaining": backup_codes_count,
                "setup_required": bool(mfa_secret and not mfa_enabled)
            }
            
        except Exception as e:
            logger.error(f"Error getting MFA status for user {user.email}: {e}")
            return {
                "enabled": False,
                "secret_configured": False,
                "backup_codes_remaining": 0,
                "setup_required": False
            }