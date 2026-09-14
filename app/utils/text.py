"""Text cleaning, extraction, and normalization utilities."""

import re
from typing import List


def clean_whitespace(text: str) -> str:
    """Normalize internal whitespace and strip leading/trailing spaces."""
    if not text:
        return ""
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    combined = "\n".join(lines)
    # Collapse multiple blank lines into double newline
    combined = re.sub(r"\n\s*\n+", "\n\n", combined)
    return combined.strip()


def extract_paragraphs(text: str) -> List[str]:
    """Split text into distinct non-empty paragraphs."""
    if not text:
        return []
    cleaned = clean_whitespace(text)
    paragraphs = cleaned.split("\n\n")
    return [p.strip() for p in paragraphs if p.strip()]


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """Truncate text to max_length without cutting words in half when possible."""
    if not text or len(text) <= max_length:
        return text or ""
    truncated = text[: max_length - len(suffix)].rsplit(" ", 1)[0]
    return truncated + suffix


def count_words(text: str) -> int:
    """Count words in a text string."""
    if not text:
        return 0
    return len(re.findall(r"\b\w+\b", text))
