"""
Vulnerability management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.services.vulnerability_service import VulnerabilityService
from app.schemas.vulnerability import VulnerabilityResponse, VulnerabilityUpdate, FeedbackCreate
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[VulnerabilityResponse])
async def get_vulnerabilities(
    scan_id: Optional[int] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get vulnerabilities with optional filters"""
    vuln_service = VulnerabilityService(db)
    
    vulnerabilities = vuln_service.get_vulnerabilities(
        user_id=current_user.id,
        scan_id=scan_id,
        severity=severity,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return vulnerabilities


@router.get("/{vuln_id}", response_model=VulnerabilityResponse)
async def get_vulnerability(
    vuln_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific vulnerability details"""
    vuln_service = VulnerabilityService(db)
    vulnerability = vuln_service.get_vulnerability(vuln_id)
    
    if not vulnerability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vulnerability not found"
        )
    
    # Check if user has access to this vulnerability
    if not vuln_service.user_has_access(vulnerability, current_user.id, current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this vulnerability"
        )
    
    return vulnerability


@router.patch("/{vuln_id}/status")
async def update_vulnerability_status(
    vuln_id: int,
    update_data: VulnerabilityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update vulnerability status"""
    vuln_service = VulnerabilityService(db)
    vulnerability = vuln_service.get_vulnerability(vuln_id)
    
    if not vulnerability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vulnerability not found"
        )
    
    # Check if user has access to this vulnerability
    if not vuln_service.user_has_access(vulnerability, current_user.id, current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this vulnerability"
        )
    
    updated_vuln = vuln_service.update_vulnerability(vuln_id, update_data)
    return updated_vuln


@router.post("/{vuln_id}/feedback")
async def add_feedback(
    vuln_id: int,
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add feedback for a vulnerability"""
    vuln_service = VulnerabilityService(db)
    vulnerability = vuln_service.get_vulnerability(vuln_id)
    
    if not vulnerability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vulnerability not found"
        )
    
    # Check if user has access to this vulnerability
    if not vuln_service.user_has_access(vulnerability, current_user.id, current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to provide feedback for this vulnerability"
        )
    
    feedback = vuln_service.add_feedback(vuln_id, current_user.id, feedback_data)
    return {"message": "Feedback added successfully", "feedback_id": feedback.id}


@router.delete("/{vuln_id}")
async def delete_vulnerability(
    vuln_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a vulnerability"""
    vuln_service = VulnerabilityService(db)
    vulnerability = vuln_service.get_vulnerability(vuln_id)
    
    if not vulnerability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vulnerability not found"
        )
    
    # Check if user has access to this vulnerability
    if not vuln_service.user_has_access(vulnerability, current_user.id, current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this vulnerability"
        )
    
    vuln_service.delete_vulnerability(vuln_id)
    return {"message": "Vulnerability deleted successfully"}


@router.post("/{vuln_id}/refresh-cve")
async def refresh_cve_data(
    vuln_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh CVE data for a vulnerability"""
    vuln_service = VulnerabilityService(db)
    vulnerability = vuln_service.get_vulnerability(vuln_id)
    
    if not vulnerability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vulnerability not found"
        )
    
    # Check if user has access to this vulnerability
    if not vuln_service.user_has_access(vulnerability, current_user.id, current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to refresh CVE data for this vulnerability"
        )
    
    updated_vuln = await vuln_service.refresh_cve_data(vuln_id)
    return updated_vuln