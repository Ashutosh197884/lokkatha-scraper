"""Standalone script for exporting structured folklore datasets."""

import argparse
import json
from pathlib import Path
from app.config.logging import configure_logging, get_logger
from app.config.settings import get_settings
from app.storage.repository import JSONFolkloreRepository

logger = get_logger("scripts.export")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Lokkatha structured folklore data.")
    parser.add_argument("--format", choices=["json", "jsonl"], default="json", help="Export format")
    parser.add_argument("--output", type=str, default="data/export.json", help="Output file path")
    args = parser.parse_args()

    settings = get_settings()
    configure_logging(log_level=settings.log_level)

    repo = JSONFolkloreRepository(base_dir=settings.storage.structured_dir)
    docs = repo.list_all()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([doc.model_dump() for doc in docs], f, indent=2)
    elif args.format == "jsonl":
        with open(output_path, "w", encoding="utf-8") as f:
            for doc in docs:
                f.write(doc.model_dump_json() + "\n")

    logger.info("export_completed", count=len(docs), output=str(output_path))
    print(f"Exported {len(docs)} documents to {output_path}")


if __name__ == "__main__":
    main()
