"""
Advanced Dashboard schemas for enhanced widgets
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class SecurityOverviewWidget(BaseModel):
    """Security overview widget with risk scoring"""
    widget_type: str = "security_overview"
    title: str = "Security Overview"
    risk_score: int = Field(..., ge=0, le=100, description="Overall risk score (0-100)")
    risk_level: str = Field(..., description="Risk level (Minimal, Low, Medium, High, Critical)")
    vulnerability_counts: Dict[str, int] = Field(..., description="Vulnerability counts by severity")
    recent_critical: List[Dict[str, Any]] = Field(default_factory=list, description="Recent critical vulnerabilities")
    trend_comparison: Dict[str, Any] = Field(..., description="Trend comparison with previous period")
    last_updated: str = Field(..., description="Last update timestamp")
    drill_down_available: bool = True


class VulnerabilityTrendsWidget(BaseModel):
    """Vulnerability trends widget with time series data"""
    widget_type: str = "vulnerability_trends"
    title: str = "Vulnerability Trends"
    period_days: int = Field(..., description="Analysis period in days")
    daily_trends: List[Dict[str, Any]] = Field(default_factory=list, description="Daily vulnerability trends")
    status_trends: List[Dict[str, Any]] = Field(default_factory=list, description="Status distribution trends")
    cvss_trends: List[Dict[str, Any]] = Field(default_factory=list, description="CVSS score trends")
    patch_velocity: Dict[str, Any] = Field(..., description="Patch velocity metrics")
    last_updated: str = Field(..., description="Last update timestamp")
    drill_down_available: bool = True


class AssetInventoryWidget(BaseModel):
    """Asset inventory widget with service analysis"""
    widget_type: str = "asset_inventory"
    title: str = "Asset Inventory"
    service_distribution: List[Dict[str, Any]] = Field(default_factory=list, description="Service distribution")
    port_analysis: List[Dict[str, Any]] = Field(default_factory=list, description="Port usage analysis")
    asset_risk_ranking: List[Dict[str, Any]] = Field(default_factory=list, description="Assets ranked by risk")
    version_analysis: List[Dict[str, Any]] = Field(default_factory=list, description="Service version analysis")
    last_updated: str = Field(..., description="Last update timestamp")
    drill_down_available: bool = True


class ThreatIntelligenceWidget(BaseModel):
    """Threat intelligence widget with CVE analysis"""
    widget_type: str = "threat_intelligence"
    title: str = "Threat Intelligence"
    cve_statistics: Dict[str, Any] = Field(..., description="CVE-related statistics")
    severity_heatmap: List[Dict[str, Any]] = Field(default_factory=list, description="Severity heatmap data")
    top_cves: List[Dict[str, Any]] = Field(default_factory=list, description="Top CVEs by impact")
    threat_trends: List[Dict[str, Any]] = Field(default_factory=list, description="Threat trends over time")
    last_updated: str = Field(..., description="Last update timestamp")
    drill_down_available: bool = True


class ComplianceWidget(BaseModel):
    """Compliance and governance widget"""
    widget_type: str = "compliance"
    title: str = "Compliance & Governance"
    compliance_score: int = Field(..., ge=0, le=100, description="Overall compliance score")
    patch_compliance: Dict[str, Any] = Field(..., description="Patch compliance metrics")
    scan_compliance: Dict[str, Any] = Field(..., description="Scan frequency compliance")
    critical_sla: Dict[str, Any] = Field(..., description="Critical vulnerability SLA metrics")
    last_updated: str = Field(..., description="Last update timestamp")
    drill_down_available: bool = True


class ActivityFeedWidget(BaseModel):
    """Activity feed widget with recent security events"""
    widget_type: str = "activity_feed"
    title: str = "Recent Activity"
    activities: List[Dict[str, Any]] = Field(default_factory=list, description="Recent activities")
    total_activities: int = Field(..., description="Total number of activities")
    last_updated: str = Field(..., description="Last update timestamp")
    drill_down_available: bool = True


class PerformanceMetricsWidget(BaseModel):
    """Security performance metrics widget"""
    widget_type: str = "performance_metrics"
    title: str = "Security Performance"
    mttd_hours: float = Field(..., description="Mean Time to Detection in hours")
    mttr_hours: float = Field(..., description="Mean Time to Resolution in hours")
    discovery_rate: Dict[str, float] = Field(..., description="Vulnerability discovery rate")
    patch_effectiveness: Dict[str, Any] = Field(..., description="Patch effectiveness metrics")
    posture_trend: List[Dict[str, Any]] = Field(default_factory=list, description="Security posture trend")
    last_updated: str = Field(..., description="Last update timestamp")
    drill_down_available: bool = True


class WidgetDrillDownRequest(BaseModel):
    """Request for widget drill-down data"""
    widget_type: str = Field(..., description="Type of widget to drill down")
    filter_params: Dict[str, Any] = Field(default_factory=dict, description="Filter parameters for drill-down")


class WidgetDrillDownResponse(BaseModel):
    """Response for widget drill-down data"""
    widget_type: str = Field(..., description="Type of widget")
    drill_down_data: Dict[str, Any] = Field(..., description="Detailed drill-down data")
    filter_applied: Dict[str, Any] = Field(default_factory=dict, description="Filters that were applied")
    total_count: Optional[int] = Field(None, description="Total count of items (if applicable)")
    generated_at: str = Field(..., description="Generation timestamp")


class DashboardLayoutConfig(BaseModel):
    """Dashboard layout configuration"""
    user_id: int = Field(..., description="User ID")
    layout: List[Dict[str, Any]] = Field(..., description="Widget layout configuration")
    theme: str = Field(default="light", description="Dashboard theme")
    refresh_interval: int = Field(default=300, description="Auto-refresh interval in seconds")
    created_at: str = Field(..., description="Configuration creation timestamp")
    updated_at: str = Field(..., description="Configuration update timestamp")


class DashboardSummary(BaseModel):
    """Complete dashboard summary with all widgets"""
    user_id: int = Field(..., description="User ID")
    security_overview: Optional[SecurityOverviewWidget] = None
    vulnerability_trends: Optional[VulnerabilityTrendsWidget] = None
    asset_inventory: Optional[AssetInventoryWidget] = None
    threat_intelligence: Optional[ThreatIntelligenceWidget] = None
    compliance: Optional[ComplianceWidget] = None
    activity_feed: Optional[ActivityFeedWidget] = None
    performance_metrics: Optional[PerformanceMetricsWidget] = None
    generated_at: str = Field(..., description="Dashboard generation timestamp")
    refresh_token: str = Field(..., description="Token for incremental updates")


class WidgetRefreshRequest(BaseModel):
    """Request to refresh specific widgets"""
    widget_types: List[str] = Field(..., description="List of widget types to refresh")
    force_refresh: bool = Field(default=False, description="Force refresh even if cached")


class DashboardMetricsComparison(BaseModel):
    """Comparison metrics between time periods"""
    metric_name: str = Field(..., description="Name of the metric")
    current_value: float = Field(..., description="Current period value")
    previous_value: float = Field(..., description="Previous period value")
    change_percent: float = Field(..., description="Percentage change")
    change_direction: str = Field(..., description="Direction of change (up/down/stable)")
    is_favorable: bool = Field(..., description="Whether the change is favorable")


class AdvancedFilterOptions(BaseModel):
    """Advanced filtering options for dashboard widgets"""
    severity_levels: Optional[List[str]] = Field(None, description="Filter by severity levels")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range filter")
    service_names: Optional[List[str]] = Field(None, description="Filter by service names")
    status_types: Optional[List[str]] = Field(None, description="Filter by status types")
    cvss_range: Optional[Dict[str, float]] = Field(None, description="CVSS score range filter")
    ports: Optional[List[int]] = Field(None, description="Filter by specific ports")
    cve_ids: Optional[List[str]] = Field(None, description="Filter by CVE IDs")


class RealTimeUpdate(BaseModel):
    """Real-time update notification"""
    update_type: str = Field(..., description="Type of update (new_vulnerability, scan_complete, etc.)")
    widget_types_affected: List[str] = Field(..., description="Widget types that need refresh")
    summary: str = Field(..., description="Brief summary of the update")
    timestamp: str = Field(..., description="Update timestamp")
    priority: str = Field(default="normal", description="Update priority (low/normal/high/critical)")


class DashboardAlert(BaseModel):
    """Dashboard alert/notification"""
    alert_id: str = Field(..., description="Unique alert identifier")
    alert_type: str = Field(..., description="Type of alert (security/compliance/performance)")
    severity: str = Field(..., description="Alert severity")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    affected_widgets: List[str] = Field(default_factory=list, description="Affected widget types")
    action_required: bool = Field(default=False, description="Whether action is required")
    action_url: Optional[str] = Field(None, description="URL for recommended action")
    created_at: str = Field(..., description="Alert creation timestamp")
    expires_at: Optional[str] = Field(None, description="Alert expiration timestamp")


class WidgetError(BaseModel):
    """Widget error information"""
    widget_type: str = Field(..., description="Type of widget that errored")
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Human-readable error message")
    timestamp: str = Field(..., description="Error timestamp")
    is_retryable: bool = Field(default=True, description="Whether the error is retryable")
    retry_after: Optional[int] = Field(None, description="Retry after seconds")


class DashboardHealth(BaseModel):
    """Dashboard service health status"""
    status: str = Field(..., description="Overall health status")
    uptime_seconds: int = Field(..., description="Service uptime in seconds")
    total_widgets: int = Field(..., description="Total number of available widgets")
    healthy_widgets: int = Field(..., description="Number of healthy widgets")
    error_widgets: int = Field(..., description="Number of widgets with errors")
    last_refresh: str = Field(..., description="Last successful refresh timestamp")
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Performance metrics")


class WidgetCustomization(BaseModel):
    """Widget customization settings"""
    widget_type: str = Field(..., description="Type of widget")
    display_options: Dict[str, Any] = Field(default_factory=dict, description="Display customization options")
    data_filters: Optional[AdvancedFilterOptions] = Field(None, description="Data filtering options")
    refresh_interval: Optional[int] = Field(None, description="Custom refresh interval")
    alert_thresholds: Dict[str, float] = Field(default_factory=dict, description="Custom alert thresholds")
    chart_type: Optional[str] = Field(None, description="Preferred chart type for visualizations")
    color_scheme: Optional[str] = Field(None, description="Custom color scheme")


class DashboardExport(BaseModel):
    """Dashboard export configuration"""
    export_format: str = Field(..., description="Export format (pdf/png/csv/json)")
    include_widgets: List[str] = Field(..., description="Widget types to include in export")
    time_range: Dict[str, str] = Field(..., description="Time range for exported data")
    include_raw_data: bool = Field(default=False, description="Include raw data in export")
    filename_prefix: Optional[str] = Field(None, description="Custom filename prefix")
    email_recipients: Optional[List[str]] = Field(None, description="Email recipients for export")
    schedule: Optional[Dict[str, Any]] = Field(None, description="Scheduled export configuration")