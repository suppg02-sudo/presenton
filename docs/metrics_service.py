"""
Metrics service for storing and retrieving LLM metrics from SQLite database.

This module handles:
- Storing metrics (tokens, response time, status)
- Retrieving metrics with various filters
- Database initialization and schema management
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from models.sql.metrics import MetricsRecord
from services.database import sql_engine, async_session_maker

logger = logging.getLogger(__name__)


async def initialize_metrics_table():
    """
    Initialize the metrics table in the database.
    Creates the table if it doesn't exist.
    """
    try:
        async with sql_engine.begin() as conn:
            await conn.run_sync(
                lambda sync_conn: SQLModel.metadata.create_all(
                    sync_conn,
                    tables=[MetricsRecord.__table__],
                )
            )
        logger.info("Metrics table initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize metrics table: {str(e)}")
        raise


async def store_metric_async(
    model_name: str,
    tokens_input: int,
    tokens_output: int,
    response_time_ms: float,
    status: str = "success",
    error_message: Optional[str] = None,
) -> MetricsRecord:
    """
    Store a metric record in the database without requiring a session.
    This is a convenience wrapper that creates its own session.

    Args:
        model_name: Name of the LLM model used
        tokens_input: Number of input tokens
        tokens_output: Number of output tokens
        response_time_ms: Response time in milliseconds
        status: Status of the request (success, error, timeout)
        error_message: Optional error message if status is error

    Returns:
        MetricsRecord: The created metric record

    Raises:
        Exception: If database operation fails
    """
    async with async_session_maker() as session:
        return await store_metric(
            session=session,
            model_name=model_name,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            response_time_ms=response_time_ms,
            status=status,
            error_message=error_message,
        )


async def store_metric(
    session: AsyncSession,
    model_name: str,
    tokens_input: int,
    tokens_output: int,
    response_time_ms: float,
    status: str = "success",
    error_message: Optional[str] = None,
) -> MetricsRecord:
    """
    Store a metric record in the database.

    Args:
        session: AsyncSession for database operations
        model_name: Name of the LLM model used
        tokens_input: Number of input tokens
        tokens_output: Number of output tokens
        response_time_ms: Response time in milliseconds
        status: Status of the request (success, error, timeout)
        error_message: Optional error message if status is error

    Returns:
        MetricsRecord: The created metric record

    Raises:
        Exception: If database operation fails
    """
    try:
        metric = MetricsRecord(
            model_name=model_name,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            response_time_ms=response_time_ms,
            status=status,
            error_message=error_message,
        )
        session.add(metric)
        await session.commit()
        await session.refresh(metric)

        logger.debug(
            f"Stored metric for model {model_name}: "
            f"input_tokens={tokens_input}, output_tokens={tokens_output}, "
            f"response_time={response_time_ms}ms, status={status}"
        )
        return metric
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to store metric: {str(e)}")
        raise


async def get_metrics(
    session: AsyncSession,
    limit: int = 100,
    model_name: Optional[str] = None,
    status: Optional[str] = None,
) -> List[MetricsRecord]:
    """
    Retrieve metrics from the database with optional filters.

    Args:
        session: AsyncSession for database operations
        limit: Maximum number of records to return (default: 100)
        model_name: Optional filter by model name
        status: Optional filter by status (success, error, timeout)

    Returns:
        List[MetricsRecord]: List of metric records

    Raises:
        Exception: If database operation fails
    """
    try:
        query = select(MetricsRecord)

        # Build filters
        filters = []
        if model_name:
            filters.append(MetricsRecord.model_name == model_name)
        if status:
            filters.append(MetricsRecord.status == status)

        if filters:
            query = query.where(and_(*filters))

        # Order by timestamp descending and apply limit
        query = query.order_by(MetricsRecord.timestamp.desc()).limit(limit)

        result = await session.execute(query)
        metrics = result.scalars().all()

        logger.debug(
            f"Retrieved {len(metrics)} metrics "
            f"(model_name={model_name}, status={status}, limit={limit})"
        )
        return list(metrics)
    except Exception as e:
        logger.error(f"Failed to retrieve metrics: {str(e)}")
        raise


async def get_metrics_by_date_range(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    model_name: Optional[str] = None,
    status: Optional[str] = None,
) -> List[MetricsRecord]:
    """
    Retrieve metrics within a specific date range.

    Args:
        session: AsyncSession for database operations
        start_date: Start date for the range (inclusive)
        end_date: End date for the range (inclusive)
        model_name: Optional filter by model name
        status: Optional filter by status (success, error, timeout)

    Returns:
        List[MetricsRecord]: List of metric records within the date range

    Raises:
        Exception: If database operation fails
    """
    try:
        query = select(MetricsRecord).where(
            and_(
                MetricsRecord.timestamp >= start_date,
                MetricsRecord.timestamp <= end_date,
            )
        )

        # Build additional filters
        filters = []
        if model_name:
            filters.append(MetricsRecord.model_name == model_name)
        if status:
            filters.append(MetricsRecord.status == status)

        if filters:
            query = query.where(and_(*filters))

        # Order by timestamp descending
        query = query.order_by(MetricsRecord.timestamp.desc())

        result = await session.execute(query)
        metrics = result.scalars().all()

        logger.debug(
            f"Retrieved {len(metrics)} metrics for date range "
            f"{start_date} to {end_date} "
            f"(model_name={model_name}, status={status})"
        )
        return list(metrics)
    except Exception as e:
        logger.error(f"Failed to retrieve metrics by date range: {str(e)}")
        raise


async def get_metrics_summary(
    session: AsyncSession,
    model_name: Optional[str] = None,
    hours: int = 24,
) -> dict:
    """
    Get a summary of metrics for the last N hours.

    Args:
        session: AsyncSession for database operations
        model_name: Optional filter by model name
        hours: Number of hours to look back (default: 24)

    Returns:
        dict: Summary statistics including total requests, avg response time, etc.

    Raises:
        Exception: If database operation fails
    """
    try:
        start_date = datetime.utcnow() - timedelta(hours=hours)
        metrics = await get_metrics_by_date_range(
            session, start_date, datetime.utcnow(), model_name=model_name
        )

        if not metrics:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_response_time_ms": 0.0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
            }

        successful = [m for m in metrics if m.status == "success"]
        failed = [m for m in metrics if m.status != "success"]

        avg_response_time = (
            sum(m.response_time_ms for m in metrics) / len(metrics) if metrics else 0.0
        )

        summary = {
            "total_requests": len(metrics),
            "successful_requests": len(successful),
            "failed_requests": len(failed),
            "avg_response_time_ms": round(avg_response_time, 2),
            "total_input_tokens": sum(m.tokens_input for m in metrics),
            "total_output_tokens": sum(m.tokens_output for m in metrics),
        }

        logger.debug(f"Generated metrics summary: {summary}")
        return summary
    except Exception as e:
        logger.error(f"Failed to generate metrics summary: {str(e)}")
        raise


async def delete_old_metrics(
    session: AsyncSession,
    days: int = 30,
) -> int:
    """
    Delete metrics older than N days.

    Args:
        session: AsyncSession for database operations
        days: Number of days to keep (default: 30)

    Returns:
        int: Number of records deleted

    Raises:
        Exception: If database operation fails
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get records to delete
        query = select(MetricsRecord).where(MetricsRecord.timestamp < cutoff_date)
        result = await session.execute(query)
        records_to_delete = result.scalars().all()

        # Delete them
        for record in records_to_delete:
            await session.delete(record)

        await session.commit()

        logger.info(f"Deleted {len(records_to_delete)} metrics older than {days} days")
        return len(records_to_delete)
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to delete old metrics: {str(e)}")
        raise
