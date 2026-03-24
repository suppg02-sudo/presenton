# Metrics Service Documentation

## Overview

The `metrics_service.py` module provides a comprehensive solution for storing and retrieving LLM metrics from a SQLite database. It tracks performance data including token usage, response times, and request status.

## Features

- **Store Metrics**: Record LLM performance data with automatic timestamps
- **Retrieve Metrics**: Query metrics with flexible filtering options
- **Date Range Queries**: Retrieve metrics within specific time periods
- **Summary Statistics**: Generate performance summaries for analysis
- **Automatic Cleanup**: Delete old metrics to manage database size
- **Error Handling**: Comprehensive error handling and logging
- **Async/Await**: Full async support for non-blocking operations

## Database Schema

### MetricsRecord Table

```sql
CREATE TABLE metrics_record (
    id UUID PRIMARY KEY,
    model_name VARCHAR NOT NULL,
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    response_time_ms FLOAT DEFAULT 0.0,
    status VARCHAR DEFAULT 'success',
    timestamp DATETIME NOT NULL,
    error_message VARCHAR
);

-- Indexes for common queries
CREATE INDEX idx_model_name ON metrics_record(model_name);
CREATE INDEX idx_status ON metrics_record(status);
CREATE INDEX idx_timestamp ON metrics_record(timestamp);
```

## API Reference

### `initialize_metrics_table()`

Initialize the metrics table in the database. Creates the table if it doesn't exist.

```python
await initialize_metrics_table()
```

**Raises**: `Exception` if database operation fails

---

### `store_metric()`

Store a metric record in the database.

```python
metric = await store_metric(
    session: AsyncSession,
    model_name: str,
    tokens_input: int,
    tokens_output: int,
    response_time_ms: float,
    status: str = "success",
    error_message: Optional[str] = None,
) -> MetricsRecord
```

**Parameters**:
- `session`: AsyncSession for database operations
- `model_name`: Name of the LLM model used (e.g., "gpt-4", "gpt-3.5-turbo")
- `tokens_input`: Number of input tokens consumed
- `tokens_output`: Number of output tokens generated
- `response_time_ms`: Response time in milliseconds
- `status`: Request status - "success", "error", or "timeout" (default: "success")
- `error_message`: Optional error message if status is "error"

**Returns**: `MetricsRecord` - The created metric record with ID and timestamp

**Example**:
```python
metric = await store_metric(
    session,
    model_name="gpt-4",
    tokens_input=150,
    tokens_output=75,
    response_time_ms=1234.5,
    status="success"
)
```

---

### `get_metrics()`

Retrieve metrics from the database with optional filters.

```python
metrics = await get_metrics(
    session: AsyncSession,
    limit: int = 100,
    model_name: Optional[str] = None,
    status: Optional[str] = None,
) -> List[MetricsRecord]
```

**Parameters**:
- `session`: AsyncSession for database operations
- `limit`: Maximum number of records to return (default: 100)
- `model_name`: Optional filter by model name
- `status`: Optional filter by status ("success", "error", "timeout")

**Returns**: `List[MetricsRecord]` - List of metrics ordered by timestamp (newest first)

**Example**:
```python
# Get last 50 successful requests for gpt-4
metrics = await get_metrics(
    session,
    limit=50,
    model_name="gpt-4",
    status="success"
)
```

---

### `get_metrics_by_date_range()`

Retrieve metrics within a specific date range.

```python
metrics = await get_metrics_by_date_range(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    model_name: Optional[str] = None,
    status: Optional[str] = None,
) -> List[MetricsRecord]
```

**Parameters**:
- `session`: AsyncSession for database operations
- `start_date`: Start date for the range (inclusive)
- `end_date`: End date for the range (inclusive)
- `model_name`: Optional filter by model name
- `status`: Optional filter by status

**Returns**: `List[MetricsRecord]` - List of metrics within the date range

**Example**:
```python
from datetime import datetime, timedelta

# Get metrics from the last 24 hours
now = datetime.utcnow()
start = now - timedelta(hours=24)
metrics = await get_metrics_by_date_range(session, start, now)
```

---

### `get_metrics_summary()`

Generate a summary of metrics for the last N hours.

```python
summary = await get_metrics_summary(
    session: AsyncSession,
    model_name: Optional[str] = None,
    hours: int = 24,
) -> dict
```

**Parameters**:
- `session`: AsyncSession for database operations
- `model_name`: Optional filter by model name
- `hours`: Number of hours to look back (default: 24)

