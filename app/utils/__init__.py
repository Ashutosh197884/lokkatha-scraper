"""Lokkatha utility functions."""

from app.utils.urls import (
    extract_domain,
    extract_hostname,
    is_valid_url,
    normalize_url,
    resolve_relative_url,
)
from app.utils.hashing import (
    compute_sha256,
    compute_url_hash,
    generate_canonical_id,
)
from app.utils.text import (
    clean_whitespace,
    extract_paragraphs,
    truncate_text,
    count_words,
)

__all__ = [
    "extract_domain",
    "extract_hostname",
    "is_valid_url",
    "normalize_url",
    "resolve_relative_url",
    "compute_sha256",
    "compute_url_hash",
    "generate_canonical_id",
    "clean_whitespace",
    "extract_paragraphs",
    "truncate_text",
    "count_words",
]
