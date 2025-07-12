"""
Enhanced Feedback model for AI analysis and vulnerability feedback
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Support both vulnerability-specific and analysis-level feedback
    vulnerability_id = Column(Integer, ForeignKey("vulnerabilities.id"), nullable=True)
    analysis_id = Column(Integer, nullable=True)  # For AI analysis feedback
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=True)
    
    # Feedback details
    rating = Column(Integer)  # 1-5 rating
    comment = Column(Text)
    is_helpful = Column(Boolean, default=True)
    feedback_type = Column(String, default="general")  # vulnerability, analysis, recommendation, query
    
    # AI-specific feedback fields
    analysis_type = Column(String)  # comprehensive, business_impact, patch_prioritization
    conversation_id = Column(String)  # For query feedback
    
    # Structured feedback data
    feedback_data = Column(JSON)  # Additional structured feedback
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    vulnerability = relationship("Vulnerability", back_populates="feedback")
    user = relationship("User", back_populates="feedback")
    scan = relationship("Scan", back_populates="feedback")