"""Language detector for English and Indian regional languages."""

import re
from typing import Optional

# Script Unicode blocks
DEVANAGARI_RANGE = (0x0900, 0x097F)
BENGALI_RANGE = (0x0980, 0x09FF)
GURMUKHI_RANGE = (0x0A00, 0x0A7F)
GUJARATI_RANGE = (0x0A80, 0x0AFF)
ORIYA_RANGE = (0x0B00, 0x0B7F)
TAMIL_RANGE = (0x0B80, 0x0BFF)
TELUGU_RANGE = (0x0C00, 0x0C7F)
KANNADA_RANGE = (0x0C80, 0x0CFF)
MALAYALAM_RANGE = (0x0D00, 0x0D7F)


class LanguageDetector:
    """Detects primary language and script from text content."""

    def detect(self, text: str) -> Optional[str]:
        """Detect language code (e.g. 'en', 'hi', 'bn', 'ta', 'te')."""
        if not text:
            return None

        # Sample first 2000 characters
        sample = text[:2000]

        script_counts = {
            "hi": sum(1 for c in sample if DEVANAGARI_RANGE[0] <= ord(c) <= DEVANAGARI_RANGE[1]),
            "bn": sum(1 for c in sample if BENGALI_RANGE[0] <= ord(c) <= BENGALI_RANGE[1]),
            "pa": sum(1 for c in sample if GURMUKHI_RANGE[0] <= ord(c) <= GURMUKHI_RANGE[1]),
            "gu": sum(1 for c in sample if GUJARATI_RANGE[0] <= ord(c) <= GUJARATI_RANGE[1]),
            "or": sum(1 for c in sample if ORIYA_RANGE[0] <= ord(c) <= ORIYA_RANGE[1]),
            "ta": sum(1 for c in sample if TAMIL_RANGE[0] <= ord(c) <= TAMIL_RANGE[1]),
            "te": sum(1 for c in sample if TELUGU_RANGE[0] <= ord(c) <= TELUGU_RANGE[1]),
            "kn": sum(1 for c in sample if KANNADA_RANGE[0] <= ord(c) <= KANNADA_RANGE[1]),
            "ml": sum(1 for c in sample if MALAYALAM_RANGE[0] <= ord(c) <= MALAYALAM_RANGE[1]),
        }

        max_lang, max_count = max(script_counts.items(), key=lambda x: x[1])
        if max_count > 20:
            return max_lang

        # Check for Latin English
        latin_count = sum(1 for c in sample if c.isascii() and c.isalpha())
        if latin_count > 20:
            return "en"

        return "unknown"
