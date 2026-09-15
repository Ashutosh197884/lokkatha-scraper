"""Lokkatha schemas module."""

from app.schemas.crawl import (
    CrawlResult,
    CrawlStatus,
    URLFrontierItem,
)
from app.schemas.document import PreservedDocument
from app.schemas.evidence import (
    Evidence,
    EvidenceStore,
    EvidenceType,
)
from app.schemas.folklore import (
    CanonicalTradition,
    Character,
    ClassificationResult,
    EnvironmentalCategory,
    EnvironmentalKnowledge,
    FolkloreDocument,
    FolkloreType,
    Location,
    Variant,
)
from app.schemas.manifest import (
    SourceManifest,
    SourceManifestItem,
    TaskMetadata,
)
from app.schemas.source import (
    SourceInfo,
    SourceQuality,
    SourceQualityFactors,
    SourceType,
)

__all__ = [
    "SourceType",
    "SourceInfo",
    "SourceQuality",
    "SourceQualityFactors",
    "EvidenceType",
    "Evidence",
    "EvidenceStore",
    "SourceManifestItem",
    "SourceManifest",
    "TaskMetadata",
    "PreservedDocument",
    "FolkloreDocument",
    "FolkloreType",
    "EnvironmentalCategory",
    "EnvironmentalKnowledge",
    "Character",
    "Location",
    "ClassificationResult",
    "Variant",
    "CanonicalTradition",
    "URLFrontierItem",
    "CrawlResult",
    "CrawlStatus",
]
