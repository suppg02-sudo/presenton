"""
Metrics API endpoints for dashboard and monitoring.

This module provides endpoints for retrieving LLM metrics and performance statistics.
"""

import csv
import io
import logging
from datetime import datetime
from typing import Dict, Optional, Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from services.database import get_async_session
from services.metrics_service import (
    get_metrics_summary,
    get_metrics_by_date_range,
)
from services.analytics_service import (
    generate_report,
    get_period_dates,
    get_daily_report,
    get_weekly_report,
    get_monthly_report,
)

logger = logging.getLogger(__name__)


class DashboardResponse(BaseModel):
    """Response model for the metrics dashboard endpoint."""

    total_requests: int = Field(
        ..., description="Total number of requests in the time period"
    )
    success_count: int = Field(..., description="Number of successful requests")
    error_count: int = Field(..., description="Number of failed requests")
    success_rate: float = Field(
        ..., description="Success rate as a percentage (0.0-100.0)"
    )
    avg_response_time_ms: float = Field(
        ..., description="Average response time in milliseconds"
    )
    model_usage: Dict[str, int] = Field(..., description="Count of requests per model")
    avg_tokens_input: float = Field(..., description="Average input tokens per request")
    avg_tokens_output: float = Field(
        ..., description="Average output tokens per request"
    )
    last_updated: datetime = Field(
        ..., description="Timestamp of when metrics were last updated"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "total_requests": 150,
                "success_count": 145,
                "error_count": 5,
                "success_rate": 96.67,
                "avg_response_time_ms": 1250.5,
                "model_usage": {"gpt-4": 75, "gpt-3.5-turbo": 75},
                "avg_tokens_input": 450.25,
                "avg_tokens_output": 320.75,
                "last_updated": "2024-02-18T12:30:45.123456",
            }
        }


class AnalyticsResponse(BaseModel):
    """Response model for the analytics endpoint."""

    period: str = Field(..., description="Period type (daily, weekly, monthly)")
    model_distribution: Dict[str, Any] = Field(
        ..., description="Model usage distribution and statistics"
    )
    performance_stats: Dict[str, Any] = Field(
        ..., description="Performance metrics and statistics"
    )
    cost_analysis: Dict[str, Any] = Field(
        ..., description="Cost analysis and savings calculation"
    )
    generated_at: datetime = Field(
        ..., description="Timestamp when the report was generated"
    )
    summary: Dict[str, Any] = Field(
        ..., description="Summary statistics for the period"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "period": "daily",
                "model_distribution": {
                    "total_requests": 100,
                    "models": {
                        "gpt-4": {
                            "count": 50,
                            "percentage": 50.0,
                            "successful": 48,
                            "failed": 2,
                            "avg_response_time_ms": 1200.5,
                            "total_input_tokens": 25000,
                            "total_output_tokens": 15000,
                        }
                    },
                    "period": {
                        "start": "2024-02-17T12:00:00",
                        "end": "2024-02-18T12:00:00",
                    },
                },
                "performance_stats": {
                    "avg_response_time_ms": 1200.5,
                    "min_response_time_ms": 500.0,
                    "max_response_time_ms": 2500.0,
                    "avg_tokens_per_request": 400.0,
                    "total_requests": 100,
                    "successful_requests": 98,
                    "failed_requests": 2,
                    "success_rate": 98.0,
                    "period": {
                        "start": "2024-02-17T12:00:00",
                        "end": "2024-02-18T12:00:00",
                    },
                },
                "cost_analysis": {
                    "total_requests": 100,
                    "total_tokens": 4000000,
                    "openrouter_cost": 0.0,
                    "ollama_estimated_cost": 0.004,
                    "savings": 0.004,
                    "savings_percentage": 100.0,
                    "period": {
                        "start": "2024-02-17T12:00:00",
                        "end": "2024-02-18T12:00:00",
                    },
                },
                "summary": {
                    "total_requests": 100,
                    "successful_requests": 98,
                    "failed_requests": 2,
                    "success_rate": 98.0,
                    "unique_models": 1,
                },
                "generated_at": "2024-02-18T12:30:45.123456",
            }
        }


METRICS_ROUTER = APIRouter(prefix="/api/v1/metrics", tags=["Metrics"])


