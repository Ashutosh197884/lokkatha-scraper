"""Tests for robots.txt parsing, compliance checking, and sitemap discovery."""

import pytest
import httpx
from app.config.settings import Settings
from app.crawler.robots import RobotsManager


ROBOTS_TXT_SAMPLE = """
User-agent: *
Disallow: /private/
Disallow: /admin/
Crawl-delay: 2.5

User-agent: LokkathaBot
Disallow: /restricted/
Allow: /private/public-folklore/

Sitemap: https://example.org/sitemap.xml
Sitemap: https://example.org/sitemap-stories.xml
"""


@pytest.mark.asyncio
async def test_robots_txt_parsing_and_sitemaps():
    """Test parsing rules, sitemap extraction, and crawl-delay."""
    manager = RobotsManager()

    # Test extracting sitemaps and delay
    sitemaps, delay = manager._extract_sitemaps_and_delay(ROBOTS_TXT_SAMPLE)
    assert len(sitemaps) == 2
    assert "https://example.org/sitemap.xml" in sitemaps
    assert delay == 2.5


@pytest.mark.asyncio
async def test_robots_txt_mock_client():
    """Test robots compliance checking against a mocked HTTP client."""
    def mock_handler(request: httpx.Request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=ROBOTS_TXT_SAMPLE)
        return httpx.Response(404)

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        manager = RobotsManager()

        # LokkathaBot specific disallow
        allowed = await manager.is_allowed("https://example.org/restricted/secret-doc", client=client)
        assert allowed is False

        # Permitted route
        allowed = await manager.is_allowed("https://example.org/stories/mumal", client=client)
        assert allowed is True

        # Sitemaps retrieved
        sitemaps = await manager.get_sitemaps("https://example.org", client=client)
        assert len(sitemaps) == 2


@pytest.mark.asyncio
async def test_robots_txt_404_allow_all():
    """Test that 404 response defaults to allowing all crawling."""
    def mock_handler(request: httpx.Request):
        return httpx.Response(404)

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        manager = RobotsManager()
        allowed = await manager.is_allowed("https://no-robots.org/stories/1", client=client)
        assert allowed is True
