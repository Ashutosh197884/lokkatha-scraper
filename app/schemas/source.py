"""Source provenance and source quality schemas."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


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
    url: str
    domain: str
    page_title: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[str] = None
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    content_hash: Optional[str] = None
    source_type: str = Field(default="website", description="e.g. website, archive, academic, digitized_book")
    license: Optional[str] = None
    quality: Optional[SourceQuality] = None
    extra_metadata: Dict[str, Any] = Field(default_factory=dict)