@METRICS_ROUTER.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Get Metrics Dashboard",
    description="Returns aggregated metrics and statistics for the last 24 hours",
)
async def get_metrics_dashboard(
    sql_session: AsyncSession = Depends(get_async_session),
    hours: int = 24,
) -> DashboardResponse:
    """
    Get metrics dashboard with aggregated statistics.

    Args:
        sql_session: Database session
        hours: Number of hours to look back (default: 24)

    Returns:
        DashboardResponse: Aggregated metrics and statistics

    Raises:
        HTTPException: If database operation fails
    """
    try:
        # Get metrics summary from service
        summary = await get_metrics_summary(sql_session, hours=hours)

        # Calculate derived metrics
        total_requests = summary.get("total_requests", 0)
        successful_requests = summary.get("successful_requests", 0)
        failed_requests = summary.get("failed_requests", 0)

        # Calculate success rate (0-100)
        success_rate = (
            (successful_requests / total_requests * 100) if total_requests > 0 else 0.0
        )

        # Calculate average tokens
        avg_tokens_input = (
            (summary.get("total_input_tokens", 0) / total_requests)
            if total_requests > 0
            else 0.0
        )
        avg_tokens_output = (
            (summary.get("total_output_tokens", 0) / total_requests)
            if total_requests > 0
            else 0.0
        )

        # Get model usage breakdown
        model_usage = await _get_model_usage_breakdown(sql_session, hours=hours)

        # Create response
        response = DashboardResponse(
            total_requests=total_requests,
            success_count=successful_requests,
            error_count=failed_requests,
            success_rate=round(success_rate, 2),
            avg_response_time_ms=summary.get("avg_response_time_ms", 0.0),
            model_usage=model_usage,
            avg_tokens_input=round(avg_tokens_input, 2),
            avg_tokens_output=round(avg_tokens_output, 2),
            last_updated=datetime.utcnow(),
        )

        logger.info(
            f"Metrics dashboard retrieved: {total_requests} total requests, "
            f"{success_rate:.2f}% success rate"
        )
        return response

    except Exception as e:
        logger.error(f"Failed to retrieve metrics dashboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve metrics: {str(e)}",
        )


async def _get_model_usage_breakdown(
    session: AsyncSession,
    hours: int = 24,
) -> Dict[str, int]:
    """
    Get breakdown of requests by model.

    Args:
        session: Database session
        hours: Number of hours to look back

    Returns:
        Dict mapping model names to request counts
    """
    try:
        from datetime import timedelta
        from sqlalchemy import select, func
        from models.sql.metrics import MetricsRecord

        start_date = datetime.utcnow() - timedelta(hours=hours)

        # Query to get count of requests per model
        query = (
            select(
                MetricsRecord.model_name,
                func.count(MetricsRecord.id).label("count"),
            )
            .where(MetricsRecord.timestamp >= start_date)
            .group_by(MetricsRecord.model_name)
        )

        result = await session.execute(query)
        rows = result.all()

        # Convert to dictionary
        model_usage = {row[0]: row[1] for row in rows}

        logger.debug(f"Model usage breakdown: {model_usage}")
        return model_usage

    except Exception as e:
        logger.error(f"Failed to get model usage breakdown: {str(e)}")
        # Return empty dict on error instead of failing
        return {}


@METRICS_ROUTER.get(
    "/analytics",
    response_model=AnalyticsResponse,
    summary="Get Analytics Report",
    description="Returns comprehensive analytics report for the specified period",
)
async def get_analytics(
    period: str = Query(
        "daily",
        description="Period type: daily, weekly, or monthly",
        regex="^(daily|weekly|monthly)$",
    ),
    sql_session: AsyncSession = Depends(get_async_session),
) -> AnalyticsResponse:
    """
    Get comprehensive analytics report for a specified period.

    Args:
        period: Period type (daily, weekly, monthly)
        sql_session: Database session

    Returns:
        AnalyticsResponse: Comprehensive analytics report

    Raises:
        HTTPException: If report generation fails
    """
    try:
        # Get date range for the period
        start_date, end_date = get_period_dates(period)

        # Generate comprehensive report
        report = await generate_report(sql_session, start_date, end_date)

        # Create response
        response = AnalyticsResponse(
            period=period,
            model_distribution=report["model_distribution"],
            performance_stats=report["performance"],
            cost_analysis=report["cost_analysis"],
            summary=report["summary"],
            generated_at=datetime.utcnow(),
        )

        logger.info(f"Analytics report generated for period: {period}")
        return response

    except ValueError as e:
        logger.error(f"Invalid period parameter: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid period: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Failed to generate analytics report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analytics report: {str(e)}",
        )


@METRICS_ROUTER.get(
    "/analytics/daily",
    response_model=AnalyticsResponse,
    summary="Get Daily Analytics Report",
    description="Returns analytics report for the last 24 hours",
)
async def get_daily_analytics(
    sql_session: AsyncSession = Depends(get_async_session),
) -> AnalyticsResponse:
    """
    Get analytics report for the last 24 hours.

    Args:
        sql_session: Database session

    Returns:
        AnalyticsResponse: Daily analytics report

    Raises:
        HTTPException: If report generation fails
    """
    try:
        report = await get_daily_report(sql_session)

        response = AnalyticsResponse(
            period="daily",
            model_distribution=report["model_distribution"],
            performance_stats=report["performance"],
            cost_analysis=report["cost_analysis"],
            summary=report["summary"],
            generated_at=datetime.utcnow(),
        )

        logger.info("Daily analytics report generated")
        return response

    except Exception as e:
        logger.error(f"Failed to generate daily analytics report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate daily analytics report: {str(e)}",
        )


