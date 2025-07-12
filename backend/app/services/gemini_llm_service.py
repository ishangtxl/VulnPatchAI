"""
Enhanced LLM Service for vulnerability analysis using Google Gemini API
with integrated feedback learning system
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import instructor
import google.generativeai as genai
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.cache_service import ai_cache

logger = logging.getLogger(__name__)


class AnalysisType(str, Enum):
    """Types of AI analysis available"""
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    RISK_ANALYSIS = "risk_analysis"
    PATCH_RECOMMENDATION = "patch_recommendation"
    BUSINESS_IMPACT = "business_impact"
    COMPLIANCE_MAPPING = "compliance_mapping"


class RemediationCommand(BaseModel):
    """Terminal command for vulnerability remediation"""
    title: str = Field(description="Command description")
    command: str = Field(description="Terminal command to execute")
    os: str = Field(description="Target operating system")
    description: str = Field(description="What this command does")
    requires_sudo: bool = Field(description="Whether command requires sudo/admin privileges")
    is_destructive: bool = Field(description="Whether command makes destructive changes")


class VulnerabilityAnalysis(BaseModel):
    """Structured vulnerability analysis output"""
    severity: str = Field(description="Vulnerability severity: Critical, High, Medium, Low")
    risk_score: float = Field(ge=0, le=10, description="Risk score from 0-10")
    recommendation: str = Field(description="Detailed remediation steps")
    remediation_commands: List[RemediationCommand] = Field(description="Terminal commands for remediation")
    business_impact: str = Field(description="Potential business impact")
    technical_details: str = Field(description="Technical explanation")
    patch_priority: str = Field(description="Patch priority: Immediate, High, Medium, Low")
    estimated_effort: str = Field(description="Estimated time to remediate")
    prerequisites: List[str] = Field(description="Prerequisites for patching")
    compliance_impact: List[str] = Field(description="Compliance frameworks affected")


class PatchRecommendation(BaseModel):
    """Structured patch recommendation output"""
    urgency: str = Field(description="Patch urgency: Critical, High, Medium, Low")
    timeline: str = Field(description="Recommended timeline for patching")
    patch_version: str = Field(description="Specific patch version or action")
    risk_if_not_patched: str = Field(description="Risk if vulnerability remains unpatched")
    deployment_strategy: str = Field(description="Recommended deployment approach")
    testing_requirements: List[str] = Field(description="Required testing steps")
    rollback_plan: str = Field(description="Rollback strategy if patch fails")


class BusinessImpactAnalysis(BaseModel):
    """Structured business impact analysis"""
    financial_impact: str = Field(description="Potential financial losses")
    operational_impact: str = Field(description="Impact on business operations")
    reputation_risk: str = Field(description="Reputation and brand impact")
    regulatory_implications: List[str] = Field(description="Regulatory compliance issues")
    customer_impact: str = Field(description="Impact on customers")
    recovery_cost: str = Field(description="Estimated recovery costs")


@dataclass
class ContextWindow:
    """Manages context window for large inputs"""
    max_tokens: int = 1000000  # Gemini 2.5 supports up to 2M tokens
    reserve_tokens: int = 5000
    
    def truncate_context(self, content: str, max_length: Optional[int] = None) -> str:
        """Truncate content to fit within context window"""
        if max_length is None:
            max_length = self.max_tokens - self.reserve_tokens
        
        if len(content) <= max_length:
            return content
        
        # Truncate and add indicator
        truncated = content[:max_length-100]
        return truncated + "...\\n[Content truncated for length]"


class GeminiLLMService:
    """Enhanced LLM service with Google Gemini API, advanced features, and feedback learning"""
    
    def __init__(self):
        self.client = None
        self.instructor_client = None
        self.context_manager = ContextWindow()
        self.conversation_memory: Dict[str, List[Dict]] = {}
        self.cache = ai_cache
        self.feedback_service = None  # Will be injected when needed
        self.learned_improvements: Dict[str, Dict] = {}  # Cache for learned improvements
        
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here":
            try:
                # Configure the google-generativeai library
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.client = genai.GenerativeModel(settings.GEMINI_MODEL)
                
                # Initialize instructor client for enhanced structured outputs
                try:
                    # Try different instructor initialization methods based on version
                    self.instructor_client = None
                    
                    # Method 1: Try from_gemini (newer versions)
                    if hasattr(instructor, 'from_gemini'):
                        try:
                            self.instructor_client = instructor.from_gemini(
                                client=self.client,
                                mode=instructor.Mode.GEMINI_JSON,
                            )
                            logger.info("Instructor client initialized with from_gemini")
                        except Exception as e:
                            logger.debug(f"from_gemini failed: {e}")
                    
                    # Method 2: Try patch method (older versions)
                    if not self.instructor_client and hasattr(instructor, 'patch'):
                        try:
                            self.instructor_client = instructor.patch(self.client, mode=instructor.Mode.GEMINI_JSON)
                            logger.info("Instructor client initialized with patch method")
                        except Exception as e:
                            logger.debug(f"patch method failed: {e}")
                    
                    # Method 3: Basic OpenAI-compatible wrapper (fallback)
                    if not self.instructor_client:
                        logger.info("Using basic Gemini API with JSON schema for structured outputs")
                        # Will use basic Gemini API with JSON schema
                        
                except Exception as inst_error:
                    logger.warning(f"Instructor initialization failed, using basic client: {inst_error}")
                    self.instructor_client = None
                
                logger.info("Gemini client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client = None
                self.instructor_client = None
        else:
            logger.warning("Gemini API key not configured")
    
    async def analyze_vulnerability(
        self,
        service_name: str,
        version: str,
        port: int,
        vulnerability_description: str,
        cve_id: Optional[str] = None,
        analysis_type: AnalysisType = AnalysisType.VULNERABILITY_ASSESSMENT
    ) -> Optional[Dict]:
        """Enhanced vulnerability analysis with structured output"""
        
        if not self.client:
            logger.warning("Gemini client not available")
            return self._fallback_analysis(service_name, version, vulnerability_description)
        
        try:
            # Select appropriate analysis method based on type
            if analysis_type == AnalysisType.VULNERABILITY_ASSESSMENT:
                return await self._structured_vulnerability_analysis(
                    service_name, version, port, vulnerability_description, cve_id
                )
            elif analysis_type == AnalysisType.BUSINESS_IMPACT:
                return await self._business_impact_analysis(
                    service_name, version, vulnerability_description, cve_id
                )
            elif analysis_type == AnalysisType.PATCH_RECOMMENDATION:
                return await self._patch_recommendation_analysis(
                    service_name, version, vulnerability_description, cve_id
                )
            else:
                return await self._general_analysis(
                    service_name, version, port, vulnerability_description, cve_id
                )
                
        except Exception as e:
            logger.error(f"Vulnerability analysis failed: {e}")
            return self._fallback_analysis(service_name, version, vulnerability_description)
    
    async def _structured_vulnerability_analysis(
        self,
        service_name: str,
        version: str,
        port: int,
        vulnerability_description: str,
        cve_id: Optional[str] = None
    ) -> Optional[Dict]:
        """Perform structured vulnerability analysis using Gemini with caching and feedback learning"""
        
        # Check cache first
        cached_analysis = self.cache.get_vulnerability_analysis(
            service_name, version, vulnerability_description
        )
        if cached_analysis:
            logger.debug(f"Cache hit for vulnerability analysis: {service_name}")
            return cached_analysis
        
        logger.debug(f"Cache miss for vulnerability analysis: {service_name}")
        
        base_prompt = f"""
        Analyze this vulnerability and provide a comprehensive assessment:

        Service: {service_name}
        Version: {version}
        Port: {port}
        Description: {vulnerability_description}
        {f"CVE ID: {cve_id}" if cve_id else ""}

        Focus on:
        1. Accurate severity assessment based on exploitability and impact
        2. Specific, actionable remediation steps (format as numbered list with clear headers)
        3. Terminal commands for immediate remediation across different operating systems
        4. Business impact analysis
        5. Realistic implementation timeline
        6. Compliance implications (PCI-DSS, HIPAA, SOX, etc.)

        IMPORTANT: 
        - Format recommendations as a structured list with clear sections using ** for headers and • for bullet points
        - Generate specific terminal commands for Ubuntu/Debian, CentOS/RHEL, and where applicable macOS
        - Include commands for: updating packages, restarting services, configuration changes, verification steps
        - Mark commands that require sudo privileges or are potentially destructive
        - Provide backup/rollback commands when applicable
        """
        
        # Enhance prompt with feedback-based improvements
        enhanced_prompt = self._enhance_prompt_with_feedback(base_prompt, "vulnerability_assessment")
        
        try:
            if self.instructor_client:
                # Use instructor for enhanced structured output
                response = self.instructor_client.messages.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a cybersecurity expert specializing in vulnerability analysis. "
                                     "Analyze vulnerabilities and provide comprehensive, actionable security recommendations. "
                                     "Always consider business impact, technical complexity, and risk factors in your analysis. "
                                     "Format recommendations as structured lists with clear section headers using ** and bullet points using •. "
                                     "Generate specific terminal commands for Ubuntu/Debian, CentOS/RHEL, and macOS when applicable. "
                                     "Include update commands, service restarts, configuration changes, and verification steps. "
                                     "Mark sudo requirements and destructive operations clearly."
                        },
                        {
                            "role": "user",
                            "content": enhanced_prompt
                        }
                    ],
                    response_model=VulnerabilityAnalysis
                )
                analysis_result = response.dict() if hasattr(response, 'dict') else response.model_dump()
            else:
                # Fallback to standard Gemini API without response schema due to $defs compatibility issue
                response = self.client.generate_content(
                    f"""You are a cybersecurity expert. {enhanced_prompt}
                    
                    Respond with a JSON object matching this structure:
                    {{
                        "severity": "Critical|High|Medium|Low",
                        "risk_score": 0-10,
                        "recommendation": "detailed steps",
                        "remediation_commands": [
                            {{
                                "title": "Command description",
                                "command": "actual terminal command",
                                "os": "ubuntu|centos|macos",
                                "description": "what this command does",
                                "requires_sudo": true/false,
                                "is_destructive": true/false
                            }}
                        ],
                        "business_impact": "impact description",
                        "technical_details": "technical explanation",
                        "patch_priority": "Immediate|High|Medium|Low",
                        "estimated_effort": "time estimate",
                        "prerequisites": ["list", "of", "prerequisites"],
                        "compliance_impact": ["frameworks", "affected"]
                    }}""",
                    generation_config=genai.GenerationConfig(temperature=0.3)
                )
                analysis_result = self._parse_gemini_response(response.text)
            
            # Cache the result
            if analysis_result:
                self.cache.set_vulnerability_analysis(
                    service_name, version, vulnerability_description, analysis_result
                )
                logger.debug(f"Cached vulnerability analysis for: {service_name}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Structured analysis failed: {e}")
            return await self._general_analysis(service_name, version, port, vulnerability_description, cve_id)
    
    async def _business_impact_analysis(
        self,
        service_name: str,
        version: str,
        vulnerability_description: str,
        cve_id: Optional[str] = None
    ) -> Optional[Dict]:
        """Perform business impact analysis with feedback learning"""
        
        base_prompt = f"""
        Analyze the business impact of this vulnerability:

        Service: {service_name} ({version})
        Vulnerability: {vulnerability_description}
        {f"CVE: {cve_id}" if cve_id else ""}

        Consider:
        1. Financial losses from potential exploitation
        2. Operational disruption scenarios
        3. Regulatory compliance implications
        4. Customer trust and reputation impact
        5. Recovery and incident response costs
        """
        
        # Enhance prompt with feedback-based improvements
        enhanced_prompt = self._enhance_prompt_with_feedback(base_prompt, "business_impact")
        
        try:
            if self.instructor_client:
                response = self.instructor_client.messages.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a business risk analyst specializing in cybersecurity impact assessment. "
                                     "Analyze vulnerabilities from a business perspective, considering financial, operational, "
                                     "and reputational impacts. Provide quantifiable estimates where possible."
                        },
                        {
                            "role": "user",
                            "content": enhanced_prompt
                        }
                    ],
                    response_model=BusinessImpactAnalysis
                )
                return response.dict() if hasattr(response, 'dict') else response.model_dump()
            else:
                response = self.client.generate_content(
                    f"""You are a business risk analyst. {enhanced_prompt}
                    
                    Respond with a JSON object with these fields:
                    {{
                        "financial_impact": "potential financial losses",
                        "operational_impact": "impact on operations",
                        "reputation_risk": "reputation impact",
                        "regulatory_implications": ["compliance", "issues"],
                        "customer_impact": "customer impact",
                        "recovery_cost": "recovery costs"
                    }}""",
                    generation_config=genai.GenerationConfig(temperature=0.3)
                )
                return self._parse_gemini_response(response.text)
            
        except Exception as e:
            logger.error(f"Business impact analysis failed: {e}")
            return None
    
    async def _patch_recommendation_analysis(
        self,
        service_name: str,
        version: str,
        vulnerability_description: str,
        cve_id: Optional[str] = None
    ) -> Optional[Dict]:
        """Generate detailed patch recommendations with feedback learning"""
        
        base_prompt = f"""
        Provide patch management recommendations for:

        Service: {service_name} ({version})
        Vulnerability: {vulnerability_description}
        {f"CVE: {cve_id}" if cve_id else ""}

        Include:
        1. Specific patch versions or mitigation steps
        2. Deployment timeline and strategy
        3. Testing requirements before deployment
        4. Rollback procedures
        5. Risk if patching is delayed
        """
        
        # Enhance prompt with feedback-based improvements
        enhanced_prompt = self._enhance_prompt_with_feedback(base_prompt, "patch_recommendation")
        
        try:
            if self.instructor_client:
                response = self.instructor_client.messages.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a patch management expert. Provide specific, actionable "
                                     "patch recommendations with deployment strategies, testing requirements, and risk assessments."
                        },
                        {
                            "role": "user",
                            "content": enhanced_prompt
                        }
                    ],
                    response_model=PatchRecommendation
                )
                return response.dict() if hasattr(response, 'dict') else response.model_dump()
            else:
                response = self.client.generate_content(
                    f"""You are a patch management expert. {enhanced_prompt}
                    
                    Respond with a JSON object with these fields:
                    {{
                        "urgency": "Critical|High|Medium|Low",
                        "timeline": "recommended timeline",
                        "patch_version": "specific patch version",
                        "risk_if_not_patched": "risk description",
                        "deployment_strategy": "deployment approach",
                        "testing_requirements": ["testing", "steps"],
                        "rollback_plan": "rollback strategy"
                    }}""",
                    generation_config=genai.GenerationConfig(temperature=0.3)
                )
                return self._parse_gemini_response(response.text)
            
        except Exception as e:
            logger.error(f"Patch recommendation failed: {e}")
            return None
    
    async def _general_analysis(
        self,
        service_name: str,
        version: str,
        port: int,
        vulnerability_description: str,
        cve_id: Optional[str] = None
    ) -> Optional[Dict]:
        """Fallback general analysis method"""
        
        prompt = f"""
        Analyze this vulnerability and provide a comprehensive assessment:

        Service: {service_name}
        Version: {version}
        Port: {port}
        Description: {vulnerability_description}
        {f"CVE ID: {cve_id}" if cve_id else ""}

        Format recommendations as structured lists with:
        **Section Title:** Brief description
        • Bullet point details
        • Implementation steps
        
        Provide analysis in JSON format with these fields:
        - severity (Critical/High/Medium/Low)
        - risk_score (0-10)
        - recommendation (detailed steps formatted with ** for headers and • for bullets)
        - business_impact (impact description)
        - technical_details (technical explanation)
        - patch_priority (Immediate/High/Medium/Low)
        """
        
        try:
            response = self.client.generate_content(
                f"""You are a cybersecurity expert. Provide detailed vulnerability analysis. {prompt}""",
                generation_config=genai.GenerationConfig(temperature=0.3)
            )
            
            return self._parse_gemini_response(response.text)
            
        except Exception as e:
            logger.error(f"General analysis failed: {e}")
            return None
    
    def _parse_gemini_response(self, content: str) -> Dict:
        """Parse Gemini response and extract structured data"""
        try:
            # Try to extract JSON from the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: create structured response from text
                return {
                    "recommendation": content,
                    "severity": "Medium",
                    "risk_score": 5.0,
                    "technical_details": content,
                    "business_impact": "Moderate security risk requiring attention",
                    "patch_priority": "Medium"
                }
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse Gemini response as JSON")
            return {
                "recommendation": content,
                "severity": "Medium",
                "risk_score": 5.0,
                "technical_details": content,
                "business_impact": "Security risk requiring evaluation",
                "patch_priority": "Medium"
            }
    
    def _fallback_analysis(self, service_name: str, version: str, description: str) -> Dict:
        """Provide fallback analysis when Gemini is unavailable"""
        return {
            "severity": "Medium",
            "risk_score": 5.0,
            "recommendation": f"Update {service_name} to the latest version and review security configuration",
            "business_impact": "Potential security vulnerability that could impact system security",
            "technical_details": description,
            "patch_priority": "Medium",
            "estimated_effort": "2-4 hours",
            "prerequisites": ["System backup", "Maintenance window", "Testing environment"]
        }
    
    async def generate_report(
        self,
        vulnerabilities: List[Dict],
        report_type: str = "executive"
    ) -> Optional[str]:
        """Generate enhanced vulnerability report using Gemini"""
        
        if not self.client:
            logger.warning("Gemini client not available")
            return None
        
        try:
            # Truncate vulnerability list if too large
            vuln_summary = self._prepare_vulnerability_summary(vulnerabilities, report_type)
            
            prompt = self._build_enhanced_report_prompt(vuln_summary, report_type)
            
            response = self.client.generate_content(
                f"""You are a cybersecurity analyst creating a {report_type} vulnerability report. 
                Focus on clear communication, actionable insights, and business value. {prompt}""",
                generation_config=genai.GenerationConfig(temperature=0.3)
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return None
    
    def _prepare_vulnerability_summary(self, vulnerabilities: List[Dict], report_type: str) -> str:
        """Prepare vulnerability summary optimized for report type"""
        
        # Count vulnerabilities by severity
        critical_count = len([v for v in vulnerabilities if v.get('severity') == 'Critical'])
        high_count = len([v for v in vulnerabilities if v.get('severity') == 'High'])
        medium_count = len([v for v in vulnerabilities if v.get('severity') == 'Medium'])
        low_count = len([v for v in vulnerabilities if v.get('severity') == 'Low'])
        
        # Count vulnerabilities by status
        open_count = len([v for v in vulnerabilities if v.get('status') == 'open'])
        patched_count = len([v for v in vulnerabilities if v.get('status') == 'patched'])
        
        summary = f"VULNERABILITY OVERVIEW:\\n"
        summary += f"Total vulnerabilities: {len(vulnerabilities)}\\n"
        summary += f"Severity breakdown: Critical({critical_count}), High({high_count}), Medium({medium_count}), Low({low_count})\\n"
        summary += f"Status: Open({open_count}), Patched({patched_count})\\n\\n"
        
        if report_type == "executive":
            # Focus on high-level metrics and business impact
            
            # Include top 5 most critical vulnerabilities
            critical_vulns = [v for v in vulnerabilities if v.get('severity') == 'Critical'][:5]
            if critical_vulns:
                summary += "CRITICAL VULNERABILITIES:\\n"
                for i, vuln in enumerate(critical_vulns, 1):
                    summary += f"{i}. {vuln.get('service_name', 'Unknown')} - {vuln.get('description', '')[:100]}...\\n"
                summary += "\\n"
            
            # Include high severity vulnerabilities
            high_vulns = [v for v in vulnerabilities if v.get('severity') == 'High'][:3]
            if high_vulns:
                summary += "HIGH SEVERITY VULNERABILITIES:\\n"
                for i, vuln in enumerate(high_vulns, 1):
                    summary += f"{i}. {vuln.get('service_name', 'Unknown')} - {vuln.get('description', '')[:100]}...\\n"
        else:
            # Technical report - include more details with remediation commands
            summary += "DETAILED VULNERABILITY ANALYSIS:\\n"
            for i, vuln in enumerate(vulnerabilities[:15], 1):  # Limit to 15 for context
                summary += f"\\n{i}. {vuln.get('service_name', 'Unknown')} "
                summary += f"({vuln.get('severity', 'Unknown')}) - Port {vuln.get('port', 'N/A')}\\n"
                summary += f"   CVE: {vuln.get('cve_id', 'N/A')} | CVSS: {vuln.get('cvss_score', 'N/A')}\\n"
                summary += f"   Description: {vuln.get('description', 'No description')[:150]}...\\n"
                
                # Include remediation commands if available
                commands = vuln.get('remediation_commands', [])
                if commands:
                    summary += f"   Available remediation commands: {len(commands)} commands\\n"
        
        return self.context_manager.truncate_context(summary)
    
    def _build_enhanced_report_prompt(self, vuln_summary: str, report_type: str) -> str:
        """Build enhanced prompts for different report types"""
        
        if report_type == "executive":
            return f"""
