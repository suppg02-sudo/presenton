"""
Request queue manager for OpenRouter API calls.
Prevents rate limiting by controlling request concurrency and order.
"""

import asyncio
import logging
from collections import deque
from datetime import datetime
from typing import Callable, Optional, Any

logger = logging.getLogger(__name__)


class RequestQueue:
    """
    Manages API requests to prevent rate limiting.
    
    Features:
    - Queues requests in FIFO order
    - Limits concurrent requests
    - Enforces minimum delay between requests
    - Tracks queue metrics
    """
    
    def __init__(
        self,
        max_concurrent: int = 2,
        min_delay_seconds: float = 0.5,
    ):
        self.max_concurrent = max_concurrent
        self.min_delay_seconds = min_delay_seconds
        self.queue: deque = deque()
        self.active_requests = 0
        self.last_request_time: Optional[datetime] = None
        self.total_queued = 0
        self.total_processed = 0
        self.lock = asyncio.Lock()
        
    async def enqueue(
        self,
        coro: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Enqueue a request and wait for it to complete.
        
        Args:
            coro: Coroutine or async function to execute
            *args: Arguments for the coroutine
            **kwargs: Keyword arguments for the coroutine
            
        Returns:
            Result of the coroutine
        """
        async with self.lock:
            self.total_queued += 1
            queue_size = len(self.queue)
            
            if queue_size > 0 or self.active_requests >= self.max_concurrent:
                logger.debug(
                    f"Request queued. Queue size: {queue_size}, "
                    f"Active: {self.active_requests}/{self.max_concurrent}"
                )
            
            # Add to queue
            request_id = self.total_queued
            self.queue.append((request_id, coro, args, kwargs))
        
        # Wait for this request to execute
        return await self._process_queue(request_id)
    
    async def _process_queue(self, request_id: int) -> Any:
        """Process requests from queue in order."""
        while True:
            async with self.lock:
                # Check if this request is next in queue and we have capacity
                if (self.queue and 
                    self.queue[0][0] == request_id and 
                    self.active_requests < self.max_concurrent):
                    
                    _, coro, args, kwargs = self.queue.popleft()
                    self.active_requests += 1
                    
                    # Enforce minimum delay between requests
                    if self.last_request_time:
                        elapsed = (datetime.utcnow() - self.last_request_time).total_seconds()
                        if elapsed < self.min_delay_seconds:
                            wait_time = self.min_delay_seconds - elapsed
                            logger.debug(f"Waiting {wait_time:.2f}s before request to prevent rate limiting")
                            await asyncio.sleep(wait_time)
                    
                    self.last_request_time = datetime.utcnow()
                    break
            
            # Request not ready yet, wait and retry
            await asyncio.sleep(0.1)
        
        try:
            # Execute the request
            result = await coro(*args, **kwargs)
            return result
        finally:
            async with self.lock:
                self.active_requests -= 1
                self.total_processed += 1
    
    def get_stats(self) -> dict:
        """Get queue statistics."""
        return {
            "queue_size": len(self.queue),
            "active_requests": self.active_requests,
            "max_concurrent": self.max_concurrent,
            "min_delay_seconds": self.min_delay_seconds,
            "total_queued": self.total_queued,
            "total_processed": self.total_processed,
            "last_request_time": self.last_request_time.isoformat() if self.last_request_time else None,
        }


# Global request queue instance
_request_queue = RequestQueue(max_concurrent=2, min_delay_seconds=0.5)


async def enqueue_request(coro: Callable, *args, **kwargs) -> Any:
    """Enqueue and execute a request."""
    return await _request_queue.enqueue(coro, *args, **kwargs)


def get_queue_stats() -> dict:
    """Get queue statistics."""
    return _request_queue.get_stats()
