"""Hashing, checksum, and canonical ID generation utilities."""

import hashlib
import re
from typing import List, Optional, Union
from app.utils.urls import normalize_url


def compute_sha256(content: Union[str, bytes]) -> str:
    """Compute SHA-256 hexadecimal hash of string or byte content."""
    if isinstance(content, str):
        content_bytes = content.encode("utf-8")
    else:
        content_bytes = content
    return hashlib.sha256(content_bytes).hexdigest()


def compute_url_hash(url: str) -> str:
    """Compute deterministic SHA-256 hash of a normalized URL."""
    normalized = normalize_url(url)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def generate_canonical_id(
    title: str,
    region: Optional[Union[str, List[str]]] = None,
    tradition: Optional[str] = None
) -> str:
    """
    Generate a deterministic canonical identifier for a folklore entry.
    Format: slugified_title-[region_or_tradition_hash]
    """
    cleaned_title = re.sub(r"[^\w\s-]", "", title.lower()).strip()
    slug = re.sub(r"[-\s]+", "-", cleaned_title)[:40]

    components = [slug]
    if isinstance(region, list) and region:
        components.append("-".join(sorted(r.lower().strip() for r in region)))
    elif isinstance(region, str) and region:
        components.append(region.lower().strip())

    if tradition:
        components.append(tradition.lower().strip())

    raw_key = ":".join(components)
    short_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:8]
    return f"folk-{slug}-{short_hash}"