Create an executive summary report for the following vulnerabilities:

{vuln_summary}

Structure the report as follows:

## Executive Summary
Brief overview of the security posture and key concerns

## Risk Assessment
- Overall risk level and business impact
- Financial implications of vulnerabilities
- Regulatory compliance concerns

## Key Findings
- Most critical vulnerabilities requiring immediate attention
- Trends and patterns in the vulnerability landscape
- Areas of greatest concern

## Strategic Recommendations
- Prioritized action items with business justification
- Resource requirements and timeline
- Risk mitigation strategies

## Remediation Roadmap
- Include specific terminal commands for critical fixes
- Step-by-step implementation guidance
- Verification procedures

## Next Steps
- Immediate actions (next 24-48 hours)
- Short-term goals (next 30 days)
- Long-term security improvements

Write in clear business language suitable for executives and decision-makers.
Focus on business impact, cost implications, and strategic recommendations.
Include actionable technical steps where appropriate.
"""
        else:  # technical report
            return f"""
Create a detailed technical report for the following vulnerabilities:

{vuln_summary}

Structure the report as follows:

## Technical Summary
Overview of the vulnerability landscape and technical concerns

## Detailed Vulnerability Analysis
For each critical vulnerability:
- Technical description and attack vectors
- Affected systems and services
- Exploitation difficulty and likelihood

