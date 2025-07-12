"""
Enhanced Feedback Service for AI learning and user feedback management
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import json

from app.models.feedback import Feedback
from app.models.user import User
from app.models.vulnerability import Vulnerability
from app.models.scan import Scan
from app.schemas.ai import FeedbackRequest, FeedbackResponse

logger = logging.getLogger(__name__)


class FeedbackService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_feedback(
        self,
        user_id: int,
        feedback_request: FeedbackRequest,
        feedback_type: str = "analysis",
        analysis_type: Optional[str] = None,
        conversation_id: Optional[str] = None,
        additional_data: Optional[Dict] = None
    ) -> Feedback:
        """Create a new feedback record"""
        
        try:
            feedback = Feedback(
                user_id=user_id,
                analysis_id=feedback_request.analysis_id,
                rating=feedback_request.rating,
                comment=feedback_request.comment,
                is_helpful=feedback_request.is_helpful,
                feedback_type=feedback_type,
                analysis_type=analysis_type,
                conversation_id=conversation_id,
                feedback_data=additional_data or {}
            )
            
            self.db.add(feedback)
            self.db.commit()
            self.db.refresh(feedback)
            
            logger.info(f"Created feedback {feedback.id} for user {user_id}")
            return feedback
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating feedback: {e}")
            raise
    
    async def create_vulnerability_feedback(
        self,
        user_id: int,
        vulnerability_id: int,
        rating: int,
        comment: Optional[str] = None,
        is_helpful: bool = True,
        recommendation_feedback: Optional[Dict] = None
    ) -> Feedback:
        """Create feedback for a specific vulnerability"""
        
        try:
            feedback = Feedback(
                user_id=user_id,
                vulnerability_id=vulnerability_id,
                rating=rating,
                comment=comment,
                is_helpful=is_helpful,
                feedback_type="vulnerability",
                feedback_data=recommendation_feedback or {}
            )
            
            self.db.add(feedback)
            self.db.commit()
            self.db.refresh(feedback)
            
            logger.info(f"Created vulnerability feedback {feedback.id} for vulnerability {vulnerability_id}")
            return feedback
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating vulnerability feedback: {e}")
            raise
    
    async def create_query_feedback(
        self,
        user_id: int,
        conversation_id: str,
        query: str,
        response: str,
        rating: int,
        comment: Optional[str] = None,
        is_helpful: bool = True
    ) -> Feedback:
        """Create feedback for an AI query response"""
        
        try:
            feedback_data = {
                "query": query,
                "response": response[:500],  # Truncate for storage
                "response_length": len(response)
            }
            
            feedback = Feedback(
                user_id=user_id,
                conversation_id=conversation_id,
                rating=rating,
                comment=comment,
                is_helpful=is_helpful,
                feedback_type="query",
                feedback_data=feedback_data
            )
            
            self.db.add(feedback)
            self.db.commit()
            self.db.refresh(feedback)
            
            logger.info(f"Created query feedback {feedback.id} for conversation {conversation_id}")
            return feedback
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating query feedback: {e}")
            raise
    
    def get_feedback_for_analysis(self, analysis_id: int) -> List[Feedback]:
        """Get all feedback for a specific analysis"""
        return (
            self.db.query(Feedback)
            .filter(Feedback.analysis_id == analysis_id)
            .order_by(Feedback.created_at.desc())
            .all()
        )
    
    def get_feedback_for_vulnerability(self, vulnerability_id: int) -> List[Feedback]:
        """Get all feedback for a specific vulnerability"""
        return (
            self.db.query(Feedback)
            .filter(Feedback.vulnerability_id == vulnerability_id)
            .order_by(Feedback.created_at.desc())
            .all()
        )
    
    def get_user_feedback(
        self, 
        user_id: int, 
        feedback_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Feedback]:
        """Get feedback submitted by a user"""
        query = self.db.query(Feedback).filter(Feedback.user_id == user_id)
        
        if feedback_type:
            query = query.filter(Feedback.feedback_type == feedback_type)
        
        return query.order_by(Feedback.created_at.desc()).limit(limit).all()
    
    def get_feedback_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get feedback analytics for the specified time period"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total feedback counts
        total_feedback = (
            self.db.query(func.count(Feedback.id))
            .filter(Feedback.created_at >= start_date)
            .scalar()
        )
        
        # Average ratings by type
        rating_stats = (
            self.db.query(
                Feedback.feedback_type,
                func.avg(Feedback.rating).label('avg_rating'),
                func.count(Feedback.id).label('count')
            )
            .filter(Feedback.created_at >= start_date)
            .group_by(Feedback.feedback_type)
            .all()
        )
        
        # Helpfulness statistics
        helpful_stats = (
            self.db.query(
                Feedback.is_helpful,
                func.count(Feedback.id).label('count')
            )
            .filter(Feedback.created_at >= start_date)
            .group_by(Feedback.is_helpful)
            .all()
        )
        
        # Analysis type ratings
        analysis_ratings = (
            self.db.query(
                Feedback.analysis_type,
                func.avg(Feedback.rating).label('avg_rating'),
                func.count(Feedback.id).label('count')
            )
            .filter(
                and_(
                    Feedback.created_at >= start_date,
                    Feedback.analysis_type.isnot(None)
                )
            )
            .group_by(Feedback.analysis_type)
            .all()
        )
        
        return {
            "period_days": days,
            "total_feedback": total_feedback,
            "rating_by_type": {
                stat.feedback_type: {
                    "average_rating": round(float(stat.avg_rating), 2),
                    "total_count": stat.count
                }
                for stat in rating_stats
            },
            "helpfulness": {
                "helpful": next((s.count for s in helpful_stats if s.is_helpful), 0),
                "not_helpful": next((s.count for s in helpful_stats if not s.is_helpful), 0)
            },
            "analysis_type_ratings": {
                stat.analysis_type: {
                    "average_rating": round(float(stat.avg_rating), 2),
                    "total_count": stat.count
                }
                for stat in analysis_ratings if stat.analysis_type
            }
        }
    
    def get_improvement_insights(self) -> Dict[str, Any]:
        """Get insights for AI improvement based on feedback"""
        
        # Low-rated items that need improvement
        low_rated_feedback = (
            self.db.query(Feedback)
            .filter(
                and_(
                    Feedback.rating <= 2,
                    Feedback.created_at >= datetime.utcnow() - timedelta(days=30)
                )
            )
            .order_by(Feedback.created_at.desc())
            .limit(20)
            .all()
        )
        
        # Common issues from comments
        comments_with_issues = (
            self.db.query(Feedback)
            .filter(
                and_(
                    Feedback.comment.isnot(None),
                    Feedback.rating <= 3,
                    Feedback.created_at >= datetime.utcnow() - timedelta(days=30)
                )
            )
            .all()
        )
        
        # Analysis type performance
        analysis_performance = (
            self.db.query(
                Feedback.analysis_type,
                func.avg(Feedback.rating).label('avg_rating'),
                func.count(Feedback.id).label('total')
            )
            .filter(
                and_(
                    Feedback.analysis_type.isnot(None),
                    Feedback.created_at >= datetime.utcnow() - timedelta(days=30)
                )
            )
            .group_by(Feedback.analysis_type)
            .all()
        )
        
        # Calculate low ratings separately for each analysis type
        low_rating_counts = {}
        for perf in analysis_performance:
            low_count = (
                self.db.query(func.count(Feedback.id))
                .filter(
                    and_(
                        Feedback.analysis_type == perf.analysis_type,
                        Feedback.rating <= 2,
                        Feedback.created_at >= datetime.utcnow() - timedelta(days=30)
                    )
                )
                .scalar()
            )
            low_rating_counts[perf.analysis_type] = low_count
        
        return {
            "low_rated_feedback": [
                {
                    "id": fb.id,
                    "type": fb.feedback_type,
                    "analysis_type": fb.analysis_type,
                    "rating": fb.rating,
                    "comment": fb.comment,
                    "created_at": fb.created_at.isoformat()
                }
                for fb in low_rated_feedback
            ],
            "improvement_areas": self._extract_improvement_areas(comments_with_issues),
            "analysis_performance": {
                stat.analysis_type: {
                    "average_rating": round(float(stat.avg_rating), 2),
                    "low_rating_percentage": round((low_rating_counts.get(stat.analysis_type, 0) / stat.total) * 100, 1) if stat.total > 0 else 0,
                    "total_feedback": stat.total,
                    "low_ratings": low_rating_counts.get(stat.analysis_type, 0)
                }
                for stat in analysis_performance
            }
        }
    
    def _extract_improvement_areas(self, feedback_list: List[Feedback]) -> List[Dict]:
        """Extract common improvement areas from feedback comments"""
        
        improvement_patterns = {
            "accuracy": ["wrong", "incorrect", "inaccurate", "mistake"],
            "completeness": ["missing", "incomplete", "more detail", "shallow"],
            "relevance": ["irrelevant", "not relevant", "off-topic", "not helpful"],
            "speed": ["slow", "takes too long", "timeout", "delayed"],
            "clarity": ["confusing", "unclear", "hard to understand", "complicated"]
        }
        
        issue_counts = {area: 0 for area in improvement_patterns.keys()}
        examples = {area: [] for area in improvement_patterns.keys()}
        
        for feedback in feedback_list:
            if not feedback.comment:
                continue
                
            comment_lower = feedback.comment.lower()
            
            for area, patterns in improvement_patterns.items():
                if any(pattern in comment_lower for pattern in patterns):
                    issue_counts[area] += 1
                    if len(examples[area]) < 3:  # Keep max 3 examples per area
                        examples[area].append({
                            "comment": feedback.comment[:200],
                            "rating": feedback.rating,
                            "type": feedback.feedback_type
                        })
        
        return [
            {
                "area": area,
                "count": count,
                "examples": examples[area]
            }
            for area, count in issue_counts.items()
            if count > 0
        ]
    
    def get_feedback_trends(self, days: int = 90) -> Dict[str, Any]:
        """Get feedback trends over time"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Daily feedback counts
        daily_feedback = (
            self.db.query(
                func.date(Feedback.created_at).label('date'),
                func.count(Feedback.id).label('count'),
                func.avg(Feedback.rating).label('avg_rating')
            )
            .filter(Feedback.created_at >= start_date)
            .group_by(func.date(Feedback.created_at))
            .order_by(func.date(Feedback.created_at))
            .all()
        )
        
        # Weekly averages
        weekly_trends = []
        current_date = start_date
        
        while current_date < datetime.utcnow():
            week_end = min(current_date + timedelta(days=7), datetime.utcnow())
            
            week_stats = (
                self.db.query(
                    func.count(Feedback.id).label('count'),
                    func.avg(Feedback.rating).label('avg_rating')
                )
                .filter(
                    and_(
                        Feedback.created_at >= current_date,
                        Feedback.created_at < week_end
                    )
                )
                .first()
            )
            
            weekly_trends.append({
                "week_start": current_date.isoformat(),
                "feedback_count": week_stats.count or 0,
                "average_rating": round(float(week_stats.avg_rating), 2) if week_stats.avg_rating else 0
            })
            
            current_date = week_end
        
        return {
            "daily_feedback": [
                {
                    "date": stat.date.isoformat(),
                    "count": stat.count,
                    "average_rating": round(float(stat.avg_rating), 2)
                }
                for stat in daily_feedback
            ],
            "weekly_trends": weekly_trends
        }
    
    def get_learning_context_for_analysis_type(self, analysis_type: str) -> Dict[str, Any]:
        """Get learning context for improving a specific analysis type"""
        
        # Get recent feedback for this analysis type
        recent_feedback = (
            self.db.query(Feedback)
            .filter(
                and_(
                    Feedback.analysis_type == analysis_type,
                    Feedback.created_at >= datetime.utcnow() - timedelta(days=30)
                )
            )
            .order_by(Feedback.created_at.desc())
            .all()
        )
        
        if not recent_feedback:
            return {"analysis_type": analysis_type, "feedback_available": False}
        
        # Calculate performance metrics
        ratings = [fb.rating for fb in recent_feedback if fb.rating]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # High-rated examples for positive patterns
        high_rated = [fb for fb in recent_feedback if fb.rating >= 4]
        low_rated = [fb for fb in recent_feedback if fb.rating <= 2]
        
        # Extract common themes from comments
        positive_feedback = [fb.comment for fb in high_rated if fb.comment]
        negative_feedback = [fb.comment for fb in low_rated if fb.comment]
        
        return {
            "analysis_type": analysis_type,
            "feedback_available": True,
            "performance_metrics": {
                "average_rating": round(avg_rating, 2),
                "total_feedback": len(recent_feedback),
                "high_rated_count": len(high_rated),
                "low_rated_count": len(low_rated)
            },
            "learning_signals": {
                "positive_patterns": self._extract_feedback_patterns(positive_feedback),
                "negative_patterns": self._extract_feedback_patterns(negative_feedback),
                "improvement_suggestions": self._generate_improvement_suggestions(
                    analysis_type, negative_feedback
                )
            }
        }
    
    def _extract_feedback_patterns(self, comments: List[str]) -> List[str]:
        """Extract common patterns from feedback comments"""
        if not comments:
            return []
        
        # Simple pattern extraction - in production, you might use NLP
        common_words = {}
        for comment in comments:
            words = comment.lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    common_words[word] = common_words.get(word, 0) + 1
        
        # Return most common meaningful words
        sorted_words = sorted(common_words.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:10] if count > 1]
    
    def _generate_improvement_suggestions(
        self, 
        analysis_type: str, 
        negative_feedback: List[str]
    ) -> List[str]:
        """Generate improvement suggestions based on negative feedback"""
        
        suggestions = []
        
        if not negative_feedback:
            return suggestions
        
        # Analyze common complaints
        all_feedback = " ".join(negative_feedback).lower()
        
        if "too general" in all_feedback or "not specific" in all_feedback:
            suggestions.append(f"Make {analysis_type} analysis more specific and detailed")
        
        if "wrong" in all_feedback or "incorrect" in all_feedback:
            suggestions.append(f"Improve accuracy of {analysis_type} assessments")
        
        if "missing" in all_feedback or "incomplete" in all_feedback:
            suggestions.append(f"Ensure {analysis_type} analysis covers all relevant aspects")
        
        if "confusing" in all_feedback or "unclear" in all_feedback:
            suggestions.append(f"Simplify language and structure for {analysis_type} reports")
        
        return suggestions
    
    async def apply_feedback_learning(
        self, 
        analysis_type: str
    ) -> Dict[str, Any]:
        """Apply feedback learning to improve future analysis"""
        
        learning_context = self.get_learning_context_for_analysis_type(analysis_type)
        
        if not learning_context.get("feedback_available"):
            return {"status": "no_feedback", "message": "No feedback available for learning"}
        
        # This is where you would integrate with the LLM service to update prompts
        # or fine-tune models based on feedback
        
        suggestions = learning_context.get("learning_signals", {}).get("improvement_suggestions", [])
        
        return {
            "status": "learning_applied",
            "analysis_type": analysis_type,
            "improvements_identified": len(suggestions),
            "suggestions": suggestions,
            "performance_metrics": learning_context["performance_metrics"]
        }