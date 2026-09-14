"""Metadata extractor for OpenGraph, schema.org, and Dublin Core tags."""

from typing import Any, Dict, Optional
from bs4 import BeautifulSoup


class MetadataExtractor:
    """Extracts semantic metadata, authors, publication dates, and licenses from HTML meta tags."""

    def extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract structured metadata from HTML head and meta tags."""
        metadata: Dict[str, Any] = {}

        # OpenGraph & standard meta tags
        for meta in soup.find_all("meta"):
            name = meta.get("name", "") or meta.get("property", "")
            content = meta.get("content", "")
            if name and content:
                metadata[name.lower()] = content

        return metadata

    def extract_author(self, metadata: Dict[str, Any], soup: BeautifulSoup) -> Optional[str]:
        """Infer author name from metadata or bylines."""
        for key in ["author", "article:author", "dc.creator", "twitter:creator"]:
            if key in metadata:
                return metadata[key]
        return None
