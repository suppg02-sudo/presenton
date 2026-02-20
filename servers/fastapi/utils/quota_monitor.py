"""
OpenRouter quota monitor.
Tracks API usage, rate limits, and quota status.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class QuotaMonitor:
    """
    Monitors OpenRouter API quota and usage patterns.
    
    Tracks:
    - Requests per minute/hour
    - Rate limit headers
    - Error patterns
    - Model usage
    """
    
    def __init__(self):
        self.requests: list = []  # (timestamp, model, tokens_used)
        self.rate_limit_hits = 0
        self.errors = 0
        self.model_usage: Dict[str, int] = {}  # model -> count
        self.total_tokens_used = 0
        
    def record_request(
        self,
        model: str,
        tokens_used: int = 0,
    ) -> None:
        """Record an API request."""
        self.requests.append((datetime.utcnow(), model, tokens_used))
        self.model_usage[model] = self.model_usage.get(model, 0) + 1
        self.total_tokens_used += tokens_used
        
        # Keep only last hour of requests
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self.requests = [(t, m, tk) for t, m, tk in self.requests if t > cutoff]
    
    def record_rate_limit_hit(self) -> None:
        """Record a rate limit (HTTP 429) error."""
        self.rate_limit_hits += 1
        logger.warning(
            f"Rate limit hit #{self.rate_limit_hits}. "
            f"Recent request rate: {self.get_requests_per_minute():.1f} req/min"
        )
    
    def record_error(self) -> None:
        """Record an error."""
        self.errors += 1
    
    def get_requests_per_minute(self) -> float:
        """Get current requests per minute."""
        if not self.requests:
            return 0.0
        
        cutoff = datetime.utcnow() - timedelta(minutes=1)
        recent = [t for t, _, _ in self.requests if t > cutoff]
        return len(recent) / 1.0 if recent else 0.0
    
    def get_requests_per_hour(self) -> float:
        """Get requests per hour."""
        return len(self.requests)  # Already filtered to last hour
    
    def get_top_models(self, limit: int = 5) -> list:
        """Get top models by usage."""
        return sorted(
            self.model_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
    
    def get_quota_status(self) -> dict:
        """Get quota status and recommendations."""
        rpm = self.get_requests_per_minute()
        requests_per_hour = self.get_requests_per_hour()
        
        # Estimate quota (free tier typically ~60 RPM)
        estimated_limit = 60
        quota_percent = (rpm / estimated_limit) * 100 if rpm > 0 else 0
        
        status = {
            "requests_per_minute": rpm,
            "requests_per_hour": requests_per_hour,
            "estimated_quota_percent": quota_percent,
            "rate_limit_hits": self.rate_limit_hits,
            "errors": self.errors,
            "total_tokens_used": self.total_tokens_used,
            "top_models": self.get_top_models(5),
            "status": self._get_status_message(quota_percent),
        }
        
        return status
    
    def _get_status_message(self, quota_percent: float) -> str:
        """Get status message based on quota usage."""
        if quota_percent < 50:
            return "✅ HEALTHY - Low usage"
        elif quota_percent < 80:
            return "⚠️ WARNING - Approaching limit"
        elif quota_percent < 95:
            return "🔴 CRITICAL - Nearing quota"
        else:
            return "❌ OVERLOADED - Quota exceeded"
    
    def get_stats(self) -> dict:
        """Get comprehensive statistics."""
        return {
            "quota": self.get_quota_status(),
            "model_usage": dict(self.get_top_models(10)),
            "total_requests": len(self.requests),
            "rate_limit_hits": self.rate_limit_hits,
            "error_count": self.errors,
            "total_tokens": self.total_tokens_used,
        }
    
    def reset_hourly(self) -> None:
        """Reset hourly statistics (keep totals)."""
        self.requests = []


# Global quota monitor instance
_quota_monitor = QuotaMonitor()


def record_request(model: str, tokens_used: int = 0) -> None:
    """Record an API request."""
    _quota_monitor.record_request(model, tokens_used)


def record_rate_limit() -> None:
    """Record rate limit error."""
    _quota_monitor.record_rate_limit_hit()


def record_error() -> None:
    """Record an error."""
    _quota_monitor.record_error()


def get_quota_status() -> dict:
    """Get current quota status."""
    return _quota_monitor.get_quota_status()


def get_monitor_stats() -> dict:
    """Get monitor statistics."""
    return _quota_monitor.get_stats()
