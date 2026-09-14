"""Per-domain rate limiter and politeness scheduler."""

import asyncio
import time
from typing import Dict, Optional
from app.config.logging import get_logger
from app.utils.urls import extract_domain

logger = get_logger("crawler.rate_limiter")


class RateLimiter:
    """Enforces polite delays between requests to the same domain while allowing multi-domain concurrency."""

    def __init__(self, default_delay: float = 1.0) -> None:
        self.default_delay = default_delay
        self._last_access: Dict[str, float] = {}
        self._domain_locks: Dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
        self._custom_delays: Dict[str, float] = {}

    async def _get_domain_lock(self, domain: str) -> asyncio.Lock:
        """Get or create an async lock dedicated to a domain."""
        async with self._global_lock:
            if domain not in self._domain_locks:
                self._domain_locks[domain] = asyncio.Lock()
            return self._domain_locks[domain]

    def set_domain_delay(self, domain: str, delay_seconds: float) -> None:
        """Override the delay for a specific domain."""
        self._custom_delays[domain.lower()] = max(0.0, delay_seconds)

    async def wait(self, url: str) -> float:
        """
        Wait if necessary to observe the required delay for the target domain.
        Returns the actual time slept in seconds.
        """
        domain = extract_domain(url)
        if not domain:
            return 0.0

        domain_lock = await self._get_domain_lock(domain)
        async with domain_lock:
            now = time.time()
            last = self._last_access.get(domain, 0.0)
            required_delay = self._custom_delays.get(domain, self.default_delay)

            elapsed = now - last
            slept = 0.0
            if elapsed < required_delay:
                slept = required_delay - elapsed
                logger.debug("rate_limit_delay", domain=domain, wait_seconds=slept)
                await asyncio.sleep(slept)

            self._last_access[domain] = time.time()
            return slept
