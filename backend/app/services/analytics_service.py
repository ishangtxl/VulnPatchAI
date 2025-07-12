"""
Predictive analytics service for vulnerability trends and insights
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, case, extract
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import logging
from collections import defaultdict
import statistics

from app.models.scan import Scan
from app.models.vulnerability import Vulnerability
from app.models.user import User

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_vulnerability_trends(
        self,
        user_id: int,
        days: int = 90,
        granularity: str = "weekly"
    ) -> Dict[str, Any]:
        """Get vulnerability trends over time with predictive analytics"""
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get historical data
        historical_data = self._get_historical_vulnerability_data(user_id, start_date, end_date, granularity)
        
        # Calculate trends
        trends = self._calculate_trends(historical_data)
        
        # Generate predictions
        predictions = self._generate_vulnerability_predictions(historical_data, granularity)
        
        # Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(user_id, days)
        
        # Identify patterns
        patterns = self._identify_vulnerability_patterns(user_id, days)
        
        return {
            "time_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days,
                "granularity": granularity
            },
            "historical_data": historical_data,
            "trends": trends,
            "predictions": predictions,
            "risk_metrics": risk_metrics,
            "patterns": patterns,
            "insights": self._generate_insights(trends, predictions, patterns)
        }
    
    def get_service_vulnerability_analysis(
        self,
        user_id: int,
        days: int = 90
    ) -> Dict[str, Any]:
        """Analyze vulnerability patterns by service type"""
        
        # Get service vulnerability data
        service_data = self._get_service_vulnerability_data(user_id, days)
        
        # Calculate service risk scores
        service_risks = self._calculate_service_risk_scores(service_data)
        
        # Identify high-risk services
        high_risk_services = self._identify_high_risk_services(service_risks)
        
        # Generate service recommendations
        recommendations = self._generate_service_recommendations(service_risks, high_risk_services)
        
        return {
            "analysis_period_days": days,
            "service_data": service_data,
            "service_risk_scores": service_risks,
            "high_risk_services": high_risk_services,
            "recommendations": recommendations,
            "service_trends": self._calculate_service_trends(user_id, days)
        }
    
    def get_severity_trend_analysis(
        self,
        user_id: int,
        days: int = 90
    ) -> Dict[str, Any]:
        """Analyze trends in vulnerability severity distribution"""
        
        # Get severity data over time
        severity_timeline = self._get_severity_timeline(user_id, days)
        
        # Calculate severity trends
        severity_trends = self._calculate_severity_trends(severity_timeline)
        
        # Predict future severity distribution
        severity_predictions = self._predict_severity_distribution(severity_timeline)
        
        # Calculate severity risk indicators
        risk_indicators = self._calculate_severity_risk_indicators(severity_timeline)
        
        return {
            "analysis_period_days": days,
            "severity_timeline": severity_timeline,
            "severity_trends": severity_trends,
            "severity_predictions": severity_predictions,
            "risk_indicators": risk_indicators,
            "recommendations": self._generate_severity_recommendations(severity_trends, risk_indicators)
        }
    
    def get_predictive_alerts(
        self,
        user_id: int,
        threshold_days: int = 30
    ) -> List[Dict[str, Any]]:
        """Generate predictive alerts based on vulnerability trends"""
        
        alerts = []
        
        # Get recent trends
        trends = self.get_vulnerability_trends(user_id, days=threshold_days, granularity="daily")
        
        # Check for increasing vulnerability trends
        overall_trend = trends["trends"].get("overall_trend")
        if overall_trend and not trends["trends"].get("insufficient_data"):
            if overall_trend.get("direction") == "increasing":
                growth_rate = overall_trend.get("growth_rate", 0)
                if growth_rate > 0.2:  # 20% increase
                    alerts.append({
                        "type": "vulnerability_surge",
                        "severity": "high",
                        "title": "Vulnerability Surge Detected",
                        "description": f"Vulnerability count has increased by {growth_rate:.1%} in the last {threshold_days} days",
                        "recommendation": "Consider immediate security review and enhanced monitoring",
                        "confidence": self._calculate_confidence(trends["historical_data"]),
                        "projected_impact": "High"
                    })
        
        # Check for critical service risks
        service_analysis = self.get_service_vulnerability_analysis(user_id, threshold_days)
        for service in service_analysis["high_risk_services"]:
            if service["risk_score"] > 8.0:
                alerts.append({
                    "type": "high_risk_service",
                    "severity": "critical",
                    "title": f"High-Risk Service: {service['service_name']}",
                    "description": f"Service has risk score of {service['risk_score']:.1f}/10",
                    "recommendation": f"Immediate attention required for {service['service_name']} service",
                    "confidence": "high",
                    "projected_impact": "Critical"
                })
        
        # Check for unusual patterns
        patterns = trends["patterns"]
        if patterns and not patterns.get("insufficient_data") and patterns.get("anomalies_detected"):
            alerts.append({
                "type": "anomaly_detected",
                "severity": "medium",
                "title": "Unusual Vulnerability Pattern",
                "description": "Detected unusual patterns in vulnerability discovery",
                "recommendation": "Review recent scanning activities and environmental changes",
                "confidence": "medium",
                "projected_impact": "Medium"
            })
        
        return alerts
    
    def get_vulnerability_forecast(
        self,
        user_id: int,
        forecast_days: int = 30
    ) -> Dict[str, Any]:
        """Generate vulnerability forecast for future periods"""
        
        # Get historical data for better prediction
        historical_data = self._get_historical_vulnerability_data(
            user_id, 
            datetime.utcnow() - timedelta(days=90), 
            datetime.utcnow(), 
            "daily"
        )
        
        # Calculate forecast
        forecast = self._calculate_vulnerability_forecast(historical_data, forecast_days)
        
        # Calculate confidence intervals
        confidence_intervals = self._calculate_forecast_confidence(historical_data, forecast)
        
        # Generate scenarios
        scenarios = self._generate_forecast_scenarios(forecast, confidence_intervals)
        
        return {
            "forecast_period_days": forecast_days,
            "base_forecast": forecast,
            "confidence_intervals": confidence_intervals,
            "scenarios": scenarios,
            "methodology": {
                "model": "trend_analysis_with_seasonal_adjustment",
                "data_points": len(historical_data),
                "accuracy_estimate": self._estimate_forecast_accuracy(historical_data)
            }
        }
    
    def _get_historical_vulnerability_data(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        granularity: str
    ) -> List[Dict[str, Any]]:
        """Get historical vulnerability data with specified granularity"""
        
        # Determine the date grouping based on granularity
        if granularity == "daily":
            date_trunc = func.date_trunc('day', Scan.upload_time)
        elif granularity == "weekly":
            date_trunc = func.date_trunc('week', Scan.upload_time)
        else:  # monthly
            date_trunc = func.date_trunc('month', Scan.upload_time)
        
        # Get vulnerability counts by time period
        results = (
            self.db.query(
                date_trunc.label('period'),
                func.count(Vulnerability.id).label('total_vulnerabilities'),
                func.sum(case([(Vulnerability.severity == 'Critical', 1)], else_=0)).label('critical_count'),
                func.sum(case([(Vulnerability.severity == 'High', 1)], else_=0)).label('high_count'),
                func.sum(case([(Vulnerability.severity == 'Medium', 1)], else_=0)).label('medium_count'),
                func.sum(case([(Vulnerability.severity == 'Low', 1)], else_=0)).label('low_count'),
                func.count(func.distinct(Scan.id)).label('scan_count')
            )
            .join(Scan)
            .filter(
                and_(
                    Scan.user_id == user_id,
                    Scan.upload_time >= start_date,
                    Scan.upload_time <= end_date
                )
            )
            .group_by(date_trunc)
            .order_by(date_trunc)
            .all()
        )
        
        return [
            {
                "period": result.period.isoformat() if result.period else None,
                "total_vulnerabilities": int(result.total_vulnerabilities or 0),
                "critical_count": int(result.critical_count or 0),
                "high_count": int(result.high_count or 0),
                "medium_count": int(result.medium_count or 0),
                "low_count": int(result.low_count or 0),
                "scan_count": int(result.scan_count or 0),
                "risk_score": self._calculate_period_risk_score(result)
            }
            for result in results
        ]
    
    def _calculate_trends(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Calculate various trend metrics from historical data"""
        
        if len(historical_data) < 2:
            return {"insufficient_data": True}
        
        # Extract vulnerability counts
        vuln_counts = [d["total_vulnerabilities"] for d in historical_data]
        critical_counts = [d["critical_count"] for d in historical_data]
        scan_counts = [d["scan_count"] for d in historical_data]
        
        # Calculate overall trend
        overall_trend = self._calculate_linear_trend(vuln_counts)
        
        # Calculate critical vulnerability trend
        critical_trend = self._calculate_linear_trend(critical_counts)
        
        # Calculate scan frequency trend
        scan_trend = self._calculate_linear_trend(scan_counts)
        
        # Calculate volatility
        volatility = statistics.stdev(vuln_counts) if len(vuln_counts) > 1 else 0
        
        return {
            "overall_trend": overall_trend,
            "critical_trend": critical_trend,
            "scan_frequency_trend": scan_trend,
            "volatility": volatility,
            "data_quality": {
                "periods_analyzed": len(historical_data),
                "data_completeness": len([d for d in historical_data if d["scan_count"] > 0]) / len(historical_data)
            }
        }
    
    def _calculate_linear_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate linear trend for a series of values"""
        
        if len(values) < 2:
            return {"direction": "insufficient_data", "slope": 0, "growth_rate": 0}
        
        # Simple linear regression
        n = len(values)
        x = list(range(n))
        
        # Calculate slope
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Determine direction
        if slope > 0.1:
            direction = "increasing"
        elif slope < -0.1:
            direction = "decreasing"
        else:
            direction = "stable"
        
        # Calculate growth rate
        initial_value = values[0] if values[0] > 0 else 1
        final_value = values[-1]
        growth_rate = (final_value - initial_value) / initial_value
        
        return {
            "direction": direction,
            "slope": slope,
            "growth_rate": growth_rate,
            "r_squared": self._calculate_r_squared(x, values, slope, y_mean)
        }
    
    def _calculate_r_squared(self, x: List[float], y: List[float], slope: float, y_mean: float) -> float:
        """Calculate R-squared for trend analysis"""
        
        if len(x) < 2:
            return 0
        
        x_mean = sum(x) / len(x)
        
        # Calculate predicted values
        intercept = y_mean - slope * x_mean
        y_pred = [slope * xi + intercept for xi in x]
        
        # Calculate R-squared
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(len(y)))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(len(y)))
        
        return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    def _generate_vulnerability_predictions(
        self,
        historical_data: List[Dict],
        granularity: str
    ) -> Dict[str, Any]:
        """Generate predictions for future vulnerability counts"""
        
        if len(historical_data) < 3:
            return {"error": "Insufficient historical data for predictions"}
        
        # Extract data for prediction
        vuln_counts = [d["total_vulnerabilities"] for d in historical_data]
        
        # Simple trend-based prediction
        trend = self._calculate_linear_trend(vuln_counts)
        
        # Predict next few periods
        periods_to_predict = 4 if granularity == "weekly" else 7 if granularity == "daily" else 2
        
        last_value = vuln_counts[-1]
        predictions = []
        
        for i in range(1, periods_to_predict + 1):
            predicted_value = max(0, last_value + (trend["slope"] * i))
            predictions.append({
                "period": i,
                "predicted_vulnerabilities": round(predicted_value),
                "confidence": max(0.3, 0.9 - (i * 0.1))  # Decreasing confidence over time
            })
        
        return {
            "predictions": predictions,
            "trend_basis": trend,
            "model_type": "linear_trend",
            "confidence_notes": "Confidence decreases with prediction distance"
        }
    
    def _calculate_risk_metrics(self, user_id: int, days: int) -> Dict[str, Any]:
        """Calculate comprehensive risk metrics"""
        
        # Get current period data
        current_date = datetime.utcnow()
        period_start = current_date - timedelta(days=days)
        
        # Get vulnerability stats
        vuln_stats = (
            self.db.query(
                func.count(Vulnerability.id).label('total'),
                func.sum(case([(Vulnerability.severity == 'Critical', 1)], else_=0)).label('critical'),
                func.sum(case([(Vulnerability.severity == 'High', 1)], else_=0)).label('high'),
                func.avg(Vulnerability.cvss_score).label('avg_cvss')
            )
            .join(Scan)
            .filter(
                and_(
                    Scan.user_id == user_id,
                    Scan.upload_time >= period_start
                )
            )
            .first()
        )
        
        # Calculate risk score
        total_vulns = int(vuln_stats.total or 0)
        critical_vulns = int(vuln_stats.critical or 0)
        high_vulns = int(vuln_stats.high or 0)
        avg_cvss = float(vuln_stats.avg_cvss or 0)
        
        risk_score = min(10, (critical_vulns * 3 + high_vulns * 2 + total_vulns * 0.1))
        
        return {
            "total_vulnerabilities": total_vulns,
            "critical_vulnerabilities": critical_vulns,
            "high_vulnerabilities": high_vulns,
            "average_cvss_score": round(avg_cvss, 2),
            "overall_risk_score": round(risk_score, 2),
            "risk_level": self._categorize_risk_level(risk_score),
            "vulnerability_density": round(total_vulns / max(days, 1), 2),
            "critical_ratio": round(critical_vulns / max(total_vulns, 1), 3)
        }
    
    def _identify_vulnerability_patterns(self, user_id: int, days: int) -> Dict[str, Any]:
        """Identify patterns in vulnerability data"""
        
        # Get daily vulnerability data
        daily_data = self._get_historical_vulnerability_data(
            user_id,
            datetime.utcnow() - timedelta(days=days),
            datetime.utcnow(),
            "daily"
        )
        
        if len(daily_data) < 7:
            return {"insufficient_data": True}
        
        vuln_counts = [d["total_vulnerabilities"] for d in daily_data]
        
        # Identify patterns
        patterns = {
            "anomalies_detected": self._detect_anomalies(vuln_counts),
            "seasonal_patterns": self._detect_seasonal_patterns(daily_data),
            "peak_days": self._identify_peak_days(daily_data),
            "consistency_score": self._calculate_consistency_score(vuln_counts),
            "discovery_patterns": self._analyze_discovery_patterns(daily_data)
        }
        
        return patterns
    
    def _generate_insights(
        self,
        trends: Dict,
        predictions: Dict,
        patterns: Dict
    ) -> List[str]:
        """Generate actionable insights from analytics"""
        
        insights = []
        
        # Trend insights
        if trends.get("overall_trend", {}).get("direction") == "increasing":
            insights.append("Vulnerability discovery is trending upward - consider enhancing security measures")
        elif trends.get("overall_trend", {}).get("direction") == "decreasing":
            insights.append("Positive trend: vulnerability discovery is decreasing")
        
        # Critical vulnerability insights
        if trends.get("critical_trend", {}).get("direction") == "increasing":
            insights.append("Critical vulnerabilities are increasing - immediate attention required")
        
        # Pattern insights
        if patterns.get("anomalies_detected"):
            insights.append("Unusual vulnerability patterns detected - investigate recent changes")
        
        # Prediction insights
        if predictions.get("predictions"):
            next_period = predictions["predictions"][0]
            if next_period.get("predicted_vulnerabilities", 0) > 10:
                insights.append(f"Predicted {next_period['predicted_vulnerabilities']} vulnerabilities in next period")
        
        return insights[:5]  # Limit to top 5 insights
    
    def _get_service_vulnerability_data(self, user_id: int, days: int) -> Dict[str, Any]:
        """Get vulnerability data grouped by service"""
        
        period_start = datetime.utcnow() - timedelta(days=days)
        
        results = (
            self.db.query(
                Vulnerability.service_name,
                func.count(Vulnerability.id).label('vulnerability_count'),
                func.sum(case([(Vulnerability.severity == 'Critical', 1)], else_=0)).label('critical_count'),
                func.sum(case([(Vulnerability.severity == 'High', 1)], else_=0)).label('high_count'),
                func.avg(Vulnerability.cvss_score).label('avg_cvss')
            )
            .join(Scan)
            .filter(
                and_(
                    Scan.user_id == user_id,
                    Scan.upload_time >= period_start,
                    Vulnerability.service_name.isnot(None)
                )
            )
            .group_by(Vulnerability.service_name)
            .order_by(desc(func.count(Vulnerability.id)))
            .all()
        )
        
        return {
            service.service_name: {
                "vulnerability_count": int(service.vulnerability_count),
                "critical_count": int(service.critical_count or 0),
                "high_count": int(service.high_count or 0),
                "average_cvss": float(service.avg_cvss or 0)
            }
            for service in results
        }
    
    def _calculate_service_risk_scores(self, service_data: Dict) -> Dict[str, float]:
        """Calculate risk scores for each service"""
        
        risk_scores = {}
        
        for service_name, data in service_data.items():
            # Calculate risk score based on vulnerability counts and severity
            risk_score = (
                data["critical_count"] * 4 +
                data["high_count"] * 2 +
                data["vulnerability_count"] * 0.5 +
                data["average_cvss"]
            )
            
            risk_scores[service_name] = min(10.0, risk_score)
        
        return risk_scores
    
    def _identify_high_risk_services(self, service_risks: Dict[str, float]) -> List[Dict]:
        """Identify services with high risk scores"""
        
        threshold = 5.0  # Risk score threshold
        
        high_risk = [
            {
                "service_name": service,
                "risk_score": score
            }
            for service, score in service_risks.items()
            if score > threshold
        ]
        
        return sorted(high_risk, key=lambda x: x["risk_score"], reverse=True)
    
    def _calculate_period_risk_score(self, result) -> float:
        """Calculate risk score for a time period"""
        
        critical = int(result.critical_count or 0)
        high = int(result.high_count or 0)
        total = int(result.total_vulnerabilities or 0)
        
        return min(10.0, (critical * 3 + high * 2 + total * 0.1))
    
    def _categorize_risk_level(self, risk_score: float) -> str:
        """Categorize risk level based on score"""
        
        if risk_score >= 8:
            return "Critical"
        elif risk_score >= 6:
            return "High"
        elif risk_score >= 4:
            return "Medium"
        else:
            return "Low"
    
    def _detect_anomalies(self, values: List[float]) -> bool:
        """Simple anomaly detection using standard deviation"""
        
        if len(values) < 3:
            return False
        
        mean_val = statistics.mean(values)
        stdev_val = statistics.stdev(values) if len(values) > 1 else 0
        
        # Check if any value is more than 2 standard deviations from mean
        threshold = mean_val + (2 * stdev_val)
        
        return any(val > threshold for val in values[-3:])  # Check last 3 values
    
    def _detect_seasonal_patterns(self, daily_data: List[Dict]) -> Dict[str, Any]:
        """Detect seasonal patterns in vulnerability discovery"""
        
        # Group by day of week
        day_groups = defaultdict(list)
        
        for data in daily_data:
            if data["period"]:
                day_of_week = datetime.fromisoformat(data["period"].replace('Z', '+00:00')).weekday()
                day_groups[day_of_week].append(data["total_vulnerabilities"])
        
        # Calculate averages by day
        day_averages = {
            day: statistics.mean(vulns) if vulns else 0
            for day, vulns in day_groups.items()
        }
        
        return {
            "weekly_pattern_detected": len(day_averages) >= 5,
            "day_averages": day_averages,
            "peak_day": max(day_averages.items(), key=lambda x: x[1])[0] if day_averages else None
        }
    
    def _identify_peak_days(self, daily_data: List[Dict]) -> List[Dict]:
        """Identify days with unusually high vulnerability counts"""
        
        if len(daily_data) < 5:
            return []
        
        vuln_counts = [d["total_vulnerabilities"] for d in daily_data]
        mean_count = statistics.mean(vuln_counts)
        stdev_count = statistics.stdev(vuln_counts) if len(vuln_counts) > 1 else 0
        
        threshold = mean_count + stdev_count
        
        peaks = [
            {
                "date": data["period"],
                "vulnerability_count": data["total_vulnerabilities"],
                "deviation_from_mean": data["total_vulnerabilities"] - mean_count
            }
            for data in daily_data
            if data["total_vulnerabilities"] > threshold
        ]
        
        return sorted(peaks, key=lambda x: x["vulnerability_count"], reverse=True)[:5]
    
    def _calculate_consistency_score(self, values: List[float]) -> float:
        """Calculate consistency score (lower is more consistent)"""
        
        if len(values) < 2:
            return 1.0
        
        mean_val = statistics.mean(values)
        if mean_val == 0:
            return 1.0
        
        stdev_val = statistics.stdev(values)
        coefficient_of_variation = stdev_val / mean_val
        
        # Convert to 0-1 scale (0 = highly variable, 1 = very consistent)
        return max(0, 1 - coefficient_of_variation)
    
    def _analyze_discovery_patterns(self, daily_data: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in vulnerability discovery"""
        
        scan_counts = [d["scan_count"] for d in daily_data]
        vuln_counts = [d["total_vulnerabilities"] for d in daily_data]
        
        # Calculate discovery efficiency
        efficiency_scores = []
        for i in range(len(daily_data)):
            if scan_counts[i] > 0:
                efficiency = vuln_counts[i] / scan_counts[i]
                efficiency_scores.append(efficiency)
        
        return {
            "average_vulns_per_scan": statistics.mean(efficiency_scores) if efficiency_scores else 0,
            "discovery_efficiency_trend": self._calculate_linear_trend(efficiency_scores) if len(efficiency_scores) > 1 else {},
            "scanning_frequency": statistics.mean(scan_counts) if scan_counts else 0
        }
    
    def _calculate_confidence(self, historical_data: List[Dict]) -> str:
        """Calculate confidence level based on data quality"""
        
        data_points = len(historical_data)
        completeness = len([d for d in historical_data if d["scan_count"] > 0]) / max(data_points, 1)
        
        if data_points >= 20 and completeness >= 0.8:
            return "high"
        elif data_points >= 10 and completeness >= 0.6:
            return "medium"
        else:
            return "low"
    
    def _get_severity_timeline(self, user_id: int, days: int) -> List[Dict]:
        """Get severity distribution over time"""
        
        return self._get_historical_vulnerability_data(
            user_id,
            datetime.utcnow() - timedelta(days=days),
            datetime.utcnow(),
            "weekly"
        )
    
    def _calculate_severity_trends(self, severity_timeline: List[Dict]) -> Dict[str, Dict]:
        """Calculate trends for each severity level"""
        
        severities = ["critical_count", "high_count", "medium_count", "low_count"]
        trends = {}
        
        for severity in severities:
            values = [d[severity] for d in severity_timeline]
            trends[severity] = self._calculate_linear_trend(values)
        
        return trends
    
    def _predict_severity_distribution(self, severity_timeline: List[Dict]) -> Dict[str, float]:
        """Predict future severity distribution"""
        
        if not severity_timeline:
            return {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        latest = severity_timeline[-1]
        total = (latest["critical_count"] + latest["high_count"] + 
                latest["medium_count"] + latest["low_count"])
        
        if total == 0:
            return {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        return {
            "critical": latest["critical_count"] / total,
            "high": latest["high_count"] / total,
            "medium": latest["medium_count"] / total,
            "low": latest["low_count"] / total
        }
    
    def _calculate_severity_risk_indicators(self, severity_timeline: List[Dict]) -> Dict[str, Any]:
        """Calculate risk indicators based on severity trends"""
        
        if not severity_timeline:
            return {}
        
        critical_counts = [d["critical_count"] for d in severity_timeline]
        high_counts = [d["high_count"] for d in severity_timeline]
        
        return {
            "critical_trend_concerning": any(c > 0 for c in critical_counts[-3:]),
            "high_severity_increasing": len(high_counts) > 1 and high_counts[-1] > high_counts[-2],
            "severity_escalation_risk": self._calculate_escalation_risk(severity_timeline)
        }
    
    def _calculate_escalation_risk(self, timeline: List[Dict]) -> float:
        """Calculate risk of severity escalation"""
        
        if len(timeline) < 2:
            return 0.0
        
        recent = timeline[-1]
        previous = timeline[-2]
        
        recent_critical_ratio = recent["critical_count"] / max(recent["total_vulnerabilities"], 1)
        previous_critical_ratio = previous["critical_count"] / max(previous["total_vulnerabilities"], 1)
        
        escalation = recent_critical_ratio - previous_critical_ratio
        
        return max(0, min(1, escalation * 10))  # Scale to 0-1
    
    def _generate_service_recommendations(self, service_risks: Dict, high_risk_services: List[Dict]) -> List[str]:
        """Generate recommendations based on service analysis"""
        
        recommendations = []
        
        if high_risk_services:
            top_risk = high_risk_services[0]
            recommendations.append(f"Prioritize security review of {top_risk['service_name']} service")
        
        if len(high_risk_services) > 3:
            recommendations.append("Multiple high-risk services detected - consider comprehensive security audit")
        
        # Add generic recommendations
        recommendations.extend([
            "Implement automated vulnerability scanning for all services",
            "Establish service-specific security baselines",
            "Review and update service configurations regularly"
        ])
        
        return recommendations[:5]
    
    def _generate_severity_recommendations(self, trends: Dict, indicators: Dict) -> List[str]:
        """Generate recommendations based on severity analysis"""
        
        recommendations = []
        
        if indicators.get("critical_trend_concerning"):
            recommendations.append("Immediate action required - critical vulnerabilities detected")
        
        if indicators.get("high_severity_increasing"):
            recommendations.append("High-severity vulnerabilities increasing - enhance monitoring")
        
        if indicators.get("severity_escalation_risk", 0) > 0.5:
            recommendations.append("Risk of severity escalation - review security controls")
        
        return recommendations
    
    def _calculate_service_trends(self, user_id: int, days: int) -> Dict[str, Any]:
        """Calculate trends for service vulnerabilities"""
        
        # This is a simplified implementation
        service_data = self._get_service_vulnerability_data(user_id, days)
        
        return {
            "total_services_analyzed": len(service_data),
            "services_with_vulnerabilities": len([s for s in service_data.values() if s["vulnerability_count"] > 0]),
            "most_vulnerable_service": max(service_data.items(), key=lambda x: x[1]["vulnerability_count"])[0] if service_data else None
        }
    
    def _calculate_vulnerability_forecast(self, historical_data: List[Dict], forecast_days: int) -> List[Dict]:
        """Calculate vulnerability forecast"""
        
        if len(historical_data) < 3:
            return []
        
        vuln_counts = [d["total_vulnerabilities"] for d in historical_data]
        trend = self._calculate_linear_trend(vuln_counts)
        
        last_value = vuln_counts[-1]
        forecast = []
        
        for day in range(1, forecast_days + 1):
            predicted = max(0, last_value + (trend["slope"] * day))
            forecast.append({
                "day": day,
                "predicted_vulnerabilities": round(predicted),
                "trend_component": trend["slope"] * day
            })
        
        return forecast
    
    def _calculate_forecast_confidence(self, historical_data: List[Dict], forecast: List[Dict]) -> Dict[str, float]:
        """Calculate confidence intervals for forecast"""
        
        vuln_counts = [d["total_vulnerabilities"] for d in historical_data]
        volatility = statistics.stdev(vuln_counts) if len(vuln_counts) > 1 else 0
        
        return {
            "confidence_95_lower": max(0, -1.96 * volatility),
            "confidence_95_upper": 1.96 * volatility,
            "expected_variance": volatility ** 2
        }
    
    def _generate_forecast_scenarios(self, forecast: List[Dict], confidence: Dict) -> Dict[str, List[Dict]]:
        """Generate different forecast scenarios"""
        
        scenarios = {
            "optimistic": [],
            "pessimistic": [],
            "most_likely": forecast
        }
        
        for day_forecast in forecast:
            base_value = day_forecast["predicted_vulnerabilities"]
            
            scenarios["optimistic"].append({
                "day": day_forecast["day"],
                "predicted_vulnerabilities": max(0, round(base_value + confidence["confidence_95_lower"]))
            })
            
            scenarios["pessimistic"].append({
                "day": day_forecast["day"],
                "predicted_vulnerabilities": round(base_value + confidence["confidence_95_upper"])
            })
        
        return scenarios
    
    def _estimate_forecast_accuracy(self, historical_data: List[Dict]) -> float:
        """Estimate forecast accuracy based on historical performance"""
        
        if len(historical_data) < 5:
            return 0.5  # Low confidence with limited data
        
        # Calculate how well linear trend would have predicted recent data
        train_data = historical_data[:-2]
        test_data = historical_data[-2:]
        
        train_values = [d["total_vulnerabilities"] for d in train_data]
        test_values = [d["total_vulnerabilities"] for d in test_data]
        
        if not train_values or not test_values:
            return 0.5
        
        trend = self._calculate_linear_trend(train_values)
        predicted = train_values[-1] + trend["slope"]
        actual = test_values[0]
        
        # Calculate accuracy (0-1 scale)
        if actual == 0 and predicted == 0:
            return 1.0
        elif actual == 0:
            return 0.0
        
        error_rate = abs(predicted - actual) / actual
        accuracy = max(0, 1 - error_rate)
        
        return round(accuracy, 2)