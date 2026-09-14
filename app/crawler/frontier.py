"""URL Frontier managing crawl queues, priority ordering, deduplication, and policy enforcement."""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple
from app.config.logging import get_logger
from app.crawler.domain_filter import DomainFilter
from app.schemas.crawl import CrawlStatus, URLFrontierItem
from app.utils.urls import extract_domain, is_valid_url, normalize_url

logger = get_logger("crawler.frontier")


class URLFrontier:
    """
    Manages the crawling frontier:
    - Normalizes URLs and avoids duplicate queuing (Level 1 deduplication)
    - Enforces max depth boundaries
    - Integrates domain allow/deny filtering
    - Dispatches items by priority and depth
    - Tracks item lifecycle statuses and statistics
    """

    def __init__(
        self,
        domain_filter: Optional[DomainFilter] = None,
        max_depth: int = 4,
    ) -> None:
        self.domain_filter = domain_filter or DomainFilter()
        self.max_depth = max_depth
        self._queue: List[URLFrontierItem] = []
        self._seen_urls: Set[str] = set()
        self._items_by_url: Dict[str, URLFrontierItem] = {}
        self._lock = asyncio.Lock()

        # Metrics counters
        self.metrics = {
            "discovered": 0,
            "queued": 0,
            "duplicate": 0,
            "rejected_domain": 0,
            "max_depth_exceeded": 0,
            "invalid_url": 0,
            "fetched": 0,
            "failed": 0,
            "blocked": 0,
        }

    async def add_url(
        self,
        url: str,
        depth: int = 0,
        priority: float = 0.5,
        discovered_from: Optional[str] = None
    ) -> Tuple[bool, CrawlStatus, Optional[str]]:
        """
        Add a URL to the frontier after normalization, deduplication, and domain checks.
        Returns (is_queued, status, reason).
        """
        if not is_valid_url(url):
            async with self._lock:
                self.metrics["discovered"] += 1
                self.metrics["invalid_url"] += 1
            return False, CrawlStatus.REJECTED, "invalid_url"

        norm_url = normalize_url(url)
        domain = extract_domain(norm_url)

        async with self._lock:
            self.metrics["discovered"] += 1

            # Check for duplicate
            if norm_url in self._seen_urls:
                self.metrics["duplicate"] += 1
                logger.debug("frontier_duplicate_url", url=norm_url)
                return False, CrawlStatus.DUPLICATE, "already_seen"

            # Check max depth
            if depth > self.max_depth:
                self.metrics["max_depth_exceeded"] += 1
                logger.debug("frontier_depth_exceeded", url=norm_url, depth=depth, max_depth=self.max_depth)
                return False, CrawlStatus.REJECTED, f"depth_{depth}_exceeds_max_{self.max_depth}"

            # Check domain policy
            allowed, reason = self.domain_filter.is_allowed(norm_url)
            if not allowed:
                self.metrics["rejected_domain"] += 1
                logger.debug("frontier_domain_rejected", url=norm_url, reason=reason)
                return False, CrawlStatus.REJECTED, reason or "domain_policy_disallowed"

            item = URLFrontierItem(
                url=url,
                normalized_url=norm_url,
                domain=domain,
                depth=depth,
                priority=priority,
                status=CrawlStatus.QUEUED,
                discovered_from=discovered_from,
            )

            self._seen_urls.add(norm_url)
            self._items_by_url[norm_url] = item
            self._queue.append(item)
            self.metrics["queued"] += 1

            # Sort queue: higher priority first, then shallower depth
            self._queue.sort(key=lambda x: (x.priority, -x.depth), reverse=True)
            return True, CrawlStatus.QUEUED, None

    async def add_urls(
        self,
        urls: List[str],
        depth: int = 0,
        priority: float = 0.5,
        discovered_from: Optional[str] = None
    ) -> int:
        """Add multiple URLs in bulk. Returns count of successfully queued URLs."""
        queued_count = 0
        for u in urls:
            success, _, _ = await self.add_url(u, depth=depth, priority=priority, discovered_from=discovered_from)
            if success:
                queued_count += 1
        return queued_count

    async def next_url(self) -> Optional[URLFrontierItem]:
        """Fetch the next available queued item and mark status as FETCHING."""
        async with self._lock:
            for item in self._queue:
                if item.status == CrawlStatus.QUEUED:
                    item.status = CrawlStatus.FETCHING
                    item.attempts += 1
                    item.last_attempt_at = datetime.now(timezone.utc).isoformat()
                    return item
            return None

    async def mark_status(
        self,
        normalized_url: str,
        status: CrawlStatus,
        error_message: Optional[str] = None
    ) -> None:
        """Update status and record metrics for a processed URL item."""
        async with self._lock:
            item = self._items_by_url.get(normalized_url)
            if item:
                item.status = status
                if error_message:
                    item.error_message = error_message

                if status == CrawlStatus.FETCHED:
                    self.metrics["fetched"] += 1
                elif status == CrawlStatus.FAILED:
                    self.metrics["failed"] += 1
                elif status == CrawlStatus.BLOCKED:
                    self.metrics["blocked"] += 1

    def is_empty(self) -> bool:
        """Return True if there are no pending queued URLs."""
        return not any(item.status == CrawlStatus.QUEUED for item in self._queue)

    def total_seen(self) -> int:
        """Return count of unique URLs registered."""
        return len(self._seen_urls)

    def get_stats(self) -> Dict[str, int]:
        """Return snapshot of frontier operational statistics."""
        return dict(self.metrics)
