"""
Enhanced AI service schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    conversation_id: Optional[str] = None


class QueryResponse(BaseModel):
    query: str
    response: str
    conversation_id: Optional[str] = None
    timestamp: Optional[datetime] = None


class AnalysisRequest(BaseModel):
    scan_id: int
    analysis_type: Optional[str] = Field(default="comprehensive", description="Type of analysis: comprehensive, business_impact, patch_prioritization, basic")


class AnalysisResponse(BaseModel):
    scan_id: int
    summary: str
    key_findings: List[str]
    recommendations: List[str]
    risk_score: float
    generated_at: datetime
    analysis_type: Optional[str] = Field(default="basic", description="Type of analysis performed")
    ai_insights: Optional[List[Dict[str, Any]]] = Field(default=None, description="AI-generated insights and analysis")
    patch_matrix: Optional[Dict[str, List[Dict]]] = Field(default=None, description="Patch prioritization matrix")
    confidence_score: Optional[float] = Field(default=None, description="AI confidence in the analysis")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FeedbackRequest(BaseModel):
    analysis_id: int
    rating: int = Field(ge=1, le=5, description="Rating from 1-5")
    comment: Optional[str] = None
    is_helpful: bool = True


class FeedbackResponse(BaseModel):
    feedback_id: int
    message: str
    created_at: datetime


class VulnerabilityInsight(BaseModel):
    """Enhanced vulnerability insight from AI analysis"""
    vulnerability_id: int
    severity_assessment: str
    business_impact: str
    technical_details: str
    patch_recommendation: str
    compliance_implications: List[str]
    estimated_effort: str
    confidence_level: float = Field(ge=0, le=1, description="AI confidence in this assessment")


class BusinessRiskAssessment(BaseModel):
    """Business risk assessment model"""
    overall_risk_level: str
    financial_impact_estimate: str
    operational_risk_factors: List[str]
    regulatory_compliance_status: Dict[str, str]
    recommended_business_actions: List[str]
    executive_summary: str


class PatchPrioritization(BaseModel):
    """Patch prioritization model"""
    immediate_patches: List[Dict[str, Any]]
    high_priority_patches: List[Dict[str, Any]]
    medium_priority_patches: List[Dict[str, Any]]
    low_priority_patches: List[Dict[str, Any]]
    deployment_timeline: Dict[str, str]
    resource_requirements: Dict[str, Any]