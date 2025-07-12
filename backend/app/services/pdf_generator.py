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
        
        # AI-Enhanced Insights
        story.extend(self._build_ai_insights_section(vulnerabilities))
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
        
        # Disclaimer with better formatting
        disclaimer = """
        <b><font color="#d32f2f">CONFIDENTIAL DOCUMENT</font></b><br/><br/>
        This vulnerability assessment report contains sensitive security information. 
        Distribution should be limited to authorized personnel only.<br/><br/>
        
        <b>Report Methodology:</b><br/>
        • Automated vulnerability scanning and detection<br/>
        • AI-powered risk assessment using Large Language Models<br/>
        • Intelligent prioritization based on exploit potential<br/>
        • Business impact analysis and remediation guidance<br/><br/>
        
        <b><font color="#f57c00">Important Notice:</font></b> The findings and recommendations in this report 
        are based on automated scanning and AI analysis. All recommendations should be 
        validated by qualified security professionals before implementation.
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
        
        # Summary paragraph with enhanced formatting
        summary_text = f"""
        This vulnerability assessment identified <b><font color="#d32f2f">{total_vulns}</font></b> security vulnerabilities 
        across the scanned network infrastructure. The automated analysis, enhanced by 
        <b>Large Language Model (LLM)</b> capabilities, provides intelligent prioritization and 
        actionable remediation guidance.
        <br/><br/>
        <b>Key Statistics:</b><br/>
        • <font color="#d32f2f"><b>Critical:</b></font> {critical} vulnerabilities requiring immediate action<br/>
        • <font color="#f57c00"><b>High:</b></font> {high} vulnerabilities needing urgent attention<br/>
        • <font color="#fbc02d"><b>Medium:</b></font> {medium} vulnerabilities to address soon<br/>
        • <font color="#388e3c"><b>Low:</b></font> {low} vulnerabilities for routine maintenance
        """
        story.append(Paragraph(summary_text, self.styles['ExecutiveSummary']))
        story.append(Spacer(1, 20))
        
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
            # Vulnerability header with color-coded severity
            severity = vuln.get('severity', 'Unknown')
            service = vuln.get('service_name', 'Unknown')
            cve = vuln.get('cve_id', 'N/A')
            
            # Color-code the severity
            severity_colors = {
                'Critical': '#d32f2f',
                'High': '#f57c00', 
                'Medium': '#fbc02d',
                'Low': '#388e3c'
            }
            severity_color = severity_colors.get(severity, '#000000')
            
            header_text = f"<b>{i}. {service}</b> - <font color='{severity_color}'><b>{severity} Severity</b></font>"
            if cve != 'N/A':
                header_text += f" <font color='blue'>({cve})</font>"
            
            story.append(Paragraph(header_text, self.styles['Heading3']))
            story.append(Spacer(1, 8))
            
            # Vulnerability details table with better formatting
            vuln_data = [
                ['Service:', vuln.get('service_name', 'N/A')],
                ['Version:', vuln.get('version', 'N/A')],
                ['Port:', str(vuln.get('port', 'N/A'))],
                ['CVE ID:', vuln.get('cve_id', 'N/A')],
                ['CVSS Score:', f"{vuln.get('cvss_score', 'N/A')}/10" if vuln.get('cvss_score') else 'N/A'],
                ['Severity:', f"<font color='{severity_color}'><b>{vuln.get('severity', 'N/A')}</b></font>"]
            ]
            
            vuln_table = Table(vuln_data, colWidths=[1.3*inch, 4.2*inch])
            vuln_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [HexColor('#f8f8f8'), white]),
                ('BOX', (0, 0), (-1, -1), 1, HexColor('#cccccc')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            story.append(vuln_table)
            story.append(Spacer(1, 12))
            
            # Description with better formatting
            description = vuln.get('description', 'No description available.')
            formatted_description = self._format_ai_content_for_pdf(description)
            story.append(Paragraph(f"<b>Description:</b>", self.styles['Normal']))
            story.append(Spacer(1, 4))
            story.append(Paragraph(formatted_description, self.styles['Normal']))
            story.append(Spacer(1, 10))
            
            # Recommendation with enhanced formatting
            recommendation = vuln.get('recommendation', 'No specific recommendation available.')
            formatted_recommendation = self._format_ai_content_for_pdf(recommendation)
            story.append(Paragraph(f"<b>AI-Enhanced Recommendations:</b>", self.styles['Normal']))
            story.append(Spacer(1, 4))
            story.append(Paragraph(formatted_recommendation, self.styles['Normal']))
            story.append(Spacer(1, 10))
            
            # Remediation Commands
            commands = vuln.get('remediation_commands', [])
            if commands:
                story.append(Paragraph("<b>Remediation Commands:</b>", self.styles['Normal']))
                story.append(Spacer(1, 8))
                
                for cmd in commands[:3]:  # Limit to 3 commands per vulnerability
                    os_name = cmd.get('os', 'Linux').upper()
                    command_text = cmd.get('command', '')
                    description = cmd.get('description', '')
                    requires_sudo = cmd.get('requires_sudo', False)
                    is_destructive = cmd.get('is_destructive', False)
                    
                    # Command header with OS and warnings - better formatting
                    header_parts = [f"<b><font color='#1976d2'>{os_name}</font></b>"]
                    if requires_sudo:
                        header_parts.append("<font color='#d32f2f'><b>[REQUIRES SUDO]</b></font>")
                    if is_destructive:
                        header_parts.append("<font color='#d32f2f'><b>[DESTRUCTIVE]</b></font>")
                    
                    story.append(Paragraph(" ".join(header_parts), self.styles['Normal']))
                    story.append(Spacer(1, 4))
                    
                    # Command in monospace with better styling
                    command_style = ParagraphStyle(
                        'CommandStyle',
                        parent=self.styles['Normal'],
                        fontName='Courier',
                        fontSize=9,
                        leftIndent=15,
                        rightIndent=15,
                        backgroundColor=HexColor('#f8f8f8'),
                        borderWidth=1,
                        borderColor=HexColor('#ddd'),
                        borderPadding=8,
                        spaceAfter=6
                    )
                    story.append(Paragraph(command_text, command_style))
                    
                    if description:
                        story.append(Spacer(1, 4))
                        story.append(Paragraph(f"<i><font color='#666'>{description}</font></i>", self.styles['Normal']))
                    story.append(Spacer(1, 12))
            
            story.append(Spacer(1, 15))
        
        return story
    
    def _format_ai_content_for_pdf(self, content: str) -> str:
        """Format AI-generated content for better PDF display"""
        if not content:
            return content
        
        # Split content into lines and process each line
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append('<br/>')
                continue
            
            # Handle headers (## or ### or **Header:**)
            if line.startswith('###'):
                header_text = line.replace('###', '').strip()
                formatted_lines.append(f'<br/><b><font color="#1976d2" size="12">{header_text}</font></b><br/><br/>')
            elif line.startswith('##'):
                header_text = line.replace('##', '').strip() 
                formatted_lines.append(f'<br/><b><font color="#1976d2" size="14">{header_text}</font></b><br/><br/>')
            # Handle **Header:** patterns
            elif line.startswith('**') and line.endswith(':**') and line.count('**') == 2:
                header_text = line.replace('**', '').replace(':', '').strip()
                formatted_lines.append(f'<br/><b><font color="#1976d2">{header_text}:</font></b><br/>')
            # Handle bullet points starting with * or -
            elif line.startswith('*') and not (line.startswith('**') and line.endswith('**')):
                bullet_text = line[1:].strip()
                # Check for bold formatting **text**
                if '**' in bullet_text:
                    bullet_text = self._process_bold_text(bullet_text)
                formatted_lines.append(f'  • {bullet_text}<br/>')
            elif line.startswith('-') and not line.startswith('--'):
                bullet_text = line[1:].strip()
                # Check for bold formatting **text**
                if '**' in bullet_text:
                    bullet_text = self._process_bold_text(bullet_text)
                formatted_lines.append(f'  • {bullet_text}<br/>')
            # Handle numbered lists
            elif line.split('.')[0].strip().isdigit():
                formatted_lines.append(f'  {line}<br/>')
            # Handle bold text **text**
            elif '**' in line:
                processed_line = self._process_bold_text(line)
                formatted_lines.append(processed_line + '<br/>')
            else:
                # Regular text with proper spacing
                formatted_lines.append(line + '<br/>')
        
        return '\n'.join(formatted_lines)
    
    def _process_bold_text(self, text: str) -> str:
        """Process bold text formatting **text**"""
        parts = text.split('**')
        formatted_parts = []
        for i, part in enumerate(parts):
            if i % 2 == 1:  # Odd indices are bold
                formatted_parts.append(f'<b>{part}</b>')
            else:
                formatted_parts.append(part)
        return ''.join(formatted_parts)
    
    def _build_ai_insights_section(self, vulnerabilities: List[Dict[str, Any]]) -> List:
        """Build AI-enhanced insights section"""
        story = []
        
        story.append(Paragraph("AI-Enhanced Security Insights", self.styles['SectionHeader']))
        
        # AI Analysis Summary
        ai_summary = f"""
        <b>Intelligent Vulnerability Analysis:</b><br/><br/>
        This section provides AI-powered insights generated using Large Language Models (LLMs) to enhance 
        traditional vulnerability scanning results. The analysis includes contextual risk assessment, 
        exploit likelihood evaluation, and intelligent remediation prioritization.
        """
        story.append(Paragraph(ai_summary, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Priority Analysis
        critical_vulns = [v for v in vulnerabilities if v.get('severity') == 'Critical']
        high_vulns = [v for v in vulnerabilities if v.get('severity') == 'High']
        
        if critical_vulns or high_vulns:
            story.append(Paragraph("🤖 AI Risk Prioritization", self.styles['Heading3']))
            story.append(Spacer(1, 8))
            
            priority_insights = f"""
            <b>Automated Risk Assessment:</b><br/>
            • <font color="#d32f2f"><b>{len(critical_vulns)}</b></font> critical vulnerabilities identified with high exploit potential<br/>
            • <font color="#f57c00"><b>{len(high_vulns)}</b></font> high-severity vulnerabilities requiring urgent attention<br/>
            • AI models indicate these vulnerabilities pose significant security risks based on:<br/>
             • Known exploit availability and attack patterns<br/>
             • Service exposure and accessibility<br/>
             • Potential business impact assessment<br/>
             • Historical vulnerability exploitation trends
            """
            story.append(Paragraph(priority_insights, self.styles['Normal']))
            story.append(Spacer(1, 15))
        
        # AI Recommendations Summary
        story.append(Paragraph("🧠 Intelligent Remediation Strategy", self.styles['Heading3']))
        story.append(Spacer(1, 8))
        
        remediation_strategy = """
        <b>AI-Generated Remediation Approach:</b><br/><br/>
        The following strategy has been developed using advanced AI analysis of your specific 
        vulnerability profile and industry best practices:<br/><br/>
        
        <b>1. Immediate Response (0-24 hours):</b><br/>
        • Focus on critical vulnerabilities with known active exploits<br/>
        • Implement temporary mitigations for services that cannot be immediately patched<br/>
        • Enhance monitoring for affected systems<br/><br/>
        
        <b>2. Short-term Actions (1-7 days):</b><br/>
        • Deploy tested patches for high and medium severity vulnerabilities<br/>
        • Conduct vulnerability re-scanning to verify remediation effectiveness<br/>
        • Update security controls and configurations<br/><br/>
        
        <b>3. Long-term Improvements (1-4 weeks):</b><br/>
        • Implement automated patch management processes<br/>
        • Establish continuous vulnerability monitoring<br/>
        • Enhance security architecture based on identified weaknesses
        """
        story.append(Paragraph(remediation_strategy, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Technical Insights
        story.append(Paragraph("⚙️ Technical Analysis Highlights", self.styles['Heading3']))
        story.append(Spacer(1, 8))
        
        # Calculate some technical metrics
        total_vulns = len(vulnerabilities)
        services_affected = len(set(v.get('service_name', 'Unknown') for v in vulnerabilities))
        avg_cvss = sum(v.get('cvss_score', 0) for v in vulnerabilities if v.get('cvss_score')) / max(len([v for v in vulnerabilities if v.get('cvss_score')]), 1)
        
        technical_analysis = f"""
        <b>Automated Technical Assessment:</b><br/>
        • <b>Attack Surface:</b> {services_affected} unique services identified with vulnerabilities<br/>
        • <b>Risk Concentration:</b> Average CVSS score of {avg_cvss:.1f}/10 across all findings<br/>
        • <b>Patch Complexity:</b> Multiple service types requiring coordinated remediation approach<br/>
        • <b>Business Impact:</b> Potential for service disruption during patching activities<br/><br/>
        
        <b>AI-Recommended Testing Strategy:</b><br/>
        • Prioritize patches based on exploitability and business criticality<br/>
        • Implement staged rollout approach for production systems<br/>
        • Maintain detailed rollback procedures for all changes<br/>
        • Monitor system performance and security posture post-remediation
        """
        story.append(Paragraph(technical_analysis, self.styles['Normal']))
        
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
            story.append(Spacer(1, 8))
            for vuln in critical_vulns:
                service_name = vuln.get('service_name', 'Unknown')
                recommendation = vuln.get('recommendation', 'Apply latest security patches')
                formatted_rec = self._format_ai_content_for_pdf(recommendation)
                rec_text = f"<b>{service_name}:</b><br/>{formatted_rec}"
                story.append(Paragraph(rec_text, self.styles['VulnItem']))
                story.append(Spacer(1, 8))
            story.append(Spacer(1, 15))
        
        if high_vulns:
            story.append(Paragraph("🟡 HIGH PRIORITY (48-72 hours)", self.styles['MediumRisk']))
            story.append(Spacer(1, 8))
            for vuln in high_vulns:
                service_name = vuln.get('service_name', 'Unknown')
                recommendation = vuln.get('recommendation', 'Apply security updates')
                formatted_rec = self._format_ai_content_for_pdf(recommendation)
                rec_text = f"<b>{service_name}:</b><br/>{formatted_rec}"
                story.append(Paragraph(rec_text, self.styles['VulnItem']))
                story.append(Spacer(1, 8))
            story.append(Spacer(1, 15))
        
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