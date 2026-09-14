"""Standalone script for triggering Lokkatha web crawl."""

import asyncio
import sys
from app.config.logging import configure_logging, get_logger
from app.config.settings import get_settings
from app.crawler.manager import CrawlManager

logger = get_logger("scripts.crawl")


async def main() -> None:
    settings = get_settings()
    configure_logging(log_level=settings.log_level)
    logger.info("launching_crawl_script", project=settings.project.name)

    manager = CrawlManager(settings)
    seeds = sys.argv[1:] if len(sys.argv) > 1 else []
    await manager.crawl(seeds=seeds)


if __name__ == "__main__":
    asyncio.run(main())
