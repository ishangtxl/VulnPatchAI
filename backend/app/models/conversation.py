"""
Conversation and message models for AI assistant memory persistence
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)  # Auto-generated or user-set title
    context_type = Column(String, default="general")  # general, scan_analysis, vulnerability_query, etc.
    context_metadata = Column(Text, nullable=True)  # JSON metadata about the conversation context
    
    # Conversation state
    is_active = Column(Boolean, default=True)
    message_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_conversations_user_activity', 'user_id', 'last_activity_at'),
        Index('idx_conversations_context', 'context_type', 'is_active'),
    )


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    
    # Message content
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    
    # Message metadata
    token_count = Column(Integer, nullable=True)  # For cost tracking
    model_used = Column(String, nullable=True)  # Which AI model was used
    processing_time_ms = Column(Integer, nullable=True)  # Response time tracking
    
    # Context and enhancement data
    context_data = Column(Text, nullable=True)  # JSON context used for this message
    enhancement_data = Column(Text, nullable=True)  # JSON data about AI enhancements used
    
    # Quality and feedback
    user_rating = Column(Integer, nullable=True)  # 1-5 rating from user
    was_helpful = Column(Boolean, nullable=True)  # User feedback
    correction_provided = Column(Text, nullable=True)  # User corrections to AI response
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_messages_conversation_created', 'conversation_id', 'created_at'),
        Index('idx_messages_role_rating', 'role', 'user_rating'),
    )


class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), unique=True, nullable=False)
    
    # Summary content
    summary = Column(Text, nullable=False)  # AI-generated summary
    key_topics = Column(Text, nullable=True)  # JSON array of key topics discussed
    user_preferences = Column(Text, nullable=True)  # JSON of learned user preferences
    context_insights = Column(Text, nullable=True)  # JSON of contextual insights
    
    # Summary metadata
    messages_summarized = Column(Integer, nullable=False)  # Number of messages in summary
    summary_quality_score = Column(Integer, nullable=True)  # AI-assessed quality score
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conversation = relationship("Conversation", backref="summary")


class ConversationTemplate(Base):
    __tablename__ = "conversation_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    context_type = Column(String, nullable=False)
    
    # Template configuration
    initial_prompt = Column(Text, nullable=False)  # Starting prompt for this template
    system_instructions = Column(Text, nullable=True)  # System instructions for AI
    suggested_questions = Column(Text, nullable=True)  # JSON array of suggested questions
    
    # Template metadata
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", backref="conversation_templates")


class UserPreference(Base):
    __tablename__ = "user_preferences_ai"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # AI interaction preferences
    preferred_response_style = Column(String, default="balanced")  # concise, detailed, balanced
    preferred_analysis_depth = Column(String, default="comprehensive")  # basic, comprehensive, expert
    preferred_explanation_level = Column(String, default="technical")  # basic, technical, expert
    
    # Conversation preferences
    enable_proactive_suggestions = Column(Boolean, default=True)
    remember_context_across_sessions = Column(Boolean, default=True)
    auto_generate_summaries = Column(Boolean, default=True)
    
    # Learning preferences
    enable_personalization = Column(Boolean, default=True)
    share_anonymous_usage = Column(Boolean, default=False)
    
    # Notification preferences
    notify_on_new_features = Column(Boolean, default=True)
    notify_on_security_insights = Column(Boolean, default=True)
    
    # Metadata
    preferences_version = Column(String, default="1.0")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="ai_preferences")
    
    # Unique constraint
    __table_args__ = (
        Index('idx_user_preferences_user', 'user_id'),
    )