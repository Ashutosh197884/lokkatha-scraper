"""Task result directory generator and provenance manifest publisher."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config.logging import get_logger
from app.schemas.document import PreservedDocument
from app.schemas.evidence import Evidence
from app.schemas.folklore import FolkloreDocument
from app.schemas.manifest import SourceManifest, SourceManifestItem, TaskMetadata

logger = get_logger("storage.task_output")


class TaskOutputManager:
    """Creates and populates the required task result directory structure:

    task_<id>/
    ├── result.json
    ├── result.md
    ├── sources.json
    ├── evidence.json
    ├── metadata.json
    ├── original/
    │   └── <doc_id>.txt
    └── cleaned/
        └── <doc_id>.txt
    """

    def __init__(self, base_tasks_dir: str = "data/tasks") -> None:
        self.base_tasks_dir = Path(base_tasks_dir)
        self.base_tasks_dir.mkdir(parents=True, exist_ok=True)

    def generate_task_bundle(
        self,
        task_id: str,
        task_name: str,
        start_time: str,
        folklore_docs: List[FolkloreDocument],
        preserved_docs: List[PreservedDocument],
        evidence_list: List[Evidence],
        manifest_items: Optional[List[SourceManifestItem]] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Construct full task output directory with all required files and layers."""
        task_dir = self.base_tasks_dir / f"task_{task_id}"
        orig_dir = task_dir / "original"
        clean_dir = task_dir / "cleaned"

        task_dir.mkdir(parents=True, exist_ok=True)
        orig_dir.mkdir(parents=True, exist_ok=True)
        clean_dir.mkdir(parents=True, exist_ok=True)

        # 1. Write original and cleaned document text layers
        for pdoc in preserved_docs:
            doc_filename = f"{pdoc.document_id}.txt"
            if pdoc.original_text:
                with open(orig_dir / doc_filename, "w", encoding="utf-8") as f:
                    f.write(pdoc.original_text)
            if pdoc.cleaned_text:
                with open(clean_dir / doc_filename, "w", encoding="utf-8") as f:
                    f.write(pdoc.cleaned_text)

        # 2. Build Source Manifest if not provided
        if manifest_items is None:
            source_map: Dict[str, SourceManifestItem] = {}
            for doc in folklore_docs:
                s = doc.source
                if s.source_id not in source_map:
                    source_map[s.source_id] = SourceManifestItem(
                        source_id=s.source_id,
                        platform=s.platform_name,
                        domain=s.domain,
                        url=s.url,
                        documents_used=1,
                        evidence_count=len(doc.evidence_ids),
                        source_type=s.source_type.value if hasattr(s.source_type, "value") else str(s.source_type),
                        license=s.license_information,
                    )
                else:
                    source_map[s.source_id].documents_used += 1
                    source_map[s.source_id].evidence_count += len(doc.evidence_ids)
            manifest_items = list(source_map.values())

        manifest = SourceManifest(
            task_id=task_id,
            sources=manifest_items,
            total_sources=len(manifest_items),
            total_documents=len(preserved_docs),
            total_evidence=len(evidence_list),
        )

        with open(task_dir / "sources.json", "w", encoding="utf-8") as f:
            f.write(manifest.model_dump_json(indent=2))

        # 3. Write evidence.json
        with open(task_dir / "evidence.json", "w", encoding="utf-8") as f:
            evidence_data = [e.model_dump() for e in evidence_list]
            json.dump(evidence_data, f, indent=2)

        # 4. Write result.json (with standard source_information)
        with open(task_dir / "result.json", "w", encoding="utf-8") as f:
            result_data = [d.model_dump_with_source_info() for d in folklore_docs]
            json.dump(result_data, f, indent=2)

        # 5. Write metadata.json
        platforms_used = list(set(s.platform for s in manifest_items))
        domains_used = list(set(s.domain for s in manifest_items if s.domain))
        source_types_used = list(set(s.source_type for s in manifest_items))

        task_meta = TaskMetadata(
            task_id=task_id,
            task_name=task_name,
            start_time=start_time,
            number_of_sources=len(manifest_items),
            number_of_domains=len(domains_used),
            number_of_documents=len(preserved_docs),
            number_of_relevant_documents=len(folklore_docs),
            evidence_count=len(evidence_list),
            folklore_records_count=len(folklore_docs),
            platforms_used=platforms_used,
            domains_used=domains_used,
            source_types_used=source_types_used,
            execution_parameters=extra_metadata or {},
        )

        with open(task_dir / "metadata.json", "w", encoding="utf-8") as f:
            f.write(task_meta.model_dump_json(indent=2))

        # 6. Write result.md (human-readable summary with provenance citations)
        self._write_result_markdown(task_dir / "result.md", task_meta, manifest, folklore_docs)

        logger.info("task_bundle_generated", task_id=task_id, path=str(task_dir))
        return task_dir

    def _write_result_markdown(
        self,
        filepath: Path,
        metadata: TaskMetadata,
        manifest: SourceManifest,
        folklore_docs: List[FolkloreDocument],
    ) -> None:
        """Generate formatted Markdown report with source citations and evidence."""
        lines = [
            f"# Lokkatha Intelligence Task Report: {metadata.task_name}",
            f"\n**Task ID**: `{metadata.task_id}`  ",
            f"**Generated**: {manifest.generated_at}  ",
            f"**Status**: {metadata.status.upper()}  ",
            f"\n## Summary Metrics",
            f"* **Sources Used**: {metadata.number_of_sources}",
            f"* **Domains Scanned**: {metadata.number_of_domains}",
            f"* **Documents Processed**: {metadata.number_of_documents}",
            f"* **Relevant Folklore Stories**: {metadata.folklore_records_count}",
            f"* **Evidence Records Extracted**: {metadata.evidence_count}",
            f"\n## Sources Manifest",
            "| Platform | Domain | Source Type | URL | Documents Used | Evidence Count |",
            "|---|---|---|---|---|---|",
        ]

        for s in manifest.sources:
            lines.append(f"| {s.platform} | {s.domain or 'N/A'} | {s.source_type} | [{s.url}]({s.url}) | {s.documents_used} | {s.evidence_count} |")

        lines.append("\n## Extracted Folklore Records\n")
        for doc in folklore_docs:
            lines.append(f"### {doc.title}")
            if doc.alternate_titles:
                lines.append(f"*Alternate Title*: *{', '.join(doc.alternate_titles)}*  ")
            lines.append(f"**Source**: [{doc.source.platform_name}]({doc.source.url}) ({doc.source.url})  ")
            lines.append(f"**Region**: {', '.join(doc.region) if doc.region else 'Pan-India'} | **Genre**: {doc.folklore_type.value}  ")
            lines.append(f"\n> {doc.summary}\n")

            if doc.characters:
                char_names = [c.name for c in doc.characters]
                lines.append(f"* **Characters**: {', '.join(char_names)}")
            if doc.motifs:
                lines.append(f"* **Motifs**: {', '.join(doc.motifs)}")
            if doc.environmental_knowledge:
                lines.append("\n**Traditional Ecological Knowledge (TEK)**:")
                for ek in doc.environmental_knowledge:
                    lines.append(f"- **{ek.category.value}**: {ek.knowledge} *(Evidence: \"{ek.evidence or 'Source Text'}\" - {ek.evidence_type.value})*")
            lines.append("\n---\n")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
