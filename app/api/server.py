"""REST API and Server-Sent Events (SSE) server for Lokkatha Intelligence Orchestrator."""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from app.config.logging import get_logger
from app.discovery.registry import SourceRegistry
from app.events.emitter import EventType, default_emitter
from app.schemas.evidence import Evidence
from app.schemas.folklore import FolkloreDocument
from app.schemas.source import SourceInfo, SourceType
from app.storage.repository import JSONFolkloreRepository
from app.storage.task_output import TaskOutputManager

logger = get_logger("api.server")


class LokkathaAPIService:
    """Core service managing REST endpoints, task runs, and SSE event streaming."""

    def __init__(
        self,
        repo: Optional[JSONFolkloreRepository] = None,
        task_output_mgr: Optional[TaskOutputManager] = None,
    ) -> None:
        self.repo = repo or JSONFolkloreRepository()
        self.task_output_mgr = task_output_mgr or TaskOutputManager()
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.registered_sources: List[SourceInfo] = [
            SourceRegistry.create_source_info("https://en.wikipedia.org/wiki/Category:Indian_folklore", "Wikipedia Indian Folklore", "Wikipedia"),
            SourceRegistry.create_source_info("https://archive.org/details/indian-folklore-collection", "Internet Archive Indian Folklore", "Internet Archive"),
            SourceRegistry.create_source_info("https://ignca.gov.in/divisions/janapada-sampada", "IGNCA Janapada Sampada", "IGNCA"),
            SourceRegistry.create_source_info("https://sahapedia.org/modules/oral-traditions", "Sahapedia Oral Traditions", "Sahapedia"),
            SourceRegistry.create_source_info("https://ruralindiaonline.org/en/articles/categories/culture/", "PARI Rural India Culture", "PARI Rural India"),
        ]

    def get_health(self) -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "system": "Lokkatha Internet Intelligence & Source-Preservation System",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sources_count": len(self.registered_sources),
            "stored_records": len(self.repo.list_all()),
        }

    def list_sources(self) -> List[Dict[str, Any]]:
        """List registered source provenance records."""
        return [s.model_dump() for s in self.registered_sources]

    def register_source(self, url: str, page_title: Optional[str] = None, platform_name: Optional[str] = None) -> Dict[str, Any]:
        """Register a new public internet source with automated classification."""
        s = SourceRegistry.create_source_info(url=url, page_title=page_title, platform_name=platform_name)
        self.registered_sources.append(s)
        asyncio.create_task(
            default_emitter.emit(
                EventType.SOURCE_DISCOVERED,
                source_id=s.source_id,
                data=s.model_dump(),
                message=f"Discovered and registered source: {s.platform_name} ({s.url})",
            )
        )
        return s.model_dump()

    def list_folklore(self, region: Optional[str] = None) -> List[Dict[str, Any]]:
        """List structured folklore records with source provenance."""
        docs = self.repo.list_all()
        if region:
            docs = [d for d in docs if any(region.lower() in r.lower() for r in d.region)]
        return [d.model_dump_with_source_info() for d in docs]

    def get_folklore(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve single folklore record with full source_information."""
        doc = self.repo.get_by_id(doc_id)
        return doc.model_dump_with_source_info() if doc else None

    def get_task_manifest(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load sources.json manifest for a completed task."""
        manifest_path = Path("data/tasks") / f"task_{task_id}" / "sources.json"
        if manifest_path.is_file():
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def get_task_evidence(self, task_id: str) -> Optional[List[Dict[str, Any]]]:
        """Load evidence.json for a completed task."""
        evidence_path = Path("data/tasks") / f"task_{task_id}" / "evidence.json"
        if evidence_path.is_file():
            with open(evidence_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def get_task_results(self, task_id: str) -> Optional[List[Dict[str, Any]]]:
        """Load result.json for a completed task."""
        result_path = Path("data/tasks") / f"task_{task_id}" / "result.json"
        if result_path.is_file():
            with open(result_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None


# Global service instance
api_service = LokkathaAPIService()
