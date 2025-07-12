"""
Conversation memory endpoints for AI assistant
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.services.conversation_service import ConversationService
from app.utils.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()


class ConversationResponse(BaseModel):
    conversation_id: str
    title: Optional[str]
    context_type: str
    message_count: int
    is_active: bool
    created_at: datetime
    last_activity_at: datetime


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    token_count: Optional[int]
    model_used: Optional[str]
    processing_time_ms: Optional[int]
    user_rating: Optional[int]
    was_helpful: Optional[bool]
    created_at: datetime


class ConversationCreateRequest(BaseModel):
    title: Optional[str] = None
    context_type: str = "general"
    context_metadata: Optional[dict] = None


class MessageFeedbackRequest(BaseModel):
    rating: Optional[int] = None
    was_helpful: Optional[bool] = None
    correction: Optional[str] = None


class UserPreferencesRequest(BaseModel):
    preferred_response_style: Optional[str] = None
    preferred_analysis_depth: Optional[str] = None
    preferred_explanation_level: Optional[str] = None
    enable_proactive_suggestions: Optional[bool] = None
    remember_context_across_sessions: Optional[bool] = None
    auto_generate_summaries: Optional[bool] = None
    enable_personalization: Optional[bool] = None


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation"""
    conversation_service = ConversationService(db)
    
    try:
        conversation = await conversation_service.create_conversation(
            user_id=current_user.id,
            context_type=request.context_type,
            context_metadata=request.context_metadata,
            title=request.title
        )
        
        return ConversationResponse(
            conversation_id=conversation.conversation_id,
            title=conversation.title,
            context_type=conversation.context_type,
            message_count=conversation.message_count,
            is_active=conversation.is_active,
            created_at=conversation.created_at,
            last_activity_at=conversation.last_activity_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating conversation: {str(e)}"
        )


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_user_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, le=50),
    include_inactive: bool = Query(default=False)
):
    """Get all conversations for the current user"""
    conversation_service = ConversationService(db)
    
    try:
        conversations = await conversation_service.get_user_conversations(
            user_id=current_user.id,
            limit=limit,
            include_inactive=include_inactive
        )
        
        return [
            ConversationResponse(
                conversation_id=conv.conversation_id,
                title=conv.title,
                context_type=conv.context_type,
                message_count=conv.message_count,
                is_active=conv.is_active,
                created_at=conv.created_at,
                last_activity_at=conv.last_activity_at
            )
            for conv in conversations
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversations: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0)
):
    """Get messages from a specific conversation"""
    conversation_service = ConversationService(db)
    
    try:
        messages = await conversation_service.get_conversation_messages(
            conversation_id=conversation_id,
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        
        return [
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                token_count=msg.token_count,
                model_used=msg.model_used,
                processing_time_ms=msg.processing_time_ms,
                user_rating=msg.user_rating,
                was_helpful=msg.was_helpful,
                created_at=msg.created_at
            )
            for msg in messages
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving messages: {str(e)}"
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation"""
    conversation_service = ConversationService(db)
    
    try:
        conversation = await conversation_service.get_conversation(
            conversation_id=conversation_id,
            user_id=current_user.id
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return ConversationResponse(
            conversation_id=conversation.conversation_id,
            title=conversation.title,
            context_type=conversation.context_type,
            message_count=conversation.message_count,
            is_active=conversation.is_active,
            created_at=conversation.created_at,
            last_activity_at=conversation.last_activity_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation: {str(e)}"
        )


@router.patch("/conversations/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: str,
    title: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update conversation title"""
    conversation_service = ConversationService(db)
    
    try:
        success = await conversation_service.update_conversation_title(
            conversation_id=conversation_id,
            user_id=current_user.id,
            title=title
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return {"message": "Conversation title updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating conversation title: {str(e)}"
        )


@router.patch("/conversations/{conversation_id}/archive")
async def archive_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Archive a conversation"""
    conversation_service = ConversationService(db)
    
    try:
        success = await conversation_service.archive_conversation(
            conversation_id=conversation_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return {"message": "Conversation archived successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error archiving conversation: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation and all its messages"""
    conversation_service = ConversationService(db)
    
    try:
        success = await conversation_service.delete_conversation(
            conversation_id=conversation_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/summary")
async def get_conversation_summary(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation summary"""
    conversation_service = ConversationService(db)
    
    try:
        summary = await conversation_service.get_conversation_summary(
            conversation_id=conversation_id,
            user_id=current_user.id
        )
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation summary not found"
            )
        
        return {
            "summary": summary.summary,
            "key_topics": summary.key_topics,
            "user_preferences": summary.user_preferences,
            "context_insights": summary.context_insights,
            "messages_summarized": summary.messages_summarized,
            "created_at": summary.created_at,
            "updated_at": summary.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation summary: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/context")
async def get_conversation_context(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    message_limit: int = Query(default=10, le=50)
):
    """Get conversation context for AI queries"""
    conversation_service = ConversationService(db)
    
    try:
        context = await conversation_service.get_conversation_context(
            conversation_id=conversation_id,
            user_id=current_user.id,
            message_limit=message_limit
        )
        
        return context
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation context: {str(e)}"
        )


@router.post("/messages/{message_id}/feedback")
async def update_message_feedback(
    message_id: int,
    feedback: MessageFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update feedback for a specific message"""
    conversation_service = ConversationService(db)
    
    try:
        success = await conversation_service.update_message_feedback(
            message_id=message_id,
            user_id=current_user.id,
            rating=feedback.rating,
            was_helpful=feedback.was_helpful,
            correction=feedback.correction
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        return {"message": "Message feedback updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating message feedback: {str(e)}"
        )


@router.get("/preferences")
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user AI preferences"""
    conversation_service = ConversationService(db)
    
    try:
        preferences = await conversation_service.get_user_preferences(current_user.id)
        
        if not preferences:
            # Return default preferences
            return {
                "preferred_response_style": "balanced",
                "preferred_analysis_depth": "comprehensive",
                "preferred_explanation_level": "technical",
                "enable_proactive_suggestions": True,
                "remember_context_across_sessions": True,
                "auto_generate_summaries": True,
                "enable_personalization": True,
                "notify_on_new_features": True,
                "notify_on_security_insights": True
            }
        
        return {
            "preferred_response_style": preferences.preferred_response_style,
            "preferred_analysis_depth": preferences.preferred_analysis_depth,
            "preferred_explanation_level": preferences.preferred_explanation_level,
            "enable_proactive_suggestions": preferences.enable_proactive_suggestions,
            "remember_context_across_sessions": preferences.remember_context_across_sessions,
            "auto_generate_summaries": preferences.auto_generate_summaries,
            "enable_personalization": preferences.enable_personalization,
            "notify_on_new_features": preferences.notify_on_new_features,
            "notify_on_security_insights": preferences.notify_on_security_insights,
            "created_at": preferences.created_at,
            "updated_at": preferences.updated_at
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user preferences: {str(e)}"
        )


@router.patch("/preferences")
async def update_user_preferences(
    preferences: UserPreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user AI preferences"""
    conversation_service = ConversationService(db)
    
    try:
        # Convert request to dict, excluding None values
        prefs_dict = {k: v for k, v in preferences.dict().items() if v is not None}
        
        updated_prefs = await conversation_service.update_user_preferences(
            user_id=current_user.id,
            preferences=prefs_dict
        )
        
        return {
            "message": "User preferences updated successfully",
            "preferences": {
                "preferred_response_style": updated_prefs.preferred_response_style,
                "preferred_analysis_depth": updated_prefs.preferred_analysis_depth,
                "preferred_explanation_level": updated_prefs.preferred_explanation_level,
                "enable_proactive_suggestions": updated_prefs.enable_proactive_suggestions,
                "remember_context_across_sessions": updated_prefs.remember_context_across_sessions,
                "auto_generate_summaries": updated_prefs.auto_generate_summaries,
                "enable_personalization": updated_prefs.enable_personalization
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user preferences: {str(e)}"
        )


@router.get("/templates")
async def get_conversation_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    context_type: Optional[str] = Query(default=None)
):
    """Get available conversation templates"""
    conversation_service = ConversationService(db)
    
    try:
        templates = await conversation_service.get_conversation_templates(
            context_type=context_type,
            user_id=current_user.id
        )
        
        return [
            {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "context_type": template.context_type,
                "initial_prompt": template.initial_prompt,
                "system_instructions": template.system_instructions,
                "suggested_questions": template.suggested_questions,
                "usage_count": template.usage_count,
                "is_custom": template.created_by == current_user.id
            }
            for template in templates
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation templates: {str(e)}"
        )


@router.post("/cleanup")
async def cleanup_old_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days_old: int = Query(default=90, ge=30, le=365)
):
    """Clean up old inactive conversations (admin only)"""
    if not current_user.email.endswith("@admin.com"):  # Simple admin check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    conversation_service = ConversationService(db)
    
    try:
        deleted_count = await conversation_service.cleanup_old_conversations(days_old)
        
        return {
            "message": f"Cleaned up {deleted_count} old conversations",
            "deleted_count": deleted_count,
            "cutoff_days": days_old
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cleaning up conversations: {str(e)}"
        )