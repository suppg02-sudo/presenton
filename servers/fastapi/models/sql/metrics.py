from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlmodel import Field, SQLModel

from utils.datetime_utils import get_current_utc_datetime


class MetricsRecord(SQLModel, table=True):
    """SQLModel for storing LLM metrics and performance data."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    model_name: str = Field(index=True)
    tokens_input: int = Field(default=0)
    tokens_output: int = Field(default=0)
    response_time_ms: float = Field(default=0.0)
    status: str = Field(default="success", index=True)  # success, error, timeout
    timestamp: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            default=get_current_utc_datetime,
            index=True,
        ),
    )
    error_message: Optional[str] = Field(default=None)
