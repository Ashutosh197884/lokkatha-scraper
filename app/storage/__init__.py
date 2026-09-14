"""Storage interfaces and repository abstractions (JSON & PostgreSQL)."""

from typing import Protocol
from app.schemas.folklore import FolkloreDocument


class FolkloreRepository(Protocol):
    """Protocol for persisting and retrieving structured folklore records."""
    async def save(self, document: FolkloreDocument) -> str:
        ...

    async def get_by_id(self, doc_id: str) -> FolkloreDocument | None:
        ...
