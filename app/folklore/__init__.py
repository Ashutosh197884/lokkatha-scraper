"""Folklore extraction, classification, validation, TEK analysis, and variant preservation module."""

from app.folklore.classifier import FolkloreClassifier
from app.folklore.culture import CulturalAnalyzer
from app.folklore.ecology import EcologyAnalyzer
from app.folklore.entities import EntityExtractor
from app.folklore.extractor import BaselineFolkloreExtractor
from app.folklore.geography import GeographyResolver
from app.folklore.validator import FolkloreValidator
from app.folklore.variant_preserver import VariantPreserver

__all__ = [
    "BaselineFolkloreExtractor",
    "FolkloreClassifier",
    "FolkloreValidator",
    "EntityExtractor",
    "GeographyResolver",
    "CulturalAnalyzer",
    "EcologyAnalyzer",
    "VariantPreserver",
]
