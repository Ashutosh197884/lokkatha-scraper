"""Layered document preservation models (RAW, ORIGINAL, CLEANED, STRUCTURED)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PreservedDocument(BaseModel):
    """Document with strict multi-layer preservation separating source content from AI analysis.

    RAW: Original fetched payload (HTML, raw XML/RSS/JSON, raw document text).
    ORIGINAL: Direct source-derived textual content.
    CLEANED: Source-derived content after removal of navigation, ads, and boilerplate.
    STRUCTURED: Mapped into Lokkatha schemas.

    Strict Isolation: Generated summaries, translations, and interpretations exist
    exclusively in isolated attributes and are never mixed into ORIGINAL or CLEANED.
    """
    document_id: str = Field(default_factory=lambda: f"doc-{uuid.uuid4().hex[:12]}")
    source_id: str = Field(description="Origin source ID")
    url: str
    title: str = ""

    # Preserved Source Layers
    raw_content: Optional[str] = Field(default=None, description="Layer 1: Raw fetched representation")
    original_text: str = Field(default="", description="Layer 2: Source-derived original textual content")
    cleaned_text: str = Field(default="", description="Layer 3: Boilerplate-stripped source content")

    # Multilingual Preservation
    original_language: Optional[str] = Field(default=None, description="ISO-639 code or language name")
    translated_text: Optional[str] = Field(default=None, description="Optional translation")
    translation_method: str = Field(default="none", description="none, source_provided, or ai_translated")

    # Isolated AI Products (NEVER mixed with source content)
    generated_summary: Optional[str] = Field(default=None, description="AI-generated summary (isolated)")
    ai_analysis: Optional[str] = Field(default=None, description="AI-generated commentary/notes (isolated)")

    content_hash: str = ""
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    paragraphs: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    links: List[str] = Field(default_factory=list)
    extra_metadata: Dict[str, Any] = Field(default_factory=dict)
