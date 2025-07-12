"""
Export service for CSV and other data export formats
"""
import csv
import io
import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import pandas as pd

from app.models.vulnerability import Vulnerability
from app.models.scan import Scan
from app.models.audit_log import AuditLog
from app.models.feedback import Feedback
from app.models.user import User

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting data in various formats"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def export_vulnerabilities_csv(
        self,
        user_id: Optional[int] = None,
        scan_id: Optional[int] = None,
        severity_filter: Optional[List[str]] = None,
        status_filter: Optional[List[str]] = None
    ) -> str:
        """Export vulnerabilities to CSV format"""
        try:
            # Build query
            query = self.db.query(Vulnerability)
            
            if user_id:
                query = query.join(Scan).filter(Scan.user_id == user_id)
            
            if scan_id:
                query = query.filter(Vulnerability.scan_id == scan_id)
            
            if severity_filter:
                query = query.filter(Vulnerability.severity.in_(severity_filter))
            
            if status_filter:
                query = query.filter(Vulnerability.status.in_(status_filter))
            
            vulnerabilities = query.all()
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            headers = [
                'ID',
                'Scan ID',
                'Service Name',
                'Service Version',
                'Port',
                'Protocol',
                'CVE ID',
                'CVSS Score',
                'Severity',
                'Description',
                'Recommendation',
                'Status',
                'Created At',
                'Updated At'
            ]
            writer.writerow(headers)
            
            # Write data rows
            for vuln in vulnerabilities:
                row = [
                    vuln.id,
                    vuln.scan_id,
                    vuln.service_name,
                    vuln.service_version,
                    vuln.port,
                    vuln.protocol,
                    vuln.cve_id or '',
                    vuln.cvss_score or '',
                    vuln.severity,
                    vuln.description,
                    vuln.recommendation or '',
                    vuln.status,
                    vuln.created_at.isoformat() if vuln.created_at else '',
                    vuln.updated_at.isoformat() if vuln.updated_at else ''
                ]
                writer.writerow(row)
            
            csv_content = output.getvalue()
            output.close()
            
            logger.info(f"Exported {len(vulnerabilities)} vulnerabilities to CSV")
            return csv_content
            
        except Exception as e:
            logger.error(f"Error exporting vulnerabilities to CSV: {e}")
            raise
    
    def export_scans_csv(self, user_id: Optional[int] = None) -> str:
        """Export scans summary to CSV format"""
        try:
            # Build query
            query = self.db.query(Scan)
            
            if user_id:
                query = query.filter(Scan.user_id == user_id)
            
            scans = query.all()
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            headers = [
                'ID',
                'User ID',
                'Filename',
                'Original Filename',
                'File Size (bytes)',
                'Status',
                'Upload Time',
                'Processed At',
                'Error Message',
                'Total Vulnerabilities',
                'Critical Count',
                'High Count',
                'Medium Count',
                'Low Count'
            ]
            writer.writerow(headers)
            
            # Write data rows
            for scan in scans:
                # Count vulnerabilities by severity
                vuln_counts = self.db.query(Vulnerability.severity, 
                                          func.count(Vulnerability.id))\
                                 .filter(Vulnerability.scan_id == scan.id)\
                                 .group_by(Vulnerability.severity).all()
                
                severity_counts = {severity: count for severity, count in vuln_counts}
                total_vulns = sum(severity_counts.values())
                
                row = [
                    scan.id,
                    scan.user_id,
                    scan.filename,
                    scan.original_filename,
                    scan.file_size,
                    scan.status,
                    scan.upload_time.isoformat() if scan.upload_time else '',
                    scan.processed_at.isoformat() if scan.processed_at else '',
                    scan.error_message or '',
                    total_vulns,
                    severity_counts.get('Critical', 0),
                    severity_counts.get('High', 0),
                    severity_counts.get('Medium', 0),
                    severity_counts.get('Low', 0)
                ]
                writer.writerow(row)
            
            csv_content = output.getvalue()
            output.close()
            
            logger.info(f"Exported {len(scans)} scans to CSV")
            return csv_content
            
        except Exception as e:
            logger.error(f"Error exporting scans to CSV: {e}")
            raise
    
    def export_audit_logs_csv(
        self,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action_filter: Optional[List[str]] = None
    ) -> str:
        """Export audit logs to CSV format"""
        try:
            # Build query
            query = self.db.query(AuditLog)
            
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            
            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)
            
            if end_date:
                query = query.filter(AuditLog.timestamp <= end_date)
            
            if action_filter:
                query = query.filter(AuditLog.action.in_(action_filter))
            
            audit_logs = query.order_by(AuditLog.timestamp.desc()).all()
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            headers = [
                'ID',
                'User ID',
                'User Email',
                'Action',
                'Details',
                'IP Address',
                'User Agent',
                'Timestamp'
            ]
            writer.writerow(headers)
            
            # Write data rows
            for log in audit_logs:
                # Get user email
                user_email = ''
                if log.user_id:
                    user = self.db.query(User).filter(User.id == log.user_id).first()
                    if user:
                        user_email = user.email
                
                row = [
                    log.id,
                    log.user_id or '',
                    user_email,
                    log.action,
                    log.details or '',
                    log.ip_address or '',
                    log.user_agent or '',
                    log.timestamp.isoformat() if log.timestamp else ''
                ]
                writer.writerow(row)
            
            csv_content = output.getvalue()
            output.close()
            
            logger.info(f"Exported {len(audit_logs)} audit logs to CSV")
            return csv_content
            
        except Exception as e:
            logger.error(f"Error exporting audit logs to CSV: {e}")
            raise
    
    def export_feedback_csv(self, user_id: Optional[int] = None) -> str:
        """Export feedback data to CSV format"""
        try:
            # Build query
            query = self.db.query(Feedback)
            
            if user_id:
                query = query.filter(Feedback.user_id == user_id)
            
            feedback_items = query.all()
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            headers = [
                'ID',
                'User ID',
                'Vulnerability ID',
                'Analysis ID',
                'Scan ID',
                'Rating',
                'Comment',
                'Is Helpful',
                'Feedback Type',
                'Analysis Type',
                'Conversation ID',
                'Created At',
                'Updated At'
            ]
            writer.writerow(headers)
            
            # Write data rows
            for feedback in feedback_items:
                row = [
                    feedback.id,
                    feedback.user_id,
                    feedback.vulnerability_id or '',
                    feedback.analysis_id or '',
                    feedback.scan_id or '',
                    feedback.rating or '',
                    feedback.comment or '',
                    feedback.is_helpful or '',
                    feedback.feedback_type or '',
                    feedback.analysis_type or '',
                    feedback.conversation_id or '',
                    feedback.created_at.isoformat() if feedback.created_at else '',
                    feedback.updated_at.isoformat() if feedback.updated_at else ''
                ]
                writer.writerow(row)
            
            csv_content = output.getvalue()
            output.close()
            
            logger.info(f"Exported {len(feedback_items)} feedback items to CSV")
            return csv_content
            
        except Exception as e:
            logger.error(f"Error exporting feedback to CSV: {e}")
            raise
    
    def export_dashboard_summary_csv(self, user_id: int) -> str:
        """Export dashboard summary data to CSV format"""
        try:
            # Get user's scans with vulnerability counts
            scans_query = self.db.query(Scan).filter(Scan.user_id == user_id)
            scans = scans_query.all()
            
            # Create comprehensive summary
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Dashboard Summary Section
            writer.writerow(['VulnPatch AI - Dashboard Summary'])
            writer.writerow(['Generated At', datetime.utcnow().isoformat()])
            writer.writerow(['User ID', user_id])
            writer.writerow([])  # Empty row
            
            # Overall Statistics
            writer.writerow(['OVERALL STATISTICS'])
            writer.writerow(['Metric', 'Value'])
            
            total_scans = len(scans)
            total_vulns = self.db.query(Vulnerability)\
                             .join(Scan)\
                             .filter(Scan.user_id == user_id)\
                             .count()
            
            # Severity distribution
            severity_query = self.db.query(Vulnerability.severity, 
                                         func.count(Vulnerability.id))\
                                .join(Scan)\
                                .filter(Scan.user_id == user_id)\
                                .group_by(Vulnerability.severity)
            
            severity_counts = {severity: count for severity, count in severity_query.all()}
            
            writer.writerow(['Total Scans', total_scans])
            writer.writerow(['Total Vulnerabilities', total_vulns])
            writer.writerow(['Critical Vulnerabilities', severity_counts.get('Critical', 0)])
            writer.writerow(['High Vulnerabilities', severity_counts.get('High', 0)])
            writer.writerow(['Medium Vulnerabilities', severity_counts.get('Medium', 0)])
            writer.writerow(['Low Vulnerabilities', severity_counts.get('Low', 0)])
            writer.writerow([])  # Empty row
            
            # Recent Scans Summary
            writer.writerow(['RECENT SCANS (Last 10)'])
            writer.writerow(['Scan ID', 'Filename', 'Status', 'Upload Time', 'Vulnerabilities'])
            
            recent_scans = scans_query.order_by(Scan.upload_time.desc()).limit(10).all()
            for scan in recent_scans:
                vuln_count = self.db.query(Vulnerability)\
                               .filter(Vulnerability.scan_id == scan.id)\
                               .count()
                
                writer.writerow([
                    scan.id,
                    scan.filename,
                    scan.status,
                    scan.upload_time.isoformat() if scan.upload_time else '',
                    vuln_count
                ])
            
            writer.writerow([])  # Empty row
            
            # Top Vulnerable Services
            writer.writerow(['TOP VULNERABLE SERVICES'])
            writer.writerow(['Service Name', 'Vulnerability Count', 'Most Common Severity'])
            
            service_query = self.db.query(Vulnerability.service_name,
                                        func.count(Vulnerability.id),
                                        Vulnerability.severity)\
                              .join(Scan)\
                              .filter(Scan.user_id == user_id)\
                              .group_by(Vulnerability.service_name, Vulnerability.severity)\
                              .order_by(func.count(Vulnerability.id).desc())\
                              .limit(10)
            
            service_data = {}
            for service, count, severity in service_query.all():
                if service not in service_data:
                    service_data[service] = {'total': 0, 'severities': {}}
                service_data[service]['total'] += count
                service_data[service]['severities'][severity] = count
            
            for service, data in sorted(service_data.items(), 
                                      key=lambda x: x[1]['total'], 
                                      reverse=True)[:10]:
                most_common_severity = max(data['severities'], 
                                         key=data['severities'].get)
                writer.writerow([service, data['total'], most_common_severity])
            
            csv_content = output.getvalue()
            output.close()
            
            logger.info(f"Exported dashboard summary to CSV for user {user_id}")
            return csv_content
            
        except Exception as e:
            logger.error(f"Error exporting dashboard summary to CSV: {e}")
            raise
    
    def export_vulnerability_trends_csv(self, user_id: int, days: int = 30) -> str:
        """Export vulnerability trends over time to CSV"""
        try:
            # Get vulnerability data over time
            from datetime import timedelta
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Query vulnerabilities by day
            daily_query = self.db.query(
                func.date(Vulnerability.created_at).label('date'),
                Vulnerability.severity,
                func.count(Vulnerability.id).label('count')
            ).join(Scan)\
             .filter(Scan.user_id == user_id)\
             .filter(Vulnerability.created_at >= start_date)\
             .group_by(
                 func.date(Vulnerability.created_at),
                 Vulnerability.severity
             )\
             .order_by('date').all()
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(['VulnPatch AI - Vulnerability Trends'])
            writer.writerow(['Period', f'Last {days} days'])
            writer.writerow(['Generated At', datetime.utcnow().isoformat()])
            writer.writerow([])
            
            writer.writerow(['Date', 'Severity', 'Count'])
            
            # Write data
            for date, severity, count in daily_query:
                writer.writerow([date.isoformat() if date else '', severity, count])
            
            csv_content = output.getvalue()
            output.close()
            
            logger.info(f"Exported vulnerability trends to CSV for user {user_id}")
            return csv_content
            
        except Exception as e:
            logger.error(f"Error exporting vulnerability trends to CSV: {e}")
            raise
    
    def get_export_metadata(self, export_type: str, user_id: int) -> Dict:
        """Get metadata about available export data"""
        try:
            metadata = {
                "export_type": export_type,
                "user_id": user_id,
                "generated_at": datetime.utcnow().isoformat(),
                "available_filters": {}
            }
            
            if export_type == "vulnerabilities":
                # Get available severity and status options
                severities = self.db.query(Vulnerability.severity.distinct())\
                               .join(Scan)\
                               .filter(Scan.user_id == user_id)\
                               .all()
                
                statuses = self.db.query(Vulnerability.status.distinct())\
                             .join(Scan)\
                             .filter(Scan.user_id == user_id)\
                             .all()
                
                metadata["available_filters"] = {
                    "severities": [s[0] for s in severities if s[0]],
                    "statuses": [s[0] for s in statuses if s[0]],
                    "total_records": self.db.query(Vulnerability)\
                                       .join(Scan)\
                                       .filter(Scan.user_id == user_id)\
                                       .count()
                }
            
            elif export_type == "audit_logs":
                # Get available action types
                actions = self.db.query(AuditLog.action.distinct())\
                            .filter(AuditLog.user_id == user_id)\
                            .all()
                
                metadata["available_filters"] = {
                    "actions": [a[0] for a in actions if a[0]],
                    "total_records": self.db.query(AuditLog)\
                                       .filter(AuditLog.user_id == user_id)\
                                       .count()
                }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting export metadata: {e}")
            raise