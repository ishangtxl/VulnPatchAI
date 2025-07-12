"""
Export endpoints for CSV and other data formats
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
import io

from app.core.database import get_db
from app.services.export_service import ExportService
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/vulnerabilities/csv")
async def export_vulnerabilities_csv(
    response: Response,
    scan_id: Optional[int] = Query(None, description="Filter by specific scan ID"),
    severity: Optional[List[str]] = Query(None, description="Filter by severity (Critical, High, Medium, Low)"),
    status: Optional[List[str]] = Query(None, description="Filter by status (open, patched, ignored, false_positive)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export vulnerabilities to CSV format
    
    Filters:
    - scan_id: Specific scan ID
    - severity: List of severities to include
    - status: List of statuses to include
    """
    try:
        export_service = ExportService(db)
        
        # Only allow users to export their own data, admins can export all
        user_filter = None if current_user.role == "admin" else current_user.id
        
        csv_content = export_service.export_vulnerabilities_csv(
            user_id=user_filter,
            scan_id=scan_id,
            severity_filter=severity,
            status_filter=status
        )
        
        # Create filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"vulnerabilities_export_{timestamp}.csv"
        
        # Return CSV as streaming response
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting vulnerabilities: {str(e)}"
        )


@router.get("/scans/csv")
async def export_scans_csv(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export scans summary to CSV format"""
    try:
        export_service = ExportService(db)
        
        # Only allow users to export their own data, admins can export all
        user_filter = None if current_user.role == "admin" else current_user.id
        
        csv_content = export_service.export_scans_csv(user_id=user_filter)
        
        # Create filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"scans_export_{timestamp}.csv"
        
        # Return CSV as streaming response
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting scans: {str(e)}"
        )


@router.get("/audit-logs/csv")
async def export_audit_logs_csv(
    response: Response,
    days: int = Query(30, description="Number of days to include (max 365)"),
    action: Optional[List[str]] = Query(None, description="Filter by action types"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export audit logs to CSV format
    
    Parameters:
    - days: Number of days to include (default 30, max 365)
    - action: List of action types to filter
    """
    try:
        # Limit days to reasonable range
        if days > 365:
            days = 365
        
        export_service = ExportService(db)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Only allow users to export their own data, admins can export all
        user_filter = None if current_user.role == "admin" else current_user.id
        
        csv_content = export_service.export_audit_logs_csv(
            user_id=user_filter,
            start_date=start_date,
            end_date=end_date,
            action_filter=action
        )
        
        # Create filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"audit_logs_export_{timestamp}.csv"
        
        # Return CSV as streaming response
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting audit logs: {str(e)}"
        )


@router.get("/feedback/csv")
async def export_feedback_csv(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export feedback data to CSV format"""
    try:
        export_service = ExportService(db)
        
        # Only allow users to export their own data, admins can export all
        user_filter = None if current_user.role == "admin" else current_user.id
        
        csv_content = export_service.export_feedback_csv(user_id=user_filter)
        
        # Create filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"feedback_export_{timestamp}.csv"
        
        # Return CSV as streaming response
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting feedback: {str(e)}"
        )


@router.get("/dashboard/csv")
async def export_dashboard_summary_csv(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export dashboard summary data to CSV format"""
    try:
        export_service = ExportService(db)
        
        csv_content = export_service.export_dashboard_summary_csv(user_id=current_user.id)
        
        # Create filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"dashboard_summary_{timestamp}.csv"
        
        # Return CSV as streaming response
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting dashboard summary: {str(e)}"
        )


