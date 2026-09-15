"""Source provenance, 21-type registry taxonomy, and source quality schemas."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """The 21-type authoritative public internet source taxonomy for Lokkatha."""
    WEB_PAGE = "WEB_PAGE"
    BLOG = "BLOG"
    NEWS = "NEWS"
    WIKI = "WIKI"
    DIGITAL_LIBRARY = "DIGITAL_LIBRARY"
    ARCHIVE = "ARCHIVE"
    ACADEMIC_PAPER = "ACADEMIC_PAPER"
    RESEARCH_REPOSITORY = "RESEARCH_REPOSITORY"
    GOVERNMENT_DOCUMENT = "GOVERNMENT_DOCUMENT"
    MUSEUM = "MUSEUM"
    UNIVERSITY = "UNIVERSITY"
    BOOK_METADATA = "BOOK_METADATA"
    PDF = "PDF"
    PUBLIC_DATASET = "PUBLIC_DATASET"
    API = "API"
    RSS = "RSS"
    XML = "XML"
    SITEMAP = "SITEMAP"
    COMMUNITY_ARCHIVE = "COMMUNITY_ARCHIVE"
    ORAL_HISTORY_ARCHIVE = "ORAL_HISTORY_ARCHIVE"
    CULTURAL_DATABASE = "CULTURAL_DATABASE"


class SourceQualityFactors(BaseModel):
    """Factors contributing to source credibility."""
    institutional: bool = False
    author_identified: bool = False
    citations: bool = False
    primary_source: bool = False
    regional_expertise: bool = False
    oral_tradition_transcription: bool = False
    peer_reviewed: bool = False


class SourceQuality(BaseModel):
    """Source quality score and evaluation breakdown."""
    score: float = Field(default=0.5, ge=0.0, le=1.0, description="Quality score from 0.0 (poor) to 1.0 (authoritative)")
    factors: SourceQualityFactors = Field(default_factory=SourceQualityFactors)


class SourceInfo(BaseModel):
    """Complete source provenance and retrieval metadata."""
    source_id: str = Field(default_factory=lambda: f"src-{uuid.uuid4().hex[:12]}")
    platform_name: str = Field(default="Public Web", description="Platform/Provider name, e.g. Sahapedia, IGNCA, Archive.org")
    domain: str = ""
    url: str
    canonical_url: Optional[str] = None
    page_title: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[str] = None
    source_type: SourceType = Field(default=SourceType.WEB_PAGE)
    retrieval_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    http_status: Optional[int] = Field(default=200)
    content_type: Optional[str] = Field(default="text/html")
    content_hash: Optional[str] = None
    robots_status: str = Field(default="allowed", description="allowed, disallowed, unverified")
    license_information: Optional[str] = None

    # Quality & legacy compatibility
    quality: Optional[SourceQuality] = None
    extra_metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def website(self) -> str:
        """Helper to get website domain or name."""
        return self.domain or self.platform_name

    @property
    def retrieved_at(self) -> str:
        """Alias for retrieval_timestamp for compatibility."""
        return self.retrieval_timestamp

    @property
    def license(self) -> Optional[str]:
        """Alias for license_information for compatibility."""
        return self.license_information

    def to_file_metadata(self) -> Dict[str, Any]:
        """Generate standardized file source_information object for JSON exports."""
        return {
            "source_information": {
                "platform": self.platform_name,
                "website": self.domain or self.platform_name,
                "url": self.url,
                "original_title": self.page_title or "",
                "author": self.author,
                "published_at": self.published_at,
                "retrieved_at": self.retrieval_timestamp,
                "source_type": self.source_type.value if isinstance(self.source_type, SourceType) else str(self.source_type),
                "content_hash": self.content_hash or "",
            }
        }
