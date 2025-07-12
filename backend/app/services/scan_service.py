"""
Scan processing service
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import asyncio
import logging

from app.models.scan import Scan
from app.models.vulnerability import Vulnerability
from app.services.xml_parser import NmapXMLParser
from app.services.llm_service import LLMService
from app.services.cve_service import CVEService
from app.services.websocket_service import manager

logger = logging.getLogger(__name__)


class ScanService:
    def __init__(self, db: Session):
        self.db = db
        self.xml_parser = NmapXMLParser()
        self.llm_service = LLMService()
        self.cve_service = CVEService()
    
    async def create_scan(self, user_id: int, filename: str, xml_content: str, file_size: int) -> Scan:
        """Create and process a new scan"""
        
        # Create scan record
        scan = Scan(
            user_id=user_id,
            filename=filename,
            original_filename=filename,
            file_size=file_size,
            raw_data=xml_content,
            status="processing"
        )
        
        self.db.add(scan)
        self.db.commit()
        self.db.refresh(scan)
        
        # Send initial scan started notification
        await manager.update_scan_progress(user_id, scan.id, {
            "progress": 0,
            "status": "started",
            "message": f"Processing scan: {filename}"
        })
        
        # Process scan asynchronously
        try:
            await self._process_scan(scan, xml_content)
        except Exception as e:
            logger.error(f"Error processing scan {scan.id}: {e}")
            scan.status = "failed"
            scan.error_message = str(e)
            self.db.commit()
            
            # Send failure notification
            await manager.update_scan_progress(user_id, scan.id, {
                "progress": 0,
                "status": "failed",
                "message": f"Scan processing failed: {str(e)}"
            })
            raise
        
        return scan
    
    async def _process_scan(self, scan: Scan, xml_content: str):
        """Process scan XML and extract vulnerabilities"""
        try:
            # Send progress update - XML parsing
            await manager.update_scan_progress(scan.user_id, scan.id, {
                "progress": 10,
                "status": "parsing",
                "message": "Parsing XML file..."
            })
            
            # Parse XML
            parsed_data = self.xml_parser.parse_xml_file(xml_content)
            scan.parsed_data = parsed_data
            
            # Send progress update - vulnerability extraction
            await manager.update_scan_progress(scan.user_id, scan.id, {
                "progress": 30,
                "status": "extracting",
                "message": "Extracting vulnerabilities..."
            })
            
            # Extract vulnerabilities
            vulnerabilities = []
            services = parsed_data.get("services", [])
            total_services = len(services)
            critical_vulns = []
            
            for idx, service in enumerate(services):
                # Send progress update during vulnerability processing
                progress = 30 + (40 * (idx + 1) / total_services)
                await manager.update_scan_progress(scan.user_id, scan.id, {
                    "progress": int(progress),
                    "status": "analyzing",
                    "message": f"Analyzing service {idx + 1}/{total_services}: {service.get('service_name', 'unknown')}"
                })
                
                for vuln_data in service.get("potential_vulnerabilities", []):
                    # Create vulnerability record
                    vulnerability = Vulnerability(
                        scan_id=scan.id,
                        service_name=service["service_name"],
                        service_version=service["version"],
                        port=service["port"],
                        protocol=service["protocol"],
                        description=vuln_data["description"],
                        severity=vuln_data["severity"],
                        status="open"
                    )
                    
                    # Enhance with CVE information
                    await self._enhance_vulnerability_with_cve(vulnerability, service)
                    
                    # Get LLM analysis
                    await self._enhance_vulnerability_with_llm(vulnerability, service)
                    
                    # Track critical vulnerabilities for immediate notification
                    if vulnerability.severity == "Critical":
                        critical_vulns.append({
                            "service_name": vulnerability.service_name,
                            "version": vulnerability.service_version,
                            "port": vulnerability.port,
                            "description": vulnerability.description,
                            "cve_id": vulnerability.cve_id
                        })
                    
                    vulnerabilities.append(vulnerability)
            
            # Send progress update - saving data
            await manager.update_scan_progress(scan.user_id, scan.id, {
                "progress": 80,
                "status": "saving",
                "message": "Saving scan results..."
            })
            
            # Save vulnerabilities
            self.db.add_all(vulnerabilities)
            
            # Update scan status
            scan.status = "completed"
            scan.processed_at = datetime.utcnow()
            
            self.db.commit()
            
            # Send completion notification with results
            results = {
                "total_vulnerabilities": len(vulnerabilities),
                "critical_count": len(critical_vulns),
                "high_count": len([v for v in vulnerabilities if v.severity == "High"]),
                "medium_count": len([v for v in vulnerabilities if v.severity == "Medium"]),
                "low_count": len([v for v in vulnerabilities if v.severity == "Low"]),
                "services_analyzed": total_services
            }
            
            await manager.notify_scan_complete(scan.user_id, scan.id, results)
            
            # Send critical vulnerability alerts if any
            for critical_vuln in critical_vulns:
                await manager.notify_critical_vulnerability(scan.user_id, critical_vuln)
            
        except Exception as e:
            logger.error(f"Error in _process_scan: {e}")
            raise
    
    async def _enhance_vulnerability_with_cve(self, vulnerability: Vulnerability, service: dict):
        """Enhance vulnerability with CVE information"""
        try:
            service_name = service["service_name"]
            version = service["version"]
            product = service["product"]
            
            logger.info(f"Looking up CVE for {service_name} {version} {product}")
            
            cve_info = await self.cve_service.lookup_cve(
                service_name,
                version,
                product
            )
            
            if cve_info and not cve_info.get("no_cve_found"):
                logger.info(f"Found CVE data for {service_name}: {cve_info.get('cve_id')}")
                vulnerability.cve_id = cve_info.get("cve_id")
                vulnerability.cvss_score = cve_info.get("cvss_score")
                if cve_info.get("severity"):
                    vulnerability.severity = cve_info["severity"]
            else:
                logger.info(f"No CVE found for {service_name} {version}")
                # Ensure fields are explicitly set to indicate no CVE found
                vulnerability.cve_id = None
                vulnerability.cvss_score = None
                
        except Exception as e:
            logger.error(f"CVE lookup failed for {service.get('service_name', 'unknown')}: {e}")
            # Ensure fields are explicitly set to None on error
            vulnerability.cve_id = None
            vulnerability.cvss_score = None
    
    async def _enhance_vulnerability_with_llm(self, vulnerability: Vulnerability, service: dict):
        """Enhance vulnerability with LLM analysis"""
        try:
            service_name = service["service_name"]
            version = service["version"]
            
            logger.info(f"Getting LLM analysis for {service_name} {version}")
            
            analysis = await self.llm_service.analyze_vulnerability(
                service_name=service_name,
                version=version,
                port=service["port"],
                vulnerability_description=vulnerability.description,
                cve_id=vulnerability.cve_id
            )
            
            if analysis:
                logger.info(f"LLM analysis successful for {service_name}")
                if analysis.get("recommendation"):
                    vulnerability.recommendation = analysis["recommendation"]
                if analysis.get("remediation_commands"):
                    vulnerability.remediation_commands = analysis["remediation_commands"]
                if analysis.get("severity") and not vulnerability.cvss_score:
                    vulnerability.severity = analysis["severity"]
            else:
                logger.warning(f"No LLM analysis returned for {service_name}")
                
        except Exception as e:
            logger.error(f"LLM analysis failed for {service.get('service_name', 'unknown')}: {e}")
            # Provide basic fallback recommendation
            if not vulnerability.recommendation:
                vulnerability.recommendation = f"Update {service.get('service_name', 'service')} to the latest version and review security configuration"
    
    def get_scan(self, scan_id: int) -> Optional[Scan]:
        """Get scan by ID"""
        return self.db.query(Scan).filter(Scan.id == scan_id).first()
    
    def get_user_scans(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Scan]:
        """Get scans for a user"""
        return (
            self.db.query(Scan)
            .filter(Scan.user_id == user_id)
            .order_by(Scan.upload_time.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def delete_scan(self, scan_id: int):
        """Delete a scan and its related data"""
        from app.models.report import Report
        from app.models.feedback import Feedback
        from app.models.patch import Patch
        
        try:
            # Delete in the correct order to respect foreign key constraints
            
            # 1. Delete patches related to vulnerabilities in this scan
            vulnerability_ids = self.db.query(Vulnerability.id).filter(Vulnerability.scan_id == scan_id).all()
            if vulnerability_ids:
                vuln_ids = [v.id for v in vulnerability_ids]
                self.db.query(Patch).filter(Patch.vulnerability_id.in_(vuln_ids)).delete(synchronize_session=False)
            
            # 2. Delete feedback related to vulnerabilities in this scan
            if vulnerability_ids:
                self.db.query(Feedback).filter(Feedback.vulnerability_id.in_(vuln_ids)).delete(synchronize_session=False)
            
            # 3. Delete feedback directly related to this scan
            self.db.query(Feedback).filter(Feedback.scan_id == scan_id).delete()
            
            # 4. Delete reports related to this scan
            self.db.query(Report).filter(Report.scan_id == scan_id).delete()
            
            # 5. Delete vulnerabilities
            self.db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id).delete()
            
            # 6. Finally, delete the scan itself
            self.db.query(Scan).filter(Scan.id == scan_id).delete()
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting scan {scan_id}: {e}")
            raise