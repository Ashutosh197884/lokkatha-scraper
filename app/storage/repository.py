"""File-based JSON and relational repository implementations with metadata provenance."""

import json
import re
from pathlib import Path
from typing import List, Optional
from app.config.logging import get_logger
from app.schemas.folklore import FolkloreDocument

logger = get_logger("storage.repository")

# Only allow safe filesystem identifiers: letters, digits, dash, underscore, dot.
_SAFE_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def validate_safe_id(doc_id: str) -> str:
    """Raise ValueError if an id could traverse directories (e.g. '../x' or absolute paths)."""
    if not doc_id or not _SAFE_ID_PATTERN.match(doc_id):
        raise ValueError(f"Unsafe document id: {doc_id!r}")
    if doc_id.startswith("."):
        raise ValueError(f"Unsafe document id: {doc_id!r}")
    return doc_id


class JSONFolkloreRepository:
    """Local JSON file repository for structured folklore documents with source provenance."""

    def __init__(self, base_dir: str = "data/structured") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, doc: FolkloreDocument) -> Path:
        """Save folklore document to JSON file with standard source_information block."""
        validate_safe_id(doc.id)
        file_path = self.base_dir / f"{doc.id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json_dict = doc.model_dump_with_source_info()
            json.dump(json_dict, f, indent=2)
        logger.info("folklore_document_saved", id=doc.id, path=str(file_path))
        return file_path

    def get_by_id(self, doc_id: str) -> Optional[FolkloreDocument]:
        """Load folklore document by ID. Raises ValueError for unsafe ids."""
        validate_safe_id(doc_id)
        file_path = self.base_dir / f"{doc_id}.json"
        if not file_path.is_file():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Remove redundant top-level source_information if present before Pydantic parsing
            return FolkloreDocument.model_validate(data)

    def list_all(self) -> List[FolkloreDocument]:
        """List all structured documents stored in JSON format."""
        docs = []
        for p in self.base_dir.glob("*.json"):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    docs.append(FolkloreDocument.model_validate(json.load(f)))
            except Exception as exc:
                logger.warning("failed_to_load_document", path=str(p), error=str(exc))
        return docs
