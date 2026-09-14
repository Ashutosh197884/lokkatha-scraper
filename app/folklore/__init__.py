"""Folklore classification, structured extraction, and traditional knowledge analysis."""

from typing import Protocol
from app.schemas.folklore import ClassificationResult, FolkloreDocument
from app.schemas.source import SourceInfo


class FolkloreExtractorInterface(Protocol):
    """Abstract protocol for folklore extraction engines."""
    async def extract(self, text: str, source: SourceInfo) -> FolkloreDocument:
        ...
