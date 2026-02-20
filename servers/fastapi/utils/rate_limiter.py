"""
Rate limiter with exponential backoff for OpenRouter API calls.
Handles rate limiting (HTTP 429) gracefully with automatic retry.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter with exponential backoff strategy.
    
    Features:
    - Detects 429 Too Many Requests errors
    - Implements exponential backoff with jitter
    - Tracks rate limit headers from responses
    - Prevents cascade of failed requests
    """
    
    def __init__(
        self,
        initial_backoff_seconds: float = 1.0,
        max_backoff_seconds: float = 60.0,
        max_retries: int = 5,
    ):
        self.initial_backoff = initial_backoff_seconds
        self.max_backoff = max_backoff_seconds
        self.max_retries = max_retries
        self.retry_count = 0
        self.last_rate_limit_time: Optional[datetime] = None
        self.backoff_until: Optional[datetime] = None
        
    async def wait_if_rate_limited(self) -> bool:
        """
        Wait if rate limited. Returns True if waited, False if ready.
        """
        if self.backoff_until and datetime.utcnow() < self.backoff_until:
            wait_seconds = (self.backoff_until - datetime.utcnow()).total_seconds()
            logger.warning(
                f"Rate limited. Waiting {wait_seconds:.1f} seconds before retry..."
            )
            await asyncio.sleep(wait_seconds)
            return True
        return False
    
    def handle_rate_limit_error(self, retry_after: Optional[int] = None) -> None:
        """
        Handle HTTP 429 error with exponential backoff.
        
        Args:
            retry_after: Optional Retry-After header value in seconds
        """
        self.retry_count += 1
        self.last_rate_limit_time = datetime.utcnow()
        
        if retry_after:
            # Use server's suggested retry time
            backoff_seconds = retry_after
            logger.info(
                f"Rate limited. Server suggests waiting {retry_after}s. "
                f"Retry attempt {self.retry_count}/{self.max_retries}"
            )
        else:
            # Calculate exponential backoff: 1s, 2s, 4s, 8s, 16s, 32s, 60s (capped)
            backoff_seconds = min(
                self.initial_backoff * (2 ** (self.retry_count - 1)),
                self.max_backoff,
            )
            logger.warning(
                f"Rate limited (HTTP 429). Exponential backoff: {backoff_seconds}s. "
                f"Retry attempt {self.retry_count}/{self.max_retries}"
            )
        
        self.backoff_until = datetime.utcnow() + timedelta(seconds=backoff_seconds)
    
    def reset(self) -> None:
        """Reset rate limiter after successful request."""
        self.retry_count = 0
        self.backoff_until = None
    
    def exceeded_max_retries(self) -> bool:
        """Check if max retries exceeded."""
        return self.retry_count > self.max_retries
    
    def get_status(self) -> dict:
        """Get current rate limiter status."""
        return {
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "rate_limited": self.backoff_until is not None,
            "wait_until": self.backoff_until.isoformat() if self.backoff_until else None,
            "last_rate_limit_time": self.last_rate_limit_time.isoformat() if self.last_rate_limit_time else None,
        }


# Global rate limiter instance
_rate_limiter = RateLimiter()


async def wait_if_rate_limited() -> bool:
    """Wait if rate limited."""
    return await _rate_limiter.wait_if_rate_limited()


def handle_rate_limit_error(retry_after: Optional[int] = None) -> None:
    """Handle rate limit error."""
    _rate_limiter.handle_rate_limit_error(retry_after)


def reset_rate_limiter() -> None:
    """Reset rate limiter after successful request."""
    _rate_limiter.reset()


def get_rate_limiter_status() -> dict:
    """Get rate limiter status."""
    return _rate_limiter.get_status()


def is_rate_limited() -> bool:
    """Check if currently rate limited."""
    return _rate_limiter.exceeded_max_retries() or (
        _rate_limiter.backoff_until is not None 
        and datetime.utcnow() < _rate_limiter.backoff_until
    )
