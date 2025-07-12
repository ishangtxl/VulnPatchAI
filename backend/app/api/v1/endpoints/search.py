"""
Advanced search and filtering endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from app.core.database import get_db
from app.services.search_service import SearchService
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()


class SearchFilters(BaseModel):
    severity: Optional[List[str]] = None
    service_name: Optional[List[str]] = None
    cvss_score_min: Optional[float] = None
    cvss_score_max: Optional[float] = None
    port: Optional[List[int]] = None
    has_cve: Optional[bool] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    action: Optional[List[str]] = None
    resource_type: Optional[List[str]] = None
    has_vulnerabilities: Optional[bool] = None
    vulnerability_count_min: Optional[int] = None
    target_host: Optional[str] = None
    ip_address: Optional[str] = None


class SearchRequest(BaseModel):
    query: Optional[str] = None
    filters: Optional[SearchFilters] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 20


@router.post("/vulnerabilities")
async def search_vulnerabilities(
    search_request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Advanced vulnerability search with filters and pagination"""
    search_service = SearchService(db)
    
    try:
        filters_dict = search_request.filters.dict() if search_request.filters else None
        
        results = search_service.search_vulnerabilities(
            user_id=current_user.id,
            query=search_request.query,
            filters=filters_dict,
            sort_by=search_request.sort_by,
            sort_order=search_request.sort_order,
            page=search_request.page,
            page_size=search_request.page_size
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching vulnerabilities: {str(e)}"
        )


