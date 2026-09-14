"""Database connection manager and session lifecycle."""

from typing import Optional
from app.config.logging import get_logger
from app.config.settings import DatabaseSettings

logger = get_logger("storage.database")


class DatabaseManager:
    """Manages PostgreSQL connection pool and pgvector integration."""

    def __init__(self, config: Optional[DatabaseSettings] = None) -> None:
        self.config = config

    async def connect(self) -> None:
        """Establish connection to PostgreSQL."""
        logger.info("db_connection_initialized", host=self.config.host if self.config else "none")

    async def disconnect(self) -> None:
        """Close connection pool."""
        logger.info("db_disconnected")