## Remediation Commands
For each vulnerability, include:
- Specific terminal commands for patching
- OS-specific instructions (Ubuntu/Debian, CentOS/RHEL)
- Service restart procedures
- Configuration file changes

## Implementation Guide
- Prerequisites and dependencies
- Step-by-step remediation instructions with command examples
- Rollback procedures with undo commands
- Verification methods with test commands

## Security Hardening Recommendations
- Additional security measures with configuration examples
- Preventive controls with implementation commands
- Monitoring and detection improvements

## Quick Reference
- Summary table of all critical commands
- Emergency procedures for immediate threats
- Contact information for escalation

Write in technical language suitable for IT professionals and system administrators.
Include specific commands, configurations, and technical procedures.
Format commands in code blocks for easy copying.
"""
    
    async def answer_query(
        self, 
        query: str, 
        context: Dict,
        conversation_id: Optional[str] = None
    ) -> Optional[str]:
        """Answer user queries with enhanced context awareness, caching, and feedback learning"""
        
        if not self.client:
            logger.warning("Gemini client not available")
            return None
        
        try:
            # Prepare enhanced context
            enhanced_context = self._enhance_query_context(context)
            
            # For caching, use a simplified context (exclude volatile data like timestamps)
            cache_context = self._prepare_cache_context(enhanced_context)
            
            # Check cache for similar queries (if not in conversation mode)
            user_id = context.get("query_metadata", {}).get("user_id", 0)
            if not conversation_id:  # Don't cache conversational queries
                cached_response = self.cache.get_query_response(query, cache_context, user_id)
                if cached_response:
                    logger.debug(f"Cache hit for query: {query[:50]}...")
                    return cached_response
            
            logger.debug(f"Cache miss for query: {query[:50]}...")
            
            # Build conversation history if available
            messages = []
            if conversation_id and conversation_id in self.conversation_memory:
                messages.extend(self.conversation_memory[conversation_id])
            
            # Create system message with context
            base_system_message = f"""You are a cybersecurity assistant helping users understand their vulnerability scan results.