@router.post("/scans")
async def search_scans(
    search_request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Advanced scan search with filters and pagination"""
    search_service = SearchService(db)
    
    try:
        filters_dict = search_request.filters.dict() if search_request.filters else None
        
        results = search_service.search_scans(
            user_id=current_user.id,
            query=search_request.query,
            filters=filters_dict,
            sort_by=search_request.sort_by,
            sort_order=search_request.sort_order,
            page=search_request.page,
            page_size=search_request.page_size
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching scans: {str(e)}"
        )


@router.post("/audit-logs")
async def search_audit_logs(
    search_request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Advanced audit log search with filters and pagination"""
    search_service = SearchService(db)
    
    try:
        filters_dict = search_request.filters.dict() if search_request.filters else None
        
        results = search_service.search_audit_logs(
            user_id=current_user.id,
            query=search_request.query,
            filters=filters_dict,
            sort_by=search_request.sort_by,
            sort_order=search_request.sort_order,
            page=search_request.page,
            page_size=search_request.page_size
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching audit logs: {str(e)}"
        )


@router.get("/global")
async def global_search(
    q: str = Query(..., description="Search query"),
    categories: Optional[List[str]] = Query(default=None, description="Categories to search in"),
    limit: int = Query(default=10, le=50, description="Max results per category"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Global search across all categories"""
    search_service = SearchService(db)
    
    try:
        results = search_service.global_search(
            user_id=current_user.id,
            query=q,
            categories=categories,
            limit=limit
        )
        
        return {
            "query": q,
            "categories_searched": categories or ["vulnerabilities", "scans", "audit_logs", "reports"],
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing global search: {str(e)}"
        )


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., description="Partial search query"),
    category: str = Query(default="vulnerabilities", description="Category for suggestions"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get search suggestions for autocomplete"""
    search_service = SearchService(db)
    
    try:
        suggestions = search_service.get_search_suggestions(
            user_id=current_user.id,
            query=q,
            category=category
        )
        
        return {
            "query": q,
            "category": category,
            "suggestions": suggestions
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting search suggestions: {str(e)}"
        )


@router.get("/filter-options/{category}")
async def get_filter_options(
    category: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available filter options for a category"""
    search_service = SearchService(db)
    
    try:
        options = search_service.get_filter_options(
            user_id=current_user.id,
            category=category
        )
        
        return {
            "category": category,
            "filter_options": options
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting filter options: {str(e)}"
        )


@router.get("/vulnerabilities/quick")
async def quick_vulnerability_search(
    q: Optional[str] = Query(default=None, description="Search query"),
    severity: Optional[str] = Query(default=None, description="Filter by severity"),
    service: Optional[str] = Query(default=None, description="Filter by service"),
    limit: int = Query(default=20, le=100, description="Max results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Quick vulnerability search with basic filters"""
    search_service = SearchService(db)
    
    try:
        filters = {}
        if severity:
            filters["severity"] = [severity]
        if service:
            filters["service_name"] = [service]
        
        results = search_service.search_vulnerabilities(
            user_id=current_user.id,
            query=q,
            filters=filters if filters else None,
            page_size=limit
        )
        
        return {
            "query": q,
            "filters": {"severity": severity, "service": service},
            "results": results["results"],
            "total_count": results["pagination"]["total_count"],
            "aggregations": results["aggregations"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing quick search: {str(e)}"
        )


@router.get("/scans/quick")
async def quick_scan_search(
    q: Optional[str] = Query(default=None, description="Search query"),
    has_vulnerabilities: Optional[bool] = Query(default=None, description="Filter by vulnerability presence"),
    days: Optional[int] = Query(default=None, description="Filter by days ago"),
    limit: int = Query(default=20, le=100, description="Max results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Quick scan search with basic filters"""
    search_service = SearchService(db)
    
    try:
        filters = {}
        if has_vulnerabilities is not None:
            filters["has_vulnerabilities"] = has_vulnerabilities
        if days:
            from datetime import datetime, timedelta
            date_from = (datetime.utcnow() - timedelta(days=days)).isoformat()
            filters["date_from"] = date_from
        
        results = search_service.search_scans(
            user_id=current_user.id,
            query=q,
            filters=filters if filters else None,
            page_size=limit
        )
        
        return {
            "query": q,
            "filters": {"has_vulnerabilities": has_vulnerabilities, "days": days},
            "results": results["results"],
            "total_count": results["pagination"]["total_count"],
            "aggregations": results["aggregations"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing quick scan search: {str(e)}"
        )


@router.get("/advanced-filters")
async def get_advanced_filter_schema():
    """Get the schema for advanced filtering"""
    return {
        "vulnerability_filters": {
            "severity": {
                "type": "array",
                "items": {"type": "string", "enum": ["Critical", "High", "Medium", "Low"]},
                "description": "Filter by vulnerability severity levels"
            },
            "service_name": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by service names"
            },
            "cvss_score_min": {
                "type": "number",
                "minimum": 0,
                "maximum": 10,
                "description": "Minimum CVSS score"
            },
            "cvss_score_max": {
                "type": "number",
                "minimum": 0,
                "maximum": 10,
                "description": "Maximum CVSS score"
            },
            "port": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Filter by port numbers"
            },
            "has_cve": {
                "type": "boolean",
                "description": "Filter by CVE presence"
            },
            "date_from": {
                "type": "string",
                "format": "date-time",
                "description": "Filter from date (ISO format)"
            },
            "date_to": {
                "type": "string",
                "format": "date-time",
                "description": "Filter to date (ISO format)"
            }
        },
        "scan_filters": {
            "has_vulnerabilities": {
                "type": "boolean",
                "description": "Filter by vulnerability presence"
            },
            "vulnerability_count_min": {
                "type": "integer",
                "minimum": 0,
                "description": "Minimum vulnerability count"
            },
            "target_host": {
                "type": "string",
                "description": "Filter by target host"
            },
            "date_from": {
                "type": "string",
                "format": "date-time",
                "description": "Filter from date (ISO format)"
            },
            "date_to": {
                "type": "string",
                "format": "date-time",
                "description": "Filter to date (ISO format)"
            }
        },
        "audit_log_filters": {
            "action": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by action types"
            },
            "resource_type": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by resource types"
            },
            "ip_address": {
                "type": "string",
                "description": "Filter by IP address"
            },
            "date_from": {
                "type": "string",
                "format": "date-time",
                "description": "Filter from date (ISO format)"
            },
            "date_to": {
                "type": "string",
                "format": "date-time",
                "description": "Filter to date (ISO format)"
            }
        },
        "sort_options": {
            "vulnerability_sort": ["created_at", "severity", "cvss_score", "service_name", "port"],
            "scan_sort": ["upload_time", "filename", "target_host"],
            "audit_log_sort": ["timestamp", "action", "resource_type"]
        },
        "sort_orders": ["asc", "desc"]
    }


@router.get("/stats")
async def get_search_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get search statistics and metrics"""
    search_service = SearchService(db)
    
    try:
        # Get basic counts
        vuln_results = search_service.search_vulnerabilities(
            user_id=current_user.id,
            page_size=1
        )
        
        scan_results = search_service.search_scans(
            user_id=current_user.id,
            page_size=1
        )
        
        audit_results = search_service.search_audit_logs(
            user_id=current_user.id,
            page_size=1
        )
        
        return {
            "total_vulnerabilities": vuln_results["pagination"]["total_count"],
            "total_scans": scan_results["pagination"]["total_count"],
            "total_audit_logs": audit_results["pagination"]["total_count"],
            "vulnerability_aggregations": vuln_results["aggregations"],
            "scan_aggregations": scan_results["aggregations"],
            "audit_log_aggregations": audit_results["aggregations"],
            "search_capabilities": {
                "full_text_search": True,
                "advanced_filtering": True,
                "sorting": True,
                "pagination": True,
                "aggregations": True,
                "suggestions": True,
                "global_search": True
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting search stats: {str(e)}"
        )