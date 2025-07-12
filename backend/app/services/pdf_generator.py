"""
PDF Report Generator for VulnPatch AI
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white, red, orange, yellow, green
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime
from typing import List, Dict, Any
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Docker
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
import base64


class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=HexColor('#1976d2'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Header styles
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=HexColor('#1976d2'),
            spaceBefore=20,
            spaceAfter=12,
            borderWidth=0,
            borderColor=HexColor('#1976d2'),
            borderPadding=5
        ))
        
        # Executive summary style
        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=black,
            spaceBefore=6,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        ))
        
        # Vulnerability item style
        self.styles.add(ParagraphStyle(
            name='VulnItem',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceBefore=8,
            spaceAfter=4,
            leftIndent=20
        ))
        
        # Risk assessment styles
        self.styles.add(ParagraphStyle(
            name='HighRisk',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#d32f2f'),
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='MediumRisk',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#f57c00'),
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='LowRisk',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#388e3c'),
            fontName='Helvetica-Bold'
        ))

    def generate_vulnerability_report(
        self,
        scan_data: Dict[str, Any],
        vulnerabilities: List[Dict[str, Any]],
        output_path: str,
        report_type: str = "comprehensive"
    ) -> str:
        """Generate a comprehensive vulnerability assessment PDF report"""
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build the story (content)
        story = []
        
        # Title Page
        story.extend(self._build_title_page(scan_data))
        story.append(PageBreak())
        
        # Executive Summary
        story.extend(self._build_executive_summary(vulnerabilities))
        story.append(PageBreak())
        
        # Vulnerability Overview
        story.extend(self._build_vulnerability_overview(vulnerabilities))
        
        # Risk Assessment Chart
        chart_path = self._create_risk_chart(vulnerabilities)
        if chart_path:
            story.append(Spacer(1, 20))
            story.append(RLImage(chart_path, width=5*inch, height=3*inch))
            story.append(Spacer(1, 20))
        
        story.append(PageBreak())
        
        # Detailed Vulnerabilities
        story.extend(self._build_detailed_vulnerabilities(vulnerabilities))
        story.append(PageBreak())
        
        # Patch Recommendations
        story.extend(self._build_patch_recommendations(vulnerabilities))
        story.append(PageBreak())
        
        # Risk Assessment Matrix
        story.extend(self._build_risk_assessment(vulnerabilities))
        
        # Build PDF
        try:
            doc.build(story)
            print(f"PDF successfully created at: {output_path}")
            
            # Verify the PDF file was created and has content
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"PDF file size: {file_size} bytes")
                if file_size == 0:
                    print("WARNING: PDF file is empty!")
            else:
                print("ERROR: PDF file was not created!")
            
        except Exception as e:
            print(f"Error building PDF: {e}")
            raise e
        
        # Clean up temporary chart
        if chart_path and os.path.exists(chart_path):
            try:
                os.remove(chart_path)
            except Exception as e:
                print(f"Warning: Could not clean up chart file: {e}")
        
        return output_path

    def _build_title_page(self, scan_data: Dict[str, Any]) -> List:
        """Build the title page"""
        story = []
        
        # Main title
        story.append(Paragraph("VulnPatch AI", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Subtitle
        story.append(Paragraph(
            "Intelligent Vulnerability Assessment Report",
            self.styles['Heading2']
        ))
        story.append(Spacer(1, 30))
        
        # Report details table
        report_data = [
            ['Report Generated:', datetime.now().strftime("%B %d, %Y at %I:%M %p")],
            ['Scan Target:', scan_data.get('target', 'N/A')],
            ['Scan Date:', scan_data.get('scan_date', 'N/A')],
            ['Report Type:', 'Comprehensive Vulnerability Assessment'],
            ['AI Model:', 'GPT-4 Enhanced Analysis']
        ]
        
        report_table = Table(report_data, colWidths=[2*inch, 4*inch])
        report_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [white, HexColor('#f5f5f5')]),
            ('BOX', (0, 0), (-1, -1), 1, black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, black),
        ]))
        
        story.append(report_table)
        story.append(Spacer(1, 50))
        
        # Disclaimer
        disclaimer = """
        <b>CONFIDENTIAL DOCUMENT</b><br/>
        This vulnerability assessment report contains sensitive security information. 
        Distribution should be limited to authorized personnel only. The findings and 
        recommendations in this report are based on automated scanning and AI analysis 
        and should be validated by security professionals.
        """
        story.append(Paragraph(disclaimer, self.styles['Normal']))
        
        return story

    def _build_executive_summary(self, vulnerabilities: List[Dict[str, Any]]) -> List:
        """Build executive summary section"""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        # Calculate statistics
        total_vulns = len(vulnerabilities)
        critical = len([v for v in vulnerabilities if v.get('severity') == 'Critical'])
        high = len([v for v in vulnerabilities if v.get('severity') == 'High'])
        medium = len([v for v in vulnerabilities if v.get('severity') == 'Medium'])
        low = len([v for v in vulnerabilities if v.get('severity') == 'Low'])
        
        # Summary paragraph
        summary_text = f"""
        This vulnerability assessment identified <b>{total_vulns}</b> security vulnerabilities 
        across the scanned network infrastructure. The automated analysis, enhanced by 
        Large Language Model (LLM) capabilities, provides intelligent prioritization and 
        actionable remediation guidance.
        """
        story.append(Paragraph(summary_text, self.styles['ExecutiveSummary']))
        story.append(Spacer(1, 15))
        
        # Risk breakdown table
        risk_data = [
            ['Severity Level', 'Count', 'Percentage', 'Risk Impact'],
            ['Critical', str(critical), f"{(critical/total_vulns*100):.1f}%" if total_vulns > 0 else "0%", 'Immediate Action Required'],
            ['High', str(high), f"{(high/total_vulns*100):.1f}%" if total_vulns > 0 else "0%", 'Address Within 48 Hours'],
            ['Medium', str(medium), f"{(medium/total_vulns*100):.1f}%" if total_vulns > 0 else "0%", 'Address Within 1 Week'],
            ['Low', str(low), f"{(low/total_vulns*100):.1f}%" if total_vulns > 0 else "0%", 'Address During Maintenance']
        ]
        
        risk_table = Table(risk_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 2.5*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f8f8')]),
            ('BOX', (0, 0), (-1, -1), 1, black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, black),
        ]))
        
        story.append(risk_table)
        story.append(Spacer(1, 20))
        
        # Key recommendations
        recommendations = """
        <b>Key Recommendations:</b><br/>
        1. <b>Immediate Action:</b> Address all critical vulnerabilities within 24 hours<br/>
        2. <b>Patch Management:</b> Implement automated patch deployment for routine updates<br/>
        3. <b>Continuous Monitoring:</b> Establish regular vulnerability scanning schedule<br/>
        4. <b>Risk Assessment:</b> Prioritize patches based on CVSS scores and business impact<br/>
        5. <b>Documentation:</b> Maintain detailed records of all remediation activities
        """
        story.append(Paragraph(recommendations, self.styles['ExecutiveSummary']))
        
        return story

    def _build_vulnerability_overview(self, vulnerabilities: List[Dict[str, Any]]) -> List:
        """Build vulnerability overview section"""
        story = []
        
        story.append(Paragraph("Vulnerability Overview", self.styles['SectionHeader']))
        
        # Group vulnerabilities by service
        services = {}
        for vuln in vulnerabilities:
            service = vuln.get('service_name', 'Unknown')
            if service not in services:
                services[service] = []
            services[service].append(vuln)
        
        # Service summary table
        service_data = [['Service', 'Version', 'Port', 'Vulnerabilities', 'Highest Severity']]
        
        for service, vulns in services.items():
            version = vulns[0].get('version', 'Unknown')
            port = vulns[0].get('port', 'Unknown')
            vuln_count = len(vulns)
            
            # Determine highest severity
            severity_order = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
            highest_severity = max(vulns, key=lambda v: severity_order.get(v.get('severity', 'Low'), 0))
            
            service_data.append([
                service,
                str(version),
                str(port),
                str(vuln_count),
                highest_severity.get('severity', 'Unknown')
            ])
        
        service_table = Table(service_data, colWidths=[1.5*inch, 1.2*inch, 0.8*inch, 1*inch, 1.2*inch])
        service_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f8f8')]),
            ('BOX', (0, 0), (-1, -1), 1, black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, black),
        ]))
        
        story.append(service_table)
        
        return story

    def _create_risk_chart(self, vulnerabilities: List[Dict[str, Any]]) -> str:
        """Create a risk assessment chart"""
        try:
            # Count by severity
            severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
            for vuln in vulnerabilities:
                severity = vuln.get('severity', 'Low')
                if severity in severity_counts:
                    severity_counts[severity] += 1
            
            # Skip chart if no vulnerabilities
            if sum(severity_counts.values()) == 0:
                return None
            
            # Create chart with explicit figure and axis
            plt.ioff()  # Turn off interactive mode
            fig, ax = plt.subplots(figsize=(8, 6))
            
            severities = list(severity_counts.keys())
            counts = list(severity_counts.values())
            colors_map = {'Critical': '#d32f2f', 'High': '#f57c00', 'Medium': '#fbc02d', 'Low': '#388e3c'}
            chart_colors = [colors_map[s] for s in severities]
            
            bars = ax.bar(severities, counts, color=chart_colors)
            
            # Customize chart
            ax.set_title('Vulnerability Distribution by Severity', fontsize=14, fontweight='bold')
            ax.set_ylabel('Number of Vulnerabilities', fontsize=12)
            ax.set_xlabel('Severity Level', fontsize=12)
            
            # Add value labels on bars
            for bar, count in zip(bars, counts):
                if count > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                           str(count), ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            
            # Ensure /tmp directory exists and save to temporary file
            os.makedirs('/tmp', exist_ok=True)
            chart_path = '/tmp/risk_chart.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            plt.ion()  # Turn interactive mode back on
            
            # Verify file was created
            if os.path.exists(chart_path) and os.path.getsize(chart_path) > 0:
                return chart_path
            else:
                print("Chart file was not created properly")
                return None
            
        except Exception as e:
            print(f"Error creating chart: {e}")
            # Clean up any partial matplotlib state
            try:
                plt.close('all')
                plt.ion()
            except:
                pass
            return None

    def _build_detailed_vulnerabilities(self, vulnerabilities: List[Dict[str, Any]]) -> List:
        """Build detailed vulnerabilities section"""
        story = []
        
        story.append(Paragraph("Detailed Vulnerability Analysis", self.styles['SectionHeader']))
        
        # Sort vulnerabilities by severity
        severity_order = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
        sorted_vulns = sorted(vulnerabilities, 
                             key=lambda v: severity_order.get(v.get('severity', 'Low'), 0), 
                             reverse=True)
        
        for i, vuln in enumerate(sorted_vulns, 1):
            # Vulnerability header
            severity = vuln.get('severity', 'Unknown')
            service = vuln.get('service_name', 'Unknown')
            cve = vuln.get('cve_id', 'N/A')
            
            header_text = f"<b>{i}. {service} - {severity} Severity</b>"
            if cve != 'N/A':
                header_text += f" ({cve})"
            
            story.append(Paragraph(header_text, self.styles['Heading3']))
            
            # Vulnerability details table
            vuln_data = [
                ['Service:', vuln.get('service_name', 'N/A')],
                ['Version:', vuln.get('version', 'N/A')],
                ['Port:', str(vuln.get('port', 'N/A'))],
                ['CVE ID:', vuln.get('cve_id', 'N/A')],
                ['CVSS Score:', str(vuln.get('cvss_score', 'N/A'))],
                ['Severity:', vuln.get('severity', 'N/A')]
            ]
            
            vuln_table = Table(vuln_data, colWidths=[1.5*inch, 4*inch])
            vuln_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [HexColor('#f8f8f8'), white]),
                ('BOX', (0, 0), (-1, -1), 1, black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, black),
            ]))
            
            story.append(vuln_table)
            story.append(Spacer(1, 10))
            
            # Description
            description = vuln.get('description', 'No description available.')
            story.append(Paragraph(f"<b>Description:</b> {description}", self.styles['Normal']))
            story.append(Spacer(1, 8))
            
            # Recommendation
            recommendation = vuln.get('recommendation', 'No specific recommendation available.')
            story.append(Paragraph(f"<b>Recommendation:</b> {recommendation}", self.styles['Normal']))
            story.append(Spacer(1, 8))
            
            # Remediation Commands
            commands = vuln.get('remediation_commands', [])
            if commands:
                story.append(Paragraph("<b>Remediation Commands:</b>", self.styles['Normal']))
                story.append(Spacer(1, 4))
                
                for cmd in commands[:3]:  # Limit to 3 commands per vulnerability
                    os_name = cmd.get('os', 'Linux').upper()
                    command_text = cmd.get('command', '')
                    description = cmd.get('description', '')
                    requires_sudo = cmd.get('requires_sudo', False)
                    is_destructive = cmd.get('is_destructive', False)
                    
                    # Command header with OS and warnings
                    header_parts = [f"<b>{os_name}:</b>"]
                    if requires_sudo:
                        header_parts.append("<font color='red'>[SUDO]</font>")
                    if is_destructive:
                        header_parts.append("<font color='red'>[DESTRUCTIVE]</font>")
                    
                    story.append(Paragraph(" ".join(header_parts), self.styles['Normal']))
                    
                    # Command in monospace
                    command_style = ParagraphStyle(
                        'CommandStyle',
                        parent=self.styles['Normal'],
                        fontName='Courier',
                        fontSize=9,
                        leftIndent=20,
                        backgroundColor=HexColor('#f0f0f0'),
                        borderWidth=1,
                        borderColor=HexColor('#ccc'),
                        borderPadding=5
                    )
                    story.append(Paragraph(command_text, command_style))
                    
                    if description:
                        story.append(Paragraph(f"<i>{description}</i>", self.styles['Normal']))
                    story.append(Spacer(1, 6))
            
            story.append(Spacer(1, 15))
        
        return story

    def _build_patch_recommendations(self, vulnerabilities: List[Dict[str, Any]]) -> List:
        """Build patch recommendations section"""
        story = []
        
        story.append(Paragraph("Patch Management Recommendations", self.styles['SectionHeader']))
        
        # Priority-based recommendations
        priority_text = """
        <b>Patching Priority Matrix:</b><br/><br/>
        The following recommendations are based on automated analysis using Large Language Models (LLMs) 
        to assess vulnerability impact, exploitability, and business risk:
        """
        story.append(Paragraph(priority_text, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Group by urgency
        critical_vulns = [v for v in vulnerabilities if v.get('severity') == 'Critical']
        high_vulns = [v for v in vulnerabilities if v.get('severity') == 'High']
        
        if critical_vulns:
            story.append(Paragraph("🔴 IMMEDIATE ACTION REQUIRED (24 hours)", self.styles['HighRisk']))
            for vuln in critical_vulns:
                rec_text = f"• {vuln.get('service_name', 'Unknown')} - {vuln.get('recommendation', 'Apply latest security patches')}"
                story.append(Paragraph(rec_text, self.styles['VulnItem']))
            story.append(Spacer(1, 10))
        
        if high_vulns:
            story.append(Paragraph("🟡 HIGH PRIORITY (48-72 hours)", self.styles['MediumRisk']))
            for vuln in high_vulns:
                rec_text = f"• {vuln.get('service_name', 'Unknown')} - {vuln.get('recommendation', 'Apply security updates')}"
                story.append(Paragraph(rec_text, self.styles['VulnItem']))
            story.append(Spacer(1, 10))
        
        # General recommendations
        general_recommendations = """
        <b>General Patch Management Best Practices:</b><br/>
        1. <b>Test Environment:</b> Always test patches in a non-production environment first<br/>
        2. <b>Backup Strategy:</b> Ensure complete backups before applying critical patches<br/>
        3. <b>Rollback Plan:</b> Have a documented rollback procedure for each patch<br/>
        4. <b>Change Management:</b> Follow organizational change management processes<br/>
        5. <b>Documentation:</b> Maintain detailed records of all patch activities<br/>
        6. <b>Monitoring:</b> Implement post-patch monitoring to verify system stability
        """
        story.append(Paragraph(general_recommendations, self.styles['Normal']))
        
        return story

    def _build_risk_assessment(self, vulnerabilities: List[Dict[str, Any]]) -> List:
        """Build risk assessment section"""
        story = []
        
        story.append(Paragraph("Risk Assessment Matrix", self.styles['SectionHeader']))
        
        # Calculate overall risk score
        total_score = 0
        scored_vulns = 0
        
        for vuln in vulnerabilities:
            cvss = vuln.get('cvss_score')
            if cvss and isinstance(cvss, (int, float)):
                total_score += cvss
                scored_vulns += 1
        
        avg_score = total_score / scored_vulns if scored_vulns > 0 else 0
        
        # Risk assessment summary
        risk_summary = f"""
        <b>Overall Risk Assessment:</b><br/>
        Average CVSS Score: {avg_score:.1f}/10<br/>
        Total Vulnerabilities: {len(vulnerabilities)}<br/>
        Risk Level: {"Critical" if avg_score >= 7 else "High" if avg_score >= 4 else "Medium"}<br/><br/>
        
        <b>Business Impact Assessment:</b><br/>
        The identified vulnerabilities pose varying levels of risk to organizational security. 
        Immediate attention should be given to critical and high-severity vulnerabilities that 
        could potentially lead to system compromise, data breaches, or service disruption.
        """
        story.append(Paragraph(risk_summary, self.styles['Normal']))
        
        return story