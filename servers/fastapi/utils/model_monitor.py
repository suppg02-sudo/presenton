"""
Model monitor and rotation for OpenRouter free tier models.
Tracks model performance and automatically rotates on failures.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ModelMonitor:
    """
    Monitors model performance and health.
    
    Tracks:
    - Success/failure rates per model
    - Response times per model
    - Availability status
    - Automatic fallback to working models
    """
    
    def __init__(self):
        self.model_stats: Dict[str, Dict] = {}  # model -> stats
        self.model_status: Dict[str, str] = {}  # model -> status (healthy/degraded/unavailable)
        self.last_updated = datetime.utcnow()
        
    def record_success(
        self,
        model: str,
        response_time_ms: float,
        tokens_used: int = 0,
    ) -> None:
        """Record successful model usage."""
        if model not in self.model_stats:
            self.model_stats[model] = {
                "success_count": 0,
                "failure_count": 0,
                "avg_response_time_ms": 0,
                "total_tokens": 0,
                "last_used": None,
                "consecutive_failures": 0,
            }
        
        stats = self.model_stats[model]
        stats["success_count"] += 1
        stats["consecutive_failures"] = 0
        stats["last_used"] = datetime.utcnow().isoformat()
        stats["total_tokens"] += tokens_used
        
        # Update average response time
        total_requests = stats["success_count"] + stats["failure_count"]
        old_avg = stats["avg_response_time_ms"]
        stats["avg_response_time_ms"] = (
            (old_avg * (total_requests - 1) + response_time_ms) / total_requests
        )
        
        # Update status
        success_rate = stats["success_count"] / max(total_requests, 1) * 100
        if success_rate >= 95:
            self.model_status[model] = "✅ healthy"
        elif success_rate >= 80:
            self.model_status[model] = "⚠️ degraded"
        else:
            self.model_status[model] = "🔴 unavailable"
        
        logger.debug(
            f"Model {model} success. "
            f"Success rate: {success_rate:.1f}%, Avg response: {stats['avg_response_time_ms']:.1f}ms"
        )
    
    def record_failure(self, model: str) -> None:
        """Record failed model usage."""
        if model not in self.model_stats:
            self.model_stats[model] = {
                "success_count": 0,
                "failure_count": 0,
                "avg_response_time_ms": 0,
                "total_tokens": 0,
                "last_used": None,
                "consecutive_failures": 0,
            }
        
        stats = self.model_stats[model]
        stats["failure_count"] += 1
        stats["consecutive_failures"] += 1
        stats["last_used"] = datetime.utcnow().isoformat()
        
        # Update status
        total_requests = stats["success_count"] + stats["failure_count"]
        success_rate = stats["success_count"] / max(total_requests, 1) * 100
        
        if success_rate >= 95:
            status = "✅ healthy"
        elif success_rate >= 80:
            status = "⚠️ degraded"
        else:
            status = "🔴 unavailable"
        
        self.model_status[model] = status
        
        logger.warning(
            f"Model {model} failure (#{stats['consecutive_failures']}). "
            f"Success rate: {success_rate:.1f}%. Status: {status}"
        )
        
        # Mark as unavailable after 3 consecutive failures
        if stats["consecutive_failures"] >= 3:
            logger.error(f"Model {model} marked UNAVAILABLE after 3 failures")
            self.model_status[model] = "🔴 unavailable"
    
    def get_healthy_models(self) -> List[str]:
        """Get list of healthy models."""
        return [
            model for model, status in self.model_status.items()
            if "healthy" in status or "degraded" in status
        ]
    
    def get_model_performance(self, model: str) -> Optional[Dict]:
        """Get performance stats for a model."""
        if model not in self.model_stats:
            return None
        
        stats = self.model_stats[model]
        total = stats["success_count"] + stats["failure_count"]
        success_rate = (stats["success_count"] / max(total, 1)) * 100 if total > 0 else 0
        
        return {
            "model": model,
            "status": self.model_status.get(model, "unknown"),
            "success_rate_percent": success_rate,
            "success_count": stats["success_count"],
            "failure_count": stats["failure_count"],
            "avg_response_time_ms": stats["avg_response_time_ms"],
            "total_tokens": stats["total_tokens"],
            "consecutive_failures": stats["consecutive_failures"],
            "last_used": stats["last_used"],
        }
    
    def get_all_models_status(self) -> Dict[str, Dict]:
        """Get status of all monitored models."""
        result = {}
        for model in self.model_stats.keys():
            perf = self.get_model_performance(model)
            if perf:
                result[model] = perf
        return result
    
    def should_rotate_model(self, current_model: str) -> bool:
        """Check if should rotate away from current model."""
        if current_model not in self.model_stats:
            return False
        
        stats = self.model_stats[current_model]
        
        # Rotate if:
        # - 3+ consecutive failures
        # - Success rate < 70%
        if stats["consecutive_failures"] >= 3:
            return True
        
        total = stats["success_count"] + stats["failure_count"]
        if total > 0:
            success_rate = (stats["success_count"] / total) * 100
            if success_rate < 70:
                return True
        
        return False
    
    def recommend_model(self) -> Optional[str]:
        """Recommend the best available model."""
        # Find model with highest success rate
        best_model = None
        best_rate = -1
        
        for model, stats in self.model_stats.items():
            total = stats["success_count"] + stats["failure_count"]
            if total == 0:
                continue
            
            success_rate = stats["success_count"] / total
            if success_rate > best_rate:
                best_rate = success_rate
                best_model = model
        
        if best_model and best_rate > 0.7:
            return best_model
        
        return None
    
    def get_summary(self) -> dict:
        """Get summary of model monitoring."""
        all_stats = self.get_all_models_status()
        healthy = [m for m, s in all_stats.items() if "healthy" in s.get("status", "")]
        degraded = [m for m, s in all_stats.items() if "degraded" in s.get("status", "")]
        unavailable = [m for m, s in all_stats.items() if "unavailable" in s.get("status", "")]
        
        return {
            "total_models_monitored": len(all_stats),
            "healthy_models": len(healthy),
            "degraded_models": len(degraded),
            "unavailable_models": len(unavailable),
            "healthy_list": healthy,
            "degraded_list": degraded,
            "unavailable_list": unavailable,
            "recommended_model": self.recommend_model(),
        }


# Global model monitor instance
_model_monitor = ModelMonitor()


def record_model_success(model: str, response_time_ms: float, tokens: int = 0) -> None:
    """Record successful model usage."""
    _model_monitor.record_success(model, response_time_ms, tokens)


def record_model_failure(model: str) -> None:
    """Record failed model usage."""
    _model_monitor.record_failure(model)


def should_rotate_model(model: str) -> bool:
    """Check if should rotate away from model."""
    return _model_monitor.should_rotate_model(model)


def get_recommended_model() -> Optional[str]:
    """Get recommended model."""
    return _model_monitor.recommend_model()


def get_model_summary() -> dict:
    """Get model monitoring summary."""
    return _model_monitor.get_summary()


def get_all_models_status() -> Dict[str, Dict]:
    """Get all models status."""
    return _model_monitor.get_all_models_status()
