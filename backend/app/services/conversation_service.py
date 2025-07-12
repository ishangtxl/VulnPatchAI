"""
Conversation memory service for AI assistant persistence
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import uuid
import logging

from app.models.conversation import Conversation, Message, ConversationSummary, ConversationTemplate, UserPreference
from app.models.user import User

logger = logging.getLogger(__name__)


class ConversationService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_conversation(
        self, 
        user_id: int, 
        context_type: str = "general",
        context_metadata: Optional[Dict] = None,
        title: Optional[str] = None
    ) -> Conversation:
        """Create a new conversation"""
        conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        
        conversation = Conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            title=title,
            context_type=context_type,
            context_metadata=json.dumps(context_metadata) if context_metadata else None,
            is_active=True,
            message_count=0
        )
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        logger.info(f"Created conversation {conversation_id} for user {user_id}")
        return conversation
    
    async def get_conversation(
        self, 
        conversation_id: str, 
        user_id: int
    ) -> Optional[Conversation]:
        """Get a conversation by ID and user"""
        return (
            self.db.query(Conversation)
            .filter(
                and_(
                    Conversation.conversation_id == conversation_id,
                    Conversation.user_id == user_id
                )
            )
            .first()
        )
    
    async def add_message(
        self,
        conversation_id: str,
        user_id: int,
        role: str,
        content: str,
        token_count: Optional[int] = None,
        model_used: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
        context_data: Optional[Dict] = None,
        enhancement_data: Optional[Dict] = None
    ) -> Optional[Message]:
        """Add a message to a conversation"""
        # Get or create conversation
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            conversation = await self.create_conversation(
                user_id=user_id,
                context_type="general"
            )
            conversation.conversation_id = conversation_id
            self.db.commit()
        
        # Create message
        message = Message(
            conversation_id=conversation.id,
            role=role,
            content=content,
            token_count=token_count,
            model_used=model_used,
            processing_time_ms=processing_time_ms,
            context_data=json.dumps(context_data) if context_data else None,
            enhancement_data=json.dumps(enhancement_data) if enhancement_data else None
        )
        
        self.db.add(message)
        
        # Update conversation metadata
        conversation.message_count += 1
        conversation.last_activity_at = datetime.utcnow()
        conversation.updated_at = datetime.utcnow()
        
        # Auto-generate title after first user message if not set
        if not conversation.title and role == "user" and conversation.message_count == 1:
            conversation.title = await self._generate_conversation_title(content)
        
        self.db.commit()
        self.db.refresh(message)
        
        logger.info(f"Added {role} message to conversation {conversation_id}")
        return message
    
    async def get_conversation_messages(
        self,
        conversation_id: str,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """Get messages from a conversation"""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return []
        
        messages = (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        return messages
    
    async def get_user_conversations(
        self,
        user_id: int,
        limit: int = 20,
        include_inactive: bool = False
    ) -> List[Conversation]:
        """Get all conversations for a user"""
        query = self.db.query(Conversation).filter(Conversation.user_id == user_id)
        
        if not include_inactive:
            query = query.filter(Conversation.is_active == True)
        
        conversations = (
            query.order_by(desc(Conversation.last_activity_at))
            .limit(limit)
            .all()
        )
        
        return conversations
    
    async def update_conversation_title(
        self,
        conversation_id: str,
        user_id: int,
        title: str
    ) -> bool:
        """Update conversation title"""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False
        
        conversation.title = title
        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    async def archive_conversation(
        self,
        conversation_id: str,
        user_id: int
    ) -> bool:
        """Archive (deactivate) a conversation"""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False
        
        conversation.is_active = False
        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Archived conversation {conversation_id}")
        return True
    
    async def delete_conversation(
        self,
        conversation_id: str,
        user_id: int
    ) -> bool:
        """Delete a conversation and all its messages"""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False
        
        # Delete all messages first (cascade should handle this, but being explicit)
        self.db.query(Message).filter(Message.conversation_id == conversation.id).delete()
        
        # Delete conversation summary if exists
        self.db.query(ConversationSummary).filter(ConversationSummary.conversation_id == conversation.id).delete()
        
        # Delete conversation
        self.db.delete(conversation)
        self.db.commit()
        
        logger.info(f"Deleted conversation {conversation_id}")
        return True
    
    async def create_conversation_summary(
        self,
        conversation_id: str,
        user_id: int,
        summary: str,
        key_topics: List[str],
        user_preferences: Dict,
        context_insights: Dict
    ) -> Optional[ConversationSummary]:
        """Create or update conversation summary"""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return None
        
        # Check if summary already exists
        existing_summary = (
            self.db.query(ConversationSummary)
            .filter(ConversationSummary.conversation_id == conversation.id)
            .first()
        )
        
        if existing_summary:
            # Update existing summary
            existing_summary.summary = summary
            existing_summary.key_topics = json.dumps(key_topics)
            existing_summary.user_preferences = json.dumps(user_preferences)
            existing_summary.context_insights = json.dumps(context_insights)
            existing_summary.messages_summarized = conversation.message_count
            existing_summary.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(existing_summary)
            return existing_summary
        else:
            # Create new summary
            conversation_summary = ConversationSummary(
                conversation_id=conversation.id,
                summary=summary,
                key_topics=json.dumps(key_topics),
                user_preferences=json.dumps(user_preferences),
                context_insights=json.dumps(context_insights),
                messages_summarized=conversation.message_count
            )
            
            self.db.add(conversation_summary)
            self.db.commit()
            self.db.refresh(conversation_summary)
            
            logger.info(f"Created summary for conversation {conversation_id}")
            return conversation_summary
    
    async def get_conversation_summary(
        self,
        conversation_id: str,
        user_id: int
    ) -> Optional[ConversationSummary]:
        """Get conversation summary"""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return None
        
        return (
            self.db.query(ConversationSummary)
            .filter(ConversationSummary.conversation_id == conversation.id)
            .first()
        )
    
    async def get_user_preferences(self, user_id: int) -> Optional[UserPreference]:
        """Get user AI preferences"""
        return (
            self.db.query(UserPreference)
            .filter(UserPreference.user_id == user_id)
            .first()
        )
    
    async def update_user_preferences(
        self,
        user_id: int,
        preferences: Dict[str, Any]
    ) -> UserPreference:
        """Update user AI preferences"""
        existing_prefs = await self.get_user_preferences(user_id)
        
        if existing_prefs:
            # Update existing preferences
            for key, value in preferences.items():
                if hasattr(existing_prefs, key):
                    setattr(existing_prefs, key, value)
            
            existing_prefs.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing_prefs)
            return existing_prefs
        else:
            # Create new preferences
            user_prefs = UserPreference(
                user_id=user_id,
                **preferences
            )
            
            self.db.add(user_prefs)
            self.db.commit()
            self.db.refresh(user_prefs)
            
            logger.info(f"Created AI preferences for user {user_id}")
            return user_prefs
    
    async def get_conversation_context(
        self,
        conversation_id: str,
        user_id: int,
        message_limit: int = 10
    ) -> Dict[str, Any]:
        """Get conversation context for AI queries"""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return {}
        
        # Get recent messages
        recent_messages = await self.get_conversation_messages(
            conversation_id, user_id, limit=message_limit
        )
        
        # Get conversation summary if available
        summary = await self.get_conversation_summary(conversation_id, user_id)
        
        # Get user preferences
        user_prefs = await self.get_user_preferences(user_id)
        
        # Build context
        context = {
            "conversation_id": conversation_id,
            "conversation_type": conversation.context_type,
            "conversation_metadata": json.loads(conversation.context_metadata) if conversation.context_metadata else {},
            "message_count": conversation.message_count,
            "recent_messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat(),
                    "context_data": json.loads(msg.context_data) if msg.context_data else {}
                }
                for msg in recent_messages
            ]
        }
        
        if summary:
            context["summary"] = {
                "text": summary.summary,
                "key_topics": json.loads(summary.key_topics) if summary.key_topics else [],
                "insights": json.loads(summary.context_insights) if summary.context_insights else {}
            }
        
        if user_prefs:
            context["user_preferences"] = {
                "response_style": user_prefs.preferred_response_style,
                "analysis_depth": user_prefs.preferred_analysis_depth,
                "explanation_level": user_prefs.preferred_explanation_level,
                "proactive_suggestions": user_prefs.enable_proactive_suggestions,
                "personalization": user_prefs.enable_personalization
            }
        
        return context
    
    async def cleanup_old_conversations(self, days_old: int = 90) -> int:
        """Clean up old inactive conversations"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        old_conversations = (
            self.db.query(Conversation)
            .filter(
                and_(
                    Conversation.is_active == False,
                    Conversation.updated_at < cutoff_date
                )
            )
            .all()
        )
        
        deleted_count = 0
        for conversation in old_conversations:
            # Delete messages and summaries (cascade)
            self.db.delete(conversation)
            deleted_count += 1
        
        self.db.commit()
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old conversations")
        
        return deleted_count
    
    async def get_conversation_templates(
        self,
        context_type: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> List[ConversationTemplate]:
        """Get available conversation templates"""
        query = self.db.query(ConversationTemplate).filter(ConversationTemplate.is_active == True)
        
        if context_type:
            query = query.filter(ConversationTemplate.context_type == context_type)
        
        if user_id:
            # Include user's custom templates and global templates
            query = query.filter(
                (ConversationTemplate.created_by == user_id) |
                (ConversationTemplate.created_by.is_(None))
            )
        
        return query.order_by(desc(ConversationTemplate.usage_count)).all()
    
    async def _generate_conversation_title(self, first_message: str) -> str:
        """Generate a conversation title from the first message"""
        # Simple title generation - could be enhanced with AI
        words = first_message.split()[:6]
        title = " ".join(words)
        
        if len(first_message) > 50:
            title += "..."
        
        return title[:100]  # Limit title length
    
    async def update_message_feedback(
        self,
        message_id: int,
        user_id: int,
        rating: Optional[int] = None,
        was_helpful: Optional[bool] = None,
        correction: Optional[str] = None
    ) -> bool:
        """Update message feedback"""
        message = (
            self.db.query(Message)
            .join(Conversation)
            .filter(
                and_(
                    Message.id == message_id,
                    Conversation.user_id == user_id
                )
            )
            .first()
        )
        
        if not message:
            return False
        
        if rating is not None:
            message.user_rating = rating
        if was_helpful is not None:
            message.was_helpful = was_helpful
        if correction is not None:
            message.correction_provided = correction
        
        message.updated_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Updated feedback for message {message_id}")
        return True