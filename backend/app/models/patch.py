"""
Patch model
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Patch(Base):
    __tablename__ = "patches"
    
    id = Column(Integer, primary_key=True, index=True)
    vulnerability_id = Column(Integer, ForeignKey("vulnerabilities.id"), nullable=False)
    status = Column(String, default="pending")  # pending, applied, failed, scheduled
    patch_details = Column(Text)
    applied_at = Column(DateTime(timezone=True))
    applied_by = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    vulnerability = relationship("Vulnerability", back_populates="patches")
    applied_by_user = relationship("User")