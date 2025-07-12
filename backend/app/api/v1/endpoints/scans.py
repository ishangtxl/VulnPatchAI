"""
Scan management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
import os
import uuid

from app.core.database import get_db
from app.core.config import settings
from app.services.scan_service import ScanService
from app.services.auth_service import AuthService
from app.schemas.scan import ScanResponse, ScanCreate, ScanList
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/upload", response_model=ScanResponse)
async def upload_scan(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process Nmap XML scan file"""
    
    # Validate file type
    if not file.filename.endswith('.xml'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only XML files are allowed"
        )
    
    # Validate file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        )
    
    try:
        # Read file content
        content = await file.read()
        xml_content = content.decode('utf-8')
        
        # Create scan service
        scan_service = ScanService(db)
        
        # Process the scan
        scan = await scan_service.create_scan(
            user_id=current_user.id,
            filename=file.filename,
            xml_content=xml_content,
            file_size=len(content)
        )
        
        return scan
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file encoding. Please ensure the file is UTF-8 encoded."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.get("/history", response_model=List[ScanList])
async def get_scan_history(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get scan history for current user"""
    scan_service = ScanService(db)
    scans = scan_service.get_user_scans(current_user.id, skip=skip, limit=limit)
    return scans


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific scan details"""
    scan_service = ScanService(db)
    scan = scan_service.get_scan(scan_id)
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    # Check if user owns the scan or is admin
    if scan.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this scan"
        )
    
    return scan


@router.delete("/{scan_id}")
async def delete_scan(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a scan"""
    scan_service = ScanService(db)
    scan = scan_service.get_scan(scan_id)
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    # Check if user owns the scan or is admin
    if scan.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this scan"
        )
    
    try:
        scan_service.delete_scan(scan_id)
        return {"message": "Scan deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete scan: {str(e)}"
        )