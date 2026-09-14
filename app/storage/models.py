"""SQLAlchemy and relational model definitions matching PostgreSQL schema."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class DBFolkloreRecord(BaseModel):
    """Relational table representation for folklore records."""
    id: str
    title: str
    summary: str
    story: str
    category: str
    original_language: Optional[str] = None
    oral_tradition: bool = False
    historical_context: Optional[str] = None
    social_context: Optional[str] = None
    confidence: Dict[str, Any] = {}
