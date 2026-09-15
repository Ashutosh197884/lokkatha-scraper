"""Tests for CrawlManager multi-page crawling loop, link discovery, and depth control."""

from pathlib import Path
import pytest
import httpx

from app.config.settings import Settings
from app.crawler.manager import CrawlManager


PAGE_1_HTML = """
<!DOCTYPE html>
<html>
<head><title>Folklore Hub</title></head>
<body>
    <h1>Indian Folklore Archive</h1>
    <a href="/stories/story-1">Story 1: Mumal</a>
    <a href="/stories/story-2">Story 2: Dhola Maru</a>
    <a href="https://external-disallowed.com/story">External Story</a>
</body>
</html>
"""

PAGE_2_HTML = """
<!DOCTYPE html>
<html>
<head><title>Story 1: Mumal</title></head>
<body>
    <h1>The Tale of Princess Mumal</h1>
    <p>A Rajasthani oral narrative...</p>
    <a href="/stories/story-3">Story 3: Padmini</a>
</body>
</html>
"""

PAGE_3_HTML = """
<!DOCTYPE html>
<html>
<head><title>Story 2: Dhola Maru</title></head>
<body>
    <h1>Dhola Maru Ballad</h1>
</body>
</html>
"""


@pytest.mark.asyncio
async def test_crawl_manager_multi_page_and_depth_limits(tmp_path):
    """Test full multi-page crawl following internal links with depth tracking."""
    def mock_handler(request: httpx.Request):
        path = request.url.path
        if path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /\n")
        elif path == "/" or path == "/index.html":
            return httpx.Response(200, text=PAGE_1_HTML, headers={"Content-Type": "text/html"})
        elif path == "/stories/story-1":
            return httpx.Response(200, text=PAGE_2_HTML, headers={"Content-Type": "text/html"})
        elif path == "/stories/story-2":
            return httpx.Response(200, text=PAGE_3_HTML, headers={"Content-Type": "text/html"})
        return httpx.Response(404, text="Not Found")

    settings = Settings(
        storage={"raw_dir": str(tmp_path / "raw")},
        crawler={
            "max_pages": 3,
            "max_depth": 1,
            "concurrency": 2,
            "delay_seconds": 0.0,
            "follow_external_links": False,
        },
    )

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        manager = CrawlManager(settings)
        results = await manager.crawl(
            seeds=["https://example.org/"],
            max_pages=3,
            max_depth=1,
            client=client,
        )

        assert len(results) >= 2
        # Verify seed was crawled
        seed_result = next((r for r in results if r.normalized_url == "https://example.org/"), None)
        assert seed_result is not None
        assert seed_result.is_success is True
        assert len(seed_result.links_extracted) >= 2

        # Verify child links were discovered and crawled
        crawled_urls = [r.normalized_url for r in results]
        assert "https://example.org/stories/story-1" in crawled_urls or "https://example.org/stories/story-2" in crawled_urls


@pytest.mark.asyncio
async def test_crawl_manager_respects_robots_blocking(tmp_path):
    """Test that CrawlManager blocks restricted pages from being fetched."""
    def mock_handler(request: httpx.Request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /blocked-story\n")
        elif request.url.path == "/blocked-story":
            return httpx.Response(200, text="<h1>Secret</h1>", headers={"Content-Type": "text/html"})
        return httpx.Response(404)

    settings = Settings(
        storage={"raw_dir": str(tmp_path / "raw")},
        crawler={"delay_seconds": 0.0},
    )

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        manager = CrawlManager(settings)
        results = await manager.crawl(
            seeds=["https://example.org/blocked-story"],
            max_pages=1,
            client=client,
        )

        # Result list shouldn't contain fetched result because robots blocked it
        assert len(results) == 0
        stats = manager.frontier.get_stats()
        assert stats["blocked"] == 1


@pytest.mark.asyncio
async def test_crawl_manager_respects_max_pages_under_concurrency(tmp_path):
    """max_pages must be an exact cap even with concurrent workers (no overshoot,
    no 0-treated-as-unlimited)."""
    fetched: list[str] = []

    def mock_handler(request: httpx.Request):
        path = request.url.path
        if path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /\n")
        fetched.append(path)
        return httpx.Response(200, text=PAGE_2_HTML, headers={"Content-Type": "text/html"})

    settings = Settings(
        storage={"raw_dir": str(tmp_path / "raw")},
        crawler={
            "max_pages": 100,  # generous default, so the explicit cap is what binds
            "max_depth": 0,
            "concurrency": 5,
            "delay_seconds": 0.0,
        },
    )

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        seeds = [f"https://example.org/page/{i}" for i in range(5)]

        for cap in (1, 3, 5):
            manager = CrawlManager(settings)
            results = await manager.crawl(
                seeds=seeds,
                max_pages=cap,
                max_depth=0,
                client=client,
            )
            assert len(results) == cap, (
                f"expected exactly {cap} pages, got {len(results)}"
            )
