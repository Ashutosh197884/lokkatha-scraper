"""Crawler subsystem modules (HTTP, Browser, Frontier, Robots, Rate Limiter)."""

from typing import Protocol
from app.schemas.crawl import CrawlResult


class BaseCrawler(Protocol):
    """Abstract interface for page crawlers."""
    async def fetch(self, url: str) -> CrawlResult:
        ...
