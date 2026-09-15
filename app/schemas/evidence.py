"""Evidence tracking schema and registry for source provenance and claim verification."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    """Classification of how a claim was evidenced in source material.

    DIRECT: Explicitly stated by the source.
    INFERRED: Derived from multiple documented pieces of evidence.
    GENERATED: Produced by an AI model (must always be clearly labelled).
    """
    DIRECT = "direct"
    INFERRED = "inferred"
    GENERATED = "generated"

    # Backward compatibility aliases
    EXPLICIT = "direct"
    INFERENCE = "inferred"
    SPECULATIVE = "generated"


class Evidence(BaseModel):
    """Core evidence record connecting extracted claims to source provenance."""
    evidence_id: str = Field(default_factory=lambda: f"evi-{uuid.uuid4().hex[:12]}")
    source_id: str = Field(description="Identifier of the origin source")
    document_id: str = Field(description="Identifier of the preserved document")
    url: str = Field(description="URL of the source where evidence was found")
    claim: str = Field(description="Exact claim or factual statement extracted from source")
    evidence_type: EvidenceType = Field(default=EvidenceType.DIRECT, description="direct, inferred, or generated")
    location: Optional[str] = Field(default=None, description="Page, section, or paragraph if available")
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    context_snippet: Optional[str] = Field(default=None, description="Surrounding sentence/passage from source")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class EvidenceStore:
    """In-memory or persistent store for task evidence records."""

    def __init__(self) -> None:
        self._evidence: Dict[str, Evidence] = {}

    def add(self, evidence: Evidence) -> str:
        """Register an evidence record."""
        self._evidence[evidence.evidence_id] = evidence
        return evidence.evidence_id

    def get(self, evidence_id: str) -> Optional[Evidence]:
        """Retrieve evidence by ID."""
        return self._evidence.get(evidence_id)

    def list_all(self) -> List[Evidence]:
        """List all registered evidence items."""
        return list(self._evidence.values())

    def filter_by_source(self, source_id: str) -> List[Evidence]:
        """Filter evidence by origin source ID."""
        return [e for e in self._evidence.values() if e.source_id == source_id]

    def filter_by_type(self, evidence_type: EvidenceType) -> List[Evidence]:
        """Filter evidence by direct, inferred, or generated."""
        return [e for e in self._evidence.values() if e.evidence_type == evidence_type]

    def clear(self) -> None:
        """Clear all registered evidence."""
        self._evidence.clear()