Context Information:
{json.dumps(enhanced_context, indent=2)}

Provide helpful, accurate answers based on the vulnerability data. 
Be specific when referencing vulnerabilities and provide actionable advice.
If asked about trends or comparisons, use the historical data provided.
"""
            
            # Enhance system message with feedback-based improvements for query analysis
            system_message = self._enhance_prompt_with_feedback(base_system_message, "query")
            
            # Build conversation for Gemini
            conversation_content = system_message + "\\n\\n"
            
            # Add conversation history
            for message in messages:
                role = "User" if message["role"] == "user" else "Assistant"
                conversation_content += f"{role}: {message['content']}\\n\\n"
            
            # Add current query
            conversation_content += f"User: {query}\\n\\nAssistant:"
            
            response = self.client.generate_content(
                conversation_content,
                generation_config=genai.GenerationConfig(temperature=0.3)
            )
            
            answer = response.text
            
            # Cache the response (if not conversational)
            if not conversation_id and answer:
                self.cache.set_query_response(query, cache_context, user_id, answer)
                logger.debug(f"Cached query response for: {query[:50]}...")
            
            # Store conversation for future context
            if conversation_id:
                if conversation_id not in self.conversation_memory:
                    self.conversation_memory[conversation_id] = []
                
                self.conversation_memory[conversation_id].extend([
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": answer}
                ])
                
                # Keep only last 10 exchanges to manage memory
                if len(self.conversation_memory[conversation_id]) > 20:
                    self.conversation_memory[conversation_id] = self.conversation_memory[conversation_id][-20:]
            
            return answer
            
        except Exception as e:
            logger.error(f"Query answering failed: {e}")
            return None
    
    def _enhance_query_context(self, context: Dict) -> Dict:
        """Enhance context with additional insights"""
        enhanced = context.copy()
        
        # Add vulnerability analysis
        if "severity_counts" in context:
            total = sum(context["severity_counts"].values())
            if total > 0:
                enhanced["risk_profile"] = {
                    "critical_percentage": (context["severity_counts"].get("Critical", 0) / total) * 100,
                    "high_percentage": (context["severity_counts"].get("High", 0) / total) * 100,
                    "overall_risk": "High" if context["severity_counts"].get("Critical", 0) > 0 else "Medium"
                }
        
        # Add service analysis
        if "common_services" in context:
            enhanced["service_analysis"] = {
                "most_vulnerable": context["common_services"][0] if context["common_services"] else None,
                "diversity": len(context["common_services"])
            }
        
        return enhanced
    
    def _prepare_cache_context(self, context: Dict) -> Dict:
        """Prepare context for caching by removing volatile data"""
        cache_context = {}
        
        # Include stable context data
        if "user_profile" in context:
            profile = context["user_profile"]
            cache_context["user_profile"] = {
                "total_scans": profile.get("total_scans", 0),
                "total_vulnerabilities": profile.get("total_vulnerabilities", 0)
            }
        
        if "severity_distribution" in context:
            severity = context["severity_distribution"]
            cache_context["severity_distribution"] = {
                "counts": severity.get("counts", {}),
                "risk_level": severity.get("risk_level", "Unknown")
            }
        
        if "service_landscape" in context:
            landscape = context["service_landscape"]
            cache_context["service_landscape"] = {
                "service_diversity": landscape.get("service_diversity", 0),
                "most_vulnerable_services": landscape.get("most_vulnerable_services", [])[:3]  # Limit for caching
            }
        
        # Include risk patterns but exclude timestamps and volatile data
        if "risk_patterns" in context:
            patterns = context["risk_patterns"]
            cache_context["risk_patterns"] = {
                "average_cvss_score": patterns.get("average_cvss_score", 0),
                "risk_concentration": patterns.get("risk_concentration", "unknown")
            }
        
        return cache_context
    
    def set_feedback_service(self, feedback_service):
        """Inject feedback service for learning integration"""
        self.feedback_service = feedback_service
    
    async def load_feedback_improvements(self, analysis_type: str = None):
        """Load and cache feedback-based improvements for analysis types"""
        if not self.feedback_service:
            logger.warning("Feedback service not available for learning")
            return
        
        analysis_types = [analysis_type] if analysis_type else [
            "vulnerability_assessment", "business_impact", "patch_recommendation"
        ]
        
        for atype in analysis_types:
            try:
                learning_context = self.feedback_service.get_learning_context_for_analysis_type(atype)
                if learning_context.get("feedback_available"):
                    self.learned_improvements[atype] = learning_context
                    logger.info(f"Loaded feedback improvements for {atype}")
            except Exception as e:
                logger.error(f"Failed to load feedback improvements for {atype}: {e}")
    
    def _enhance_prompt_with_feedback(self, base_prompt: str, analysis_type: str) -> str:
        """Enhance prompts with feedback-based improvements"""
        if analysis_type not in self.learned_improvements:
            return base_prompt
        
        learning_data = self.learned_improvements[analysis_type]
        performance_metrics = learning_data.get("performance_metrics", {})
        learning_signals = learning_data.get("learning_signals", {})
        
        # Add performance context
        avg_rating = performance_metrics.get("average_rating", 0)
        if avg_rating < 3.0:
            base_prompt += f"""
            
