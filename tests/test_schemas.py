"""Tests for Pydantic domain schemas and serialization."""

import pytest
from pydantic import ValidationError
from app.schemas.crawl import CrawlResult, CrawlStatus, URLFrontierItem
from app.schemas.folklore import (
    Character,
    ClassificationResult,
    EnvironmentalCategory,
    EnvironmentalKnowledge,
    EvidenceType,
    FolkloreDocument,
    FolkloreType,
    Location,
    Variant,
)
from app.schemas.source import SourceInfo, SourceQuality, SourceQualityFactors


def test_source_info_schema():
    """Test SourceInfo instantiation and serialization."""
    quality = SourceQuality(
        score=0.85,
        factors=SourceQualityFactors(
            institutional=True,
            author_identified=True,
            citations=True,
            primary_source=False,
        ),
    )
    source = SourceInfo(
        url="https://ignca.gov.in/stories/mumal",
        domain="ignca.gov.in",
        page_title="The Legend of Mumal and Mahendra",
        author="Dr. Narayan Singh",
        quality=quality,
    )
    assert source.domain == "ignca.gov.in"
    assert source.quality.score == 0.85
    assert source.quality.factors.institutional is True

    # Test serialization round-trip
    dumped = source.model_dump()
    loaded = SourceInfo.model_validate(dumped)
    assert loaded.url == source.url


def test_folklore_document_complete():
    """Test comprehensive FolkloreDocument model."""
    source = SourceInfo(
        url="https://ignca.gov.in/stories/mumal",
        domain="ignca.gov.in",
        page_title="Mumal Mahendra",
    )

    character = Character(
        name="Mumal",
        role="protagonist",
        gender="female",
        species="human",
        description="Princess of Lodrawa known for her beauty and tragic love.",
    )

    location = Location(
        name="Lodrawa",
        type="historical_settlement",
        region="Rajasthan",
        country="India",
        mentioned_in_story=True,
    )

    env_knowledge = EnvironmentalKnowledge(
        knowledge="Traditional desert rainwater harvesting through tankas and oasis ponds",
        category=EnvironmentalCategory.WATER_MANAGEMENT,
        description="Storage of seasonal monsoon runoff in Thar desert sand basins",
        resources=["rainwater", "sand basin"],
        ecosystem="desert",
        confidence=0.92,
        evidence_type=EvidenceType.EXPLICIT,
    )

    doc = FolkloreDocument(
        id="folk-mumal-mahendra-12345678",
        title="Mumal and Mahendra",
        alternate_titles=["Moomal Mahendar"],
        category="legend",
        folklore_type=FolkloreType.LOVE_STORY,
        story="In the ancient desert kingdom of Lodrawa lived Princess Mumal...",
        summary="A legendary romantic folktale from Rajasthan.",
        region=["Rajasthan", "Marwar"],
        language=["Rajasthani", "Hindi"],
        characters=[character],
        locations=[location],
        environmental_knowledge=[env_knowledge],
        oral_tradition=True,
        source=source,
    )

    assert doc.title == "Mumal and Mahendra"
    assert len(doc.characters) == 1
    assert doc.characters[0].name == "Mumal"
    assert len(doc.environmental_knowledge) == 1
    assert doc.environmental_knowledge[0].category == EnvironmentalCategory.WATER_MANAGEMENT
    assert doc.environmental_knowledge[0].evidence_type == EvidenceType.EXPLICIT

    # JSON round trip
    json_str = doc.model_dump_json()
    reconstructed = FolkloreDocument.model_validate_json(json_str)
    assert reconstructed.id == doc.id
    assert reconstructed.characters[0].name == "Mumal"


def test_environmental_knowledge_validation():
    """Test confidence bounds and evidence type enum validation."""
    with pytest.raises(ValidationError):
        EnvironmentalKnowledge(
            knowledge="Invalid confidence",
            confidence=1.5,  # Must be <= 1.0
        )

    tek = EnvironmentalKnowledge(
        knowledge="Valid TEK",
        category=EnvironmentalCategory.MEDICINAL_PLANTS,
        confidence=0.8,
        evidence_type=EvidenceType.INFERENCE,
    )
    assert tek.evidence_type == EvidenceType.INFERENCE


def test_frontier_item_schema():
    """Test URLFrontierItem schema."""
    item = URLFrontierItem(
        url="https://example.org/tales/1",
        normalized_url="https://example.org/tales/1",
        domain="example.org",
        depth=1,
        priority=0.8,
        status=CrawlStatus.QUEUED,
    )
    assert item.status == CrawlStatus.QUEUED
    assert item.priority == 0.8
    assert item.attempts == 0
