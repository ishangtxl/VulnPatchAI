"""
User model
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="user")  # user, admin, analyst
    is_active = Column(Boolean, default=True)
    
    # Multi-Factor Authentication
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String, nullable=True)  # TOTP secret key
    mfa_backup_codes = Column(String, nullable=True)  # JSON array of backup codes
    
    # User Preferences
    theme_preference = Column(String, default="light")  # light, dark, auto
    language_preference = Column(String, default="en")  # en, es, fr, de, etc.
    timezone_preference = Column(String, default="UTC")  # User timezone
    dashboard_layout = Column(String, nullable=True)  # JSON dashboard configuration
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    scans = relationship("Scan", back_populates="user")
    reports = relationship("Report", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")