"""Tests for URL Frontier queue, prioritization, deduplication, and metrics."""

import pytest
from app.config.settings import DomainPolicySettings
from app.crawler.domain_filter import DomainFilter
from app.crawler.frontier import URLFrontier
from app.schemas.crawl import CrawlStatus


@pytest.mark.asyncio
async def test_frontier_priority_queueing():
    """Test that higher priority URLs are retrieved before lower priority ones."""
    frontier = URLFrontier(max_depth=3)

    await frontier.add_url("https://example.org/low", priority=0.2)
    await frontier.add_url("https://example.org/high", priority=0.9)
    await frontier.add_url("https://example.org/medium", priority=0.5)

    item1 = await frontier.next_url()
    assert item1 is not None
    assert item1.url == "https://example.org/high"

    item2 = await frontier.next_url()
    assert item2 is not None
    assert item2.url == "https://example.org/medium"

    item3 = await frontier.next_url()
    assert item3 is not None
    assert item3.url == "https://example.org/low"

    # Queue should now be empty
    assert await frontier.next_url() is None


@pytest.mark.asyncio
async def test_frontier_deduplication():
    """Test that normalized duplicate URLs are rejected."""
    frontier = URLFrontier()

    # Add base URL
    ok1, status1, _ = await frontier.add_url("https://example.org/story?id=10")
    assert ok1 is True
    assert status1 == CrawlStatus.QUEUED

    # Add equivalent URL with tracking params and uppercase
    ok2, status2, reason2 = await frontier.add_url("HTTPS://Example.ORG/story/?utm_source=twitter&id=10#chapter")
    assert ok2 is False
    assert status2 == CrawlStatus.DUPLICATE
    assert reason2 == "already_seen"

    assert frontier.total_seen() == 1


@pytest.mark.asyncio
async def test_frontier_max_depth_enforcement():
    """Test rejecting URLs exceeding max depth."""
    frontier = URLFrontier(max_depth=2)

    ok1, _, _ = await frontier.add_url("https://example.org/depth-2", depth=2)
    assert ok1 is True

    ok2, status2, reason2 = await frontier.add_url("https://example.org/depth-3", depth=3)
    assert ok2 is False
    assert status2 == CrawlStatus.REJECTED
    assert "exceeds_max" in reason2


@pytest.mark.asyncio
async def test_frontier_domain_policy_rejection():
    """Test frontier integrates domain policy to reject blacklisted domains."""
    policy = DomainPolicySettings(deny=["spam-stories.com"])
    domain_filter = DomainFilter(policy=policy)
    frontier = URLFrontier(domain_filter=domain_filter)

    ok, status, reason = await frontier.add_url("https://spam-stories.com/tale/1")
    assert ok is False
    assert status == CrawlStatus.REJECTED
    assert "denied_by_rule" in reason


@pytest.mark.asyncio
async def test_frontier_status_lifecycle_and_stats():
    """Test URL status transitions and stats reporting."""
    frontier = URLFrontier()

    await frontier.add_urls([
        "https://example.org/story1",
        "https://example.org/story2",
    ])

    item1 = await frontier.next_url()
    assert item1 is not None
    assert item1.status == CrawlStatus.FETCHING

    await frontier.mark_status(item1.normalized_url, CrawlStatus.FETCHED)

    item2 = await frontier.next_url()
    assert item2 is not None
    await frontier.mark_status(item2.normalized_url, CrawlStatus.FAILED, error_message="500 Internal Error")

    stats = frontier.get_stats()
    assert stats["discovered"] == 2
    assert stats["queued"] == 2
    assert stats["fetched"] == 1
    assert stats["failed"] == 1
