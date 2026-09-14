"""Standalone script for analyzing extracted folklore content."""

import sys
from pathlib import Path
from app.config.logging import configure_logging, get_logger
from app.config.settings import get_settings
from app.storage.repository import JSONFolkloreRepository

logger = get_logger("scripts.analyze")


def main() -> None:
    settings = get_settings()
    configure_logging(log_level=settings.log_level)
    target_dir = sys.argv[1] if len(sys.argv) > 1 else settings.storage.structured_dir
    logger.info("analyzing_folklore_repository", target_dir=target_dir)

    repo = JSONFolkloreRepository(base_dir=target_dir)
    docs = repo.list_all()
    print(f"Loaded {len(docs)} folklore documents from {target_dir}")


if __name__ == "__main__":
    main()
