"""
Dashboard endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardMetrics, TrendData
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard metrics"""
    dashboard_service = DashboardService(db)
    metrics = dashboard_service.get_user_metrics(current_user.id)
    return metrics


@router.get("/trends", response_model=TrendData)
async def get_trends(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trend data for charts"""
    dashboard_service = DashboardService(db)
    trends = dashboard_service.get_trends(current_user.id, days)
    return trends