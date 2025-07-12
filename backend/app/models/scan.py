"""
Scan model
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String)
    file_size = Column(Integer)
    status = Column(String, default="processing")  # processing, completed, failed
    raw_data = Column(Text)  # Original XML content
    parsed_data = Column(JSON)  # Parsed JSON data
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="scans")
    vulnerabilities = relationship("Vulnerability", back_populates="scan")
    reports = relationship("Report", back_populates="scan")
    feedback = relationship("Feedback", back_populates="scan")