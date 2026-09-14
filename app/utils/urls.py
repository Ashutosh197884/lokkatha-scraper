"""URL processing, normalization, and validation utilities."""

import re
from typing import Set
from urllib.parse import (
    parse_qsl,
    urlencode,
    urljoin,
    urlparse,
    urlunparse,
)
import tldextract

# Standard tracking and analytics query parameter keys to discard
TRACKING_PARAMS: Set[str] = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "utm_id",
    "fbclid",
    "gclid",
    "gclsrc",
    "dclid",
    "msclkid",
    "mc_cid",
    "mc_eid",
    "_ga",
    "_gl",
    "_hsenc",
    "_hsmi",
    "ref",
    "source",
    "fb_action_ids",
    "fb_action_types",
    "fb_source",
    "action_object_map",
    "action_type_map",
    "action_ref_map",
}


def extract_domain(url: str) -> str:
    """Extract registered domain or hostname (e.g., 'example.org' from 'https://sub.example.org/path')."""
    try:
        extracted = tldextract.extract(url)
        if hasattr(extracted, "top_domain_under_public_suffix") and extracted.top_domain_under_public_suffix:
            return extracted.top_domain_under_public_suffix.lower()
        if extracted.domain and extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}".lower()
        parsed = urlparse(url)
        return parsed.hostname.lower() if parsed.hostname else ""
    except Exception:
        parsed = urlparse(url)
        return parsed.hostname.lower() if parsed.hostname else ""


def extract_hostname(url: str) -> str:
    """Extract full hostname (e.g., 'sub.example.org')."""
    try:
        parsed = urlparse(url)
        return parsed.hostname.lower() if parsed.hostname else ""
    except Exception:
        return ""


def is_valid_url(url: str) -> bool:
    """Check if the string is a valid HTTP/HTTPS URL."""
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def normalize_url(url: str, strip_tracking: bool = True, lowercase_path: bool = True) -> str:
    """
    Normalize a URL for deduplication and crawling:
    - Normalizes scheme and netloc to lowercase
    - Removes default ports (80 for http, 443 for https)
    - Strips URL fragments (#anchor)
    - Removes known marketing tracking parameters (utm_*, fbclid, etc.)
    - Sorts and standardizes query parameters
    - Normalizes path (collapses consecutive slashes, removes trailing slash unless root)
    """
    if not url:
        return ""

    url = url.strip()
    parsed = urlparse(url)

    if not parsed.scheme or not parsed.netloc:
        return url

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    # Remove default port
    if scheme == "http" and netloc.endswith(":80"):
        netloc = netloc[:-3]
    elif scheme == "https" and netloc.endswith(":443"):
        netloc = netloc[:-4]

    # Normalize path
    path = parsed.path or "/"
    if lowercase_path:
        path = path.lower()
    # Collapse multiple slashes into single slash
    path = re.sub(r"/+", "/", path)
    # Strip trailing slash if path length > 1
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]

    # Clean query parameters
    query = ""
    if parsed.query:
        query_pairs = parse_qsl(parsed.query, keep_blank_values=False)
        cleaned_pairs = []
        for key, value in query_pairs:
            key_lower = key.lower()
            if strip_tracking and (key_lower in TRACKING_PARAMS or key_lower.startswith("utm_")):
                continue
            cleaned_pairs.append((key, value))

        # Sort query pairs for deterministic deduplication
        cleaned_pairs.sort(key=lambda x: x[0])
        if cleaned_pairs:
            query = urlencode(cleaned_pairs)

    # Fragments are stripped for canonical crawl URLs
    fragment = ""

    return urlunparse((scheme, netloc, path, parsed.params, query, fragment))


def resolve_relative_url(base_url: str, relative_url: str) -> str:
    """Resolve a relative URL against a base URL."""
    if not relative_url:
        return ""
    joined = urljoin(base_url, relative_url.strip())
    return normalize_url(joined)
