"""Level 3 Deduplication: Semantic similarity and variant relationship classification."""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.folklore import Variant


class SimilarityMatch(BaseModel):
    """Semantic comparison result between two stories."""
    canonical_id: str
    target_id: str
    similarity_score: float = Field(ge=0.0, le=1.0)
    relationship: str = Field(description="exact_duplicate, near_duplicate, probable_variant, related_story, unrelated")


class SemanticDeduplicator:
    """Detects narrative variants and semantic duplicates using embeddings."""

    def __init__(self, threshold: float = 0.90) -> None:
        self.threshold = threshold

    def classify_relationship(self, similarity: float) -> str:
        """Classify relationship category based on cosine similarity score."""
        if similarity >= 0.98:
            return "exact_duplicate"
        elif similarity >= 0.90:
            return "near_duplicate"
        elif similarity >= 0.75:
            return "probable_variant"
        elif similarity >= 0.50:
            return "related_story"
        return "unrelated"
