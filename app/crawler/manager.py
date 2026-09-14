"""Crawl coordinator managing concurrent workers, frontier, robots, rate limiting, and link discovery."""

import asyncio
from typing import List, Optional
import httpx

from app.config.logging import get_logger
from app.config.settings import Settings, get_settings
from app.crawler.domain_filter import DomainFilter
from app.crawler.frontier import URLFrontier
from app.crawler.http_client import HTTPCrawler
from app.crawler.rate_limiter import RateLimiter
from app.crawler.robots import RobotsManager
from app.discovery.links import LinkExtractor
from app.schemas.crawl import CrawlResult, CrawlStatus

logger = get_logger("crawler.manager")


class CrawlManager:
    """Coordinates the asynchronous crawl loop across frontier, politeness controls, and fetchers."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        frontier: Optional[URLFrontier] = None,
        robots: Optional[RobotsManager] = None,
        rate_limiter: Optional[RateLimiter] = None,
        http_crawler: Optional[HTTPCrawler] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.domain_filter = DomainFilter(self.settings.domains)
        self.frontier = frontier or URLFrontier(
            domain_filter=self.domain_filter,
            max_depth=self.settings.crawler.max_depth,
        )
        self.robots = robots or RobotsManager(self.settings)
        self.rate_limiter = rate_limiter or RateLimiter(
            default_delay=self.settings.crawler.delay_seconds
        )
        self.http_crawler = http_crawler or HTTPCrawler(self.settings)
        self.link_extractor = LinkExtractor()

    async def _crawl_worker(
        self,
        worker_id: int,
        client: httpx.AsyncClient,
        results: List[CrawlResult],
        max_pages: int,
        max_depth: int,
        semaphore: asyncio.Semaphore,
        stop_event: asyncio.Event,
    ) -> None:
        """Individual asynchronous worker task."""
        while not stop_event.is_set():
            if len(results) >= max_pages:
                stop_event.set()
                break

            item = await self.frontier.next_url()
            if item is None:
                # Check if all frontier items processed
                if self.frontier.is_empty():
                    await asyncio.sleep(0.1)
                    if self.frontier.is_empty():
                        break
                await asyncio.sleep(0.05)
                continue

            async with semaphore:
                norm_url = item.normalized_url

                # Check robots.txt compliance
                is_allowed_by_robots = await self.robots.is_allowed(item.url, client=client)
                if not is_allowed_by_robots:
                    logger.info("url_blocked_by_robots", url=norm_url)
                    await self.frontier.mark_status(norm_url, CrawlStatus.BLOCKED, error_message="robots_txt_disallow")
                    continue

                # Rate limiting politeness wait
                await self.rate_limiter.wait(item.url)

                # Fetch page via HTTP
                result = await self.http_crawler.fetch(item.url, client=client)
                results.append(result)

                if result.is_success:
                    await self.frontier.mark_status(norm_url, CrawlStatus.FETCHED)

                    # Discover links if below max depth
                    if item.depth < max_depth and result.raw_html_path:
                        try:
                            with open(result.raw_html_path, "r", encoding="utf-8", errors="replace") as f:
                                html_content = f.read()

                            links = self.link_extractor.extract_from_html(
                                base_url=item.url,
                                html_content=html_content,
                                allow_external=self.settings.crawler.follow_external_links,
                            )
                            result.links_extracted = links

                            # Queue newly discovered child links
                            child_priority = max(0.1, round(item.priority * 0.85, 2))
                            await self.frontier.add_urls(
                                urls=links,
                                depth=item.depth + 1,
                                priority=child_priority,
                                discovered_from=norm_url,
                            )
                        except Exception as parse_err:
                            logger.warning("link_extraction_error", url=norm_url, error=str(parse_err))
                else:
                    await self.frontier.mark_status(norm_url, CrawlStatus.FAILED, error_message=result.error)

    async def crawl(
        self,
        seeds: Optional[List[str]] = None,
        max_pages: Optional[int] = None,
        max_depth: Optional[int] = None,
        client: Optional[httpx.AsyncClient] = None,
    ) -> List[CrawlResult]:
        """Execute full asynchronous crawl from provided seed URLs."""
        seeds = seeds or []
        limit = max_pages or self.settings.crawler.max_pages
        depth = max_depth if max_depth is not None else self.settings.crawler.max_depth
        concurrency = self.settings.crawler.concurrency

        # Seed the frontier
        for seed_url in seeds:
            await self.frontier.add_url(seed_url, depth=0, priority=1.0)

        logger.info(
            "crawl_run_started",
            seeds_count=len(seeds),
            max_pages=limit,
            max_depth=depth,
            concurrency=concurrency,
        )

        results: List[CrawlResult] = []
        semaphore = asyncio.Semaphore(concurrency)
        stop_event = asyncio.Event()

        should_close_client = False
        if client is None:
            client = httpx.AsyncClient(
                timeout=self.settings.crawler.request_timeout,
                headers={"User-Agent": self.settings.crawler.user_agent},
                follow_redirects=True,
            )
            should_close_client = True

        try:
            # Spawn worker pool
            workers = [
                asyncio.create_task(
                    self._crawl_worker(
                        worker_id=i,
                        client=client,
                        results=results,
                        max_pages=limit,
                        max_depth=depth,
                        semaphore=semaphore,
                        stop_event=stop_event,
                    )
                )
                for i in range(concurrency)
            ]

            await asyncio.gather(*workers)

        finally:
            if should_close_client:
                await client.aclose()

        stats = self.frontier.get_stats()
        logger.info(
            "crawl_run_completed",
            pages_crawled=len(results),
            successful=sum(1 for r in results if r.is_success),
            failed=sum(1 for r in results if not r.is_success),
            stats=stats,
        )
        return results
