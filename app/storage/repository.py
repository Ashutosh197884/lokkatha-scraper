"""File-based JSON and relational repository implementations."""

import json
from pathlib import Path
from typing import List, Optional
from app.config.logging import get_logger
from app.schemas.folklore import FolkloreDocument

logger = get_logger("storage.repository")


class JSONFolkloreRepository:
    """Local JSON file repository for structured folklore documents."""

    def __init__(self, base_dir: str = "data/structured") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, doc: FolkloreDocument) -> Path:
        """Save folklore document to JSON file named after doc.id."""
        file_path = self.base_dir / f"{doc.id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(doc.model_dump_json(indent=2))
        logger.info("folklore_document_saved", id=doc.id, path=str(file_path))
        return file_path

    def get_by_id(self, doc_id: str) -> Optional[FolkloreDocument]:
        """Load folklore document by ID."""
        file_path = self.base_dir / f"{doc_id}.json"
        if not file_path.is_file():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
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
