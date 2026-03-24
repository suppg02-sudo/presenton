"""
Unit tests for analytics_service module.

Tests cover:
- Model distribution analysis
- Performance statistics
- Cost savings calculations
- Comprehensive report generation
- Period filtering (daily, weekly, monthly)
- Error handling
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

from models.sql.metrics import MetricsRecord
from services.metrics_service import store_metric
from services.analytics_service import (
    get_model_distribution,
    get_performance_stats,
    calculate_cost_savings,
    generate_report,
    get_period_dates,
    get_daily_report,
    get_weekly_report,
    get_monthly_report,
)


@pytest.fixture
async def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session_maker() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def sample_metrics(test_db):
    """Create sample metrics for testing."""
    now = datetime.utcnow()

    # Store metrics for different models
    await store_metric(
        test_db,
        model_name="gpt-4",
        tokens_input=100,
        tokens_output=50,
        response_time_ms=1000.0,
        status="success",
    )

    await store_metric(
        test_db,
        model_name="gpt-4",
        tokens_input=120,
        tokens_output=60,
        response_time_ms=1100.0,
        status="success",
    )

    await store_metric(
        test_db,
        model_name="gpt-3.5",
        tokens_input=80,
        tokens_output=40,
        response_time_ms=800.0,
        status="success",
    )

    await store_metric(
        test_db,
        model_name="gpt-3.5",
        tokens_input=0,
        tokens_output=0,
        response_time_ms=5000.0,
        status="error",
        error_message="Rate limit exceeded",
    )

    await store_metric(
        test_db,
        model_name="claude-3",
        tokens_input=150,
        tokens_output=75,
        response_time_ms=1200.0,
        status="success",
    )

    return test_db


@pytest.mark.asyncio
async def test_get_model_distribution(sample_metrics):
    """Test model distribution analysis."""
    now = datetime.utcnow()
    start = now - timedelta(hours=1)
    end = now

    result = await get_model_distribution(sample_metrics, start, end)

    assert result["total_requests"] == 5
    assert len(result["models"]) == 3
    assert "gpt-4" in result["models"]
    assert "gpt-3.5" in result["models"]
    assert "claude-3" in result["models"]

    # Check gpt-4 stats
    gpt4_stats = result["models"]["gpt-4"]
    assert gpt4_stats["count"] == 2
    assert gpt4_stats["percentage"] == 40.0
    assert gpt4_stats["successful"] == 2
    assert gpt4_stats["failed"] == 0
    assert gpt4_stats["total_input_tokens"] == 220
    assert gpt4_stats["total_output_tokens"] == 110

    # Check gpt-3.5 stats
    gpt35_stats = result["models"]["gpt-3.5"]
    assert gpt35_stats["count"] == 2
    assert gpt35_stats["percentage"] == 40.0
    assert gpt35_stats["successful"] == 1
    assert gpt35_stats["failed"] == 1


@pytest.mark.asyncio
async def test_get_model_distribution_empty(test_db):
    """Test model distribution with no metrics."""
    now = datetime.utcnow()
    start = now - timedelta(hours=1)
    end = now

    result = await get_model_distribution(test_db, start, end)

    assert result["total_requests"] == 0
    assert result["models"] == {}


@pytest.mark.asyncio
async def test_get_performance_stats(sample_metrics):
    """Test performance statistics."""
    now = datetime.utcnow()
    start = now - timedelta(hours=1)
    end = now

    result = await get_performance_stats(sample_metrics, start, end)

    assert result["total_requests"] == 5
    assert result["successful_requests"] == 4
    assert result["failed_requests"] == 1
    assert result["success_rate"] == 80.0
    assert result["avg_response_time_ms"] > 0
    assert result["min_response_time_ms"] == 800.0
    assert result["max_response_time_ms"] == 5000.0
    assert result["avg_tokens_per_request"] > 0


@pytest.mark.asyncio
async def test_get_performance_stats_with_model_filter(sample_metrics):
    """Test performance stats filtered by model."""
    now = datetime.utcnow()
    start = now - timedelta(hours=1)
    end = now

    result = await get_performance_stats(sample_metrics, start, end, model_name="gpt-4")

    assert result["total_requests"] == 2
    assert result["successful_requests"] == 2
    assert result["failed_requests"] == 0
    assert result["success_rate"] == 100.0


@pytest.mark.asyncio
async def test_get_performance_stats_empty(test_db):
    """Test performance stats with no metrics."""
    now = datetime.utcnow()
    start = now - timedelta(hours=1)
    end = now

    result = await get_performance_stats(test_db, start, end)

    assert result["total_requests"] == 0
    assert result["successful_requests"] == 0
    assert result["failed_requests"] == 0
    assert result["success_rate"] == 0.0
    assert result["avg_response_time_ms"] == 0.0


@pytest.mark.asyncio
async def test_calculate_cost_savings(sample_metrics):
    """Test cost savings calculation."""
    now = datetime.utcnow()
    start = now - timedelta(hours=1)
    end = now

    result = await calculate_cost_savings(sample_metrics, start, end)

    assert result["total_requests"] == 5
    assert result["total_tokens"] > 0
    assert result["openrouter_cost"] == 0.0  # Free tier
    assert result["ollama_estimated_cost"] > 0
    assert result["savings"] > 0
    assert result["savings_percentage"] > 0


@pytest.mark.asyncio
async def test_calculate_cost_savings_empty(test_db):
    """Test cost savings with no metrics."""
    now = datetime.utcnow()
    start = now - timedelta(hours=1)
    end = now

    result = await calculate_cost_savings(test_db, start, end)

    assert result["total_requests"] == 0
    assert result["total_tokens"] == 0
    assert result["openrouter_cost"] == 0.0
    assert result["ollama_estimated_cost"] == 0.0
    assert result["savings"] == 0.0


@pytest.mark.asyncio
async def test_generate_report(sample_metrics):
    """Test comprehensive report generation."""
    now = datetime.utcnow()
    start = now - timedelta(hours=1)
    end = now

    report = await generate_report(sample_metrics, start, end)

    # Check report structure
    assert "period" in report
    assert "summary" in report
    assert "model_distribution" in report
    assert "performance" in report
    assert "cost_analysis" in report
    assert "generated_at" in report

    # Check summary
    assert report["summary"]["total_requests"] == 5
    assert report["summary"]["successful_requests"] == 4
    assert report["summary"]["failed_requests"] == 1
    assert report["summary"]["success_rate"] == 80.0
    assert report["summary"]["unique_models"] == 3

    # Check model distribution
    assert report["model_distribution"]["total_requests"] == 5
    assert len(report["model_distribution"]["models"]) == 3

    # Check performance
    assert report["performance"]["total_requests"] == 5
    assert report["performance"]["success_rate"] == 80.0

    # Check cost analysis
    assert report["cost_analysis"]["total_requests"] == 5
    assert report["cost_analysis"]["savings"] > 0


@pytest.mark.asyncio
async def test_get_period_dates_daily():
    """Test daily period date calculation."""
    start, end = get_period_dates("daily")

    # Should be approximately 24 hours
    diff = end - start
    assert 23 <= diff.total_seconds() / 3600 <= 25


@pytest.mark.asyncio
async def test_get_period_dates_weekly():
    """Test weekly period date calculation."""
    start, end = get_period_dates("weekly")

    # Should be approximately 7 days
    diff = end - start
    assert 6.9 <= diff.total_seconds() / (3600 * 24) <= 7.1


@pytest.mark.asyncio
async def test_get_period_dates_monthly():
    """Test monthly period date calculation."""
    start, end = get_period_dates("monthly")

    # Should be approximately 30 days
    diff = end - start
    assert 29.9 <= diff.total_seconds() / (3600 * 24) <= 30.1


@pytest.mark.asyncio
async def test_get_period_dates_invalid():
    """Test invalid period raises error."""
    with pytest.raises(ValueError):
        get_period_dates("invalid")


@pytest.mark.asyncio
async def test_get_daily_report(sample_metrics):
    """Test daily report generation."""
    report = await get_daily_report(sample_metrics)

    assert "period" in report
    assert "summary" in report
    assert report["summary"]["total_requests"] == 5


@pytest.mark.asyncio
async def test_get_weekly_report(sample_metrics):
    """Test weekly report generation."""
    report = await get_weekly_report(sample_metrics)

    assert "period" in report
    assert "summary" in report
    assert report["summary"]["total_requests"] == 5


@pytest.mark.asyncio
async def test_get_monthly_report(sample_metrics):
    """Test monthly report generation."""
    report = await get_monthly_report(sample_metrics)

    assert "period" in report
    assert "summary" in report
    assert report["summary"]["total_requests"] == 5


@pytest.mark.asyncio
async def test_model_distribution_response_time_calculation(sample_metrics):
    """Test that average response time is calculated correctly."""
    now = datetime.utcnow()
    start = now - timedelta(hours=1)
    end = now

    result = await get_model_distribution(sample_metrics, start, end)

    # gpt-4 has response times of 1000.0 and 1100.0
    gpt4_avg = result["models"]["gpt-4"]["avg_response_time_ms"]
    assert gpt4_avg == 1050.0

    # gpt-3.5 has response times of 800.0 and 5000.0
    gpt35_avg = result["models"]["gpt-3.5"]["avg_response_time_ms"]
    assert gpt35_avg == 2900.0


@pytest.mark.asyncio
async def test_performance_stats_token_calculation(sample_metrics):
    """Test that token calculations are correct."""
    now = datetime.utcnow()
    start = now - timedelta(hours=1)
    end = now

    result = await get_performance_stats(sample_metrics, start, end)

    # Total tokens: (100+50) + (120+60) + (80+40) + (0+0) + (150+75) = 675
    # Average per request: 675 / 5 = 135
    assert result["avg_tokens_per_request"] == 135.0


@pytest.mark.asyncio
async def test_cost_savings_calculation_accuracy(sample_metrics):
    """Test cost savings calculation accuracy."""
    now = datetime.utcnow()
    start = now - timedelta(hours=1)
    end = now

    result = await calculate_cost_savings(sample_metrics, start, end)

    # Total tokens: 675
    # Ollama cost: (675 / 1,000,000) * 0.001 = 0.000675
    # OpenRouter cost: 0.0
    # Savings: 0.000675
    assert result["total_tokens"] == 675
    assert abs(result["ollama_estimated_cost"] - 0.000675) < 0.0001
    assert result["openrouter_cost"] == 0.0
    assert abs(result["savings"] - 0.000675) < 0.0001


@pytest.mark.asyncio
async def test_report_period_dates_included(sample_metrics):
    """Test that report includes period dates."""
    now = datetime.utcnow()
    start = now - timedelta(hours=1)
    end = now

    report = await generate_report(sample_metrics, start, end)

    assert report["period"]["start"] == start.isoformat()
    assert report["period"]["end"] == end.isoformat()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
