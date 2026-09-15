"""Web discovery modules for sitemaps, feeds, APIs, PDFs, archives, and link extraction."""

from app.discovery.api import APIDiscoverer
from app.discovery.archive import ArchiveDiscoverer, ArchiveItem
from app.discovery.feed import FeedDiscoverer, FeedItem
from app.discovery.links import LinkExtractor
from app.discovery.pdf import PDFExtractor, PDFExtractResult
from app.discovery.registry import SourceRegistry, SourceRegistryEntry
from app.discovery.search import SearchDiscoverer
from app.discovery.sitemap import SitemapDiscoverer

__all__ = [
    "SourceRegistry",
    "SourceRegistryEntry",
    "SitemapDiscoverer",
    "FeedDiscoverer",
    "FeedItem",
    "APIDiscoverer",
    "PDFExtractor",
    "PDFExtractResult",
    "ArchiveDiscoverer",
    "ArchiveItem",
    "LinkExtractor",
    "SearchDiscoverer",
]
