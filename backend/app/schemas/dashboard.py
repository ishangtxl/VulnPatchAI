"""
Dashboard schemas
"""
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime


class VulnerabilitySummary(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    total: int = 0


class DashboardMetrics(BaseModel):
    total_scans: int
    vulnerabilities: VulnerabilitySummary
    patch_completion_rate: float
    recent_scans: int
    avg_cvss_score: float


class TrendPoint(BaseModel):
    date: str
    value: int


class TrendData(BaseModel):
    vulnerability_trends: List[TrendPoint]
    scan_trends: List[TrendPoint]
    severity_distribution: Dict[str, int]