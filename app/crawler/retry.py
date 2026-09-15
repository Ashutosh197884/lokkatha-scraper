"""Retry mechanism with exponential backoff and jitter for transient network failures."""

import asyncio
import random
from typing import Any, Callable, Coroutine, Optional, Tuple, Type, TypeVar
import httpx

from app.config.logging import get_logger

logger = get_logger("crawler.retry")

T = TypeVar("T")

# HTTP statuses that are transient and worth retrying with backoff.
RETRYABLE_HTTP_STATUSES = {429, 500, 502, 503, 504}


class RetryableHTTPStatusError(Exception):
    """Raised when a fetch returns a transient HTTP status (e.g. 429/503) so the retry layer can back off.

    Carries the offending status code for downstream error reporting.
    """

    def __init__(self, status_code: int, message: str = "") -> None:
        self.status_code = status_code
        super().__init__(message or f"retryable_http_status_{status_code}")


DEFAULT_RETRYABLE_EXCEPTIONS: Tuple[Type[Exception], ...] = (
    RetryableHTTPStatusError,
    httpx.TimeoutException,
    httpx.NetworkError,
    httpx.RemoteProtocolError,
    httpx.HTTPStatusError,
    ConnectionError,
    TimeoutError,
    asyncio.TimeoutError,
)


async def retry_with_backoff(
    coro_fn: Callable[[], Coroutine[Any, Any, T]],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 30.0,
    jitter: bool = True,
    retry_exceptions: Tuple[Type[Exception], ...] = DEFAULT_RETRYABLE_EXCEPTIONS,
) -> T:
    """
    Execute coroutine with exponential backoff and optional jitter on transient failures.
    
    Formula:
        delay = min(max_delay, initial_delay * (backoff_factor ** (attempt - 1)))
        if jitter: delay += random.uniform(0, delay * 0.1)
    """
    last_exception: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        try:
            return await coro_fn()
        except retry_exceptions as exc:
            last_exception = exc
            if attempt >= max_retries:
                logger.error("max_retries_exceeded", attempt=attempt, max_retries=max_retries, error=str(exc))
                raise

            base_delay = min(max_delay, initial_delay * (backoff_factor ** (attempt - 1)))
            actual_delay = base_delay + (random.uniform(0, base_delay * 0.2) if jitter else 0.0)

            logger.warning(
                "retryable_failure_encountered",
                attempt=attempt,
                max_retries=max_retries,
                next_delay_seconds=round(actual_delay, 2),
                error=str(exc),
            )
            await asyncio.sleep(actual_delay)

    if last_exception:
        raise last_exception
    raise RuntimeError("Retry loop exited without returning or raising")
