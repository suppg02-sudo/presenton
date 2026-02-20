"""
Monitoring API endpoints for quota, rate limiting, and model health.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from utils.rate_limiter import get_rate_limiter_status
from utils.request_queue import get_queue_stats
from utils.quota_monitor import get_quota_status, get_monitor_stats
from utils.model_monitor import get_model_summary, get_all_models_status

MONITORING_ROUTER = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])


@MONITORING_ROUTER.get("/rate-limiter")
async def get_rate_limiter():
    """Get rate limiter status and exponential backoff information."""
    return JSONResponse({"status": "rate_limiter", "data": get_rate_limiter_status()})


@MONITORING_ROUTER.get("/queue")
async def get_queue():
    """Get request queue status and statistics."""
    return JSONResponse({"status": "queue", "data": get_queue_stats()})


@MONITORING_ROUTER.get("/quota")
async def get_quota():
    """Get OpenRouter quota status and usage metrics."""
    return JSONResponse({"status": "quota", "data": get_quota_status()})


@MONITORING_ROUTER.get("/models")
async def get_models():
    """Get model health and performance status."""
    return JSONResponse(
        {
            "status": "models",
            "summary": get_model_summary(),
            "details": get_all_models_status(),
        }
    )


@MONITORING_ROUTER.get("/health")
async def get_health():
    """Get comprehensive health check with all monitoring data."""
    return JSONResponse(
        {
            "status": "healthy",
            "rate_limiter": get_rate_limiter_status(),
            "queue": get_queue_stats(),
            "quota": get_quota_status(),
            "models": get_model_summary(),
            "monitor_stats": get_monitor_stats(),
        }
    )


@MONITORING_ROUTER.get("/summary")
async def get_summary():
    """Get quick summary of system health."""
    quota = get_quota_status()
    models = get_model_summary()
    queue = get_queue_stats()

    return JSONResponse(
        {
            "system_status": "operational",
            "quota_status": quota.get("status"),
            "quota_usage_percent": quota.get("estimated_quota_percent"),
            "rate_limit_hits": quota.get("rate_limit_hits"),
            "active_requests": queue.get("active_requests"),
            "queue_size": queue.get("queue_size"),
            "healthy_models": models.get("healthy_models"),
            "model_recommendation": models.get("recommended_model"),
        }
    )
