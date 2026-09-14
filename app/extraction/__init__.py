"""Content extraction and document cleaning modules."""

from typing import Optional, Protocol
from pydantic import BaseModel


class ExtractedDocument(BaseModel):
    """Raw parsed document container."""
    title: str = ""
    author: Optional[str] = None
    published_date: Optional[str] = None
    clean_text: str = ""
    raw_html: str = ""
    language: Optional[str] = None


class ContentExtractor(Protocol):
    """Protocol for document content extractors."""
    def extract(self, html: str, url: str) -> ExtractedDocument:
        ...
