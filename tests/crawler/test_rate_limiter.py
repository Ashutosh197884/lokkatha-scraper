"""Tests for per-domain rate limiting and multi-domain concurrency."""

import asyncio
import time
import pytest
from app.crawler.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_same_domain_delay():
    """Test that subsequent requests to the same domain observe the configured delay."""
    limiter = RateLimiter(default_delay=0.1)

    url = "https://example.org/story1"
    start = time.time()

    # First request shouldn't wait
    s1 = await limiter.wait(url)
    assert s1 == 0.0

    # Second request immediately after should wait ~0.1s
    s2 = await limiter.wait(url)
    elapsed = time.time() - start

    assert s2 > 0.05
    assert elapsed >= 0.09


@pytest.mark.asyncio
async def test_rate_limiter_multi_domain_parallelism():
    """Test that requests to different domains execute concurrently without waiting on each other."""
    limiter = RateLimiter(default_delay=0.2)

    url_a = "https://site-a.org/story"
    url_b = "https://site-b.org/story"

    start = time.time()
    # Execute both in parallel
    results = await asyncio.gather(
        limiter.wait(url_a),
        limiter.wait(url_b),
    )
    elapsed = time.time() - start

    # Both are initial requests to different domains, total time should be near 0
    assert elapsed < 0.1
    assert results == [0.0, 0.0]


@pytest.mark.asyncio
async def test_rate_limiter_custom_domain_override():
    """Test custom delay configuration for specific domains."""
    limiter = RateLimiter(default_delay=0.05)
    limiter.set_domain_delay("slow-archive.org", 0.15)

    url = "https://slow-archive.org/tales"
    await limiter.wait(url)

    start = time.time()
    s = await limiter.wait(url)
    elapsed = time.time() - start

    assert s >= 0.1
    assert elapsed >= 0.14
