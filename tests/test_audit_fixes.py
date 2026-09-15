"""Regression tests for audit fixes: pipeline wiring, path safety, retry escalation, politeness."""

from pathlib import Path

import httpx
import pytest

from app.config.settings import Settings
from app.crawler.http_client import HTTPCrawler
from app.crawler.retry import RetryableHTTPStatusError, retry_with_backoff
from app.pipeline import process_crawl_results
from app.storage.repository import JSONFolkloreRepository, validate_safe_id


FOLK_PAGE = """
<!DOCTYPE html>
<html>
<head><title>The Legend of Mumal and Mahendra</title></head>
<body>
<nav><a href="/">Home</a><a href="/about">About</a></nav>
<article>
<h1>The Legend of Mumal and Mahendra</h1>
<p>Princess Mumal of Lodrawa was renowned across the Marwar desert as the most
beautiful woman of her age. Prince Mahendra of Umerkot crossed the dunes each
night, guided by the fire she lit in her palace window.</p>
<p>The storytellers of Rajasthan sing how Mumal tested her lover with illusions,
disguising her sisters as strangers and hiding the palace in shifting sands.</p>
<p>When Mahendra finally failed the test and turned away, Mumal took her own life
on the funeral pyre, and the lovers were burned together in Lodrawa.</p>
<p>Villagers still point travellers to the ruins and call the folktale a legend
of faithful love that outlasted death in the Thar desert.</p>
</article>
<footer>Copyright example.org</footer>
</body>
</html>
"""


def _make_result(tmp_path: Path, url: str, html: str, content_hash: str):
    """Build a successful CrawlResult with a raw HTML file on disk."""
    from app.schemas.crawl import CrawlResult

    raw_file = tmp_path / "raw" / f"{content_hash}.html"
    raw_file.parent.mkdir(parents=True, exist_ok=True)
    raw_file.write_text(html, encoding="utf-8")
    return CrawlResult(
        url=url,
        normalized_url=url,
        domain="example.org",
        status_code=200,
        content_type="text/html",
        raw_html_path=str(raw_file),
        content_hash=content_hash,
        is_success=True,
    )


class TestPipeline:
    def test_pipeline_extracts_folklore_document(self, tmp_path):
        from app.utils.hashing import compute_sha256

        result = _make_result(tmp_path, "https://example.org/mumal", FOLK_PAGE, compute_sha256(FOLK_PAGE))
        settings = Settings(storage={"structured_dir": str(tmp_path / "structured")})

        docs, evidence, duplicates = process_crawl_results([result], settings=settings)

        assert len(docs) == 1
        assert "Mumal" in docs[0].title
        assert len(docs[0].story) > 100
        assert len(evidence) > 0
        assert duplicates == 0

    def test_pipeline_deduplicates_identical_content(self, tmp_path):
        from app.utils.hashing import compute_sha256

        h = compute_sha256(FOLK_PAGE)
        r1 = _make_result(tmp_path, "https://example.org/mumal", FOLK_PAGE, h)
        r2 = _make_result(tmp_path, "https://example.org/mirror/mumal", FOLK_PAGE, h)
        settings = Settings(storage={"structured_dir": str(tmp_path / "structured")})

        docs, _, duplicates = process_crawl_results([r1, r2], settings=settings)

        assert len(docs) == 1
        assert duplicates == 1


class TestRepositoryPathSafety:
    def test_validate_safe_id_rejects_traversal(self):
        with pytest.raises(ValueError):
            validate_safe_id("../../etc/passwd")
        with pytest.raises(ValueError):
            validate_safe_id("..")
        with pytest.raises(ValueError):
            validate_safe_id("a/b")
        with pytest.raises(ValueError):
            validate_safe_id("")

    def test_validate_safe_id_accepts_normal_ids(self):
        assert validate_safe_id("folk-mumal-1234abcd") == "folk-mumal-1234abcd"
        assert validate_safe_id("doc_1.2") == "doc_1.2"

    def test_repository_rejects_unsafe_lookup(self, tmp_path):
        repo = JSONFolkloreRepository(base_dir=str(tmp_path))
        with pytest.raises(ValueError):
            repo.get_by_id("../../secrets")


class TestRetryableHTTPStatus:
    def test_retryable_error_is_retried_then_succeeds(self):
        calls = {"n": 0}

        async def flaky():
            calls["n"] += 1
            if calls["n"] < 3:
                raise RetryableHTTPStatusError(503)
            return "ok"

        import asyncio

        result = asyncio.run(retry_with_backoff(flaky, max_retries=3, initial_delay=0.01))
        assert result == "ok"
        assert calls["n"] == 3

    def test_non_retryable_status_not_escalated(self):
        import asyncio

        async def immediate():
            raise RetryableHTTPStatusError(404)

        with pytest.raises(RetryableHTTPStatusError):
            asyncio.run(retry_with_backoff(immediate, max_retries=2, initial_delay=0.01))


class TestHTTPCrawlerRetries5xx:
    @pytest.mark.asyncio
    async def test_503_is_retried_until_exhaustion(self, tmp_path):
        calls = {"n": 0}

        def handler(request: httpx.Request):
            calls["n"] += 1
            return httpx.Response(503, text="busy")

        settings = Settings(storage={"raw_dir": str(tmp_path / "raw")}, crawler={"save_raw_html": False})
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as client:
            crawler = HTTPCrawler(settings)
            result = await crawler.fetch("https://example.org/busy", client=client)

        assert result.is_success is False
        assert result.status_code == 503
        assert "retries_exhausted" in result.error
        assert calls["n"] == 3  # initial + 2 retries


class TestFrontierPendingWork:
    @pytest.mark.asyncio
    async def test_has_pending_work_counts_in_flight(self):
        from app.crawler.frontier import URLFrontier

        frontier = URLFrontier()
        await frontier.add_url("https://example.org/a")

        item = await frontier.next_url()
        assert item is not None
        # No queued items left, but one is in flight.
        assert frontier.is_empty() is True
        assert frontier.has_pending_work() is True

        await frontier.mark_status(item.normalized_url, "fetched")
        assert frontier.has_pending_work() is False
