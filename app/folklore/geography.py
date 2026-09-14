"""Geographical entity resolution and Indian state/region mapping."""

from typing import List, Optional

INDIAN_STATES = {
    "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh",
    "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka",
    "kerala", "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram",
    "nagaland", "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu",
    "telangana", "tripura", "uttar pradesh", "uttarakhand", "west bengal",
    "ladakh", "jammu and kashmir",
}


class GeographyResolver:
    """Resolves regional identifiers and maps them to standard Indian administrative regions."""

    def detect_regions(self, text: str) -> List[str]:
        """Find mentioned states and cultural regions in text."""
        text_lower = text.lower()
        found: List[str] = []
        for state in INDIAN_STATES:
            if state in text_lower:
                found.append(state.title())
        return found
