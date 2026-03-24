"""
Analytics service for generating reports on model usage, cost savings, and performance.

This module provides analytics functions to:
- Analyze model distribution and usage patterns
- Calculate cost savings vs local Ollama baseline
- Generate performance statistics
- Create comprehensive analytics reports
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from models.sql.metrics import MetricsRecord
from services.metrics_service import get_metrics_by_date_range

logger = logging.getLogger(__name__)

# Cost estimation constants
# OpenRouter free tier: $0 (free models)
# Local Ollama: ~$0.001 per 1M tokens (estimated compute cost)
OLLAMA_COST_PER_1M_TOKENS = 0.001
OPENROUTER_COST_PER_1M_TOKENS = 0.0  # Free tier


async def get_model_distribution(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime,
) -> Dict[str, Any]:
    """
    Get model distribution and usage statistics for a date range.

    Args:
        session: AsyncSession for database operations
        start_date: Start date for the analysis period
        end_date: End date for the analysis period

    Returns:
        dict with model distribution data:
        {
            "total_requests": int,
            "models": {
                "model_name": {
                    "count": int,
                    "percentage": float,
                    "successful": int,
                    "failed": int,
                    "avg_response_time_ms": float,
                    "total_input_tokens": int,
                    "total_output_tokens": int,
                }
            }
        }

    Raises:
        Exception: If database operation fails
    """
    try:
        metrics = await get_metrics_by_date_range(session, start_date, end_date)

        if not metrics:
            return {
                "total_requests": 0,
                "models": {},
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }

        # Group metrics by model
        model_stats = defaultdict(
            lambda: {
                "count": 0,
                "successful": 0,
                "failed": 0,
                "response_times": [],
                "total_input_tokens": 0,
                "total_output_tokens": 0,
            }
        )

        for metric in metrics:
            stats = model_stats[metric.model_name]
            stats["count"] += 1
            stats["response_times"].append(metric.response_time_ms)
            stats["total_input_tokens"] += metric.tokens_input
            stats["total_output_tokens"] += metric.tokens_output

            if metric.status == "success":
                stats["successful"] += 1
            else:
                stats["failed"] += 1

        # Calculate percentages and averages
        total_requests = len(metrics)
        models_data = {}

        for model_name, stats in model_stats.items():
            avg_response_time = (
                sum(stats["response_times"]) / len(stats["response_times"])
                if stats["response_times"]
                else 0.0
            )

            models_data[model_name] = {
                "count": stats["count"],
                "percentage": round((stats["count"] / total_requests) * 100, 2),
                "successful": stats["successful"],
                "failed": stats["failed"],
                "avg_response_time_ms": round(avg_response_time, 2),
                "total_input_tokens": stats["total_input_tokens"],
                "total_output_tokens": stats["total_output_tokens"],
            }

        result = {
            "total_requests": total_requests,
            "models": models_data,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
        }

        logger.debug(f"Generated model distribution for {total_requests} requests")
        return result

    except Exception as e:
        logger.error(f"Failed to get model distribution: {str(e)}")
        raise


async def get_performance_stats(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    model_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get performance statistics for a date range.

    Args:
        session: AsyncSession for database operations
        start_date: Start date for the analysis period
        end_date: End date for the analysis period
        model_name: Optional filter by specific model

    Returns:
        dict with performance statistics:
        {
            "avg_response_time_ms": float,
            "min_response_time_ms": float,
            "max_response_time_ms": float,
            "avg_tokens_per_request": float,
            "total_requests": int,
            "successful_requests": int,
            "failed_requests": int,
            "success_rate": float,
        }

    Raises:
        Exception: If database operation fails
    """
    try:
        metrics = await get_metrics_by_date_range(
            session, start_date, end_date, model_name=model_name
        )

        if not metrics:
            return {
                "avg_response_time_ms": 0.0,
                "min_response_time_ms": 0.0,
                "max_response_time_ms": 0.0,
                "avg_tokens_per_request": 0.0,
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "success_rate": 0.0,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }

        response_times = [m.response_time_ms for m in metrics]
        successful = [m for m in metrics if m.status == "success"]
        failed = [m for m in metrics if m.status != "success"]

        total_tokens = sum(m.tokens_input + m.tokens_output for m in metrics)
        avg_tokens_per_request = total_tokens / len(metrics) if metrics else 0.0

        success_rate = (len(successful) / len(metrics)) * 100 if metrics else 0.0

        result = {
            "avg_response_time_ms": round(sum(response_times) / len(response_times), 2),
            "min_response_time_ms": round(min(response_times), 2),
            "max_response_time_ms": round(max(response_times), 2),
            "avg_tokens_per_request": round(avg_tokens_per_request, 2),
            "total_requests": len(metrics),
            "successful_requests": len(successful),
            "failed_requests": len(failed),
            "success_rate": round(success_rate, 2),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
        }

        logger.debug(f"Generated performance stats for {len(metrics)} requests")
        return result

    except Exception as e:
        logger.error(f"Failed to get performance stats: {str(e)}")
        raise


