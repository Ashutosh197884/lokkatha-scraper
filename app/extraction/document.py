"""Document model and DOM representation."""

from typing import List, Optional
from pydantic import BaseModel, Field


class DOMNode(BaseModel):
    """Simplified DOM element representation."""
    tag: str
    text: str = ""
    attributes: dict[str, str] = Field(default_factory=dict)
    children: List["DOMNode"] = Field(default_factory=list)


class ParsedWebDocument(BaseModel):
    """Complete parsed webpage document structure."""
    url: str
    title: str = ""
    author: Optional[str] = None
    publish_date: Optional[str] = None
    main_text: str = ""
    paragraphs: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    links: List[str] = Field(default_factory=list)
    language: Optional[str] = None
