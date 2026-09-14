"""Tests for URL, hashing, and text utility functions."""

from app.utils.hashing import compute_sha256, compute_url_hash, generate_canonical_id
from app.utils.text import clean_whitespace, count_words, extract_paragraphs, truncate_text
from app.utils.urls import (
    extract_domain,
    extract_hostname,
    is_valid_url,
    normalize_url,
    resolve_relative_url,
)


def test_normalize_url_tracking_and_fragments():
    """Test URL normalization stripping fragments, tracking params, and default ports."""
    url = "HTTPS://Example.COM:443/Story/?utm_source=twitter&id=10&utm_medium=social#chapter-1"
    normalized = normalize_url(url)
    assert normalized == "https://example.com/story?id=10"


def test_normalize_url_trailing_slash():
    """Test trailing slash normalization."""
    assert normalize_url("https://example.org/folklore/") == "https://example.org/folklore"
    assert normalize_url("https://example.org/") == "https://example.org/"


def test_normalize_url_query_sorting():
    """Test query parameter sorting for deterministic comparison."""
    url1 = "https://example.org/story?b=2&a=1"
    url2 = "https://example.org/story?a=1&b=2"
    assert normalize_url(url1) == normalize_url(url2)
    assert normalize_url(url1) == "https://example.org/story?a=1&b=2"


def test_extract_domain():
    """Test domain extraction."""
    assert extract_domain("https://subdomain.example.gov.in/stories") == "example.gov.in"
    assert extract_domain("http://ignca.gov.in/path") == "ignca.gov.in"


def test_is_valid_url():
    """Test URL validation."""
    assert is_valid_url("https://example.org/story") is True
    assert is_valid_url("http://localhost:8000/test") is True
    assert is_valid_url("ftp://example.org/file") is False
    assert is_valid_url("javascript:void(0)") is False
    assert is_valid_url("") is False


def test_resolve_relative_url():
    """Test relative URL resolution."""
    base = "https://example.org/folklore/index.html"
    relative = "story1.html"
    assert resolve_relative_url(base, relative) == "https://example.org/folklore/story1.html"

    root_relative = "/about.html"
    assert resolve_relative_url(base, root_relative) == "https://example.org/about.html"


def test_compute_sha256():
    """Test SHA-256 calculation."""
    text = "Princess Mumal of Lodrawa"
    h1 = compute_sha256(text)
    h2 = compute_sha256(text.encode("utf-8"))
    assert h1 == h2
    assert len(h1) == 64


def test_generate_canonical_id():
    """Test deterministic canonical ID generation."""
    id1 = generate_canonical_id("The Legend of Mumal", region=["Rajasthan"])
    id2 = generate_canonical_id("the legend of mumal", region=["Rajasthan"])
    assert id1 == id2
    assert id1.startswith("folk-the-legend-of-mumal-")


def test_text_utilities():
    """Test whitespace cleaning, paragraph extraction, and truncation."""
    raw = "  Once upon   a time. \n\n In the desert.   \n\n\n\n There lived a king.  "
    cleaned = clean_whitespace(raw)
    assert cleaned == "Once upon a time.\n\nIn the desert.\n\nThere lived a king."

    paras = extract_paragraphs(raw)
    assert len(paras) == 3
    assert paras[0] == "Once upon a time."

    assert count_words("Once upon a time in Rajasthan") == 6
    assert truncate_text("A very long folktale narrative text", max_length=15) == "A very long..."