async def calculate_cost_savings(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime,
) -> Dict[str, Any]:
    """
    Calculate cost savings using OpenRouter free tier vs local Ollama.

    Args:
        session: AsyncSession for database operations
        start_date: Start date for the analysis period
        end_date: End date for the analysis period

    Returns:
        dict with cost analysis:
        {
            "total_requests": int,
            "total_tokens": int,
            "openrouter_cost": float,
            "ollama_estimated_cost": float,
            "savings": float,
            "savings_percentage": float,
        }

    Raises:
        Exception: If database operation fails
    """
    try:
        metrics = await get_metrics_by_date_range(session, start_date, end_date)

        if not metrics:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "openrouter_cost": 0.0,
                "ollama_estimated_cost": 0.0,
                "savings": 0.0,
                "savings_percentage": 0.0,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }

        total_requests = len(metrics)
        total_tokens = sum(m.tokens_input + m.tokens_output for m in metrics)

        # OpenRouter free tier cost (free)
        openrouter_cost = 0.0

        # Estimated Ollama cost (local compute)
        # Assuming ~$0.001 per 1M tokens for local compute resources
        ollama_estimated_cost = (total_tokens / 1_000_000) * OLLAMA_COST_PER_1M_TOKENS

        savings = ollama_estimated_cost - openrouter_cost
        savings_percentage = (
            (savings / ollama_estimated_cost) * 100
            if ollama_estimated_cost > 0
            else 0.0
        )

        result = {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "openrouter_cost": round(openrouter_cost, 4),
            "ollama_estimated_cost": round(ollama_estimated_cost, 4),
            "savings": round(savings, 4),
            "savings_percentage": round(savings_percentage, 2),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
        }

        logger.debug(
            f"Calculated cost savings: ${savings:.4f} saved "
            f"({savings_percentage:.2f}%) for {total_requests} requests"
        )
        return result

    except Exception as e:
        logger.error(f"Failed to calculate cost savings: {str(e)}")
        raise


async def generate_report(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime,
) -> Dict[str, Any]:
    """
    Generate a comprehensive analytics report for a date range.

    Args:
        session: AsyncSession for database operations
        start_date: Start date for the analysis period
        end_date: End date for the analysis period

    Returns:
        dict with comprehensive report:
        {
            "period": {...},
            "summary": {...},
            "model_distribution": {...},
            "performance": {...},
            "cost_analysis": {...},
            "generated_at": str,
        }

    Raises:
        Exception: If database operation fails
    """
    try:
        # Gather all analytics
        model_dist = await get_model_distribution(session, start_date, end_date)
        perf_stats = await get_performance_stats(session, start_date, end_date)
        cost_analysis = await calculate_cost_savings(session, start_date, end_date)

        # Create summary
        summary = {
            "total_requests": model_dist["total_requests"],
            "successful_requests": perf_stats["successful_requests"],
            "failed_requests": perf_stats["failed_requests"],
            "success_rate": perf_stats["success_rate"],
            "unique_models": len(model_dist["models"]),
        }

        report = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "summary": summary,
            "model_distribution": model_dist,
            "performance": perf_stats,
            "cost_analysis": cost_analysis,
            "generated_at": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Generated comprehensive report for period "
            f"{start_date.date()} to {end_date.date()}"
        )
        return report

    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        raise


def get_period_dates(period: str = "daily") -> tuple[datetime, datetime]:
    """
    Get start and end dates for a given period.

    Args:
        period: Period type - 'daily', 'weekly', or 'monthly'

    Returns:
        tuple of (start_date, end_date) as datetime objects

    Raises:
        ValueError: If period is not recognized
    """
    now = datetime.utcnow()

    if period == "daily":
        # Last 24 hours
        start = now - timedelta(days=1)
        end = now
    elif period == "weekly":
        # Last 7 days
        start = now - timedelta(days=7)
        end = now
    elif period == "monthly":
        # Last 30 days
        start = now - timedelta(days=30)
        end = now
    else:
        raise ValueError(
            f"Invalid period: {period}. Must be 'daily', 'weekly', or 'monthly'"
        )

    return start, end


async def get_daily_report(session: AsyncSession) -> Dict[str, Any]:
    """
    Get analytics report for the last 24 hours.

    Args:
        session: AsyncSession for database operations

    Returns:
        dict with daily analytics report

    Raises:
        Exception: If database operation fails
    """
    start, end = get_period_dates("daily")
    return await generate_report(session, start, end)


async def get_weekly_report(session: AsyncSession) -> Dict[str, Any]:
    """
    Get analytics report for the last 7 days.

    Args:
        session: AsyncSession for database operations

    Returns:
        dict with weekly analytics report

    Raises:
        Exception: If database operation fails
    """
    start, end = get_period_dates("weekly")
    return await generate_report(session, start, end)


async def get_monthly_report(session: AsyncSession) -> Dict[str, Any]:
    """
    Get analytics report for the last 30 days.

    Args:
        session: AsyncSession for database operations

    Returns:
        dict with monthly analytics report

    Raises:
        Exception: If database operation fails
    """
    start, end = get_period_dates("monthly")
    return await generate_report(session, start, end)
