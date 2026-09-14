"""Lokkatha data schemas and type definitions."""

from app.schemas.source import (
    SourceInfo,
    SourceQuality,
    SourceQualityFactors,
)
from app.schemas.folklore import (
    Character,
    Location,
    EvidenceType,
    EnvironmentalCategory,
    EnvironmentalKnowledge,
    FolkloreType,
    ClassificationResult,
    Variant,
    FolkloreDocument,
)
from app.schemas.crawl import (
    CrawlStatus,
    URLFrontierItem,
    CrawlResult,
)

__all__ = [
    "SourceInfo",
    "SourceQuality",
    "SourceQualityFactors",
    "Character",
    "Location",
    "EvidenceType",
    "EnvironmentalCategory",
    "EnvironmentalKnowledge",
    "FolkloreType",
    "ClassificationResult",
    "Variant",
    "FolkloreDocument",
    "CrawlStatus",
    "URLFrontierItem",
    "CrawlResult",
]
