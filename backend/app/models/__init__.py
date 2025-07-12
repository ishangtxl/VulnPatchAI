"""
Database models for VulnPatch AI
"""
from .user import User
from .scan import Scan
from .vulnerability import Vulnerability
from .patch import Patch
from .report import Report
from .feedback import Feedback
from .audit_log import AuditLog
from .conversation import Conversation, Message, ConversationSummary, ConversationTemplate, UserPreference

__all__ = [
    "User",
    "Scan", 
    "Vulnerability",
    "Patch",
    "Report",
    "Feedback",
    "AuditLog",
    "Conversation",
    "Message",
    "ConversationSummary",
    "ConversationTemplate",
    "UserPreference"
]