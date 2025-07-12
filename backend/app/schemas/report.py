"""
Report schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReportBase(BaseModel):
    scan_id: int
    report_type: str  # executive, technical
    format: str = "html"  # html, pdf, json


class ReportCreate(ReportBase):
    pass


class ReportList(BaseModel):
    id: int
    scan_id: int
    report_type: str
    title: Optional[str] = None
    format: str
    generated_at: datetime
    
    class Config:
        from_attributes = True


class ReportResponse(ReportBase):
    id: int
    user_id: int
    title: Optional[str] = None
    content: Optional[str] = None
    file_path: Optional[str] = None
    generated_at: datetime
    
    class Config:
        from_attributes = True