**Returns**: `dict` with keys:
- `total_requests`: Total number of requests
- `successful_requests`: Number of successful requests
- `failed_requests`: Number of failed requests
- `avg_response_time_ms`: Average response time in milliseconds
- `total_input_tokens`: Total input tokens consumed
- `total_output_tokens`: Total output tokens generated

**Example**:
```python
# Get summary for last 24 hours
summary = await get_metrics_summary(session, hours=24)
print(f"Total requests: {summary['total_requests']}")
print(f"Avg response time: {summary['avg_response_time_ms']}ms")
```

---

### `delete_old_metrics()`

Delete metrics older than N days.

```python
deleted_count = await delete_old_metrics(
    session: AsyncSession,
    days: int = 30,
) -> int
```

**Parameters**:
- `session`: AsyncSession for database operations
- `days`: Number of days to keep (default: 30)

**Returns**: `int` - Number of records deleted

**Example**:
```python
# Delete metrics older than 30 days
deleted = await delete_old_metrics(session, days=30)
print(f"Deleted {deleted} old metrics")
```

---

## Usage Examples

### Basic Setup

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from services.database import get_async_session
from services.metrics_service import initialize_metrics_table, store_metric

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Initialize metrics table on startup
    await initialize_metrics_table()

@app.post("/api/generate")
async def generate(request: GenerateRequest, session: AsyncSession = Depends(get_async_session)):
    import time
    start_time = time.time()
    
    try:
        # Call LLM
        response = await llm_client.generate(request.prompt)
        
        # Calculate metrics
        response_time_ms = (time.time() - start_time) * 1000
        
        # Store metrics
        await store_metric(
            session,
            model_name=request.model,
            tokens_input=response.usage.prompt_tokens,
            tokens_output=response.usage.completion_tokens,
            response_time_ms=response_time_ms,
            status="success"
        )
        
        return response
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        
        # Store error metric
        await store_metric(
            session,
            model_name=request.model,
            tokens_input=0,
            tokens_output=0,
            response_time_ms=response_time_ms,
            status="error",
            error_message=str(e)
        )
        raise
```

### Monitoring Endpoint

```python
@app.get("/api/metrics/summary")
async def get_metrics_summary_endpoint(
    hours: int = 24,
    session: AsyncSession = Depends(get_async_session)
):
    from services.metrics_service import get_metrics_summary
    summary = await get_metrics_summary(session, hours=hours)
    return summary

@app.get("/api/metrics")
async def get_metrics_endpoint(
    limit: int = 100,
    model: Optional[str] = None,
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session)
):
    from services.metrics_service import get_metrics
    metrics = await get_metrics(session, limit=limit, model_name=model, status=status)
    return metrics
```

### Cleanup Task

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=2, minute=0)
async def cleanup_old_metrics():
    """Delete metrics older than 30 days every day at 2 AM"""
    async with get_async_session() as session:
        deleted = await delete_old_metrics(session, days=30)
        logger.info(f"Cleanup: Deleted {deleted} old metrics")

scheduler.start()
```

## Error Handling

All functions include comprehensive error handling:

```python
try:
    metric = await store_metric(session, "gpt-4", 100, 50, 1000.0)
except Exception as e:
    logger.error(f"Failed to store metric: {str(e)}")
    # Handle error appropriately
```

## Logging

The module uses Python's standard logging module. Enable debug logging to see detailed operations:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("services.metrics_service")
```

## Testing

Run the unit tests:

```bash
pytest servers/fastapi/tests/test_metrics_service.py -v
```

## Performance Considerations

1. **Indexes**: The metrics table includes indexes on `model_name`, `status`, and `timestamp` for fast queries
2. **Cleanup**: Regularly delete old metrics to keep the database size manageable
3. **Batch Operations**: For high-volume metrics, consider batching inserts
4. **Query Limits**: Always use reasonable limits when querying to avoid memory issues

## Migration

To apply the database migration:

```bash
python servers/fastapi/migrations/001_create_metrics_table.py
```

To rollback:

```bash
python servers/fastapi/migrations/001_create_metrics_table.py down
```

## Status Values

- `success`: Request completed successfully
- `error`: Request failed with an error
- `timeout`: Request timed out

## Future Enhancements

- Batch insert operations for high-volume scenarios
- Metrics aggregation and rollup
- Cost tracking per model
- Performance alerts and thresholds
- Export metrics to external monitoring systems
