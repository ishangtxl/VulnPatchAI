"""
Advanced Dashboard endpoints with enhanced widgets and drill-down capabilities
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.services.advanced_dashboard_service import AdvancedDashboardService
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.advanced_dashboard import (
    SecurityOverviewWidget,
    VulnerabilityTrendsWidget,
    AssetInventoryWidget,
    ThreatIntelligenceWidget,
    ComplianceWidget,
    ActivityFeedWidget,
    PerformanceMetricsWidget,
    DashboardSummary,
    WidgetDrillDownRequest,
    WidgetDrillDownResponse,
    WidgetRefreshRequest,
    DashboardHealth,
    AdvancedFilterOptions
)

router = APIRouter()


@router.get("/health", response_model=DashboardHealth)
async def get_dashboard_health():
    """Get dashboard service health status"""
    return DashboardHealth(
        status="healthy",
        uptime_seconds=3600,  # Placeholder
        total_widgets=7,
        healthy_widgets=7,
        error_widgets=0,
        last_refresh="2025-07-11T20:30:00Z",
        performance_metrics={
            "avg_response_time_ms": 245.5,
            "cache_hit_rate": 0.85,
            "error_rate": 0.02
        }
    )


@router.get("/widgets/security-overview", response_model=SecurityOverviewWidget)
async def get_security_overview_widget(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get security overview widget with risk scoring"""
    try:
        dashboard_service = AdvancedDashboardService(db)
        widget_data = dashboard_service.get_security_overview_widget(current_user.id)
        
        if "error" in widget_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=widget_data["error"]
            )
        
        return SecurityOverviewWidget(**widget_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating security overview widget: {str(e)}"
        )


