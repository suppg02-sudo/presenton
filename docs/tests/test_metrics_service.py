"""
Unit tests for metrics_service module.

Tests cover:
- Storing metrics
- Retrieving metrics with filters
- Date range queries
- Summary statistics
- Error handling
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

from models.sql.metrics import MetricsRecord
from services.metrics_service import (
    store_metric,
    get_metrics,
    get_metrics_by_date_range,
    get_metrics_summary,
    delete_old_metrics,
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


@pytest.mark.asyncio
async def test_store_metric(test_db):
    """Test storing a single metric."""
    metric = await store_metric(
        test_db,
        model_name="gpt-4",
        tokens_input=100,
        tokens_output=50,
        response_time_ms=1234.5,
        status="success",
    )

    assert metric.model_name == "gpt-4"
    assert metric.tokens_input == 100
    assert metric.tokens_output == 50
    assert metric.response_time_ms == 1234.5
    assert metric.status == "success"
    assert metric.error_message is None
    assert metric.id is not None
    assert metric.timestamp is not None


@pytest.mark.asyncio
async def test_store_metric_with_error(test_db):
    """Test storing a metric with error status."""
    metric = await store_metric(
        test_db,
        model_name="gpt-4",
        tokens_input=0,
        tokens_output=0,
        response_time_ms=5000.0,
        status="error",
        error_message="API rate limit exceeded",
    )

    assert metric.status == "error"
    assert metric.error_message == "API rate limit exceeded"


@pytest.mark.asyncio
async def test_get_metrics(test_db):
    """Test retrieving metrics."""
    # Store multiple metrics
    await store_metric(test_db, "gpt-4", 100, 50, 1000.0)
    await store_metric(test_db, "gpt-3.5", 80, 40, 800.0)
    await store_metric(test_db, "gpt-4", 120, 60, 1200.0)

    # Get all metrics
    metrics = await get_metrics(test_db)
    assert len(metrics) == 3

    # Verify ordering (most recent first)
    assert metrics[0].response_time_ms == 1200.0
    assert metrics[1].response_time_ms == 800.0
    assert metrics[2].response_time_ms == 1000.0


@pytest.mark.asyncio
async def test_get_metrics_with_model_filter(test_db):
    """Test retrieving metrics filtered by model name."""
    await store_metric(test_db, "gpt-4", 100, 50, 1000.0)
    await store_metric(test_db, "gpt-3.5", 80, 40, 800.0)
    await store_metric(test_db, "gpt-4", 120, 60, 1200.0)

    metrics = await get_metrics(test_db, model_name="gpt-4")
    assert len(metrics) == 2
    assert all(m.model_name == "gpt-4" for m in metrics)


@pytest.mark.asyncio
async def test_get_metrics_with_status_filter(test_db):
    """Test retrieving metrics filtered by status."""
    await store_metric(test_db, "gpt-4", 100, 50, 1000.0, status="success")
    await store_metric(test_db, "gpt-4", 0, 0, 5000.0, status="error")
    await store_metric(test_db, "gpt-4", 0, 0, 30000.0, status="timeout")

    success_metrics = await get_metrics(test_db, status="success")
    assert len(success_metrics) == 1
    assert success_metrics[0].status == "success"

    error_metrics = await get_metrics(test_db, status="error")
    assert len(error_metrics) == 1
    assert error_metrics[0].status == "error"


@pytest.mark.asyncio
async def test_get_metrics_with_limit(test_db):
    """Test retrieving metrics with limit."""
    for i in range(10):
        await store_metric(test_db, "gpt-4", 100 + i, 50 + i, 1000.0 + i)

    metrics = await get_metrics(test_db, limit=5)
    assert len(metrics) == 5


@pytest.mark.asyncio
async def test_get_metrics_by_date_range(test_db):
    """Test retrieving metrics by date range."""
    now = datetime.utcnow()

    # Store metrics at different times
    metric1 = await store_metric(test_db, "gpt-4", 100, 50, 1000.0)

    # Manually set timestamp for testing
    metric1.timestamp = now - timedelta(hours=2)
    await test_db.merge(metric1)
    await test_db.commit()

    metric2 = await store_metric(test_db, "gpt-4", 110, 55, 1100.0)
    metric2.timestamp = now - timedelta(hours=1)
    await test_db.merge(metric2)
    await test_db.commit()

    metric3 = await store_metric(test_db, "gpt-4", 120, 60, 1200.0)
    metric3.timestamp = now
    await test_db.merge(metric3)
    await test_db.commit()

    # Query for metrics in the last 90 minutes
    start = now - timedelta(minutes=90)
    end = now
    metrics = await get_metrics_by_date_range(test_db, start, end)

    assert len(metrics) == 2  # Should get metric2 and metric3


@pytest.mark.asyncio
async def test_get_metrics_summary(test_db):
    """Test generating metrics summary."""
    await store_metric(test_db, "gpt-4", 100, 50, 1000.0, status="success")
    await store_metric(test_db, "gpt-4", 110, 55, 1100.0, status="success")
    await store_metric(test_db, "gpt-4", 0, 0, 5000.0, status="error")

    summary = await get_metrics_summary(test_db)

    assert summary["total_requests"] == 3
    assert summary["successful_requests"] == 2
    assert summary["failed_requests"] == 1
    assert summary["total_input_tokens"] == 210
    assert summary["total_output_tokens"] == 105
    assert summary["avg_response_time_ms"] > 0


@pytest.mark.asyncio
async def test_get_metrics_summary_empty(test_db):
    """Test generating summary with no metrics."""
    summary = await get_metrics_summary(test_db)

    assert summary["total_requests"] == 0
    assert summary["successful_requests"] == 0
    assert summary["failed_requests"] == 0
    assert summary["avg_response_time_ms"] == 0.0


@pytest.mark.asyncio
async def test_delete_old_metrics(test_db):
    """Test deleting old metrics."""
    now = datetime.utcnow()

    # Store old metric
    old_metric = await store_metric(test_db, "gpt-4", 100, 50, 1000.0)
    old_metric.timestamp = now - timedelta(days=31)
    await test_db.merge(old_metric)
    await test_db.commit()

    # Store recent metric
    recent_metric = await store_metric(test_db, "gpt-4", 110, 55, 1100.0)
    recent_metric.timestamp = now - timedelta(days=5)
    await test_db.merge(recent_metric)
    await test_db.commit()

    # Delete metrics older than 30 days
    deleted_count = await delete_old_metrics(test_db, days=30)

    assert deleted_count == 1

    # Verify only recent metric remains
    remaining = await get_metrics(test_db)
    assert len(remaining) == 1
    assert remaining[0].tokens_input == 110


@pytest.mark.asyncio
async def test_store_metric_error_handling(test_db):
    """Test error handling in store_metric."""
    # Close the session to cause an error
    await test_db.close()

    with pytest.raises(Exception):
        await store_metric(test_db, "gpt-4", 100, 50, 1000.0)


@pytest.mark.asyncio
async def test_get_metrics_combined_filters(test_db):
    """Test retrieving metrics with multiple filters."""
    await store_metric(test_db, "gpt-4", 100, 50, 1000.0, status="success")
    await store_metric(test_db, "gpt-4", 0, 0, 5000.0, status="error")
    await store_metric(test_db, "gpt-3.5", 80, 40, 800.0, status="success")

    metrics = await get_metrics(test_db, model_name="gpt-4", status="success")
    assert len(metrics) == 1
    assert metrics[0].model_name == "gpt-4"
    assert metrics[0].status == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
