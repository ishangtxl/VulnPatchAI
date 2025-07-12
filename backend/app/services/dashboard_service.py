"""
Dashboard service
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Dict, List

from app.models.scan import Scan
from app.models.vulnerability import Vulnerability
from app.schemas.dashboard import DashboardMetrics, VulnerabilitySummary, TrendData, TrendPoint


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_metrics(self, user_id: int) -> DashboardMetrics:
        """Get dashboard metrics for user"""
        
        # Total scans
        total_scans = (
            self.db.query(Scan)
            .filter(Scan.user_id == user_id)
            .count()
        )
        
        # Vulnerability summary
        vuln_summary = self._get_vulnerability_summary(user_id)
        
        # Recent scans (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_scans = (
            self.db.query(Scan)
            .filter(and_(Scan.user_id == user_id, Scan.upload_time >= week_ago))
            .count()
        )
        
        # Average CVSS score
        avg_cvss = (
            self.db.query(func.avg(Vulnerability.cvss_score))
            .join(Scan)
            .filter(and_(
                Scan.user_id == user_id,
                Vulnerability.cvss_score.isnot(None)
            ))
            .scalar() or 0.0
        )
        
        # Patch completion rate
        total_vulns = vuln_summary.total
        patched_vulns = (
            self.db.query(Vulnerability)
            .join(Scan)
            .filter(and_(
                Scan.user_id == user_id,
                Vulnerability.status == "patched"
            ))
            .count()
        )
        
        patch_completion_rate = (patched_vulns / total_vulns * 100) if total_vulns > 0 else 0.0
        
        return DashboardMetrics(
            total_scans=total_scans,
            vulnerabilities=vuln_summary,
            patch_completion_rate=patch_completion_rate,
            recent_scans=recent_scans,
            avg_cvss_score=round(avg_cvss, 2)
        )
    
    def _get_vulnerability_summary(self, user_id: int) -> VulnerabilitySummary:
        """Get vulnerability count by severity"""
        
        severity_counts = (
            self.db.query(
                Vulnerability.severity,
                func.count(Vulnerability.id)
            )
            .join(Scan)
            .filter(Scan.user_id == user_id)
            .group_by(Vulnerability.severity)
            .all()
        )
        
        summary = VulnerabilitySummary()
        
        for severity, count in severity_counts:
            if severity:
                severity_lower = severity.lower()
                if severity_lower == "critical":
                    summary.critical = count
                elif severity_lower == "high":
                    summary.high = count
                elif severity_lower == "medium":
                    summary.medium = count
                elif severity_lower == "low":
                    summary.low = count
        
        summary.total = summary.critical + summary.high + summary.medium + summary.low
        
        return summary
    
    def get_trends(self, user_id: int, days: int = 30) -> TrendData:
        """Get trend data for charts"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Vulnerability trends
        vuln_trends = self._get_vulnerability_trends(user_id, start_date)
        
        # Scan trends
        scan_trends = self._get_scan_trends(user_id, start_date)
        
        # Severity distribution
        severity_dist = self._get_severity_distribution(user_id)
        
        return TrendData(
            vulnerability_trends=vuln_trends,
            scan_trends=scan_trends,
            severity_distribution=severity_dist
        )
    
    def _get_vulnerability_trends(self, user_id: int, start_date: datetime) -> List[TrendPoint]:
        """Get vulnerability count trends over time"""
        
        trends = (
            self.db.query(
                func.date(Vulnerability.created_at).label('date'),
                func.count(Vulnerability.id).label('count')
            )
            .join(Scan)
            .filter(and_(
                Scan.user_id == user_id,
                Vulnerability.created_at >= start_date
            ))
            .group_by(func.date(Vulnerability.created_at))
            .order_by(func.date(Vulnerability.created_at))
            .all()
        )
        
        return [
            TrendPoint(date=str(date), value=count)
            for date, count in trends
        ]
    
    def _get_scan_trends(self, user_id: int, start_date: datetime) -> List[TrendPoint]:
        """Get scan count trends over time"""
        
        trends = (
            self.db.query(
                func.date(Scan.upload_time).label('date'),
                func.count(Scan.id).label('count')
            )
            .filter(and_(
                Scan.user_id == user_id,
                Scan.upload_time >= start_date
            ))
            .group_by(func.date(Scan.upload_time))
            .order_by(func.date(Scan.upload_time))
            .all()
        )
        
        return [
            TrendPoint(date=str(date), value=count)
            for date, count in trends
        ]
    
    def _get_severity_distribution(self, user_id: int) -> Dict[str, int]:
        """Get current severity distribution"""
        
        distribution = (
            self.db.query(
                Vulnerability.severity,
                func.count(Vulnerability.id)
            )
            .join(Scan)
            .filter(Scan.user_id == user_id)
            .group_by(Vulnerability.severity)
            .all()
        )
        
        return {
            severity or "Unknown": count
            for severity, count in distribution
        }