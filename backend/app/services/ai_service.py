"""
Enhanced AI service for queries and analysis with advanced LLM integration
"""
from sqlalchemy.orm import Session
from typing import Dict, Optional, Any, List
from datetime import datetime
import uuid
import logging

from app.models.scan import Scan
from app.models.vulnerability import Vulnerability
from app.models.feedback import Feedback
from app.services.gemini_llm_service import gemini_llm_service, AnalysisType
from app.services.conversation_service import ConversationService
from app.schemas.ai import AnalysisResponse

logger = logging.getLogger(__name__)


class EnhancedAIService:
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = gemini_llm_service
        self.conversation_service = ConversationService(db)
    
    async def process_query(
        self, 
        query: str, 
        user_id: int, 
        context: Optional[Dict] = None,
        conversation_id: Optional[str] = None
    ) -> Optional[str]:
        """Process user query with enhanced AI capabilities and conversation memory"""
        
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = f"user_{user_id}_{uuid.uuid4().hex[:8]}"
        
        start_time = datetime.utcnow()
        
        # Get conversation context and user preferences
        conversation_context = await self.conversation_service.get_conversation_context(
            conversation_id, user_id
        )
        
        # Get comprehensive user context
        user_context = await self._get_enhanced_user_context(user_id)
        
        # Merge all contexts
        if context:
            user_context.update(context)
        if conversation_context:
            user_context["conversation"] = conversation_context
        
        # Add query metadata
        user_context["query_metadata"] = {
            "timestamp": start_time.isoformat(),
            "user_id": user_id,
            "conversation_id": conversation_id
        }
        
        # Store user message in conversation
        await self.conversation_service.add_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="user",
            content=query,
            context_data={"user_context": user_context}
        )
        
        try:
            # Process with enhanced LLM
            response = await self.llm_service.answer_query(
                query=query, 
                context=user_context,
                conversation_id=conversation_id
            )
            
            if response:
                # Calculate processing time
                processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                # Store AI response in conversation
                await self.conversation_service.add_message(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    role="assistant",
                    content=response,
                    model_used="gemini-2.5-flash-8b",
                    processing_time_ms=processing_time,
                    enhancement_data={"analysis_type": "query_response"}
                )
            
            # Log the interaction for analytics
            await self._log_query_interaction(user_id, query, response, conversation_id)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            # Store error response
            await self.conversation_service.add_message(
                conversation_id=conversation_id,
                user_id=user_id,
                role="assistant",
                content=f"I encountered an error processing your query: {str(e)}",
                enhancement_data={"error": str(e)}
            )
            raise
    
    async def analyze_scan(
        self, 
        scan_id: int, 
        user_id: int,
        analysis_type: str = "comprehensive"
    ) -> Optional[AnalysisResponse]:
        """Enhanced scan analysis with multiple analysis types"""
        
        # Get scan and vulnerabilities
        scan = (
            self.db.query(Scan)
            .filter(Scan.id == scan_id, Scan.user_id == user_id)
            .first()
        )
        
        if not scan:
            return None
        
        vulnerabilities = (
            self.db.query(Vulnerability)
            .filter(Vulnerability.scan_id == scan_id)
            .all()
        )
        
        if not vulnerabilities:
            return AnalysisResponse(
                scan_id=scan_id,
                summary="No vulnerabilities found in this scan",
                key_findings=["Scan completed successfully with no vulnerabilities detected"],
                recommendations=["Continue regular security scanning", "Maintain current security posture"],
                risk_score=0.0,
                generated_at=datetime.utcnow()
            )
        
        # Perform different types of analysis based on request
        if analysis_type == "comprehensive":
            return await self._comprehensive_analysis(scan_id, vulnerabilities)
        elif analysis_type == "business_impact":
            return await self._business_impact_analysis(scan_id, vulnerabilities)
        elif analysis_type == "patch_prioritization":
            return await self._patch_prioritization_analysis(scan_id, vulnerabilities)
        else:
            return await self._basic_analysis(scan_id, vulnerabilities)
    
    async def _comprehensive_analysis(
        self, 
        scan_id: int, 
        vulnerabilities: List[Vulnerability]
    ) -> AnalysisResponse:
        """Perform comprehensive vulnerability analysis"""
        
        # Prepare vulnerability data for AI analysis
        vuln_data = await self._prepare_vulnerability_data(vulnerabilities)
        
        # Get AI-powered insights for top vulnerabilities
        ai_insights = []
        critical_vulns = [v for v in vulnerabilities if v.severity == "Critical"][:5]
        
        for vuln in critical_vulns:
            insight = await self.llm_service.analyze_vulnerability(
                service_name=vuln.service_name or "Unknown",
                version=vuln.service_version or "Unknown",
                port=vuln.port or 0,
                vulnerability_description=vuln.description or "No description",
                cve_id=vuln.cve_id,
                analysis_type=AnalysisType.VULNERABILITY_ASSESSMENT
            )
            if insight:
                ai_insights.append(insight)
        
        # Generate comprehensive summary
        summary = await self._generate_ai_summary(vuln_data, ai_insights)
        
        # Extract enhanced key findings
        key_findings = await self._extract_enhanced_findings(vulnerabilities, ai_insights)
        
        # Generate AI-powered recommendations
        recommendations = await self._generate_ai_recommendations(vuln_data, ai_insights)
        
        # Calculate enhanced risk score
        risk_score = await self._calculate_enhanced_risk_score(vulnerabilities, ai_insights)
        
        return AnalysisResponse(
            scan_id=scan_id,
            summary=summary,
            key_findings=key_findings,
            recommendations=recommendations,
            risk_score=risk_score,
            ai_insights=ai_insights,
            analysis_type="comprehensive",
            generated_at=datetime.utcnow()
        )
    
    async def _business_impact_analysis(
        self, 
        scan_id: int, 
        vulnerabilities: List[Vulnerability]
    ) -> AnalysisResponse:
        """Perform business impact focused analysis"""
        
        # Focus on business impact for critical vulnerabilities
        critical_vulns = [v for v in vulnerabilities if v.severity in ["Critical", "High"]]
        
        business_insights = []
        for vuln in critical_vulns[:3]:  # Analyze top 3 for performance
            insight = await self.llm_service.analyze_vulnerability(
                service_name=vuln.service_name or "Unknown",
                version=vuln.service_version or "Unknown",
                port=vuln.port or 0,
                vulnerability_description=vuln.description or "No description",
                cve_id=vuln.cve_id,
                analysis_type=AnalysisType.BUSINESS_IMPACT
            )
            if insight:
                business_insights.append(insight)
        
        # Generate business-focused summary
        summary = await self._generate_business_summary(vulnerabilities, business_insights)
        
        # Business-focused findings
        key_findings = [
            f"Business Impact Analysis for {len(vulnerabilities)} vulnerabilities",
            f"Financial risk exposure from {len(critical_vulns)} high-risk vulnerabilities",
            "Regulatory compliance implications identified",
            "Operational continuity assessment completed"
        ]
        
        # Business-focused recommendations
        recommendations = [
            "Immediate executive briefing on critical vulnerabilities",
            "Budget allocation for emergency patching activities",
            "Legal and compliance team notification required",
            "Customer communication strategy preparation"
        ]
        
        risk_score = self._calculate_business_risk_score(vulnerabilities)
        
        return AnalysisResponse(
            scan_id=scan_id,
            summary=summary,
            key_findings=key_findings,
            recommendations=recommendations,
            risk_score=risk_score,
            ai_insights=business_insights,
            analysis_type="business_impact",
            generated_at=datetime.utcnow()
        )
    
    async def _patch_prioritization_analysis(
        self, 
        scan_id: int, 
        vulnerabilities: List[Vulnerability]
    ) -> AnalysisResponse:
        """Perform patch prioritization analysis"""
        
        # Get patch recommendations for all vulnerabilities
        patch_insights = []
        for vuln in vulnerabilities:
            if vuln.severity in ["Critical", "High"]:  # Focus on high priority
                insight = await self.llm_service.analyze_vulnerability(
                    service_name=vuln.service_name or "Unknown",
                    version=vuln.service_version or "Unknown",
                    port=vuln.port or 0,
                    vulnerability_description=vuln.description or "No description",
                    cve_id=vuln.cve_id,
                    analysis_type=AnalysisType.PATCH_RECOMMENDATION
                )
                if insight:
                    patch_insights.append({**insight, "vulnerability_id": vuln.id})
        
        # Create patch priority matrix
        patch_matrix = self._create_patch_priority_matrix(vulnerabilities, patch_insights)
        
        summary = f"Patch prioritization analysis for {len(vulnerabilities)} vulnerabilities. " \
                 f"Identified {len(patch_insights)} high-priority patches requiring immediate attention."
        
        key_findings = [
            f"Patch Priority Matrix: {len(patch_matrix.get('immediate', []))} immediate, "
            f"{len(patch_matrix.get('high', []))} high priority",
            "Deployment timeline recommendations generated",
            "Testing and rollback strategies identified",
            "Resource allocation requirements calculated"
        ]
        
        recommendations = [
            "Deploy emergency patches for critical vulnerabilities within 24 hours",
            "Schedule high-priority patches for next maintenance window",
            "Implement automated testing pipeline for patch validation",
            "Establish rollback procedures for all patch deployments"
        ]
        
        risk_score = self._calculate_patch_urgency_score(vulnerabilities)
        
        return AnalysisResponse(
            scan_id=scan_id,
            summary=summary,
            key_findings=key_findings,
            recommendations=recommendations,
            risk_score=risk_score,
            ai_insights=patch_insights,
            analysis_type="patch_prioritization",
            patch_matrix=patch_matrix,
            generated_at=datetime.utcnow()
        )
    
    async def _basic_analysis(
        self, 
        scan_id: int, 
        vulnerabilities: List[Vulnerability]
    ) -> AnalysisResponse:
        """Basic analysis for backward compatibility"""
        
        vuln_data = await self._prepare_vulnerability_data(vulnerabilities)
        
        # Simple AI-generated summary
        summary = f"Scan analysis completed. Found {len(vulnerabilities)} vulnerabilities requiring attention."
        
        # Basic findings
        key_findings = self._extract_basic_findings(vulnerabilities)
        
        # Basic recommendations
        recommendations = await self._generate_basic_recommendations(vuln_data)
        
        # Simple risk calculation
        risk_score = self._calculate_basic_risk_score(vulnerabilities)
        
        return AnalysisResponse(
            scan_id=scan_id,
            summary=summary,
            key_findings=key_findings,
            recommendations=recommendations,
            risk_score=risk_score,
            analysis_type="basic",
            generated_at=datetime.utcnow()
        )
    
    async def _get_enhanced_user_context(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user context for AI queries"""
        
        # Get scan statistics
        total_scans = self.db.query(Scan).filter(Scan.user_id == user_id).count()
        
        # Get vulnerability statistics
        vulnerabilities = (
            self.db.query(Vulnerability)
            .join(Scan)
            .filter(Scan.user_id == user_id)
            .all()
        )
        
        # Enhanced context with trends and patterns
        context = {
            "user_profile": {
                "total_scans": total_scans,
                "total_vulnerabilities": len(vulnerabilities),
                "average_vulns_per_scan": len(vulnerabilities) / max(total_scans, 1)
            },
            "severity_distribution": self._analyze_severity_distribution(vulnerabilities),
            "service_landscape": self._analyze_service_landscape(vulnerabilities),
            "temporal_trends": await self._analyze_temporal_trends(user_id),
            "risk_patterns": self._analyze_risk_patterns(vulnerabilities)
        }
        
        return context
    
    def _analyze_severity_distribution(self, vulnerabilities: List[Vulnerability]) -> Dict:
        """Analyze severity distribution with percentages"""
        counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        
        for vuln in vulnerabilities:
            if vuln.severity in counts:
                counts[vuln.severity] += 1
        
        total = sum(counts.values())
        percentages = {k: (v / total * 100) if total > 0 else 0 for k, v in counts.items()}
        
        return {
            "counts": counts,
            "percentages": percentages,
            "total": total,
            "risk_level": "High" if counts["Critical"] > 0 else "Medium" if counts["High"] > 0 else "Low"
        }
    
    def _analyze_service_landscape(self, vulnerabilities: List[Vulnerability]) -> Dict:
        """Analyze service vulnerability landscape"""
        service_counts = {}
        service_severities = {}
        
        for vuln in vulnerabilities:
            service = vuln.service_name or "Unknown"
            service_counts[service] = service_counts.get(service, 0) + 1
            
            if service not in service_severities:
                service_severities[service] = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
            if vuln.severity in service_severities[service]:
                service_severities[service][vuln.severity] += 1
        
        # Find most vulnerable services
        top_vulnerable = sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "service_counts": service_counts,
            "service_severities": service_severities,
            "most_vulnerable_services": top_vulnerable,
            "service_diversity": len(service_counts)
        }
    
    async def _analyze_temporal_trends(self, user_id: int) -> Dict:
        """Analyze temporal vulnerability trends"""
        # Get recent scans for trend analysis
        recent_scans = (
            self.db.query(Scan)
            .filter(Scan.user_id == user_id)
            .order_by(Scan.upload_time.desc())
            .limit(10)
            .all()
        )
        
        # Simple trend analysis
        if len(recent_scans) >= 2:
            latest_scan_vulns = len([v for v in recent_scans[0].vulnerabilities if v]) if recent_scans[0].vulnerabilities else 0
            prev_scan_vulns = len([v for v in recent_scans[1].vulnerabilities if v]) if len(recent_scans) > 1 and recent_scans[1].vulnerabilities else 0
            
            trend = "improving" if latest_scan_vulns < prev_scan_vulns else "worsening" if latest_scan_vulns > prev_scan_vulns else "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "recent_scan_count": len(recent_scans),
            "trend_direction": trend,
            "scan_frequency": "regular" if len(recent_scans) >= 5 else "irregular"
        }
    
    def _analyze_risk_patterns(self, vulnerabilities: List[Vulnerability]) -> Dict:
        """Analyze risk patterns and indicators"""
        
        # Calculate various risk indicators
        cvss_scores = [v.cvss_score for v in vulnerabilities if v.cvss_score]
        avg_cvss = sum(cvss_scores) / len(cvss_scores) if cvss_scores else 0
        
        # Port analysis
        common_ports = {}
        for vuln in vulnerabilities:
            if vuln.port:
                common_ports[vuln.port] = common_ports.get(vuln.port, 0) + 1
        
        # Service version analysis
        outdated_services = []
        for vuln in vulnerabilities:
            if vuln.service_version and any(word in vuln.description.lower() for word in ["outdated", "old", "vulnerable"] if vuln.description):
                outdated_services.append(vuln.service_name)
        
        return {
            "average_cvss_score": round(avg_cvss, 2),
            "most_vulnerable_ports": sorted(common_ports.items(), key=lambda x: x[1], reverse=True)[:5],
            "outdated_services_count": len(set(outdated_services)),
            "risk_concentration": "high" if len(set(v.service_name for v in vulnerabilities)) < 3 else "distributed"
        }
    
    async def _prepare_vulnerability_data(self, vulnerabilities: List[Vulnerability]) -> List[Dict]:
        """Prepare vulnerability data for AI analysis"""
        return [
            {
                "id": v.id,
                "service_name": v.service_name or "Unknown",
                "version": v.service_version or "Unknown",
                "port": v.port or 0,
                "severity": v.severity or "Unknown",
                "cve_id": v.cve_id,
                "cvss_score": v.cvss_score or 0,
                "description": v.description or "No description",
                "recommendation": v.recommendation
            }
            for v in vulnerabilities
        ]
    
    async def _generate_ai_summary(self, vuln_data: List[Dict], ai_insights: List[Dict]) -> str:
        """Generate AI-powered summary"""
        if not vuln_data:
            return "No vulnerabilities found in this scan."
        
        critical_count = len([v for v in vuln_data if v.get("severity") == "Critical"])
        high_count = len([v for v in vuln_data if v.get("severity") == "High"])
        
        # Use AI insights to enhance summary
        key_risks = []
        for insight in ai_insights:
            if isinstance(insight, dict) and insight.get("business_impact"):
                key_risks.append(insight["business_impact"][:100])
        
        summary = f"Comprehensive analysis of {len(vuln_data)} vulnerabilities identified "
        summary += f"{critical_count} critical and {high_count} high-severity issues. "
        
        if key_risks:
            summary += f"Key business risks include: {'; '.join(key_risks[:2])}."
        
        return summary
    
    async def _generate_business_summary(self, vulnerabilities: List[Vulnerability], business_insights: List[Dict]) -> str:
        """Generate business-focused summary"""
        critical_count = len([v for v in vulnerabilities if v.severity == "Critical"])
        high_count = len([v for v in vulnerabilities if v.severity == "High"])
        
        summary = f"Business Impact Analysis: {len(vulnerabilities)} vulnerabilities pose varying degrees of risk to business operations. "
        summary += f"{critical_count} critical and {high_count} high-severity vulnerabilities require immediate executive attention. "
        
        # Add insights from business impact analysis
        financial_risks = []
        operational_risks = []
        
        for insight in business_insights:
            if isinstance(insight, dict):
                if insight.get("financial_impact"):
                    financial_risks.append(insight["financial_impact"][:50])
                if insight.get("operational_impact"):
                    operational_risks.append(insight["operational_impact"][:50])
        
        if financial_risks:
            summary += f"Financial impact concerns include {financial_risks[0]}. "
        if operational_risks:
            summary += f"Operational risks include {operational_risks[0]}."
        
        return summary
    
    async def _extract_enhanced_findings(self, vulnerabilities: List[Vulnerability], ai_insights: List[Dict]) -> List[str]:
        """Extract enhanced findings using AI insights"""
        findings = []
        
        # Basic statistical findings
        severity_counts = {}
        for vuln in vulnerabilities:
            severity_counts[vuln.severity] = severity_counts.get(vuln.severity, 0) + 1
        
        if severity_counts.get("Critical", 0) > 0:
            findings.append(f"{severity_counts['Critical']} critical vulnerabilities require immediate attention")
        
        if severity_counts.get("High", 0) > 0:
            findings.append(f"{severity_counts['High']} high-severity vulnerabilities need urgent patching")
        
        # AI-enhanced findings
        for insight in ai_insights:
            if isinstance(insight, dict):
                if insight.get("compliance_impact"):
                    findings.append(f"Compliance implications: {', '.join(insight['compliance_impact'][:2])}")
                if insight.get("patch_priority") == "Immediate":
                    findings.append("Immediate patching required for critical services")
        
        # Service concentration analysis
        service_counts = {}
        for vuln in vulnerabilities:
            service = vuln.service_name or "Unknown"
            service_counts[service] = service_counts.get(service, 0) + 1
        
        if service_counts:
            most_vulnerable = max(service_counts.items(), key=lambda x: x[1])
            findings.append(f"{most_vulnerable[0]} service has the highest vulnerability count ({most_vulnerable[1]})")
        
        return findings[:10]  # Limit to top 10 findings
    
    async def _generate_ai_recommendations(self, vuln_data: List[Dict], ai_insights: List[Dict]) -> List[str]:
        """Generate AI-powered recommendations"""
        recommendations = []
        
        # AI-enhanced recommendations
        patch_priorities = {"Immediate": [], "High": [], "Medium": []}
        
        for insight in ai_insights:
            if isinstance(insight, dict) and insight.get("patch_priority"):
                priority = insight.get("patch_priority")
                if priority in patch_priorities:
                    patch_priorities[priority].append(insight.get("recommendation", ""))
        
        # Prioritized recommendations
        if patch_priorities["Immediate"]:
            recommendations.append(f"IMMEDIATE: {patch_priorities['Immediate'][0][:100]}...")
        
        if patch_priorities["High"]:
            recommendations.append(f"HIGH PRIORITY: {patch_priorities['High'][0][:100]}...")
        
        # General strategic recommendations
        critical_count = len([v for v in vuln_data if v.get("severity") == "Critical"])
        if critical_count > 0:
            recommendations.append("Establish emergency patch deployment procedure")
            recommendations.append("Notify security team and management immediately")
        
        recommendations.extend([
            "Implement continuous vulnerability monitoring",
            "Schedule regular security assessments",
            "Review and update security policies"
        ])
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    async def _generate_basic_recommendations(self, vuln_data: List[Dict]) -> List[str]:
        """Generate basic recommendations"""
        recommendations = []
        
        critical_count = len([v for v in vuln_data if v.get("severity") == "Critical"])
        high_count = len([v for v in vuln_data if v.get("severity") == "High"])
        
        if critical_count > 0:
            recommendations.append(f"Immediately patch {critical_count} critical vulnerabilities")
        
        if high_count > 0:
            recommendations.append(f"Schedule patching for {high_count} high-severity vulnerabilities")
        
        recommendations.extend([
            "Implement regular vulnerability scanning",
            "Establish a patch management process",
            "Review security configurations"
        ])
        
        return recommendations
    
    def _extract_basic_findings(self, vulnerabilities: List[Vulnerability]) -> List[str]:
        """Extract basic findings"""
        findings = []
        
        severity_counts = {}
        for vuln in vulnerabilities:
            severity_counts[vuln.severity] = severity_counts.get(vuln.severity, 0) + 1
        
        for severity, count in severity_counts.items():
            if count > 0:
                findings.append(f"{count} {severity.lower()}-severity vulnerabilities identified")
        
        # Service analysis
        service_counts = {}
        for vuln in vulnerabilities:
            service = vuln.service_name or "Unknown"
            service_counts[service] = service_counts.get(service, 0) + 1
        
        if service_counts:
            most_common = max(service_counts.items(), key=lambda x: x[1])
            findings.append(f"{most_common[0]} has the most vulnerabilities ({most_common[1]})")
        
        return findings
    
    async def _calculate_enhanced_risk_score(self, vulnerabilities: List[Vulnerability], ai_insights: List[Dict]) -> float:
        """Calculate enhanced risk score using AI insights"""
        if not vulnerabilities:
            return 0.0
        
        # Base CVSS calculation
        base_score = self._calculate_basic_risk_score(vulnerabilities)
        
        # AI enhancement factors
        ai_risk_modifier = 1.0
        
        for insight in ai_insights:
            if isinstance(insight, dict):
                # Business impact modifier
                if insight.get("business_impact"):
                    impact = insight["business_impact"].lower()
                    if any(word in impact for word in ["critical", "severe", "major"]):
                        ai_risk_modifier += 0.5
                
                # Patch priority modifier
                if insight.get("patch_priority") == "Immediate":
                    ai_risk_modifier += 0.3
                
                # Compliance impact modifier
                if insight.get("compliance_impact"):
                    ai_risk_modifier += 0.2
        
        # Apply modifier with ceiling
        enhanced_score = base_score * min(ai_risk_modifier, 1.5)
        
        return round(min(enhanced_score, 10.0), 2)
    
    def _calculate_basic_risk_score(self, vulnerabilities: List[Vulnerability]) -> float:
        """Calculate basic risk score"""
        if not vulnerabilities:
            return 0.0
        
        total_score = 0.0
        count = 0
        
        for vuln in vulnerabilities:
            if vuln.cvss_score:
                total_score += vuln.cvss_score
                count += 1
            else:
                # Default scores based on severity
                severity_scores = {
                    "Critical": 9.0,
                    "High": 7.0,
                    "Medium": 5.0,
                    "Low": 2.0
                }
                total_score += severity_scores.get(vuln.severity, 5.0)
                count += 1
        
        return round(total_score / count, 2) if count > 0 else 0.0
    
    def _calculate_business_risk_score(self, vulnerabilities: List[Vulnerability]) -> float:
        """Calculate business-focused risk score"""
        if not vulnerabilities:
            return 0.0
        
        # Weight critical and high vulnerabilities more heavily for business impact
        business_score = 0.0
        
        for vuln in vulnerabilities:
            if vuln.severity == "Critical":
                business_score += 3.0  # High business weight
            elif vuln.severity == "High":
                business_score += 2.0
            elif vuln.severity == "Medium":
                business_score += 1.0
            else:
                business_score += 0.5
        
        # Normalize to 0-10 scale
        max_possible = len(vulnerabilities) * 3.0
        normalized_score = (business_score / max_possible) * 10 if max_possible > 0 else 0
        
        return round(min(normalized_score, 10.0), 2)
    
    def _calculate_patch_urgency_score(self, vulnerabilities: List[Vulnerability]) -> float:
        """Calculate patch urgency score"""
        if not vulnerabilities:
            return 0.0
        
        urgency_score = 0.0
        
        # Higher urgency for services that are commonly exploited
        high_risk_services = ["ssh", "http", "https", "ftp", "telnet", "smtp", "mysql", "postgresql"]
        
        for vuln in vulnerabilities:
            base_urgency = {"Critical": 4.0, "High": 3.0, "Medium": 2.0, "Low": 1.0}.get(vuln.severity, 1.0)
            
            # Increase urgency for high-risk services
            if vuln.service_name and vuln.service_name.lower() in high_risk_services:
                base_urgency *= 1.2
            
            urgency_score += base_urgency
        
        # Normalize to 0-10 scale
        max_possible = len(vulnerabilities) * 4.0
        normalized_score = (urgency_score / max_possible) * 10 if max_possible > 0 else 0
        
        return round(min(normalized_score, 10.0), 2)
    
    def _create_patch_priority_matrix(self, vulnerabilities: List[Vulnerability], patch_insights: List[Dict]) -> Dict:
        """Create patch priority matrix"""
        matrix = {
            "immediate": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for vuln in vulnerabilities:
            # Find corresponding AI insight
            insight = None
            for ai_insight in patch_insights:
                if ai_insight.get("vulnerability_id") == vuln.id:
                    insight = ai_insight
                    break
            
            # Determine priority
            if vuln.severity == "Critical":
                priority = "immediate"
            elif vuln.severity == "High":
                priority = "high"
            elif vuln.severity == "Medium":
                priority = "medium"
            else:
                priority = "low"
            
            # Enhance with AI insight
            if insight and insight.get("urgency"):
                ai_urgency = insight["urgency"].lower()
                if ai_urgency == "critical":
                    priority = "immediate"
                elif ai_urgency == "high" and priority not in ["immediate"]:
                    priority = "high"
            
            matrix[priority].append({
                "vulnerability_id": vuln.id,
                "service": vuln.service_name,
                "severity": vuln.severity,
                "cve_id": vuln.cve_id,
                "ai_recommendation": insight.get("recommendation") if insight else None
            })
        
        return matrix
    
    async def _log_query_interaction(
        self, 
        user_id: int, 
        query: str, 
        response: Optional[str],
        conversation_id: str
    ):
        """Log query interaction for analytics and improvement"""
        try:
            # In a production system, you might log to a dedicated analytics service
            logger.info(f"Query interaction - User: {user_id}, Conversation: {conversation_id}, "
                       f"Query length: {len(query)}, Response: {'success' if response else 'failed'}")
        except Exception as e:
            logger.error(f"Failed to log query interaction: {e}")
    
    async def close(self):
        """Clean up resources"""
        if hasattr(self.llm_service, 'close'):
            await self.llm_service.close()


# Backward compatibility
AIService = EnhancedAIService