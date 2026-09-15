"""Source manifest and task metadata schemas."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SourceManifestItem(BaseModel):
    """Manifest item identifying a distinct public source utilized in a task."""
    source_id: str
    platform: str
    domain: str
    url: str
    documents_used: int = 1
    evidence_count: int = 0
    source_type: str = "WEB_PAGE"
    license: Optional[str] = None


class SourceManifest(BaseModel):
    """Complete source manifest generated for every completed task."""
    task_id: str
    sources: List[SourceManifestItem] = Field(default_factory=list)
    total_sources: int = 0
    total_documents: int = 0
    total_evidence: int = 0
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TaskMetadata(BaseModel):
    """Metadata tracking task execution counts, telemetry, and source diversity."""
    task_id: str
    task_name: str
    status: str = "completed"
    start_time: str
    end_time: Optional[str] = None
    elapsed_seconds: float = 0.0

    number_of_sources: int = 0
    number_of_domains: int = 0
    number_of_documents: int = 0
    number_of_relevant_documents: int = 0
    evidence_count: int = 0
    folklore_records_count: int = 0

    platforms_used: List[str] = Field(default_factory=list)
    domains_used: List[str] = Field(default_factory=list)
    source_types_used: List[str] = Field(default_factory=list)

    execution_parameters: Dict[str, Any] = Field(default_factory=dict)