IMPORTANT - FEEDBACK INTEGRATION:
Recent user feedback indicates this analysis type needs improvement (avg rating: {avg_rating:.1f}/5).
"""
        
        # Add improvement suggestions
        suggestions = learning_signals.get("improvement_suggestions", [])
        if suggestions:
            base_prompt += "\nBased on user feedback, please focus on:\n"
            for suggestion in suggestions[:3]:  # Limit to top 3 suggestions
                base_prompt += f"- {suggestion}\n"
        
        # Add positive patterns to reinforce
        positive_patterns = learning_signals.get("positive_patterns", [])
        if positive_patterns:
            base_prompt += f"\nUsers particularly appreciate: {', '.join(positive_patterns[:5])}\n"
        
        # Add negative patterns to avoid
        negative_patterns = learning_signals.get("negative_patterns", [])
        if negative_patterns:
            base_prompt += f"\nAvoid these issues reported by users: {', '.join(negative_patterns[:5])}\n"
        
        return base_prompt
    
    def _get_analysis_type_from_method(self, analysis_type: AnalysisType) -> str:
        """Convert AnalysisType enum to string for feedback lookup"""
        return {
            AnalysisType.VULNERABILITY_ASSESSMENT: "vulnerability_assessment",
            AnalysisType.BUSINESS_IMPACT: "business_impact", 
            AnalysisType.PATCH_RECOMMENDATION: "patch_recommendation",
            AnalysisType.RISK_ANALYSIS: "risk_analysis",
            AnalysisType.COMPLIANCE_MAPPING: "compliance_mapping"
        }.get(analysis_type, "general")
    
    async def refresh_learning_cache(self):
        """Refresh the learning cache with latest feedback"""
        if self.feedback_service:
            await self.load_feedback_improvements()
            logger.info("Refreshed feedback learning cache")

    async def close(self):
        """Clean up resources"""
        # Gemini client doesn't require explicit closing like aiohttp
        self.conversation_memory.clear()
        self.learned_improvements.clear()


# Create a singleton instance
gemini_llm_service = GeminiLLMService()

# Backward compatibility aliases
llm_service = gemini_llm_service
LLMService = GeminiLLMService
EnhancedLLMService = GeminiLLMService