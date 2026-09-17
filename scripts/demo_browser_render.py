"""Runnable demo: proves the crawler renders JavaScript-only pages with real Chrome.

Serves a local SPA shell (empty <div id="root"> + <noscript>), crawls it through
CrawlManager, and asserts the returned content was produced by JavaScript —
i.e., the browser fallback fired and rendered what plain HTTP cannot see.

Run:  python scripts/demo_browser_render.py
"""

import asyncio
import http.server
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # allow direct script run

SHELL_PAGE = """<!DOCTYPE html>
<html>
<head><title>JS Folk Tales</title></head>
<body>
  <noscript>This archive requires JavaScript.</noscript>
  <div id="root"></div>
  <script>
    document.getElementById('root').innerHTML =
      '<h1>The Parrot and the Mynah</h1><p>Rendered by JavaScript at load time: '
      + new Date().toISOString() + '</p>';
  </script>
</body>
</html>
"""


class ShellHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 — stdlib API
        body = SHELL_PAGE.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # silence request logging
        pass


async def main() -> int:
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), ShellHandler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()

    from httpx import AsyncClient

    from app.config.settings import Settings
    from app.crawler.manager import CrawlManager

    settings = Settings(
        crawler={"delay_seconds": 0.0, "max_depth": 0, "concurrency": 1},
    )
    try:
        async with AsyncClient(timeout=30) as client:
            manager = CrawlManager(settings)
            try:
                results = await manager.crawl(
                    seeds=[f"http://127.0.0.1:{port}/"],
                    max_pages=1,
                    max_depth=0,
                    client=client,
                )
            finally:
                await manager.browser_crawler.close()

        result = results[0]
        rendered_via_browser = result.response_headers.get("x-rendered-by") == "browser"
        raw_html = ""
        if result.raw_html_path:
            raw_html = open(result.raw_html_path, encoding="utf-8", errors="replace").read()

        print(f"success:            {result.is_success}")
        print(f"rendered_by:        {'browser (real Chrome/Chromium)' if rendered_via_browser else 'plain HTTP'}")
        print(f"js content visible: {'The Parrot and the Mynah' in raw_html}")

        assert result.is_success, f"crawl failed: {result.error}"
        assert rendered_via_browser, "browser fallback did not fire on the JS shell"
        assert "The Parrot and the Mynah" in raw_html, "JavaScript-rendered text missing"
        print("\nOK: JavaScript-only page was rendered by the browser crawler.")
        return 0
    finally:
        server.shutdown()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
