"""Asynchronous event emitter and pub/sub bus for Lokkatha pipeline telemetry."""

import asyncio
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from app.config.logging import get_logger

logger = get_logger("events.emitter")


class EventType(str, Enum):
    """The 16 core pipeline event types."""
    SOURCE_DISCOVERED = "source.discovered"
    SOURCE_CONNECTED = "source.connected"
    SOURCE_STARTED = "source.started"
    SOURCE_COMPLETED = "source.completed"
    SOURCE_FAILED = "source.failed"

    PAGE_DISCOVERED = "page.discovered"
    PAGE_FETCHED = "page.fetched"
    PAGE_FAILED = "page.failed"

    DOCUMENT_EXTRACTED = "document.extracted"
    EVIDENCE_CREATED = "evidence.created"

    FOLKLORE_DISCOVERED = "folklore.discovered"
    FOLKLORE_EXTRACTED = "folklore.extracted"
    FOLKLORE_VALIDATED = "folklore.validated"

    TASK_STARTED = "task.started"
    TASK_PROGRESS = "task.progress"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"


class PipelineEvent(BaseModel):
    """Structured event message emitted across the extraction and crawl lifecycle."""
    event_type: EventType
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    task_id: Optional[str] = None
    source_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    message: str = ""


class EventEmitter:
    """Asynchronous event dispatcher and subscriber registry."""

    def __init__(self) -> None:
        self._subscribers: List[asyncio.Queue] = []
        self._history: List[PipelineEvent] = []

    def subscribe(self) -> asyncio.Queue:
        """Subscribe a new listener queue (e.g. for an SSE or WebSocket client)."""
        q = asyncio.Queue()
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        """Remove a subscriber queue."""
        if q in self._subscribers:
            self._subscribers.remove(q)

    async def emit(
        self,
        event_type: EventType,
        task_id: Optional[str] = None,
        source_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        message: str = "",
    ) -> PipelineEvent:
        """Dispatch a pipeline event to all active subscriber queues."""
        event = PipelineEvent(
            event_type=event_type,
            task_id=task_id,
            source_id=source_id,
            data=data or {},
            message=message,
        )
        self._history.append(event)
        if len(self._history) > 1000:
            self._history.pop(0)

        for q in list(self._subscribers):
            try:
                q.put_nowait(event)
            except Exception:
                pass

        logger.debug("event_emitted", type=event_type.value, task=task_id, source=source_id)
        return event

    def get_recent_events(self, limit: int = 50) -> List[PipelineEvent]:
        """Return the most recent event history."""
        return self._history[-limit:]


# Global shared emitter instance
default_emitter = EventEmitter()