@router.get("/vulnerability-trends/csv")
async def export_vulnerability_trends_csv(
    response: Response,
    days: int = Query(30, description="Number of days for trend analysis (max 365)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export vulnerability trends over time to CSV format"""
    try:
        # Limit days to reasonable range
        if days > 365:
            days = 365
            
        export_service = ExportService(db)
        
        csv_content = export_service.export_vulnerability_trends_csv(
            user_id=current_user.id,
            days=days
        )
        
        # Create filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"vulnerability_trends_{days}days_{timestamp}.csv"
        
        # Return CSV as streaming response
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting vulnerability trends: {str(e)}"
        )


@router.get("/metadata/{export_type}")
async def get_export_metadata(
    export_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get metadata about available export data
    
    export_type: vulnerabilities, scans, audit_logs, feedback
    """
    try:
        valid_types = ["vulnerabilities", "scans", "audit_logs", "feedback"]
        
        if export_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid export type. Must be one of: {', '.join(valid_types)}"
            )
        
        export_service = ExportService(db)
        
        metadata = export_service.get_export_metadata(export_type, current_user.id)
        
        return {
            "metadata": metadata,
            "available_exports": [
                {
                    "type": "vulnerabilities",
                    "endpoint": "/api/v1/export/vulnerabilities/csv",
                    "description": "Export vulnerability data with optional filters",
                    "filters": ["scan_id", "severity", "status"]
                },
                {
                    "type": "scans",
                    "endpoint": "/api/v1/export/scans/csv",
                    "description": "Export scan summary data",
                    "filters": []
                },
                {
                    "type": "audit_logs",
                    "endpoint": "/api/v1/export/audit-logs/csv",
                    "description": "Export audit log data",
                    "filters": ["days", "action"]
                },
                {
                    "type": "feedback",
                    "endpoint": "/api/v1/export/feedback/csv",
                    "description": "Export feedback data",
                    "filters": []
                },
                {
                    "type": "dashboard_summary",
                    "endpoint": "/api/v1/export/dashboard/csv",
                    "description": "Export comprehensive dashboard summary",
                    "filters": []
                },
                {
                    "type": "vulnerability_trends",
                    "endpoint": "/api/v1/export/vulnerability-trends/csv",
                    "description": "Export vulnerability trends over time",
                    "filters": ["days"]
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving export metadata: {str(e)}"
        )


@router.post("/generate")
async def generate_bulk_export(
    export_types: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate bulk export for multiple data types
    Returns download URLs for each export type
    """
    try:
        valid_types = ["vulnerabilities", "scans", "audit_logs", "feedback", "dashboard_summary"]
        
        # Validate export types
        invalid_types = [t for t in export_types if t not in valid_types]
        if invalid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid export types: {', '.join(invalid_types)}"
            )
        
        # Generate timestamp for this export session
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Create download URLs for each export type
        export_urls = []
        base_url = "/api/v1/export"
        
        for export_type in export_types:
            if export_type == "vulnerabilities":
                url = f"{base_url}/vulnerabilities/csv"
            elif export_type == "scans":
                url = f"{base_url}/scans/csv"
            elif export_type == "audit_logs":
                url = f"{base_url}/audit-logs/csv"
            elif export_type == "feedback":
                url = f"{base_url}/feedback/csv"
            elif export_type == "dashboard_summary":
                url = f"{base_url}/dashboard/csv"
            
            export_urls.append({
                "type": export_type,
                "download_url": url,
                "filename": f"{export_type}_export_{timestamp}.csv"
            })
        
        return {
            "status": "success",
            "message": f"Bulk export prepared for {len(export_types)} data types",
            "export_session": timestamp,
            "exports": export_urls,
            "instructions": "Use the download_url for each export to download the CSV files"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating bulk export: {str(e)}"
        )


@router.get("/health")
async def export_service_health():
    """Export service health check"""
    return {
        "status": "healthy",
        "service": "Export Service",
        "version": "1.0.0",
        "features": {
            "csv_export": True,
            "bulk_export": True,
            "filtered_export": True,
            "metadata_support": True
        },
        "supported_formats": ["CSV"],
        "supported_data_types": [
            "vulnerabilities",
            "scans", 
            "audit_logs",
            "feedback",
            "dashboard_summary",
            "vulnerability_trends"
        ]
    }