"""Validation engine enforcing Lokkatha provenance integrity, source authority, and no-hallucination policy."""

import re
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from app.schemas.evidence import EvidenceType
from app.schemas.folklore import FolkloreDocument


class FolkloreValidator:
    """Validates folklore documents against strict provenance, source authority, and no-hallucination rules."""

    def is_valid_source_url(self, url: Optional[str]) -> bool:
        """Verify that a URL is a syntactically valid public internet web URL."""
        if not url or not isinstance(url, str):
            return False
        parsed = urlparse(url)
        # Must have scheme http/https and a valid network domain
        if parsed.scheme not in ("http", "https"):
            return False
        if not parsed.netloc or len(parsed.netloc.split(".")) < 2:
            return False
        # Catch common AI hallucinated placeholder URLs
        if any(fake in url.lower() for fake in ["example.com", "fakeurl", "synthetic", "placeholder", "ai-generated"]):
            return False
        return True

    def validate(self, doc: FolkloreDocument) -> Tuple[bool, List[str]]:
        """Validate folklore document against strict provenance and content integrity rules.

        Returns (is_valid, list_of_validation_errors).
        """
        errors: List[str] = []

        # 1. Structural Checks
        if not doc.title or not doc.title.strip():
            errors.append("Title must not be empty.")

        if not doc.story or not doc.story.strip():
            errors.append("Story narrative must not be empty.")

        # 2. Source Provenance & URL Legitimacy
        if not doc.source or not doc.source.url:
            errors.append("Source provenance URL is required.")
        elif not self.is_valid_source_url(doc.source.url):
            errors.append(f"Invalid or synthetic source URL '{doc.source.url}'. Real public source required.")

        # 3. Environmental Knowledge Integrity & No-Hallucination
        for ek in doc.environmental_knowledge:
            if ek.evidence_type == EvidenceType.GENERATED and ek.confidence > 0.8:
                errors.append(f"Generated environmental knowledge '{ek.knowledge}' cannot have confidence > 0.8.")
            if not ek.evidence or not ek.evidence.strip():
                errors.append(f"TEK item '{ek.knowledge}' requires explicit source passage evidence.")

        # 4. Character & Location Evidence Checks
        for char in doc.characters:
            if not char.name or not char.name.strip():
                errors.append("Character entity must have a valid name.")

        return len(errors) == 0, errors
