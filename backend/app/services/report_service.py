"""
Report generation service
"""
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime

from app.models.report import Report
from app.models.scan import Scan
from app.models.vulnerability import Vulnerability
from app.services.llm_service import LLMService
from app.services.pdf_generator import PDFReportGenerator
from app.core.config import settings


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = LLMService()
        self.pdf_generator = PDFReportGenerator()
    
    async def generate_report(
        self,
        scan_id: int,
        report_type: str,
        user_id: int,
        format: str = "html"
    ) -> Report:
        """Generate a new report"""
        
        # Get scan and vulnerabilities
        scan = self.db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise ValueError("Scan not found")
        
        vulnerabilities = (
            self.db.query(Vulnerability)
            .filter(Vulnerability.scan_id == scan_id)
            .all()
        )
        
        # Generate content using LLM with enhanced data
        vuln_data = []
        for v in vulnerabilities:
            vuln_dict = {
                "service_name": v.service_name,
                "version": v.service_version,
                "port": v.port,
                "severity": v.severity,
                "cve_id": v.cve_id,
                "cvss_score": v.cvss_score,
                "description": v.description,
                "recommendation": v.recommendation,
                "status": v.status,
                "remediation_commands": v.remediation_commands or []
            }
            vuln_data.append(vuln_dict)
        
        content = await self.llm_service.generate_report(vuln_data, report_type)
        
        if not content:
            content = self._generate_fallback_report(vulnerabilities, report_type)
        
        # Create report record
        title = f"{report_type.title()} Report - {scan.filename}"
        
        report = Report(
            scan_id=scan_id,
            user_id=user_id,
            report_type=report_type,
            title=title,
            content=content,
            format=format
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        # Save to file if needed
        if format in ["pdf", "html"]:
            file_path = await self._save_report_file(report, content, format)
            report.file_path = file_path
            self.db.commit()
        
        return report
    
    def _generate_fallback_report(self, vulnerabilities: List[Vulnerability], report_type: str) -> str:
        """Generate fallback report when LLM is unavailable"""
        
        # Single detailed report type combining both executive and technical content
        return self._generate_detailed_fallback(vulnerabilities)
    
    def _generate_detailed_fallback(self, vulnerabilities: List[Vulnerability]) -> str:
        """Generate detailed report fallback combining executive and technical content"""
        
        total = len(vulnerabilities)
        critical = len([v for v in vulnerabilities if v.severity == "Critical"])
        high = len([v for v in vulnerabilities if v.severity == "High"])
        medium = len([v for v in vulnerabilities if v.severity == "Medium"])
        low = len([v for v in vulnerabilities if v.severity == "Low"])
        
        content = f"""
# Detailed Vulnerability Assessment Report

## Executive Summary
This report provides a comprehensive analysis of security vulnerabilities identified in your network infrastructure scan.

## Key Findings
- **Total Vulnerabilities**: {total}
- **Critical**: {critical}
- **High**: {high}
- **Medium**: {medium}
- **Low**: {low}

## Risk Assessment
"""
        
        if critical > 0:
            content += f"**IMMEDIATE ACTION REQUIRED**: {critical} critical vulnerabilities pose significant security risks.\n\n"
        
        if high > 0:
            content += f"**HIGH PRIORITY**: {high} high-severity vulnerabilities should be addressed within 48 hours.\n\n"
        
        content += """
## Recommendations
1. Prioritize patching of critical and high-severity vulnerabilities
2. Implement regular vulnerability scanning
3. Establish a formal patch management process
4. Consider implementing additional security controls

## Detailed Vulnerability Analysis

"""
        
        for i, vuln in enumerate(vulnerabilities[:20], 1):  # Limit to first 20
            content += f"""
### {i}. {vuln.service_name} - {vuln.severity}

- **Service**: {vuln.service_name} {vuln.service_version or ''}
- **Port**: {vuln.port}
- **Protocol**: {vuln.protocol}
- **CVE ID**: {vuln.cve_id or 'N/A'}
- **CVSS Score**: {vuln.cvss_score or 'N/A'}
- **Description**: {vuln.description or 'No description available'}
- **Recommendation**: {vuln.recommendation or 'Update to latest version'}

---
"""
        
        if len(vulnerabilities) > 20:
            content += f"\n*Note: Showing first 20 of {len(vulnerabilities)} vulnerabilities.*\n"
            
        content += """

## Next Steps
Please coordinate with your IT team to implement the recommended remediation actions, starting with critical and high-severity vulnerabilities.
"""
        
        return content
    
    async def _save_report_file(self, report: Report, content: str, format: str) -> str:
        """Save report content to file"""
        
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(settings.UPLOAD_DIR, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{report.id}_{timestamp}.{format}"
        file_path = os.path.join(reports_dir, filename)
        
        if format == "pdf":
            # Generate PDF using the PDF generator
            await self._generate_pdf_report(report, file_path)
        else:
            # Save as HTML or text
            with open(file_path, 'w', encoding='utf-8') as f:
                if format == "html":
                    # Convert newlines to HTML breaks outside of f-string
                    content_with_breaks = content.replace('\n', '<br>\n')
                    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{report.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2, h3 {{ color: #333; }}
        .severity-critical {{ color: #d32f2f; }}
        .severity-high {{ color: #f57c00; }}
        .severity-medium {{ color: #fbc02d; }}
        .severity-low {{ color: #388e3c; }}
    </style>
</head>
<body>
{content_with_breaks}
</body>
</html>
"""
                    f.write(html_content)
                else:
                    f.write(content)
        
        return file_path
    
    async def _generate_pdf_report(self, report: Report, file_path: str) -> None:
        """Generate PDF report using the PDF generator"""
        
        # Get scan and vulnerability data
        scan = self.db.query(Scan).filter(Scan.id == report.scan_id).first()
        vulnerabilities = (
            self.db.query(Vulnerability)
            .filter(Vulnerability.scan_id == report.scan_id)
            .all()
        )
        
        # Prepare scan data
        target = 'Unknown'
        if scan:
            # Try to get target from parsed data first, fallback to filename
            if scan.parsed_data and isinstance(scan.parsed_data, dict):
                target = scan.parsed_data.get('target', scan.filename)
            else:
                target = scan.filename
        
        scan_data = {
            'target': target,
            'scan_date': scan.upload_time.strftime("%B %d, %Y") if scan and scan.upload_time else 'Unknown'
        }
        
        # Prepare vulnerability data with enhanced information
        vuln_data = []
        for vuln in vulnerabilities:
            vuln_dict = {
                'service_name': vuln.service_name or 'Unknown',
                'version': vuln.service_version or 'Unknown',
                'port': vuln.port or 'Unknown',
                'severity': vuln.severity or 'Unknown',
                'cve_id': vuln.cve_id or 'N/A',
                'cvss_score': vuln.cvss_score or 0,
                'description': vuln.description or 'No description available',
                'recommendation': vuln.recommendation or 'No recommendation available',
                'remediation_commands': vuln.remediation_commands or [],
                'status': vuln.status or 'open'
            }
            vuln_data.append(vuln_dict)
        
        # Generate PDF report
        print(f"Generating PDF report at: {file_path}")
        print(f"Scan data: {scan_data}")
        print(f"Number of vulnerabilities: {len(vuln_data)}")
        
        self.pdf_generator.generate_vulnerability_report(
            scan_data=scan_data,
            vulnerabilities=vuln_data,
            output_path=file_path,
            report_type=report.report_type
        )
        
        print(f"PDF generation completed for: {file_path}")
    
    def get_report(self, report_id: int) -> Optional[Report]:
        """Get report by ID"""
        return self.db.query(Report).filter(Report.id == report_id).first()
    
    def get_user_reports(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Report]:
        """Get reports for a user"""
        return (
            self.db.query(Report)
            .filter(Report.user_id == user_id)
            .order_by(Report.generated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def delete_report(self, report_id: int) -> bool:
        """Delete a report and its associated file"""
        try:
            # Get the report
            report = self.db.query(Report).filter(Report.id == report_id).first()
            if not report:
                return False
            
            # Delete the file if it exists
            if report.file_path and os.path.exists(report.file_path):
                try:
                    os.remove(report.file_path)
                    print(f"Deleted report file: {report.file_path}")
                except OSError as e:
                    print(f"Warning: Could not delete report file {report.file_path}: {e}")
                    # Continue with database deletion even if file deletion fails
            
            # Delete the database record
            self.db.delete(report)
            self.db.commit()
            
            print(f"Successfully deleted report {report_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting report {report_id}: {e}")
            self.db.rollback()
            return False
