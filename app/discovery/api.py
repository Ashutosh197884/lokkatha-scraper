"""Public API and JSON endpoint discoverer."""

from typing import Any, Dict, List, Optional
import httpx

from app.config.logging import get_logger

logger = get_logger("discovery.api")


class APIDiscoverer:
    """Discovers folkloric documents and records from public JSON APIs."""

    def __init__(self, timeout: float = 15.0) -> None:
        self.timeout = timeout

    async def fetch_json(
        self,
        endpoint_url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        client: Optional[httpx.AsyncClient] = None,
    ) -> Optional[Dict[str, Any]]:
        """Fetch JSON payload from public endpoint."""
        logger.info("fetching_api_endpoint", endpoint=endpoint_url)
        should_close = False
        if client is None:
            client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
            should_close = True

        try:
            resp = await client.get(endpoint_url, params=params, headers=headers)
            if resp.status_code == 200:
                return resp.json()
            logger.warning("api_request_failed", endpoint=endpoint_url, status=resp.status_code)
            return None
        except Exception as exc:
            logger.warning("api_request_error", endpoint=endpoint_url, error=str(exc))
            return None
        finally:
            if should_close:
                await client.aclose()

    def extract_urls_from_payload(self, data: Any) -> List[str]:
        """Recursively scan JSON response for public URLs."""
        urls: List[str] = []
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, str) and (v.startswith("http://") or v.startswith("https://")):
                    urls.append(v)
                elif isinstance(v, (dict, list)):
                    urls.extend(self.extract_urls_from_payload(v))
        elif isinstance(data, list):
            for item in data:
                urls.extend(self.extract_urls_from_payload(item))
        return list(set(urls))
