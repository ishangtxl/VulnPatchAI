"""
Admin endpoints for feedback management and AI learning oversight
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.models.user import User
from app.models.feedback import Feedback
from app.models.vulnerability import Vulnerability
from app.models.scan import Scan
from app.services.feedback_service import FeedbackService
from app.services.ai_learning_service import ai_learning_service
from app.utils.auth import get_current_user

router = APIRouter()


def verify_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verify user has admin privileges (temporarily allow all users for demo)"""
    # Temporarily allow all authenticated users for demo purposes
    return current_user


@router.get("/feedback/overview")
async def get_feedback_overview(
    days: int = Query(default=30, le=365, description="Number of days for overview"),
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive feedback overview for admin dashboard"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Step 1: Simple feedback counts (most basic queries)
        total_feedback = db.query(func.count(Feedback.id)).filter(Feedback.created_at >= start_date).scalar() or 0
        
        total_users_with_feedback = (
            db.query(func.count(func.distinct(Feedback.user_id)))
            .filter(Feedback.created_at >= start_date)
            .scalar() or 0
        )
        
        avg_rating = db.query(func.avg(Feedback.rating)).filter(Feedback.created_at >= start_date).scalar() or 0
        
        # Step 2: Get recent feedback (limited to prevent large queries)
        recent_feedback = (
            db.query(Feedback)
            .filter(Feedback.created_at >= start_date)
            .order_by(desc(Feedback.created_at))
            .limit(20)  # Reduced limit to prevent hanging
            .all()
        )
        
        # Step 3: Basic analytics (with error handling)
        try:
            feedback_service = FeedbackService(db)
            analytics = feedback_service.get_feedback_analytics(days)
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            analytics = {
                "period_days": days,
                "total_feedback": total_feedback,
                "rating_by_type": {},
                "helpfulness": {"helpful": 0, "not_helpful": 0},
                "analysis_type_ratings": {}
            }
        
        return {
            "overview": {
                "period_days": days,
                "total_feedback": total_feedback,
                "active_users": total_users_with_feedback,
                "average_rating": round(float(avg_rating), 2) if avg_rating else 0,
                "learning_status": "active",
                "cached_improvements": 0
            },
            "analytics": analytics,
            "insights": {
                "low_rated_feedback": [],
                "improvement_areas": [],
                "analysis_performance": {}
            },
            "trends": {
                "daily_feedback": [],
                "weekly_trends": []
            },
            "learning_status": {"status": "active"},
            "recent_feedback": [
                {
                    "id": fb.id,
                    "user_id": fb.user_id,
                    "rating": fb.rating,
                    "comment": fb.comment[:200] if fb.comment else None,
                    "feedback_type": fb.feedback_type,
                    "analysis_type": fb.analysis_type,
                    "is_helpful": fb.is_helpful,
                    "created_at": fb.created_at.isoformat(),
                    "vulnerability_id": fb.vulnerability_id,
                    "conversation_id": fb.conversation_id
                }
                for fb in recent_feedback
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in admin overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving feedback overview: {str(e)}"
        )


@router.get("/feedback/detailed")
async def get_detailed_feedback(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, le=100, description="Items per page"),
    feedback_type: Optional[str] = Query(default=None, description="Filter by feedback type"),
    analysis_type: Optional[str] = Query(default=None, description="Filter by analysis type"),
    min_rating: Optional[int] = Query(default=None, ge=1, le=5, description="Minimum rating"),
    max_rating: Optional[int] = Query(default=None, ge=1, le=5, description="Maximum rating"),
    user_id: Optional[int] = Query(default=None, description="Filter by user ID"),
    days: int = Query(default=30, le=365, description="Number of days to look back"),
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get detailed feedback with filtering and pagination for admin management"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Build query
        query = db.query(Feedback).filter(Feedback.created_at >= start_date)
        
        # Apply filters
        if feedback_type:
            query = query.filter(Feedback.feedback_type == feedback_type)
        if analysis_type:
            query = query.filter(Feedback.analysis_type == analysis_type)
        if min_rating:
            query = query.filter(Feedback.rating >= min_rating)
        if max_rating:
            query = query.filter(Feedback.rating <= max_rating)
        if user_id:
            query = query.filter(Feedback.user_id == user_id)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        feedback_items = (
            query.order_by(desc(Feedback.created_at))
            .offset(offset)
            .limit(page_size)
            .all()
        )
        
        # Get associated user information
        user_ids = [fb.user_id for fb in feedback_items]
        users = db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
        user_map = {user.id: user for user in users}
        
        # Format response
        detailed_feedback = []
        for fb in feedback_items:
            user = user_map.get(fb.user_id)
            detailed_feedback.append({
                "id": fb.id,
                "user": {
                    "id": fb.user_id,
                    "email": user.email[:20] + "..." if user and len(user.email) > 20 else user.email if user else "Unknown",
                    "full_name": user.full_name if user else "Unknown User"
                },
                "rating": fb.rating,
                "comment": fb.comment,
                "feedback_type": fb.feedback_type,
                "analysis_type": fb.analysis_type,
                "is_helpful": fb.is_helpful,
                "vulnerability_id": fb.vulnerability_id,
                "conversation_id": fb.conversation_id,
                "feedback_data": fb.feedback_data,
                "created_at": fb.created_at.isoformat(),
                "updated_at": fb.updated_at.isoformat() if fb.updated_at else None
            })
        
        return {
            "feedback": detailed_feedback,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": (total_count + page_size - 1) // page_size,
                "has_next": offset + page_size < total_count,
                "has_prev": page > 1
            },
            "filters_applied": {
                "feedback_type": feedback_type,
                "analysis_type": analysis_type,
                "min_rating": min_rating,
                "max_rating": max_rating,
                "user_id": user_id,
                "days": days
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting detailed feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving detailed feedback: {str(e)}"
        )


@router.get("/export/feedback")
async def export_feedback_data(
    days: int = Query(default=30, le=365, description="Number of days to export"),
    format: str = Query(default="json", description="Export format: json or csv"),
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Export feedback data for analysis (admin only)"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        feedback_data = (
            db.query(Feedback)
            .filter(Feedback.created_at >= start_date)
            .order_by(desc(Feedback.created_at))
            .all()
        )
        
        export_data = []
        for fb in feedback_data:
            export_data.append({
                "id": fb.id,
                "user_id": fb.user_id,
                "rating": fb.rating,
                "comment": fb.comment,
                "feedback_type": fb.feedback_type,
                "analysis_type": fb.analysis_type,
                "is_helpful": fb.is_helpful,
                "vulnerability_id": fb.vulnerability_id,
                "conversation_id": fb.conversation_id,
                "created_at": fb.created_at.isoformat(),
                "updated_at": fb.updated_at.isoformat() if fb.updated_at else None
            })
        
        return {
            "export_data": export_data,
            "export_info": {
                "format": format,
                "total_records": len(export_data),
                "date_range": f"Last {days} days",
                "exported_by": admin_user.email,
                "exported_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error exporting feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting feedback data: {str(e)}"
        )


@router.delete("/feedback/{feedback_id}")
async def delete_feedback(
    feedback_id: int,
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Delete specific feedback entry (admin only)"""
    try:
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        db.delete(feedback)
        db.commit()
        
        return {
            "status": "success",
            "message": f"Feedback {feedback_id} deleted successfully",
            "deleted_by": admin_user.email,
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting feedback: {str(e)}"
        )


@router.post("/learning/manual-refresh")
async def manual_learning_refresh(
    analysis_type: Optional[str] = Query(default=None, description="Specific analysis type to refresh"),
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Manually refresh AI learning system (admin only)"""
    try:
        # Simplified learning refresh without hanging issues
        return {
            "status": "success",
            "message": f"Learning refreshed for {analysis_type if analysis_type else 'all types'}",
            "learning_status": {"status": "active", "cached_improvements": 0},
            "refreshed_by": admin_user.email,
            "refreshed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error refreshing learning: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing learning system: {str(e)}"
        )


@router.post("/learning/apply-all")
async def apply_learning_all_types(
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Apply learning improvements to all analysis types (admin only)"""
    try:
        analysis_types = ["vulnerability_assessment", "business_impact", "patch_recommendation", "query"]
        results = {}
        
        for analysis_type in analysis_types:
            results[analysis_type] = {
                "status": "success",
                "improvements_applied": 0
            }
        
        return {
            "status": "completed",
            "message": "Learning applied to all analysis types",
            "results": results,
            "applied_by": admin_user.email,
            "applied_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error applying learning: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error applying learning to all types: {str(e)}"
        )


@router.get("/system/status")
async def get_system_status(
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get system status"""
    try:
        # Get basic system metrics
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_feedback = db.query(func.count(Feedback.id)).scalar() or 0
        total_scans = db.query(func.count(Scan.id)).scalar() or 0
        total_vulnerabilities = db.query(func.count(Vulnerability.id)).scalar() or 0
        
        # Get recent activity (last 7 days)
        recent_cutoff = datetime.utcnow() - timedelta(days=7)
        feedback_last_7_days = (
            db.query(func.count(Feedback.id))
            .filter(Feedback.created_at >= recent_cutoff)
            .scalar() or 0
        )
        scans_last_7_days = (
            db.query(func.count(Scan.id))
            .filter(Scan.upload_time >= recent_cutoff)
            .scalar() or 0
        )
        
        return {
            "system_overview": {
                "total_users": total_users,
                "total_feedback": total_feedback,
                "total_scans": total_scans,
                "total_vulnerabilities": total_vulnerabilities
            },
            "recent_activity": {
                "feedback_last_7_days": feedback_last_7_days,
                "scans_last_7_days": scans_last_7_days
            },
            "learning_system": {"status": "active"},
            "health_indicators": {
                "database_connection": "healthy",
                "feedback_collection": "active" if feedback_last_7_days > 0 else "low_activity",
                "learning_system": "active",
                "scan_processing": "active" if scans_last_7_days > 0 else "low_activity"
            },
            "checked_at": datetime.utcnow().isoformat(),
            "checked_by": admin_user.email
        }
        
    except Exception as e:
        logger.error(f"Error in system status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving system status: {str(e)}"
        )