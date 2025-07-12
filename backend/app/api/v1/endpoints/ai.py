"""
Enhanced AI assistant endpoints with advanced analysis capabilities
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.services.ai_service import EnhancedAIService
from app.schemas.ai import (
    QueryRequest, QueryResponse, AnalysisRequest, AnalysisResponse,
    FeedbackRequest, FeedbackResponse, BusinessRiskAssessment,
    PatchPrioritization, VulnerabilityInsight
)
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def ask_ai(
    query_request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask AI assistant about vulnerabilities with conversation memory"""
    ai_service = EnhancedAIService(db)
    
    try:
        response = await ai_service.process_query(
            query=query_request.query,
            user_id=current_user.id,
            context=query_request.context,
            conversation_id=query_request.conversation_id
        )
        
        if not response:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is currently unavailable. Please check your OpenAI API configuration."
            )
        
        return QueryResponse(
            query=query_request.query,
            response=response,
            conversation_id=query_request.conversation_id,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_scan(
    analysis_request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get enhanced AI analysis for a scan with multiple analysis types"""
    ai_service = EnhancedAIService(db)
    
    try:
        analysis = await ai_service.analyze_scan(
            scan_id=analysis_request.scan_id,
            user_id=current_user.id,
            analysis_type=analysis_request.analysis_type
        )
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found or analysis failed"
            )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing scan: {str(e)}"
        )


@router.post("/analyze/business-impact", response_model=AnalysisResponse)
async def analyze_business_impact(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get business impact analysis for a scan"""
    ai_service = EnhancedAIService(db)
    
    try:
        analysis = await ai_service.analyze_scan(
            scan_id=scan_id,
            user_id=current_user.id,
            analysis_type="business_impact"
        )
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found or business impact analysis failed"
            )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing business impact analysis: {str(e)}"
        )


