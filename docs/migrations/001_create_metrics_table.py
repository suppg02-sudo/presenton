"""
Database migration: Create metrics table

This migration creates the metrics table for storing LLM metrics and performance data.

Migration ID: 001
Created: 2026-02-18
Description: Create metrics table with schema for storing model performance metrics
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from models.sql.metrics import MetricsRecord
from utils.db_utils import get_database_url_and_connect_args


async def upgrade():
    """Apply the migration - create metrics table."""
    database_url, connect_args = get_database_url_and_connect_args()
    engine = create_async_engine(database_url, connect_args=connect_args)

    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: SQLModel.metadata.create_all(
                sync_conn,
                tables=[MetricsRecord.__table__],
            )
        )

    await engine.dispose()
    print("✓ Migration 001: Created metrics table")


async def downgrade():
    """Rollback the migration - drop metrics table."""
    database_url, connect_args = get_database_url_and_connect_args()
    engine = create_async_engine(database_url, connect_args=connect_args)

    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: MetricsRecord.__table__.drop(sync_conn, checkfirst=True)
        )

    await engine.dispose()
    print("✓ Migration 001: Dropped metrics table")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "down":
        asyncio.run(downgrade())
    else:
        asyncio.run(upgrade())
