"""Asynchronous HTTP crawler client using httpx with content validation and size limits."""

from pathlib import Path
from typing import Optional, Set
import httpx

from app.config.logging import get_logger
from app.config.settings import Settings, get_settings
from app.crawler.retry import RETRYABLE_HTTP_STATUSES, RetryableHTTPStatusError, retry_with_backoff
from app.schemas.crawl import CrawlResult
from app.utils.hashing import compute_sha256
from app.utils.urls import extract_domain, normalize_url

logger = get_logger("crawler.http_client")

# Permitted MIME types for text and web document crawling
ACCEPTED_CONTENT_TYPES: Set[str] = {
    "text/html",
    "application/xhtml+xml",
    "text/plain",
    "application/xml",
    "text/xml",
}

# Explicitly rejected binary resource extensions and MIME types
REJECTED_EXTENSIONS: Set[str] = {
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico",
    ".mp3", ".mp4", ".wav", ".avi", ".mkv", ".mov", ".zip", ".tar",
    ".gz", ".rar", ".7z", ".exe", ".bin", ".dmg", ".iso", ".doc",
    ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".css", ".js", ".json"
}


class HTTPCrawler:
    """Asynchronous HTTP crawler with Content-Type filtering, size enforcement, and retries."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.headers = {
            "User-Agent": self.settings.crawler.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        }
        self.max_bytes = int(self.settings.crawler.max_content_size_mb * 1024 * 1024)
        self.raw_dir = Path(self.settings.storage.raw_dir)
        if self.settings.crawler.save_raw_html:
            self.raw_dir.mkdir(parents=True, exist_ok=True)

    def is_binary_url(self, url: str) -> bool:
        """Check if URL path ends with an unsupported binary file extension."""
        path = normalize_url(url).lower().split("?")[0].split("#")[0]
        return any(path.endswith(ext) for ext in REJECTED_EXTENSIONS)

    async def fetch(
        self,
        url: str,
        client: Optional[httpx.AsyncClient] = None
    ) -> CrawlResult:
        """Fetch a webpage via HTTP GET with validation, size check, retries, and persistence."""
        norm_url = normalize_url(url)
        domain = extract_domain(norm_url)

        # Pre-check URL extension
        if self.is_binary_url(norm_url):
            logger.debug("rejected_binary_url", url=norm_url)
            return CrawlResult(
                url=url,
                normalized_url=norm_url,
                domain=domain,
                is_success=False,
                error="rejected_binary_extension",
            )

        should_close_client = False
        if client is None:
            client = httpx.AsyncClient(
                timeout=self.settings.crawler.request_timeout,
                follow_redirects=True,
                headers=self.headers,
            )
            should_close_client = True

        async def _execute_request() -> CrawlResult:
            response = await client.get(norm_url)

            # Escalate transient HTTP statuses (429/5xx) so retry_with_backoff can kick in.
            if response.status_code in RETRYABLE_HTTP_STATUSES:
                raise RetryableHTTPStatusError(response.status_code)

            content_type_header = response.headers.get("content-type", "").lower()
            mime_type = content_type_header.split(";")[0].strip()

            # Reject non-HTML/text content types
            if mime_type and not any(mime_type.startswith(accepted) for accepted in ACCEPTED_CONTENT_TYPES):
                logger.debug("rejected_content_type", url=norm_url, content_type=content_type_header)
                return CrawlResult(
                    url=url,
                    normalized_url=norm_url,
                    domain=domain,
                    status_code=response.status_code,
                    content_type=content_type_header,
                    response_headers=dict(response.headers),
                    is_success=False,
                    error=f"unsupported_content_type:{mime_type}",
                )

            # Check content length header if present
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > self.max_bytes:
                logger.warning("content_length_exceeded", url=norm_url, size=content_length, max=self.max_bytes)
                return CrawlResult(
                    url=url,
                    normalized_url=norm_url,
                    domain=domain,
                    status_code=response.status_code,
                    content_type=content_type_header,
                    response_headers=dict(response.headers),
                    is_success=False,
                    error=f"max_content_size_exceeded:{content_length}",
                )

            body_bytes = response.content
            if len(body_bytes) > self.max_bytes:
                return CrawlResult(
                    url=url,
                    normalized_url=norm_url,
                    domain=domain,
                    status_code=response.status_code,
                    content_type=content_type_header,
                    response_headers=dict(response.headers),
                    is_success=False,
                    error=f"max_content_size_exceeded:{len(body_bytes)}",
                )

            body_text = response.text
            content_hash = compute_sha256(body_bytes)

            raw_path = None
            if self.settings.crawler.save_raw_html and response.is_success:
                raw_file = self.raw_dir / f"{content_hash}.html"
                try:
                    with open(raw_file, "w", encoding="utf-8", errors="replace") as f:
                        f.write(body_text)
                    raw_path = str(raw_file)
                except Exception as save_err:
                    logger.warning("failed_to_save_raw_html", path=str(raw_file), error=str(save_err))

            return CrawlResult(
                url=url,
                normalized_url=norm_url,
                domain=domain,
                status_code=response.status_code,
                content_type=content_type_header,
                response_headers=dict(response.headers),
                raw_html_path=raw_path,
                content_hash=content_hash,
                is_success=response.is_success,
                error=None if response.is_success else f"http_status_{response.status_code}",
            )

        try:
            return await retry_with_backoff(_execute_request, max_retries=3, initial_delay=1.0)
        except RetryableHTTPStatusError as exc:
            logger.warning("http_crawl_retries_exhausted", url=norm_url, status=exc.status_code)
            return CrawlResult(
                url=url,
                normalized_url=norm_url,
                domain=domain,
                status_code=exc.status_code,
                is_success=False,
                error=f"http_status_{exc.status_code}_retries_exhausted",
            )
        except Exception as exc:
            logger.warning("http_crawl_failed", url=norm_url, error=str(exc))
            return CrawlResult(
                url=url,
                normalized_url=norm_url,
                domain=domain,
                is_success=False,
                error=str(exc),
            )
        finally:
            if should_close_client:
                await client.aclose()
