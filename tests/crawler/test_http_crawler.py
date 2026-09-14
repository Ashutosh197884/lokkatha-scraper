"""Tests for HTTPCrawler client, Content-Type validation, size limits, and persistence."""

from pathlib import Path
import pytest
import httpx

from app.config.settings import Settings
from app.crawler.http_client import HTTPCrawler
from app.utils.hashing import compute_sha256


@pytest.mark.asyncio
async def test_http_crawler_success_and_save_html(tmp_path):
    """Test fetching HTML successfully and saving raw file."""
    html_content = "<html><body><h1>Mumal Mahendra Tale</h1><p>A Rajasthani folk legend.</p></body></html>"

    def mock_handler(request: httpx.Request):
        return httpx.Response(
            200,
            text=html_content,
            headers={"Content-Type": "text/html; charset=utf-8"},
        )

    settings = Settings(
        storage={"raw_dir": str(tmp_path / "raw")},
        crawler={"save_raw_html": True},
    )
    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        crawler = HTTPCrawler(settings)
        result = await crawler.fetch("https://example.org/stories/mumal", client=client)

        assert result.is_success is True
        assert result.status_code == 200
        assert result.content_hash == compute_sha256(html_content)
        assert result.raw_html_path is not None
        assert Path(result.raw_html_path).is_file()

        # Read back saved file
        with open(result.raw_html_path, "r", encoding="utf-8") as f:
            assert f.read() == html_content


@pytest.mark.asyncio
async def test_http_crawler_rejects_binary_extension():
    """Test that URL with binary file extension is rejected without making network call."""
    crawler = HTTPCrawler()
    result = await crawler.fetch("https://example.org/documents/archive.pdf")

    assert result.is_success is False
    assert result.error == "rejected_binary_extension"


@pytest.mark.asyncio
async def test_http_crawler_rejects_binary_mime_type():
    """Test that response with unsupported binary MIME type is rejected."""
    def mock_handler(request: httpx.Request):
        return httpx.Response(
            200,
            content=b"%PDF-1.4...",
            headers={"Content-Type": "application/pdf"},
        )

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        crawler = HTTPCrawler()
        result = await crawler.fetch("https://example.org/story-download", client=client)

        assert result.is_success is False
        assert "unsupported_content_type" in result.error


@pytest.mark.asyncio
async def test_http_crawler_max_size_limit():
    """Test that response exceeding max_content_size_mb is rejected."""
    huge_text = "x" * 200000

    def mock_handler(request: httpx.Request):
        return httpx.Response(
            200,
            text=huge_text,
            headers={
                "Content-Type": "text/html",
                "Content-Length": str(len(huge_text)),
            },
        )

    # Set limit to ~0.1 MB (100,000 bytes)
    settings = Settings(crawler={"max_content_size_mb": 0.1})
    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        crawler = HTTPCrawler(settings)
        result = await crawler.fetch("https://example.org/huge-page", client=client)

        assert result.is_success is False
        assert "max_content_size_exceeded" in result.error


@pytest.mark.asyncio
async def test_http_crawler_404_error():
    """Test handling 404 HTTP status."""
    def mock_handler(request: httpx.Request):
        return httpx.Response(404, text="Not Found", headers={"Content-Type": "text/html"})

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        crawler = HTTPCrawler()
        result = await crawler.fetch("https://example.org/missing-story", client=client)

        assert result.is_success is False
        assert result.status_code == 404
        assert result.error == "http_status_404"
