"""Storage module for folklore documents, repositories, and task output bundles."""

from app.storage.database import DatabaseManager
from app.storage.models import DBFolkloreRecord
from app.storage.repository import JSONFolkloreRepository
from app.storage.task_output import TaskOutputManager

__all__ = [
    "JSONFolkloreRepository",
    "TaskOutputManager",
    "DatabaseManager",
    "DBFolkloreRecord",
]
