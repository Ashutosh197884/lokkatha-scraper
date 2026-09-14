"""Folklore content classifier based on keyword and narrative pattern heuristics."""

import re
from typing import Set
from app.config.logging import get_logger
from app.schemas.folklore import ClassificationResult, FolkloreType

logger = get_logger("folklore.classifier")

FOLKLORE_KEYWORDS: Set[str] = {
    "folktale", "folklore", "legend", "myth", "mythology", "fable",
    "fairy tale", "ballad", "oral tradition", "tales of", "story of",
    "lokkatha", "lok katha", "janapada", "panchatantra", "jataka",
    "hitopadesha", "baital pachisi", "singhasan battisi", "akbar birbal",
    "tenali raman", "thakurmar jhuli", "burhi aair sadhu", "yakshi"
}


class FolkloreClassifier:
    """Heuristic and rule-based classifier to identify folklore content."""

    def classify(self, text: str, title: str = "") -> ClassificationResult:
        """Evaluate whether the content represents folklore."""
        combined = f"{title}\n{text}".lower()
        keyword_matches = [kw for kw in FOLKLORE_KEYWORDS if re.search(r"\b" + re.escape(kw) + r"\b", combined)]

        confidence = min(0.3 + (0.15 * len(keyword_matches)), 0.95)
        is_folklore = len(keyword_matches) > 0 or "once upon a time" in combined

        folklore_type = FolkloreType.FOLKTALE
        if "myth" in combined:
            folklore_type = FolkloreType.MYTH
        elif "legend" in combined:
            folklore_type = FolkloreType.LEGEND
        elif "fable" in combined or "panchatantra" in combined:
            folklore_type = FolkloreType.FABLE
        elif "song" in combined or "ballad" in combined:
            folklore_type = FolkloreType.FOLK_SONG

        return ClassificationResult(
            is_folklore=is_folklore,
            confidence=confidence if is_folklore else 0.1,
            type=folklore_type,
            oral_tradition=True,
        )
