"""Rule-based and LLM-ready structured folklore extractor."""

from typing import Optional
from app.config.logging import get_logger
from app.schemas.folklore import FolkloreDocument, FolkloreType
from app.schemas.source import SourceInfo
from app.utils.hashing import generate_canonical_id
from app.utils.text import clean_whitespace, truncate_text

logger = get_logger("folklore.extractor")


class BaselineFolkloreExtractor:
    """Baseline heuristic extractor (operates without requiring an LLM)."""

    def extract(self, text: str, source: SourceInfo, title: Optional[str] = None) -> FolkloreDocument:
        """Extract baseline structured folklore entity from text and source metadata."""
        clean_text = clean_whitespace(text)
        doc_title = title or source.page_title or "Untitled Folklore"
        summary = truncate_text(clean_text, 300)
        doc_id = generate_canonical_id(doc_title, region=[])

        return FolkloreDocument(
            id=doc_id,
            title=doc_title,
            story=clean_text,
            summary=summary,
            source=source,
            folklore_type=FolkloreType.FOLKTALE,
            oral_tradition=True,
            confidence={"baseline_extraction": 0.6},
        )