@router.post("/analyze/patch-prioritization", response_model=AnalysisResponse)
async def analyze_patch_prioritization(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patch prioritization analysis for a scan"""
    ai_service = EnhancedAIService(db)
    
    try:
        analysis = await ai_service.analyze_scan(
            scan_id=scan_id,
            user_id=current_user.id,
            analysis_type="patch_prioritization"
        )
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found or patch prioritization analysis failed"
            )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing patch prioritization analysis: {str(e)}"
        )


@router.get("/conversation/{conversation_id}/history")
async def get_conversation_history(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, le=100, description="Maximum number of messages to return")
):
    """Get conversation history for a specific conversation (Deprecated - use /conversation endpoints)"""
    try:
        # Redirect to new conversation service
        from app.services.conversation_service import ConversationService
        conversation_service = ConversationService(db)
        
        messages = await conversation_service.get_conversation_messages(
            conversation_id=conversation_id,
            user_id=current_user.id,
            limit=limit
        )
        
        return {
            "conversation_id": conversation_id,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat(),
                    "token_count": msg.token_count,
                    "model_used": msg.model_used,
                    "processing_time_ms": msg.processing_time_ms
                }
                for msg in messages
            ],
            "total_messages": len(messages),
            "note": "This endpoint is deprecated. Use /api/v1/conversation/{conversation_id}/messages instead."
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation history: {str(e)}"
        )


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback_request: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback on AI analysis"""
    try:
        # Create feedback record
        from app.models.feedback import Feedback
        
        feedback = Feedback(
            user_id=current_user.id,
            analysis_id=feedback_request.analysis_id,
            rating=feedback_request.rating,
            comment=feedback_request.comment,
            is_helpful=feedback_request.is_helpful
        )
        
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        return FeedbackResponse(
            feedback_id=feedback.id,
            message="Feedback submitted successfully. Thank you for helping us improve!",
            created_at=feedback.created_at
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting feedback: {str(e)}"
        )


@router.get("/models/available")
async def get_available_models(
    current_user: User = Depends(get_current_user)
):
    """Get list of available AI models and analysis types"""
    return {
        "analysis_types": [
            {
                "type": "comprehensive",
                "name": "Comprehensive Analysis",
                "description": "Complete vulnerability assessment with AI insights"
            },
            {
                "type": "business_impact",
                "name": "Business Impact Analysis",
                "description": "Focus on business and financial implications"
            },
            {
                "type": "patch_prioritization",
                "name": "Patch Prioritization",
                "description": "Strategic patch management recommendations"
            },
            {
                "type": "basic",
                "name": "Basic Analysis",
                "description": "Standard vulnerability summary"
            }
        ],
        "ai_models": [
            {
                "model": "gpt-4",
                "capabilities": ["vulnerability_analysis", "business_impact", "patch_recommendations"],
                "status": "available"
            }
        ],
        "features": [
            "Structured vulnerability analysis",
            "Business impact assessment",
            "Patch prioritization matrix",
            "Conversation memory",
            "Compliance mapping",
            "Risk scoring with AI enhancement"
        ]
    }


@router.post("/suggest-questions")
async def get_suggested_questions(
    scan_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-suggested questions based on scan context"""
    ai_service = EnhancedAIService(db)
    
    try:
        # Get user context for suggestions
        user_context = await ai_service._get_enhanced_user_context(current_user.id)
        
        # Generate contextual suggestions
        suggestions = []
        
        # Basic suggestions
        base_suggestions = [
            "What are my most critical vulnerabilities?",
            "How can I improve my security posture?",
            "What services should I patch first?",
            "Show me vulnerabilities by severity",
            "What is my overall risk score?"
        ]
        
        # Context-aware suggestions
        if user_context.get("severity_distribution", {}).get("counts", {}).get("Critical", 0) > 0:
            suggestions.append("What business impact do my critical vulnerabilities have?")
            suggestions.append("How quickly should I patch critical vulnerabilities?")
        
        if user_context.get("service_landscape", {}).get("service_diversity", 0) > 5:
            suggestions.append("Which services are most vulnerable in my environment?")
        
        if user_context.get("temporal_trends", {}).get("trend_direction") == "worsening":
            suggestions.append("Why are my vulnerability numbers increasing?")
            suggestions.append("What can I do to reverse the vulnerability trend?")
        
        # Combine and limit suggestions
        all_suggestions = base_suggestions + suggestions
        
        return {
            "suggestions": all_suggestions[:8],
            "context_based": len(suggestions) > 0,
            "user_profile": {
                "total_vulnerabilities": user_context.get("user_profile", {}).get("total_vulnerabilities", 0),
                "risk_level": user_context.get("severity_distribution", {}).get("risk_level", "Unknown")
            }
        }
        
    except Exception as e:
        # Fallback to basic suggestions if context analysis fails
        return {
            "suggestions": [
                "What are my most critical vulnerabilities?",
                "How can I improve my security posture?",
                "What services should I patch first?",
                "Show me vulnerabilities by severity",
                "What is my overall risk score?"
            ],
            "context_based": False,
            "error": f"Context analysis failed: {str(e)}"
        }


@router.get("/feedback/analytics")
async def get_feedback_analytics(
    days: int = Query(default=30, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feedback analytics and insights"""
    try:
        from app.services.feedback_service import FeedbackService
        
        feedback_service = FeedbackService(db)
        analytics = feedback_service.get_feedback_analytics(days)
        
        return {
            "analytics": analytics,
            "period": f"Last {days} days",
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving feedback analytics: {str(e)}"
        )


@router.get("/feedback/insights")
async def get_improvement_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI improvement insights based on user feedback"""
    try:
        from app.services.feedback_service import FeedbackService
        
        feedback_service = FeedbackService(db)
        insights = feedback_service.get_improvement_insights()
        
        return {
            "insights": insights,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving improvement insights: {str(e)}"
        )


@router.get("/feedback/trends")
async def get_feedback_trends(
    days: int = Query(default=90, le=365, description="Number of days for trend analysis"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feedback trends over time"""
    try:
        from app.services.feedback_service import FeedbackService
        
        feedback_service = FeedbackService(db)
        trends = feedback_service.get_feedback_trends(days)
        
        return {
            "trends": trends,
            "period": f"Last {days} days",
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving feedback trends: {str(e)}"
        )


@router.post("/learning/apply/{analysis_type}")
async def apply_feedback_learning(
    analysis_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply feedback learning to improve AI analysis"""
    try:
        from app.services.ai_learning_service import ai_learning_service
        
        # Initialize learning service with database session
        ai_learning_service.initialize_with_db(db)
        
        # Apply learning for the specific analysis type
        result = await ai_learning_service.apply_feedback_to_analysis_type(analysis_type)
        
        return {
            "learning_result": result,
            "applied_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error applying feedback learning: {str(e)}"
        )


@router.get("/learning/status")
async def get_learning_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current AI learning status and metrics"""
    try:
        from app.services.ai_learning_service import ai_learning_service
        
        # Initialize learning service with database session
        ai_learning_service.initialize_with_db(db)
        
        status = ai_learning_service.get_learning_status()
        analytics = ai_learning_service.get_feedback_analytics()
        insights = ai_learning_service.get_improvement_insights()
        
        return {
            "learning_status": status,
            "feedback_analytics": analytics,
            "improvement_insights": insights,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving learning status: {str(e)}"
        )


@router.post("/learning/refresh")
async def refresh_learning_cache(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh AI learning cache with latest feedback"""
    try:
        from app.services.ai_learning_service import ai_learning_service
        
        # Initialize learning service with database session
        ai_learning_service.initialize_with_db(db)
        
        # Refresh learning cache
        await ai_learning_service.refresh_learning_cache()
        
        return {
            "status": "success",
            "message": "AI learning cache refreshed successfully",
            "refreshed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing learning cache: {str(e)}"
        )


@router.post("/learning/load/{analysis_type}")
async def load_learning_improvements(
    analysis_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Load feedback-based improvements for specific analysis type"""
    try:
        from app.services.ai_learning_service import ai_learning_service
        
        # Initialize learning service with database session
        ai_learning_service.initialize_with_db(db)
        
        # Load improvements for specific analysis type
        await ai_learning_service.load_learning_improvements(analysis_type)
        
        return {
            "status": "success",
            "analysis_type": analysis_type,
            "message": f"Learning improvements loaded for {analysis_type}",
            "loaded_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading learning improvements: {str(e)}"
        )


@router.get("/cache/stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_user)
):
    """Get cache statistics and performance metrics"""
    try:
        from app.services.cache_service import cache_service
        
        stats = cache_service.get_stats()
        
        return {
            "cache_stats": stats,
            "cache_features": [
                "CVE lookup caching (24h TTL)",
                "AI vulnerability analysis caching (1h TTL)",
                "Query response caching (30min TTL)",
                "Report generation caching (2h TTL)"
            ],
            "performance_benefits": [
                "Reduced API calls to external services",
                "Faster response times for repeated queries",
                "Lower OpenAI API costs",
                "Improved user experience"
            ],
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving cache stats: {str(e)}"
        )


@router.post("/cache/clear")
async def clear_user_cache(
    current_user: User = Depends(get_current_user),
    cache_type: str = Query(default="all", description="Type of cache to clear: ai, cve, or all")
):
    """Clear cache for the current user"""
    try:
        from app.services.cache_service import cache_service, ai_cache
        
        cleared_items = 0
        
        if cache_type in ["ai", "all"]:
            # Clear AI query cache for user
            cleared_items += ai_cache.invalidate_user_cache(current_user.id)
        
        if cache_type in ["cve", "all"]:
            # Clear CVE cache (affects all users, so be cautious)
            if current_user.email.endswith("@admin.com"):  # Admin only
                pattern = "cve:*"
                cleared_items += cache_service.delete_pattern(pattern)
        
        return {
            "status": "success",
            "message": f"Cleared {cleared_items} cache entries",
            "cache_type": cache_type,
            "cleared_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cache: {str(e)}"
        )


@router.get("/performance/metrics")
async def get_performance_metrics(
    current_user: User = Depends(get_current_user)
):
    """Get AI performance metrics including cache effectiveness"""
    try:
        from app.services.cache_service import cache_service
        
        cache_stats = cache_service.get_stats()
        
        # Calculate performance improvements
        hit_rate = cache_stats.get("hit_rate", 0)
        estimated_savings = {
            "api_calls_saved": int(cache_stats.get("keyspace_hits", 0)),
            "estimated_cost_savings": f"${(cache_stats.get('keyspace_hits', 0) * 0.002):.2f}",  # Rough estimate
            "response_time_improvement": f"{min(hit_rate * 0.8, 70):.1f}%"  # Estimated improvement
        }
        
        return {
            "cache_performance": cache_stats,
            "estimated_savings": estimated_savings,
            "ai_features_active": [
                "Structured vulnerability analysis",
                "Business impact assessment", 
                "Patch prioritization",
                "Conversation memory",
                "Context-aware responses"
            ],
            "optimization_recommendations": [
                "Enable caching for better performance",
                "Use specific queries for better cache hits",
                "Regular cache cleanup for optimal performance"
            ] if hit_rate < 30 else [
                "Cache is performing well",
                "Good query patterns detected",
                "Optimal performance achieved"
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving performance metrics: {str(e)}"
        )