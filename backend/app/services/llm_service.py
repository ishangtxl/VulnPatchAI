"""
Enhanced LLM Service - Redirects to Gemini LLM Service for backward compatibility
"""
import logging

# Import the new Gemini service and provide backward compatibility
from app.services.gemini_llm_service import (
    GeminiLLMService,
    AnalysisType,
    VulnerabilityAnalysis,
    PatchRecommendation,
    BusinessImpactAnalysis,
    ContextWindow,
    gemini_llm_service
)

logger = logging.getLogger(__name__)

# Backward compatibility aliases - existing code will continue to work
EnhancedLLMService = GeminiLLMService
llm_service = gemini_llm_service
LLMService = GeminiLLMService

# Export all classes and instances for backward compatibility
__all__ = [
    'EnhancedLLMService',
    'GeminiLLMService', 
    'AnalysisType',
    'VulnerabilityAnalysis',
    'PatchRecommendation',
    'BusinessImpactAnalysis',
    'ContextWindow',
    'llm_service',
    'LLMService'
]