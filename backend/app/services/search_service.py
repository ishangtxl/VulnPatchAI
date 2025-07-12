"""
Advanced search and filtering service for VulnPatch AI
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, case, String
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import logging

from app.models.scan import Scan
from app.models.vulnerability import Vulnerability
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.feedback import Feedback
from app.models.report import Report

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self, db: Session):
        self.db = db
    
    def search_vulnerabilities(
        self,
        user_id: int,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Advanced vulnerability search with filters"""
        
        # Base query
        base_query = (
            self.db.query(Vulnerability)
            .join(Scan)
            .filter(Scan.user_id == user_id)
        )
        
        # Apply text search
        if query:
            search_conditions = [
                Vulnerability.service_name.ilike(f"%{query}%"),
                Vulnerability.service_version.ilike(f"%{query}%"),
                Vulnerability.description.ilike(f"%{query}%"),
                Vulnerability.cve_id.ilike(f"%{query}%"),
                Vulnerability.recommendation.ilike(f"%{query}%"),
                Scan.filename.ilike(f"%{query}%")
            ]
            base_query = base_query.filter(or_(*search_conditions))
        
        # Apply filters
        if filters:
            base_query = self._apply_vulnerability_filters(base_query, filters)
        
        # Get total count before pagination
        total_count = base_query.count()
        
        # Apply sorting
        base_query = self._apply_sorting(base_query, Vulnerability, sort_by, sort_order)
        
        # Apply pagination
        offset = (page - 1) * page_size
        vulnerabilities = base_query.offset(offset).limit(page_size).all()
        
        # Calculate aggregations
        aggregations = self._calculate_vulnerability_aggregations(user_id, filters)
        
        return {
            "results": [self._vulnerability_to_dict(vuln) for vuln in vulnerabilities],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": (total_count + page_size - 1) // page_size
            },
            "aggregations": aggregations,
            "filters_applied": filters or {},
            "search_query": query
        }
    
    def search_scans(
        self,
        user_id: int,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "upload_time",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Advanced scan search with filters"""
        
        # Base query
        base_query = self.db.query(Scan).filter(Scan.user_id == user_id)
        
        # Apply text search
        if query:
            search_conditions = [
                Scan.filename.ilike(f"%{query}%"),
                Scan.original_filename.ilike(f"%{query}%"),
                Scan.raw_data.ilike(f"%{query}%")
            ]
            base_query = base_query.filter(or_(*search_conditions))
        
        # Apply filters
        if filters:
            base_query = self._apply_scan_filters(base_query, filters)
        
        # Get total count
        total_count = base_query.count()
        
        # Apply sorting
        base_query = self._apply_sorting(base_query, Scan, sort_by, sort_order)
        
        # Apply pagination
        offset = (page - 1) * page_size
        scans = base_query.offset(offset).limit(page_size).all()
        
        # Calculate aggregations
        aggregations = self._calculate_scan_aggregations(user_id, filters)
        
        return {
            "results": [self._scan_to_dict(scan) for scan in scans],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": (total_count + page_size - 1) // page_size
            },
            "aggregations": aggregations,
            "filters_applied": filters or {},
            "search_query": query
        }
    
    def search_audit_logs(
        self,
        user_id: int,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "timestamp",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Advanced audit log search with filters"""
        
        # Base query
        base_query = self.db.query(AuditLog).filter(AuditLog.user_id == user_id)
        
        # Apply text search
        if query:
            search_conditions = [
                AuditLog.action.ilike(f"%{query}%"),
                AuditLog.resource_type.ilike(f"%{query}%"),
                func.cast(AuditLog.details, String).ilike(f"%{query}%"),
                AuditLog.ip_address.ilike(f"%{query}%"),
                AuditLog.user_agent.ilike(f"%{query}%")
            ]
            # Only add resource_id search if query is numeric
            try:
                resource_id_query = int(query)
                search_conditions.append(AuditLog.resource_id == resource_id_query)
            except ValueError:
                pass
            
            base_query = base_query.filter(or_(*search_conditions))
        
        # Apply filters
        if filters:
            base_query = self._apply_audit_log_filters(base_query, filters)
        
        # Get total count
        total_count = base_query.count()
        
        # Apply sorting
        base_query = self._apply_sorting(base_query, AuditLog, sort_by, sort_order)
        
        # Apply pagination
        offset = (page - 1) * page_size
        audit_logs = base_query.offset(offset).limit(page_size).all()
        
        # Calculate aggregations
        aggregations = self._calculate_audit_log_aggregations(user_id, filters)
        
        return {
            "results": [self._audit_log_to_dict(log) for log in audit_logs],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": (total_count + page_size - 1) // page_size
            },
            "aggregations": aggregations,
            "filters_applied": filters or {},
            "search_query": query
        }
    
    def global_search(
        self,
        user_id: int,
        query: str,
        categories: Optional[List[str]] = None,
        limit: int = 10
    ) -> Dict[str, List[Dict]]:
        """Global search across all entities"""
        
        if not categories:
            categories = ["vulnerabilities", "scans", "audit_logs", "reports"]
        
        results = {}
        
        if "vulnerabilities" in categories:
            vuln_results = self.search_vulnerabilities(
                user_id=user_id,
                query=query,
                page_size=limit
            )
            results["vulnerabilities"] = vuln_results["results"]
        
        if "scans" in categories:
            scan_results = self.search_scans(
                user_id=user_id,
                query=query,
                page_size=limit
            )
            results["scans"] = scan_results["results"]
        
        if "audit_logs" in categories:
            audit_results = self.search_audit_logs(
                user_id=user_id,
                query=query,
                page_size=limit
            )
            results["audit_logs"] = audit_results["results"]
        
        if "reports" in categories:
            report_results = self._search_reports(user_id, query, limit)
            results["reports"] = report_results
        
        return results
    
    def get_search_suggestions(
        self,
        user_id: int,
        query: str,
        category: str = "vulnerabilities"
    ) -> List[str]:
        """Get search suggestions based on partial query"""
        
        suggestions = []
        
        if category == "vulnerabilities":
            # Get service name suggestions
            service_suggestions = (
                self.db.query(Vulnerability.service_name)
                .join(Scan)
                .filter(
                    and_(
                        Scan.user_id == user_id,
                        Vulnerability.service_name.ilike(f"%{query}%"),
                        Vulnerability.service_name.isnot(None)
                    )
                )
                .distinct()
                .limit(5)
                .all()
            )
            suggestions.extend([s[0] for s in service_suggestions if s[0]])
            
            # Get CVE suggestions
            cve_suggestions = (
                self.db.query(Vulnerability.cve_id)
                .join(Scan)
                .filter(
                    and_(
                        Scan.user_id == user_id,
                        Vulnerability.cve_id.ilike(f"%{query}%"),
                        Vulnerability.cve_id.isnot(None)
                    )
                )
                .distinct()
                .limit(5)
                .all()
            )
            suggestions.extend([s[0] for s in cve_suggestions if s[0]])
        
        elif category == "scans":
            # Get filename suggestions
            filename_suggestions = (
                self.db.query(Scan.filename)
                .filter(
                    and_(
                        Scan.user_id == user_id,
                        Scan.filename.ilike(f"%{query}%")
                    )
                )
                .distinct()
                .limit(5)
                .all()
            )
            suggestions.extend([s[0] for s in filename_suggestions if s[0]])
            
            # Get filename suggestions for target hosts
            host_suggestions = (
                self.db.query(Scan.original_filename)
                .filter(
                    and_(
                        Scan.user_id == user_id,
                        Scan.original_filename.ilike(f"%{query}%"),
                        Scan.original_filename.isnot(None)
                    )
                )
                .distinct()
                .limit(5)
                .all()
            )
            suggestions.extend([s[0] for s in host_suggestions if s[0]])
        
        # Remove duplicates and limit
        return list(set(suggestions))[:10]
    
    def get_filter_options(self, user_id: int, category: str) -> Dict[str, List]:
        """Get available filter options for a category"""
        
        if category == "vulnerabilities":
            return self._get_vulnerability_filter_options(user_id)
        elif category == "scans":
            return self._get_scan_filter_options(user_id)
        elif category == "audit_logs":
            return self._get_audit_log_filter_options(user_id)
        else:
            return {}
    
    def _apply_vulnerability_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to vulnerability query"""
        
        if "severity" in filters and filters["severity"]:
            if isinstance(filters["severity"], list):
                query = query.filter(Vulnerability.severity.in_(filters["severity"]))
            else:
                query = query.filter(Vulnerability.severity == filters["severity"])
        
        if "service_name" in filters and filters["service_name"]:
            if isinstance(filters["service_name"], list):
                query = query.filter(Vulnerability.service_name.in_(filters["service_name"]))
            else:
                query = query.filter(Vulnerability.service_name == filters["service_name"])
        
        if "cvss_score_min" in filters and filters["cvss_score_min"] is not None:
            query = query.filter(Vulnerability.cvss_score >= filters["cvss_score_min"])
        
        if "cvss_score_max" in filters and filters["cvss_score_max"] is not None:
            query = query.filter(Vulnerability.cvss_score <= filters["cvss_score_max"])
        
        if "port" in filters and filters["port"]:
            if isinstance(filters["port"], list):
                query = query.filter(Vulnerability.port.in_(filters["port"]))
            else:
                query = query.filter(Vulnerability.port == filters["port"])
        
        if "has_cve" in filters:
            if filters["has_cve"]:
                query = query.filter(Vulnerability.cve_id.isnot(None))
            else:
                query = query.filter(Vulnerability.cve_id.is_(None))
        
        if "date_from" in filters and filters["date_from"]:
            date_from = datetime.fromisoformat(filters["date_from"])
            query = query.join(Scan).filter(Scan.upload_time >= date_from)
        
        if "date_to" in filters and filters["date_to"]:
            date_to = datetime.fromisoformat(filters["date_to"])
            query = query.join(Scan).filter(Scan.upload_time <= date_to)
        
        return query
    
    def _apply_scan_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to scan query"""
        
        if "date_from" in filters and filters["date_from"]:
            date_from = datetime.fromisoformat(filters["date_from"])
            query = query.filter(Scan.upload_time >= date_from)
        
        if "date_to" in filters and filters["date_to"]:
            date_to = datetime.fromisoformat(filters["date_to"])
            query = query.filter(Scan.upload_time <= date_to)
        
        if "has_vulnerabilities" in filters:
            if filters["has_vulnerabilities"]:
                query = query.filter(Scan.vulnerabilities.any())
            else:
                query = query.filter(~Scan.vulnerabilities.any())
        
        if "vulnerability_count_min" in filters and filters["vulnerability_count_min"] is not None:
            subquery = (
                self.db.query(Vulnerability.scan_id, func.count(Vulnerability.id).label('vuln_count'))
                .group_by(Vulnerability.scan_id)
                .subquery()
            )
            query = query.join(subquery, Scan.id == subquery.c.scan_id)
            query = query.filter(subquery.c.vuln_count >= filters["vulnerability_count_min"])
        
        if "target_host" in filters and filters["target_host"]:
            query = query.filter(Scan.raw_data.ilike(f"%{filters['target_host']}%"))
        
        return query
    
    def _apply_audit_log_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to audit log query"""
        
        if "action" in filters and filters["action"]:
            if isinstance(filters["action"], list):
                query = query.filter(AuditLog.action.in_(filters["action"]))
            else:
                query = query.filter(AuditLog.action == filters["action"])
        
        if "resource_type" in filters and filters["resource_type"]:
            if isinstance(filters["resource_type"], list):
                query = query.filter(AuditLog.resource_type.in_(filters["resource_type"]))
            else:
                query = query.filter(AuditLog.resource_type == filters["resource_type"])
        
        if "date_from" in filters and filters["date_from"]:
            date_from = datetime.fromisoformat(filters["date_from"])
            query = query.filter(AuditLog.timestamp >= date_from)
        
        if "date_to" in filters and filters["date_to"]:
            date_to = datetime.fromisoformat(filters["date_to"])
            query = query.filter(AuditLog.timestamp <= date_to)
        
        if "ip_address" in filters and filters["ip_address"]:
            query = query.filter(AuditLog.ip_address == filters["ip_address"])
        
        return query
    
    def _apply_sorting(self, query, model_class, sort_by: str, sort_order: str):
        """Apply sorting to query"""
        
        if not hasattr(model_class, sort_by):
            sort_by = "id"  # Default fallback
        
        sort_column = getattr(model_class, sort_by)
        
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        return query
    
    def _calculate_vulnerability_aggregations(self, user_id: int, filters: Optional[Dict] = None) -> Dict:
        """Calculate vulnerability aggregations"""
        
        base_query = (
            self.db.query(Vulnerability)
            .join(Scan)
            .filter(Scan.user_id == user_id)
        )
        
        if filters:
            base_query = self._apply_vulnerability_filters(base_query, filters)
        
        # Severity distribution
        severity_counts = (
            base_query
            .with_entities(Vulnerability.severity, func.count(Vulnerability.id))
            .group_by(Vulnerability.severity)
            .all()
        )
        
        # Service distribution
        service_counts = (
            base_query
            .with_entities(Vulnerability.service_name, func.count(Vulnerability.id))
            .filter(Vulnerability.service_name.isnot(None))
            .group_by(Vulnerability.service_name)
            .order_by(desc(func.count(Vulnerability.id)))
            .limit(10)
            .all()
        )
        
        # CVSS score statistics
        cvss_stats = (
            base_query
            .filter(Vulnerability.cvss_score.isnot(None))
            .with_entities(
                func.min(Vulnerability.cvss_score).label('min_cvss'),
                func.max(Vulnerability.cvss_score).label('max_cvss'),
                func.avg(Vulnerability.cvss_score).label('avg_cvss')
            )
            .first()
        )
        
        return {
            "severity_distribution": dict(severity_counts),
            "service_distribution": dict(service_counts),
            "cvss_statistics": {
                "min": float(cvss_stats.min_cvss) if cvss_stats.min_cvss else 0,
                "max": float(cvss_stats.max_cvss) if cvss_stats.max_cvss else 0,
                "average": float(cvss_stats.avg_cvss) if cvss_stats.avg_cvss else 0
            } if cvss_stats else {"min": 0, "max": 0, "average": 0}
        }
    
    def _calculate_scan_aggregations(self, user_id: int, filters: Optional[Dict] = None) -> Dict:
        """Calculate scan aggregations"""
        
        base_query = self.db.query(Scan).filter(Scan.user_id == user_id)
        
        if filters:
            base_query = self._apply_scan_filters(base_query, filters)
        
        # Scan count by month
        scan_timeline = (
            base_query
            .with_entities(
                func.date_trunc('month', Scan.upload_time).label('month'),
                func.count(Scan.id).label('count')
            )
            .group_by(func.date_trunc('month', Scan.upload_time))
            .order_by(func.date_trunc('month', Scan.upload_time))
            .limit(12)
            .all()
        )
        
        return {
            "scan_timeline": [
                {
                    "month": month.isoformat() if month else None,
                    "count": count
                }
                for month, count in scan_timeline
            ]
        }
    
    def _calculate_audit_log_aggregations(self, user_id: int, filters: Optional[Dict] = None) -> Dict:
        """Calculate audit log aggregations"""
        
        base_query = self.db.query(AuditLog).filter(AuditLog.user_id == user_id)
        
        if filters:
            base_query = self._apply_audit_log_filters(base_query, filters)
        
        # Action distribution
        action_counts = (
            base_query
            .with_entities(AuditLog.action, func.count(AuditLog.id))
            .group_by(AuditLog.action)
            .order_by(desc(func.count(AuditLog.id)))
            .all()
        )
        
        # Resource type distribution
        resource_counts = (
            base_query
            .with_entities(AuditLog.resource_type, func.count(AuditLog.id))
            .group_by(AuditLog.resource_type)
            .order_by(desc(func.count(AuditLog.id)))
            .all()
        )
        
        return {
            "action_distribution": dict(action_counts),
            "resource_distribution": dict(resource_counts)
        }
    
    def _get_vulnerability_filter_options(self, user_id: int) -> Dict[str, List]:
        """Get filter options for vulnerabilities"""
        
        base_query = (
            self.db.query(Vulnerability)
            .join(Scan)
            .filter(Scan.user_id == user_id)
        )
        
        # Severity options
        severities = (
            base_query
            .with_entities(Vulnerability.severity)
            .filter(Vulnerability.severity.isnot(None))
            .distinct()
            .all()
        )
        
        # Service name options
        services = (
            base_query
            .with_entities(Vulnerability.service_name)
            .filter(Vulnerability.service_name.isnot(None))
            .distinct()
            .order_by(Vulnerability.service_name)
            .all()
        )
        
        # Port options (top 20)
        ports = (
            base_query
            .with_entities(Vulnerability.port)
            .filter(Vulnerability.port.isnot(None))
            .distinct()
            .order_by(Vulnerability.port)
            .limit(20)
            .all()
        )
        
        return {
            "severities": [s[0] for s in severities if s[0]],
            "services": [s[0] for s in services if s[0]],
            "ports": [p[0] for p in ports if p[0] is not None]
        }
    
    def _get_scan_filter_options(self, user_id: int) -> Dict[str, List]:
        """Get filter options for scans"""
        
        base_query = self.db.query(Scan).filter(Scan.user_id == user_id)
        
        # Filename options
        filenames = (
            base_query
            .with_entities(Scan.filename)
            .filter(Scan.filename.isnot(None))
            .distinct()
            .order_by(Scan.filename)
            .limit(50)
            .all()
        )
        
        return {
            "filenames": [f[0] for f in filenames]
        }
    
    def _get_audit_log_filter_options(self, user_id: int) -> Dict[str, List]:
        """Get filter options for audit logs"""
        
        base_query = self.db.query(AuditLog).filter(AuditLog.user_id == user_id)
        
        # Action options
        actions = (
            base_query
            .with_entities(AuditLog.action)
            .distinct()
            .order_by(AuditLog.action)
            .all()
        )
        
        # Resource type options
        resource_types = (
            base_query
            .with_entities(AuditLog.resource_type)
            .distinct()
            .order_by(AuditLog.resource_type)
            .all()
        )
        
        return {
            "actions": [a[0] for a in actions],
            "resource_types": [r[0] for r in resource_types]
        }
    
    def _search_reports(self, user_id: int, query: str, limit: int) -> List[Dict]:
        """Search reports"""
        
        reports = (
            self.db.query(Report)
            .filter(
                and_(
                    Report.user_id == user_id,
                    or_(
                        Report.title.ilike(f"%{query}%"),
                        Report.report_type.ilike(f"%{query}%"),
                        Report.content.ilike(f"%{query}%")
                    )
                )
            )
            .order_by(desc(Report.generated_at))
            .limit(limit)
            .all()
        )
        
        return [self._report_to_dict(report) for report in reports]
    
    def _vulnerability_to_dict(self, vuln: Vulnerability) -> Dict:
        """Convert vulnerability to dictionary"""
        return {
            "id": vuln.id,
            "service_name": vuln.service_name,
            "service_version": vuln.service_version,
            "port": vuln.port,
            "severity": vuln.severity,
            "cve_id": vuln.cve_id,
            "cvss_score": vuln.cvss_score,
            "description": vuln.description,
            "recommendation": vuln.recommendation,
            "scan_id": vuln.scan_id,
            "created_at": vuln.created_at.isoformat() if vuln.created_at else None
        }
    
    def _scan_to_dict(self, scan: Scan) -> Dict:
        """Convert scan to dictionary"""
        return {
            "id": scan.id,
            "filename": scan.filename,
            "original_filename": scan.original_filename,
            "status": scan.status,
            "upload_time": scan.upload_time.isoformat() if scan.upload_time else None,
            "processed_at": scan.processed_at.isoformat() if scan.processed_at else None,
            "file_size": scan.file_size,
            "vulnerability_count": len(scan.vulnerabilities) if scan.vulnerabilities else 0
        }
    
    def _audit_log_to_dict(self, log: AuditLog) -> Dict:
        """Convert audit log to dictionary"""
        return {
            "id": log.id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None
        }
    
    def _report_to_dict(self, report: Report) -> Dict:
        """Convert report to dictionary"""
        return {
            "id": report.id,
            "title": report.title,
            "report_type": report.report_type,
            "format": report.format,
            "file_path": report.file_path,
            "scan_id": report.scan_id,
            "generated_at": report.generated_at.isoformat() if report.generated_at else None
        }