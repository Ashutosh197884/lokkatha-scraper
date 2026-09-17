"""Regression tests for audit fixes: pipeline wiring, path safety, retry escalation, politeness."""

import asyncio
import json
from pathlib import Path

import httpx
import pytest

from app.config.settings import Settings
from app.crawler.http_client import HTTPCrawler
from app.crawler.retry import RetryableHTTPStatusError, retry_with_backoff
from app.pipeline import process_crawl_results
from app.storage.repository import JSONFolkloreRepository, validate_safe_id


class TestAPIServer:
    """Tests for the runnable stdlib HTTP + SSE server."""

    @pytest.mark.asyncio
    async def test_api_server_endpoints_and_sse(self, tmp_path):
        import httpx

        from app.api.run_server import LokkathaHTTPServer

        server = LokkathaHTTPServer(repo=JSONFolkloreRepository(str(tmp_path / "structured")))
        tcp = await asyncio.start_server(server.handle_client, "127.0.0.1", 0)
        port = tcp.sockets[0].getsockname()[1]
        try:
            async with httpx.AsyncClient(base_url=f"http://127.0.0.1:{port}", timeout=10) as client:
                # Health endpoint
                r = await client.get("/api/health")
                assert r.status_code == 200
                assert r.json()["status"] == "healthy"

                # Sources listing + registration
                r = await client.get("/api/sources")
                assert r.status_code == 200 and len(r.json()) >= 1
                r = await client.post("/api/sources", json={"url": "https://example.org/tales"})
                assert r.status_code == 200

                # Unknown route + bad body
                r = await client.get("/api/nope")
                assert r.status_code == 404
                r = await client.post("/api/tasks", content=b"not json")
                assert r.status_code == 400

                # Traversal-safe doc id handling
                r = await client.get("/api/folklore/..%2F..%2Fsecrets")
                assert r.status_code == 400

                # SSE: subscribe, then trigger an event via a task start
                events: list = []

                async def listen():
                    async with client.stream("GET", "/api/events") as sse:
                        async for chunk in sse.aiter_text():
                            for line in chunk.splitlines():
                                if line.startswith("data: "):
                                    events.append(json.loads(line[6:])["event_type"])
                                    if events[-1] == "task.started":
                                        return

                listener = asyncio.create_task(listen())
                await asyncio.sleep(0.1)
                await client.post("/api/tasks", json={"url": "https://127.0.0.1:1/x", "max_pages": 1, "depth": 0})
                await asyncio.wait_for(listener, timeout=10)
                assert "task.started" in events
        finally:
            tcp.close()
            await tcp.wait_closed()


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


class TestBrowserFallback:
    @staticmethod
    def _manager_with_html(tmp_path, html, extra=None):
        """Build a CrawlManager serving one fixed HTML page via MockTransport."""
        from app.crawler.manager import CrawlManager

        def handler(request: httpx.Request):
            if request.url.path == "/robots.txt":
                return httpx.Response(200, text="User-agent: *\nAllow: /\n")
            return httpx.Response(200, text=html, headers={"Content-Type": "text/html"})

        crawler_kwargs = {"delay_seconds": 0.0}
        if extra:
            crawler_kwargs.update(extra)
        settings = Settings(
            storage={"raw_dir": str(tmp_path / "raw")},
            crawler=crawler_kwargs,
        )
        transport = httpx.MockTransport(handler)
        return settings, transport

    @pytest.mark.asyncio
    async def test_js_shell_page_routes_to_browser(self, tmp_path, monkeypatch):
        """An SPA shell (<noscript> + empty root) must be re-rendered by the
        browser crawler; the post-JS HTML then flows through the pipeline."""
        from unittest.mock import AsyncMock

        from app.crawler.manager import CrawlManager

        shell = (
            '<!DOCTYPE html><html><head><title>App</title></head>'
            '<body><noscript>Enable JavaScript</noscript><div id="root"></div>'
            '<script src="/bundle.js"></script></body></html>'
        )
        settings, transport = self._manager_with_html(tmp_path, shell)

        rendered = AsyncMock(return_value="<html><body><p>Rendered story text</p></body></html>")
        monkeypatch.setattr(
            "app.crawler.browser.BrowserCrawler._render", rendered, raising=False
        )

        async with httpx.AsyncClient(transport=transport) as client:
            manager = CrawlManager(settings)
            results = await manager.crawl(
                seeds=["https://example.org/app"], max_pages=1, max_depth=0, client=client
            )
            await manager.browser_crawler.close()

        assert len(results) == 1
        assert results[0].is_success
        assert results[0].response_headers.get("x-rendered-by") == "browser"
        assert rendered.await_count == 1

    @pytest.mark.asyncio
    async def test_static_html_never_hits_browser(self, tmp_path, monkeypatch):
        """A normal static page must NOT trigger the browser fallback."""
        from unittest.mock import AsyncMock

        from app.crawler.manager import CrawlManager

        settings, transport = self._manager_with_html(tmp_path, FOLK_PAGE)
        rendered = AsyncMock(return_value="<html></html>")
        monkeypatch.setattr(
            "app.crawler.browser.BrowserCrawler._render", rendered, raising=False
        )

        async with httpx.AsyncClient(transport=transport) as client:
            manager = CrawlManager(settings)
            results = await manager.crawl(
                seeds=["https://example.org/static"], max_pages=1, max_depth=0, client=client
            )
            await manager.browser_crawler.close()

        assert len(results) == 1 and results[0].is_success
        assert rendered.await_count == 0


class TestRobotsFailClosed:
    @pytest.mark.asyncio
    async def test_robots_fetch_failure_disallows(self, tmp_path, monkeypatch):
        """When robots.txt cannot be fetched (500/exception), the crawler must
        NOT crawl the host — fail closed instead of the old allow-all behavior."""
        from app.crawler.robots import RobotsManager

        def handler(request: httpx.Request):
            if request.url.path == "/robots.txt":
                return httpx.Response(500, text="boom")
            return httpx.Response(200, text="<html>content</html>", headers={"Content-Type": "text/html"})

        settings = Settings()
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as client:
            robots = RobotsManager(settings)
            allowed = await robots.is_allowed("https://example.org/page", client=client)

        assert allowed is False


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
