"""Crawl, URL frontier, and HTTP response schemas."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CrawlStatus(str, Enum):
    """Lifecycle statuses for URLs in the crawl frontier."""
    QUEUED = "queued"
    FETCHING = "fetching"
    FETCHED = "fetched"
    PARSED = "parsed"
    PROCESSED = "processed"
    FAILED = "failed"
    BLOCKED = "blocked"
    REJECTED = "rejected"
    DUPLICATE = "duplicate"


class URLFrontierItem(BaseModel):
    """An item managed in the URL crawl frontier."""
    url: str
    normalized_url: str
    domain: str
    depth: int = Field(default=0, ge=0)
    priority: float = Field(default=0.5, ge=0.0, le=1.0)
    status: CrawlStatus = Field(default=CrawlStatus.QUEUED)
    discovered_from: Optional[str] = None
    discovered_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    attempts: int = Field(default=0, ge=0)
    last_attempt_at: Optional[str] = None
    error_message: Optional[str] = None


class CrawlResult(BaseModel):
    """Result of fetching and extracting a webpage."""
    url: str
    normalized_url: str
    domain: str
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    response_headers: Dict[str, str] = Field(default_factory=dict)
    raw_html_path: Optional[str] = None
    clean_text_path: Optional[str] = None
    content_hash: Optional[str] = None
    links_extracted: List[str] = Field(default_factory=list)
    requires_browser: bool = False
    is_success: bool = False
    error: Optional[str] = None
    crawled_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