@router.get("/widgets/vulnerability-trends", response_model=VulnerabilityTrendsWidget)
async def get_vulnerability_trends_widget(
    days: int = Query(30, ge=1, le=365, description="Number of days for trend analysis"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get vulnerability trends widget with time series data"""
    try:
        dashboard_service = AdvancedDashboardService(db)
        widget_data = dashboard_service.get_vulnerability_trends_widget(current_user.id, days)
        
        if "error" in widget_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=widget_data["error"]
            )
        
        return VulnerabilityTrendsWidget(**widget_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating vulnerability trends widget: {str(e)}"
        )


@router.get("/widgets/asset-inventory", response_model=AssetInventoryWidget)
async def get_asset_inventory_widget(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get asset inventory widget with service analysis"""
    try:
        dashboard_service = AdvancedDashboardService(db)
        widget_data = dashboard_service.get_asset_inventory_widget(current_user.id)
        
        if "error" in widget_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=widget_data["error"]
            )
        
        return AssetInventoryWidget(**widget_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating asset inventory widget: {str(e)}"
        )


@router.get("/widgets/threat-intelligence", response_model=ThreatIntelligenceWidget)
async def get_threat_intelligence_widget(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get threat intelligence widget with CVE analysis"""
    try:
        dashboard_service = AdvancedDashboardService(db)
        widget_data = dashboard_service.get_threat_intelligence_widget(current_user.id)
        
        if "error" in widget_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=widget_data["error"]
            )
        
        return ThreatIntelligenceWidget(**widget_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating threat intelligence widget: {str(e)}"
        )


@router.get("/widgets/compliance", response_model=ComplianceWidget)
async def get_compliance_widget(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get compliance and governance widget"""
    try:
        dashboard_service = AdvancedDashboardService(db)
        widget_data = dashboard_service.get_compliance_widget(current_user.id)
        
        if "error" in widget_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=widget_data["error"]
            )
        
        return ComplianceWidget(**widget_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating compliance widget: {str(e)}"
        )


@router.get("/widgets/activity-feed", response_model=ActivityFeedWidget)
async def get_activity_feed_widget(
    limit: int = Query(10, ge=1, le=50, description="Number of activities to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity feed widget with recent security events"""
    try:
        dashboard_service = AdvancedDashboardService(db)
        widget_data = dashboard_service.get_activity_feed_widget(current_user.id, limit)
        
        if "error" in widget_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=widget_data["error"]
            )
        
        return ActivityFeedWidget(**widget_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating activity feed widget: {str(e)}"
        )


@router.get("/widgets/performance-metrics", response_model=PerformanceMetricsWidget)
async def get_performance_metrics_widget(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get security performance metrics widget"""
    try:
        dashboard_service = AdvancedDashboardService(db)
        widget_data = dashboard_service.get_performance_metrics_widget(current_user.id)
        
        if "error" in widget_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=widget_data["error"]
            )
        
        return PerformanceMetricsWidget(**widget_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating performance metrics widget: {str(e)}"
        )


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    include_widgets: Optional[List[str]] = Query(
        None, 
        description="Specific widgets to include (default: all)"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete dashboard summary with all widgets"""
    try:
        dashboard_service = AdvancedDashboardService(db)
        
        # Default to all widgets if none specified
        if not include_widgets:
            include_widgets = [
                "security_overview", "vulnerability_trends", "asset_inventory",
                "threat_intelligence", "compliance", "activity_feed", "performance_metrics"
            ]
        
        summary_data = {
            "user_id": current_user.id,
            "generated_at": "2025-07-11T20:30:00Z",
            "refresh_token": f"rt_{current_user.id}_1626030000"
        }
        
        # Generate requested widgets
        if "security_overview" in include_widgets:
            widget_data = dashboard_service.get_security_overview_widget(current_user.id)
            if "error" not in widget_data:
                summary_data["security_overview"] = SecurityOverviewWidget(**widget_data)
        
        if "vulnerability_trends" in include_widgets:
            widget_data = dashboard_service.get_vulnerability_trends_widget(current_user.id)
            if "error" not in widget_data:
                summary_data["vulnerability_trends"] = VulnerabilityTrendsWidget(**widget_data)
        
        if "asset_inventory" in include_widgets:
            widget_data = dashboard_service.get_asset_inventory_widget(current_user.id)
            if "error" not in widget_data:
                summary_data["asset_inventory"] = AssetInventoryWidget(**widget_data)
        
        if "threat_intelligence" in include_widgets:
            widget_data = dashboard_service.get_threat_intelligence_widget(current_user.id)
            if "error" not in widget_data:
                summary_data["threat_intelligence"] = ThreatIntelligenceWidget(**widget_data)
        
        if "compliance" in include_widgets:
            widget_data = dashboard_service.get_compliance_widget(current_user.id)
            if "error" not in widget_data:
                summary_data["compliance"] = ComplianceWidget(**widget_data)
        
        if "activity_feed" in include_widgets:
            widget_data = dashboard_service.get_activity_feed_widget(current_user.id)
            if "error" not in widget_data:
                summary_data["activity_feed"] = ActivityFeedWidget(**widget_data)
        
        if "performance_metrics" in include_widgets:
            widget_data = dashboard_service.get_performance_metrics_widget(current_user.id)
            if "error" not in widget_data:
                summary_data["performance_metrics"] = PerformanceMetricsWidget(**widget_data)
        
        return DashboardSummary(**summary_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating dashboard summary: {str(e)}"
        )


@router.post("/widgets/drill-down", response_model=WidgetDrillDownResponse)
async def get_widget_drill_down(
    request: WidgetDrillDownRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get drill-down data for specific widget"""
    try:
        dashboard_service = AdvancedDashboardService(db)
        drill_down_data = dashboard_service.get_widget_drill_down(
            current_user.id, 
            request.widget_type, 
            request.filter_params
        )
        
        if "error" in drill_down_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=drill_down_data["error"]
            )
        
        return WidgetDrillDownResponse(
            widget_type=request.widget_type,
            drill_down_data=drill_down_data,
            filter_applied=request.filter_params,
            total_count=drill_down_data.get("total_count"),
            generated_at="2025-07-11T20:30:00Z"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting drill-down data: {str(e)}"
        )


@router.post("/widgets/refresh")
async def refresh_widgets(
    request: WidgetRefreshRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh specific widgets"""
    try:
        # In a real implementation, this would trigger cache invalidation
        # and potentially notify WebSocket clients
        
        refreshed_widgets = []
        dashboard_service = AdvancedDashboardService(db)
        
        for widget_type in request.widget_types:
            if widget_type == "security_overview":
                widget_data = dashboard_service.get_security_overview_widget(current_user.id)
            elif widget_type == "vulnerability_trends":
                widget_data = dashboard_service.get_vulnerability_trends_widget(current_user.id)
            elif widget_type == "asset_inventory":
                widget_data = dashboard_service.get_asset_inventory_widget(current_user.id)
            elif widget_type == "threat_intelligence":
                widget_data = dashboard_service.get_threat_intelligence_widget(current_user.id)
            elif widget_type == "compliance":
                widget_data = dashboard_service.get_compliance_widget(current_user.id)
            elif widget_type == "activity_feed":
                widget_data = dashboard_service.get_activity_feed_widget(current_user.id)
            elif widget_type == "performance_metrics":
                widget_data = dashboard_service.get_performance_metrics_widget(current_user.id)
            else:
                continue
            
            if "error" not in widget_data:
                refreshed_widgets.append(widget_type)
        
        return {
            "status": "success",
            "message": f"Refreshed {len(refreshed_widgets)} widgets",
            "refreshed_widgets": refreshed_widgets,
            "failed_widgets": list(set(request.widget_types) - set(refreshed_widgets)),
            "timestamp": "2025-07-11T20:30:00Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing widgets: {str(e)}"
        )


@router.get("/widgets/available")
async def get_available_widgets():
    """Get list of available widgets and their capabilities"""
    return {
        "available_widgets": [
            {
                "widget_type": "security_overview",
                "title": "Security Overview",
                "description": "Risk scoring and vulnerability summary",
                "supports_drill_down": True,
                "supports_filtering": True,
                "refresh_interval": 300
            },
            {
                "widget_type": "vulnerability_trends",
                "title": "Vulnerability Trends",
                "description": "Time series analysis of vulnerabilities",
                "supports_drill_down": True,
                "supports_filtering": True,
                "refresh_interval": 600
            },
            {
                "widget_type": "asset_inventory",
                "title": "Asset Inventory",
                "description": "Service and asset analysis",
                "supports_drill_down": True,
                "supports_filtering": True,
                "refresh_interval": 900
            },
            {
                "widget_type": "threat_intelligence",
                "title": "Threat Intelligence",
                "description": "CVE analysis and threat trends",
                "supports_drill_down": True,
                "supports_filtering": True,
                "refresh_interval": 1800
            },
            {
                "widget_type": "compliance",
                "title": "Compliance & Governance",
                "description": "Compliance metrics and SLA tracking",
                "supports_drill_down": True,
                "supports_filtering": False,
                "refresh_interval": 3600
            },
            {
                "widget_type": "activity_feed",
                "title": "Recent Activity",
                "description": "Recent security events and activities",
                "supports_drill_down": True,
                "supports_filtering": True,
                "refresh_interval": 60
            },
            {
                "widget_type": "performance_metrics",
                "title": "Security Performance",
                "description": "Security KPIs and performance metrics",
                "supports_drill_down": True,
                "supports_filtering": False,
                "refresh_interval": 1800
            }
        ],
        "total_widgets": 7,
        "capabilities": {
            "real_time_updates": True,
            "custom_layouts": True,
            "export_support": True,
            "alert_thresholds": True,
            "responsive_design": True
        }
    }


@router.get("/widgets/filters/{widget_type}")
async def get_widget_filter_options(
    widget_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available filter options for a specific widget"""
    try:
        # This would typically query the database to get available filter values
        # For now, returning static filter options based on widget type
        
        filter_options = {}
        
        if widget_type in ["security_overview", "vulnerability_trends", "threat_intelligence"]:
            filter_options.update({
                "severity_levels": ["Critical", "High", "Medium", "Low"],
                "status_types": ["open", "patched", "ignored", "false_positive"]
            })
        
        if widget_type in ["asset_inventory", "vulnerability_trends"]:
            # Get actual service names from database
            services = db.query(
                getattr(__import__('app.models.vulnerability', fromlist=['Vulnerability']), 'Vulnerability').service_name.distinct()
            ).join(
                getattr(__import__('app.models.scan', fromlist=['Scan']), 'Scan')
            ).filter(
                getattr(__import__('app.models.scan', fromlist=['Scan']), 'Scan').user_id == current_user.id
            ).all()
            
            filter_options["service_names"] = [s[0] for s in services if s[0]]
        
        if widget_type == "activity_feed":
            filter_options["activity_types"] = ["scan", "vulnerability", "audit"]
        
        # Common date range options
        filter_options["date_ranges"] = [
            {"label": "Last 24 hours", "value": "24h"},
            {"label": "Last 7 days", "value": "7d"},
            {"label": "Last 30 days", "value": "30d"},
            {"label": "Last 90 days", "value": "90d"},
            {"label": "Custom range", "value": "custom"}
        ]
        
        return {
            "widget_type": widget_type,
            "filter_options": filter_options,
            "supports_custom_filters": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting filter options: {str(e)}"
        )


@router.get("/analytics/summary")
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard analytics and usage statistics"""
    try:
        # This would typically track dashboard usage, widget performance, etc.
        return {
            "user_id": current_user.id,
            "dashboard_views": 45,
            "most_used_widgets": [
                {"widget_type": "security_overview", "views": 25},
                {"widget_type": "vulnerability_trends", "views": 18},
                {"widget_type": "activity_feed", "views": 15}
            ],
            "average_session_duration": 425,  # seconds
            "widgets_with_alerts": 2,
            "last_dashboard_access": "2025-07-11T19:45:00Z",
            "performance_metrics": {
                "avg_load_time": 1.2,  # seconds
                "cache_hit_rate": 0.78,
                "error_rate": 0.01
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting dashboard analytics: {str(e)}"
        )