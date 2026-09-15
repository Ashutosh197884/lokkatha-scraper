"""PDF document parser and page-level text extractor for folkloric surveys and papers."""

import re
from typing import Any, Dict, List, Optional
from app.config.logging import get_logger

logger = get_logger("discovery.pdf")


class PDFExtractResult:
    """Preserved PDF text extraction result with page-level provenance."""

    def __init__(
        self,
        url: str,
        title: str = "",
        author: Optional[str] = None,
        page_count: int = 1,
        pages: Optional[List[str]] = None,
        full_text: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.url = url
        self.title = title
        self.author = author
        self.page_count = page_count
        self.pages = pages or []
        self.full_text = full_text
        self.metadata = metadata or {}


class PDFExtractor:
    """Extracts raw text, title, author, and page-level passages from PDF files or stream payloads."""

    def extract_from_text_stream(self, text_content: str, url: str) -> PDFExtractResult:
        """Parse structured text representation of a PDF document."""
        # Split on page breaks if present
        pages = re.split(r"(?:--- Page \d+ ---|\f|\n\s*\n\s*\[Page \d+\]\s*\n)", text_content)
        clean_pages = [p.strip() for p in pages if p.strip()]
        if not clean_pages:
            clean_pages = [text_content.strip()]

        # Heuristic title detection (first non-empty line)
        first_lines = [l.strip() for l in clean_pages[0].split("\n") if l.strip()]
        title = first_lines[0] if first_lines else "PDF Document"

        # Heuristic author detection
        author = None
        for line in first_lines[1:5]:
            if line.lower().startswith("by ") or "author" in line.lower():
                author = line.replace("by ", "").replace("By ", "").strip()
                break

        return PDFExtractResult(
            url=url,
            title=title,
            author=author,
            page_count=len(clean_pages),
            pages=clean_pages,
            full_text="\n\n".join(clean_pages),
        )
