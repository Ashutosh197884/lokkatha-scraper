"""Level 2 Deduplication: Exact content hashing with SHA-256."""

from typing import Set, Union
from app.utils.hashing import compute_sha256


class ExactContentDeduplicator:
    """Detects identical articles or texts using SHA-256 content hashes."""

    def __init__(self) -> None:
        self._seen_hashes: Set[str] = set()

    def is_duplicate(self, content: Union[str, bytes]) -> bool:
        """Check if identical content hash has been seen."""
        h = compute_sha256(content)
        return h in self._seen_hashes

    def add(self, content: Union[str, bytes]) -> tuple[bool, str]:
        """Register content hash. Returns (is_new, content_hash)."""
        h = compute_sha256(content)
        if h in self._seen_hashes:
            return False, h
        self._seen_hashes.add(h)
        return True, h
