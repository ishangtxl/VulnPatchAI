"""
Predictive analytics endpoints for vulnerability trends
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.services.analytics_service import AnalyticsService
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/vulnerability-trends")
async def get_vulnerability_trends(
    days: int = Query(default=90, ge=7, le=365, description="Number of days to analyze"),
    granularity: str = Query(default="weekly", regex="^(daily|weekly|monthly)$", description="Data granularity"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get vulnerability trends with predictive analytics"""
    analytics_service = AnalyticsService(db)
    
    try:
        trends = analytics_service.get_vulnerability_trends(
            user_id=current_user.id,
            days=days,
            granularity=granularity
        )
        
        return {
            "status": "success",
            "data": trends,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing vulnerability trends: {str(e)}"
        )


@router.get("/service-analysis")
async def get_service_vulnerability_analysis(
    days: int = Query(default=90, ge=7, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get service-based vulnerability analysis"""
    analytics_service = AnalyticsService(db)
    
    try:
        analysis = analytics_service.get_service_vulnerability_analysis(
            user_id=current_user.id,
            days=days
        )
        
        return {
            "status": "success",
            "data": analysis,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing service vulnerabilities: {str(e)}"
        )


@router.get("/severity-trends")
async def get_severity_trend_analysis(
    days: int = Query(default=90, ge=7, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get severity distribution trends and analysis"""
    analytics_service = AnalyticsService(db)
    
    try:
        analysis = analytics_service.get_severity_trend_analysis(
            user_id=current_user.id,
            days=days
        )
        
        return {
            "status": "success",
            "data": analysis,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing severity trends: {str(e)}"
        )


@router.get("/predictive-alerts")
async def get_predictive_alerts(
    threshold_days: int = Query(default=30, ge=7, le=90, description="Days to analyze for alerts"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get predictive alerts based on vulnerability trends"""
    analytics_service = AnalyticsService(db)
    
    try:
        alerts = analytics_service.get_predictive_alerts(
            user_id=current_user.id,
            threshold_days=threshold_days
        )
        
        return {
            "status": "success",
            "alerts": alerts,
            "alert_count": len(alerts),
            "analysis_period_days": threshold_days,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating predictive alerts: {str(e)}"
        )


@router.get("/forecast")
async def get_vulnerability_forecast(
    forecast_days: int = Query(default=30, ge=7, le=90, description="Number of days to forecast"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get vulnerability forecast for future periods"""
    analytics_service = AnalyticsService(db)
    
    try:
        forecast = analytics_service.get_vulnerability_forecast(
            user_id=current_user.id,
            forecast_days=forecast_days
        )
        
        return {
            "status": "success",
            "forecast": forecast,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating vulnerability forecast: {str(e)}"
        )


@router.get("/dashboard-summary")
async def get_analytics_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics summary for dashboard"""
    analytics_service = AnalyticsService(db)
    
    try:
        # Get key analytics data
        trends_30d = analytics_service.get_vulnerability_trends(
            user_id=current_user.id,
            days=30,
            granularity="daily"
        )
        
        service_analysis = analytics_service.get_service_vulnerability_analysis(
            user_id=current_user.id,
            days=30
        )
        
        alerts = analytics_service.get_predictive_alerts(
            user_id=current_user.id,
            threshold_days=30
        )
        
        forecast = analytics_service.get_vulnerability_forecast(
            user_id=current_user.id,
            forecast_days=14
        )
        
        # Create summary
        summary = {
            "trend_analysis": {
                "overall_trend": trends_30d.get("trends", {}).get("overall_trend", {}),
                "risk_level": trends_30d.get("risk_metrics", {}).get("risk_level", "Unknown"),
                "total_vulnerabilities": trends_30d.get("risk_metrics", {}).get("total_vulnerabilities", 0),
                "volatility": trends_30d.get("trends", {}).get("volatility", 0)
            },
            "service_insights": {
                "high_risk_services_count": len(service_analysis.get("high_risk_services", [])),
                "most_vulnerable_service": service_analysis.get("service_trends", {}).get("most_vulnerable_service"),
                "services_analyzed": service_analysis.get("service_trends", {}).get("total_services_analyzed", 0)
            },
            "alerts_summary": {
                "total_alerts": len(alerts),
                "critical_alerts": len([a for a in alerts if a.get("severity") == "critical"]),
                "high_alerts": len([a for a in alerts if a.get("severity") == "high"])
            },
            "forecast_summary": {
                "forecast_available": len(forecast.get("base_forecast", [])) > 0,
                "prediction_confidence": forecast.get("methodology", {}).get("accuracy_estimate", 0),
                "next_week_prediction": forecast.get("base_forecast", [{}])[6].get("predicted_vulnerabilities", 0) if len(forecast.get("base_forecast", [])) > 6 else 0
            },
            "key_insights": trends_30d.get("insights", [])
        }
        
        return {
            "status": "success",
            "summary": summary,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating analytics dashboard summary: {str(e)}"
        )


@router.get("/risk-assessment")
async def get_comprehensive_risk_assessment(
    days: int = Query(default=90, ge=30, le=365, description="Analysis period in days"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive risk assessment with analytics"""
    analytics_service = AnalyticsService(db)
    
    try:
        # Get all relevant analytics
        vulnerability_trends = analytics_service.get_vulnerability_trends(
            user_id=current_user.id,
            days=days,
            granularity="weekly"
        )
        
        service_analysis = analytics_service.get_service_vulnerability_analysis(
            user_id=current_user.id,
            days=days
        )
        
        severity_analysis = analytics_service.get_severity_trend_analysis(
            user_id=current_user.id,
            days=days
        )
        
        alerts = analytics_service.get_predictive_alerts(
            user_id=current_user.id,
            threshold_days=min(days, 60)
        )
        
        # Compile comprehensive assessment
        risk_assessment = {
            "overall_risk_score": vulnerability_trends.get("risk_metrics", {}).get("overall_risk_score", 0),
            "risk_level": vulnerability_trends.get("risk_metrics", {}).get("risk_level", "Unknown"),
            "analysis_period": {
                "days": days,
                "start_date": vulnerability_trends.get("time_period", {}).get("start_date"),
                "end_date": vulnerability_trends.get("time_period", {}).get("end_date")
            },
            "vulnerability_metrics": vulnerability_trends.get("risk_metrics", {}),
            "trend_indicators": {
                "overall_direction": vulnerability_trends.get("trends", {}).get("overall_trend", {}).get("direction"),
                "critical_trend": vulnerability_trends.get("trends", {}).get("critical_trend", {}).get("direction"),
                "volatility_level": "High" if vulnerability_trends.get("trends", {}).get("volatility", 0) > 5 else "Low"
            },
            "service_risk_factors": {
                "high_risk_services": service_analysis.get("high_risk_services", []),
                "service_count": len(service_analysis.get("service_data", {})),
                "concentration_risk": len(service_analysis.get("high_risk_services", [])) > 0
            },
            "severity_risk_factors": {
                "critical_trend_concerning": severity_analysis.get("risk_indicators", {}).get("critical_trend_concerning", False),
                "severity_escalation_risk": severity_analysis.get("risk_indicators", {}).get("severity_escalation_risk", 0),
                "high_severity_increasing": severity_analysis.get("risk_indicators", {}).get("high_severity_increasing", False)
            },
            "predictive_indicators": {
                "alerts_generated": len(alerts),
                "immediate_action_required": any(a.get("severity") == "critical" for a in alerts),
                "trend_deteriorating": vulnerability_trends.get("trends", {}).get("overall_trend", {}).get("direction") == "increasing"
            },
            "recommendations": self._generate_risk_recommendations(
                vulnerability_trends, service_analysis, severity_analysis, alerts
            ),
            "confidence_assessment": {
                "data_quality": vulnerability_trends.get("trends", {}).get("data_quality", {}),
                "analysis_confidence": self._assess_overall_confidence(vulnerability_trends, service_analysis)
            }
        }
        
        return {
            "status": "success",
            "risk_assessment": risk_assessment,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating risk assessment: {str(e)}"
        )


@router.get("/analytics-capabilities")
async def get_analytics_capabilities():
    """Get information about available analytics capabilities"""
    return {
        "capabilities": {
            "vulnerability_trends": {
                "description": "Historical vulnerability trend analysis with predictions",
                "granularity_options": ["daily", "weekly", "monthly"],
                "max_analysis_period_days": 365,
                "features": ["trend_detection", "growth_rate_analysis", "volatility_assessment"]
            },
            "service_analysis": {
                "description": "Service-based vulnerability risk analysis",
                "features": ["risk_scoring", "high_risk_identification", "service_trends"]
            },
            "severity_analysis": {
                "description": "Vulnerability severity distribution and trends",
                "features": ["severity_trends", "escalation_risk", "distribution_prediction"]
            },
            "predictive_alerts": {
                "description": "AI-generated alerts based on vulnerability patterns",
                "alert_types": ["vulnerability_surge", "high_risk_service", "anomaly_detected"],
                "confidence_levels": ["high", "medium", "low"]
            },
            "forecasting": {
                "description": "Vulnerability count predictions for future periods",
                "max_forecast_days": 90,
                "scenarios": ["optimistic", "most_likely", "pessimistic"],
                "features": ["confidence_intervals", "accuracy_estimates"]
            },
            "risk_assessment": {
                "description": "Comprehensive security risk evaluation",
                "components": ["vulnerability_metrics", "trend_indicators", "service_risks", "severity_risks"],
                "output": "overall_risk_score_and_recommendations"
            }
        },
        "data_requirements": {
            "minimum_scans": 3,
            "minimum_days": 7,
            "recommended_data_points": 20,
            "optimal_analysis_period": "90_days"
        },
        "accuracy_factors": [
            "Number of historical data points",
            "Consistency of scanning frequency", 
            "Variety of vulnerability types",
            "Recency of data"
        ],
        "limitations": [
            "Predictions based on historical patterns only",
            "External factors not considered in forecasting",
            "Accuracy decreases with longer prediction periods",
            "Limited effectiveness with sparse data"
        ]
    }


def _generate_risk_recommendations(
    vulnerability_trends: dict,
    service_analysis: dict,
    severity_analysis: dict,
    alerts: list
) -> List[str]:
    """Generate comprehensive risk recommendations"""
    
    recommendations = []
    
    # Critical alerts
    if any(a.get("severity") == "critical" for a in alerts):
        recommendations.append("CRITICAL: Immediate security review required based on predictive alerts")
    
    # Trend-based recommendations
    if vulnerability_trends.get("trends", {}).get("overall_trend", {}).get("direction") == "increasing":
        recommendations.append("Vulnerability discovery trending upward - enhance security monitoring")
    
    # Service-based recommendations
    high_risk_services = service_analysis.get("high_risk_services", [])
    if high_risk_services:
        top_service = high_risk_services[0]["service_name"]
        recommendations.append(f"Prioritize security hardening for {top_service} service")
    
    # Severity-based recommendations
    if severity_analysis.get("risk_indicators", {}).get("critical_trend_concerning"):
        recommendations.append("Critical vulnerability trend concerning - implement emergency response procedures")
    
    # General recommendations
    recommendations.extend([
        "Maintain regular vulnerability scanning schedule",
        "Implement automated security monitoring",
        "Review and update incident response procedures"
    ])
    
    return recommendations[:8]  # Limit to top 8


def _assess_overall_confidence(vulnerability_trends: dict, service_analysis: dict) -> str:
    """Assess overall confidence in the analysis"""
    
    data_quality = vulnerability_trends.get("trends", {}).get("data_quality", {})
    periods = data_quality.get("periods_analyzed", 0)
    completeness = data_quality.get("data_completeness", 0)
    
    if periods >= 20 and completeness >= 0.8:
        return "high"
    elif periods >= 10 and completeness >= 0.6:
        return "medium"
    else:
        return "low"