"""Level 1 Deduplication: Canonical normalized URL hash tracking."""

from typing import Set
from app.utils.urls import normalize_url


class URLDeduplicator:
    """Detects previously encountered URLs using canonical URL normalization."""

    def __init__(self) -> None:
        self._seen_urls: Set[str] = set()

    def is_duplicate(self, url: str) -> bool:
        """Check if URL has already been registered."""
        norm = normalize_url(url)
        return norm in self._seen_urls

    def add(self, url: str) -> bool:
        """Register URL. Returns True if added, False if already seen."""
        norm = normalize_url(url)
        if norm in self._seen_urls:
            return False
        self._seen_urls.add(norm)
        return True
