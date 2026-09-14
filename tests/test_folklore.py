"""Tests for folklore classification, geography mapping, entities, and validation."""

from app.folklore.classifier import FolkloreClassifier
from app.folklore.geography import GeographyResolver
from app.folklore.validator import FolkloreValidator
from app.schemas.folklore import (
    EvidenceType,
    FolkloreDocument,
    FolkloreType,
)
from app.schemas.source import SourceInfo


def test_folklore_classifier():
    classifier = FolkloreClassifier()

    # Folktale detection
    res = classifier.classify("This is an ancient panchatantra story of two jackals in the forest.")
    assert res.is_folklore is True
    assert res.type in (FolkloreType.FABLE, FolkloreType.FOLKTALE)
    assert res.confidence > 0.4

    # Non-folklore content
    non_folk = classifier.classify("Quarterly financial report for corporate shareholders in Q3.")
    assert non_folk.confidence <= 0.3


def test_geography_resolver():
    resolver = GeographyResolver()
    text = "The story originated in the deserts of Rajasthan and migrated into Gujarat and Punjab."
    regions = resolver.detect_regions(text)
    assert "Rajasthan" in regions
    assert "Gujarat" in regions
    assert "Punjab" in regions


def test_folklore_validator():
    validator = FolkloreValidator()

    # Valid document
    valid_doc = FolkloreDocument(
        id="folk-test-123",
        title="The Tale of Dhola Maru",
        folklore_type=FolkloreType.LEGEND,
        region=["Rajasthan"],
        language=["hi"],
        story="Dhola and Maru were separated by circumstances but reunited across the Thar desert.",
        source=SourceInfo(
            url="https://ignca.gov.in/stories/dhola-maru",
            domain="ignca.gov.in",
        ),
    )
    is_valid, errors = validator.validate(valid_doc)
    assert is_valid is True
    assert len(errors) == 0

    # Invalid document (missing title and story)
    invalid_doc = FolkloreDocument(
        id="folk-invalid-001",
        title="",
        folklore_type=FolkloreType.FOLKTALE,
        story="",
        source=SourceInfo(url="https://example.org", domain="example.org"),
    )
    is_valid, errors = validator.validate(invalid_doc)
    assert is_valid is False
    assert len(errors) >= 2
