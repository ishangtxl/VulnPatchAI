"""
API v1 router
"""
from fastapi import APIRouter
from .endpoints import auth, scans, vulnerabilities, reports, dashboard, ai, websocket, export, mfa, advanced_dashboard, theme, conversation, search, analytics, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(scans.router, prefix="/scan", tags=["scans"])
api_router.include_router(vulnerabilities.router, prefix="/vulnerabilities", tags=["vulnerabilities"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(mfa.router, prefix="/mfa", tags=["mfa"])
api_router.include_router(advanced_dashboard.router, prefix="/advanced-dashboard", tags=["advanced-dashboard"])
api_router.include_router(theme.router, prefix="/theme", tags=["theme"])
api_router.include_router(conversation.router, prefix="/conversation", tags=["conversation"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])