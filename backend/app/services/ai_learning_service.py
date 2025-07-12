"""
AI Learning Service - Integrates feedback with LLM services for continuous improvement
"""
import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session

from app.services.feedback_service import FeedbackService
from app.services.gemini_llm_service import gemini_llm_service
from app.core.database import get_db

logger = logging.getLogger(__name__)


class AILearningService:
    """Service to manage AI learning from user feedback"""
    
    def __init__(self):
        self.llm_service = gemini_llm_service
        self.feedback_service: Optional[FeedbackService] = None
        self.initialized = False
    
    def initialize_with_db(self, db: Session):
        """Initialize the service with database session"""
        self.feedback_service = FeedbackService(db)
        self.llm_service.set_feedback_service(self.feedback_service)
        self.initialized = True
        logger.info("AI Learning Service initialized with feedback integration")
    
    async def load_learning_improvements(self, analysis_type: str = None):
        """Load feedback-based improvements for analysis types"""
        if not self.initialized:
            logger.warning("AI Learning Service not initialized")
            return
        
        await self.llm_service.load_feedback_improvements(analysis_type)
        logger.info(f"Loaded learning improvements for {analysis_type or 'all types'}")
    
    async def refresh_learning_cache(self):
        """Refresh the learning cache with latest feedback"""
        if not self.initialized:
            logger.warning("AI Learning Service not initialized")
            return
        
        await self.llm_service.refresh_learning_cache()
        logger.info("Refreshed AI learning cache")
    
    def get_learning_status(self) -> Dict:
        """Get current learning status and metrics"""
        if not self.initialized:
            return {"status": "not_initialized"}
        
        return {
            "status": "active",
            "initialized": self.initialized,
            "cached_improvements": len(self.llm_service.learned_improvements),
            "available_analysis_types": list(self.llm_service.learned_improvements.keys())
        }
    
    async def apply_feedback_to_analysis_type(self, analysis_type: str) -> Dict:
        """Apply feedback learning to specific analysis type"""
        if not self.initialized:
            return {"status": "not_initialized"}
        
        try:
            # Load latest feedback for this analysis type
            await self.load_learning_improvements(analysis_type)
            
            # Apply learning (this would trigger prompt updates)
            result = await self.feedback_service.apply_feedback_learning(analysis_type)
            
            return {
                "status": "success",
                "analysis_type": analysis_type,
                "learning_applied": True,
                "result": result
            }
        except Exception as e:
            logger.error(f"Failed to apply feedback learning for {analysis_type}: {e}")
            return {
                "status": "error",
                "analysis_type": analysis_type,
                "error": str(e)
            }
    
    def get_feedback_analytics(self, days: int = 30) -> Dict:
        """Get feedback analytics for learning insights"""
        if not self.initialized:
            return {"status": "not_initialized"}
        
        return self.feedback_service.get_feedback_analytics(days)
    
    def get_improvement_insights(self) -> Dict:
        """Get improvement insights based on feedback"""
        if not self.initialized:
            return {"status": "not_initialized"}
        
        return self.feedback_service.get_improvement_insights()


# Create singleton instance
ai_learning_service = AILearningService()