@METRICS_ROUTER.get(
    "/analytics/weekly",
    response_model=AnalyticsResponse,
    summary="Get Weekly Analytics Report",
    description="Returns analytics report for the last 7 days",
)
async def get_weekly_analytics(
    sql_session: AsyncSession = Depends(get_async_session),
) -> AnalyticsResponse:
    """
    Get analytics report for the last 7 days.

    Args:
        sql_session: Database session

    Returns:
        AnalyticsResponse: Weekly analytics report

    Raises:
        HTTPException: If report generation fails
    """
    try:
        report = await get_weekly_report(sql_session)

        response = AnalyticsResponse(
            period="weekly",
            model_distribution=report["model_distribution"],
            performance_stats=report["performance"],
            cost_analysis=report["cost_analysis"],
            summary=report["summary"],
            generated_at=datetime.utcnow(),
        )

        logger.info("Weekly analytics report generated")
        return response

    except Exception as e:
        logger.error(f"Failed to generate weekly analytics report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate weekly analytics report: {str(e)}",
        )


@METRICS_ROUTER.get(
    "/analytics/monthly",
    response_model=AnalyticsResponse,
    summary="Get Monthly Analytics Report",
    description="Returns analytics report for the last 30 days",
)
async def get_monthly_analytics(
    sql_session: AsyncSession = Depends(get_async_session),
) -> AnalyticsResponse:
    """
    Get analytics report for the last 30 days.

    Args:
        sql_session: Database session

    Returns:
        AnalyticsResponse: Monthly analytics report

    Raises:
        HTTPException: If report generation fails
    """
    try:
        report = await get_monthly_report(sql_session)

        response = AnalyticsResponse(
            period="monthly",
            model_distribution=report["model_distribution"],
            performance_stats=report["performance"],
            cost_analysis=report["cost_analysis"],
            summary=report["summary"],
            generated_at=datetime.utcnow(),
        )

        logger.info("Monthly analytics report generated")
        return response

    except Exception as e:
        logger.error(f"Failed to generate monthly analytics report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate monthly analytics report: {str(e)}",
        )


@METRICS_ROUTER.get(
    "/export",
    summary="Export Metrics",
    description="Export metrics in JSON or CSV format with optional date range filtering",
)
async def export_metrics(
    format: str = Query(
        "json",
        description="Export format: json or csv",
        regex="^(json|csv)$",
    ),
    start_date: Optional[str] = Query(
        None,
        description="Start date in ISO format (YYYY-MM-DD or ISO 8601)",
    ),
    end_date: Optional[str] = Query(
        None,
        description="End date in ISO format (YYYY-MM-DD or ISO 8601)",
    ),
    sql_session: AsyncSession = Depends(get_async_session),
):
    """
    Export metrics in JSON or CSV format.

    Args:
        format: Export format (json or csv, default: json)
        start_date: Optional start date for filtering (ISO format)
        end_date: Optional end date for filtering (ISO format)
        sql_session: Database session

    Returns:
        JSON array or CSV file with metrics data

    Raises:
        HTTPException: If format is invalid or database operation fails
    """
    try:
        # Parse date range
        if start_date and end_date:
            try:
                start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            except ValueError as e:
                logger.error(f"Invalid date format: {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid date format. Use ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
                )
        else:
            # Default to last 24 hours if no date range provided
            from datetime import timedelta

            end = datetime.utcnow()
            start = end - timedelta(hours=24)

        # Retrieve metrics from database
        metrics = await get_metrics_by_date_range(
            sql_session, start_date=start, end_date=end
        )

        if format == "json":
            # Convert metrics to JSON-serializable format
            metrics_data = [
                {
                    "id": str(m.id),
                    "model_name": m.model_name,
                    "tokens_input": m.tokens_input,
                    "tokens_output": m.tokens_output,
                    "response_time_ms": m.response_time_ms,
                    "status": m.status,
                    "timestamp": m.timestamp.isoformat(),
                    "error_message": m.error_message,
                }
                for m in metrics
            ]

            logger.info(f"Exported {len(metrics_data)} metrics in JSON format")
            return metrics_data

        elif format == "csv":
            # Create CSV in memory
            output = io.StringIO()
            if metrics:
                # Write CSV with headers
                fieldnames = [
                    "id",
                    "model_name",
                    "tokens_input",
                    "tokens_output",
                    "response_time_ms",
                    "status",
                    "timestamp",
                    "error_message",
                ]
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()

                # Write metric rows
                for m in metrics:
                    writer.writerow(
                        {
                            "id": str(m.id),
                            "model_name": m.model_name,
                            "tokens_input": m.tokens_input,
                            "tokens_output": m.tokens_output,
                            "response_time_ms": m.response_time_ms,
                            "status": m.status,
                            "timestamp": m.timestamp.isoformat(),
                            "error_message": m.error_message or "",
                        }
                    )
            else:
                # Write empty CSV with headers only
                fieldnames = [
                    "id",
                    "model_name",
                    "tokens_input",
                    "tokens_output",
                    "response_time_ms",
                    "status",
                    "timestamp",
                    "error_message",
                ]
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()

            csv_content = output.getvalue()
            logger.info(f"Exported {len(metrics)} metrics in CSV format")

            # Return as streaming response with proper headers
            return StreamingResponse(
                iter([csv_content]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": "attachment; filename=metrics_export.csv"
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export metrics: {str(e)}",
        )
