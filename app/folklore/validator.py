"""Validation engine enforcing Lokkatha folklore standards and provenance."""

from typing import List, Tuple
from app.schemas.folklore import EvidenceType, FolkloreDocument


class FolkloreValidator:
    """Validates folklore documents against strict provenance and content integrity rules."""

    def validate(self, doc: FolkloreDocument) -> Tuple[bool, List[str]]:
        """
        Validate folklore document.
        Returns (is_valid, list_of_validation_errors).
        """
        errors: List[str] = []

        if not doc.title or not doc.title.strip():
            errors.append("Title must not be empty.")

        if not doc.story or not doc.story.strip():
            errors.append("Story narrative must not be empty.")

        if not doc.source or not doc.source.url:
            errors.append("Source provenance URL is required.")

        for ek in doc.environmental_knowledge:
            if ek.evidence_type == EvidenceType.SPECULATIVE and ek.confidence > 0.8:
                errors.append(f"Speculative environmental knowledge '{ek.knowledge}' cannot have confidence > 0.8.")

        return len(errors) == 0, errors
