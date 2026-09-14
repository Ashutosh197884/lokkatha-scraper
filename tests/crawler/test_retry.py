"""Tests for retry handler with exponential backoff and jitter."""

import pytest
import httpx
from app.crawler.retry import retry_with_backoff


@pytest.mark.asyncio
async def test_retry_success_on_first_try():
    """Test successful coroutine returns immediately without retry."""
    call_count = 0

    async def successful_call():
        nonlocal call_count
        call_count += 1
        return "success"

    result = await retry_with_backoff(successful_call, max_retries=3, initial_delay=0.01)
    assert result == "success"
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_transient_failure_then_success():
    """Test coroutine failing once with ConnectError then succeeding on retry."""
    call_count = 0

    async def flaky_call():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise httpx.ConnectError("Connection refused")
        return "recovered"

    result = await retry_with_backoff(flaky_call, max_retries=3, initial_delay=0.01)
    assert result == "recovered"
    assert call_count == 2


@pytest.mark.asyncio
async def test_retry_max_retries_exceeded():
    """Test raising exception after exceeding max_retries."""
    call_count = 0

    async def always_failing_call():
        nonlocal call_count
        call_count += 1
        raise httpx.TimeoutException("Read timeout")

    with pytest.raises(httpx.TimeoutException):
        await retry_with_backoff(always_failing_call, max_retries=3, initial_delay=0.01)

    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_non_retryable_exception_raises_immediately():
    """Test that non-retryable exceptions are not retried."""
    call_count = 0

    async def fatal_error_call():
        nonlocal call_count
        call_count += 1
        raise ValueError("Non-retryable data validation error")

    with pytest.raises(ValueError):
        await retry_with_backoff(fatal_error_call, max_retries=3, initial_delay=0.01)

    assert call_count == 1
