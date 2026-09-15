"""Source Type Registry defining taxonomy, platform classification, and politeness parameters."""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from app.schemas.source import SourceInfo, SourceType


class SourceRegistryEntry:
    """Descriptor for a registered public internet source type."""

    def __init__(
        self,
        source_type: SourceType,
        name: str,
        description: str,
        category: str,
        default_delay: float = 1.0,
        requires_browser: bool = False,
        domain_patterns: Optional[List[str]] = None,
    ) -> None:
        self.source_type = source_type
        self.name = name
        self.description = description
        self.category = category
        self.default_delay = default_delay
        self.requires_browser = requires_browser
        self.domain_patterns = domain_patterns or []


class SourceRegistry:
    """Central registry of the 21 authoritative source types and classifier."""

    _REGISTRY: Dict[SourceType, SourceRegistryEntry] = {
        SourceType.WEB_PAGE: SourceRegistryEntry(
            SourceType.WEB_PAGE, "Web Page", "General public web page with folklore articles", "Web", 1.0
        ),
        SourceType.BLOG: SourceRegistryEntry(
            SourceType.BLOG, "Blog", "Cultural commentary, independent folklore blogs and essays", "Articles", 1.0
        ),
        SourceType.NEWS: SourceRegistryEntry(
            SourceType.NEWS, "News", "Journalistic coverage of festivals, oral history and folklore", "Media", 1.0
        ),
        SourceType.WIKI: SourceRegistryEntry(
            SourceType.WIKI, "Wiki", "Collaborative encyclopedic folklore collections (e.g. Wikipedia)", "Encyclopedic", 0.5,
            domain_patterns=[r"wikipedia\.org", r"wikimedia\.org", r"fandom\.com"]
        ),
        SourceType.DIGITAL_LIBRARY: SourceRegistryEntry(
            SourceType.DIGITAL_LIBRARY, "Digital Library", "Digitized rare books, manuscripts and collections", "Library", 1.5,
            domain_patterns=[r"ndl\.gov\.in", r"dli\.ernet\.in", r"bdigital\.org"]
        ),
        SourceType.ARCHIVE: SourceRegistryEntry(
            SourceType.ARCHIVE, "Archive", "Internet Archive, historical repositories, and preserved collections", "Archive", 1.0,
            domain_patterns=[r"archive\.org", r"loc\.gov"]
        ),
        SourceType.ACADEMIC_PAPER: SourceRegistryEntry(
            SourceType.ACADEMIC_PAPER, "Academic Paper", "Peer-reviewed papers in folklore, anthropology, and ethnology", "Academic", 1.5,
            domain_patterns=[r"jstor\.org", r"researchgate\.net", r"academia\.edu", r"springer\.com"]
        ),
        SourceType.RESEARCH_REPOSITORY: SourceRegistryEntry(
            SourceType.RESEARCH_REPOSITORY, "Research Repository", "Institutional university open-access repositories", "Academic", 1.5,
            domain_patterns=[r"shodhganga\.inflibnet\.ac\.in", r"zenodo\.org", r"arxiv\.org"]
        ),
        SourceType.GOVERNMENT_DOCUMENT: SourceRegistryEntry(
            SourceType.GOVERNMENT_DOCUMENT, "Government Document", "Ministry of Culture, Sahitya Akademi, IGNCA portals", "Government", 1.0,
            domain_patterns=[r"\.gov\.in", r"ignca\.gov\.in", r"sahitya-akademi\.gov\.in"]
        ),
        SourceType.MUSEUM: SourceRegistryEntry(
            SourceType.MUSEUM, "Museum", "Museum catalog descriptions, folklore artifacts, and exhibitions", "Cultural", 1.2,
            domain_patterns=[r"museum", r"nationalmuseumindia\.gov\.in"]
        ),
        SourceType.UNIVERSITY: SourceRegistryEntry(
            SourceType.UNIVERSITY, "University", "Department of Folklore, Cultural Studies university portals", "Academic", 1.0,
            domain_patterns=[r"\.ac\.in", r"\.edu"]
        ),
        SourceType.BOOK_METADATA: SourceRegistryEntry(
            SourceType.BOOK_METADATA, "Book Metadata", "Library of Congress, OpenLibrary, and bibliographic databases", "Metadata", 0.8,
            domain_patterns=[r"openlibrary\.org", r"worldcat\.org", r"books\.google\.com"]
        ),
        SourceType.PDF: SourceRegistryEntry(
            SourceType.PDF, "PDF Document", "Publicly accessible PDF surveys, reports, and folk story transcripts", "Document", 1.5
        ),
        SourceType.PUBLIC_DATASET: SourceRegistryEntry(
            SourceType.PUBLIC_DATASET, "Public Dataset", "Structured public datasets (JSON, CSV, RDF)", "Data", 0.5,
            domain_patterns=[r"data\.gov\.in", r"kaggle\.com", r"huggingface\.co"]
        ),
        SourceType.API: SourceRegistryEntry(
            SourceType.API, "Public API", "Public JSON endpoints and Open Data APIs", "API", 0.5
        ),
        SourceType.RSS: SourceRegistryEntry(
            SourceType.RSS, "RSS Feed", "RSS 2.0 / Atom syndication feeds", "Feed", 0.5
        ),
        SourceType.XML: SourceRegistryEntry(
            SourceType.XML, "XML Feed", "Structured XML documents and data dumps", "Data", 0.5
        ),
        SourceType.SITEMAP: SourceRegistryEntry(
            SourceType.SITEMAP, "Sitemap", "XML sitemap index and URL listings", "Navigation", 0.5
        ),
        SourceType.COMMUNITY_ARCHIVE: SourceRegistryEntry(
            SourceType.COMMUNITY_ARCHIVE, "Community Archive", "Grassroots, tribal, and indigenous storytelling archives", "Community", 1.0,
            domain_patterns=[r"ruralindiaonline\.org", r"sahapedia\.org", r"folklore\.org"]
        ),
        SourceType.ORAL_HISTORY_ARCHIVE: SourceRegistryEntry(
            SourceType.ORAL_HISTORY_ARCHIVE, "Oral History Archive", "Field interviews, elder testimonies, and audio transcriptions", "Oral History", 1.0,
            domain_patterns=[r"oralhistory", r"1947partitionarchive\.org"]
        ),
        SourceType.CULTURAL_DATABASE: SourceRegistryEntry(
            SourceType.CULTURAL_DATABASE, "Cultural Database", "Specialized folk deity (Gramadevata) and narrative databases", "Cultural", 1.0,
            domain_patterns=[r"indianculture\.gov\.in", r"culturopedia\.com"]
        ),
    }

    @classmethod
    def get_all(cls) -> List[SourceRegistryEntry]:
        """List all 21 registered source types."""
        return list(cls._REGISTRY.values())

    @classmethod
    def get_entry(cls, source_type: SourceType) -> Optional[SourceRegistryEntry]:
        """Get registry entry for a specific source type."""
        return cls._REGISTRY.get(source_type)

    @classmethod
    def classify_url(cls, url: str) -> SourceType:
        """Heuristically classify a URL into one of the 21 source types."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()

        # Check explicit file extensions
        if path.endswith(".pdf"):
            return SourceType.PDF
        if path.endswith(".xml") or path.endswith("sitemap.xml"):
            return SourceType.SITEMAP if "sitemap" in path else SourceType.XML
        if path.endswith(".rss") or path.endswith("/feed") or path.endswith("/rss.xml") or path.endswith("/atom.xml"):
            return SourceType.RSS
        if path.endswith(".json") or "/api/" in path:
            return SourceType.API

        # Check domain patterns
        for s_type, entry in cls._REGISTRY.items():
            for pat in entry.domain_patterns:
                if re.search(pat, domain):
                    return s_type

        # Check path patterns
        if "/wiki/" in path:
            return SourceType.WIKI
        if "/blog/" in path or "/blogs/" in path:
            return SourceType.BLOG
        if "/news/" in path:
            return SourceType.NEWS

        return SourceType.WEB_PAGE

    @classmethod
    def create_source_info(cls, url: str, page_title: Optional[str] = None, platform_name: Optional[str] = None) -> SourceInfo:
        """Construct full SourceInfo provenance object with classified source type."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        stype = cls.classify_url(url)
        
        # Derive pleasant platform name if not provided
        derived_platform = platform_name
        if not derived_platform:
            if "wikipedia" in domain:
                derived_platform = "Wikipedia"
            elif "archive.org" in domain:
                derived_platform = "Internet Archive"
            elif "ignca.gov.in" in domain:
                derived_platform = "IGNCA Janapada Sampada"
            elif "sahapedia.org" in domain:
                derived_platform = "Sahapedia"
            elif "ruralindiaonline.org" in domain:
                derived_platform = "PARI Rural India"
            elif "ndl.gov.in" in domain:
                derived_platform = "National Digital Library of India"
            elif domain:
                # Capitalized clean domain name
                clean = domain.replace("www.", "").split(".")[0]
                derived_platform = clean.capitalize()
            else:
                derived_platform = "Public Web"

        return SourceInfo(
            url=url,
            domain=domain,
            platform_name=derived_platform,
            page_title=page_title,
            source_type=stype,
        )
