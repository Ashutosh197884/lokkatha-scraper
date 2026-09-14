"""Three-level deduplication subsystem (URL, Exact SHA-256, Semantic similarity)."""

from typing import Protocol


class Deduplicator(Protocol):
    """Protocol for deduplication engines."""
    def is_duplicate(self, item: str) -> bool:
        ...
