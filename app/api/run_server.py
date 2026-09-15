"""Runnable HTTP + SSE server for the Lokkatha Intelligence Orchestrator.

Exposes the LokkathaAPIService over a stdlib-only HTTP server (no new
dependencies) so the dashboard frontend can consume REST endpoints and the
live Server-Sent-Events stream. Starting a task runs a real in-process crawl
and streams task/pipeline events to every connected client.

Usage:
    python -m app.api.run_server --host 127.0.0.1 --port 8000

Endpoints:
    GET  /api/health                 Health + record counts
    GET  /api/sources                Registered source provenance records
    POST /api/sources                Register a source  {"url", "page_title"?, "platform_name"?}
    GET  /api/folklore?region=       Structured folklore records
    GET  /api/folklore/{doc_id}      Single folklore record with provenance
    GET  /api/tasks                  Started tasks and their status
    POST /api/tasks                  Start a crawl task  {"url", "max_pages"?, "depth"?}
    GET  /api/tasks/{id}/manifest    sources.json for a completed task
    GET  /api/tasks/{id}/evidence    evidence.json for a completed task
    GET  /api/tasks/{id}/results     result.json for a completed task
    GET  /api/events                 SSE stream of pipeline events
"""

import argparse
import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from app.api.server import api_service
from app.config.logging import get_logger
from app.config.settings import get_settings
from app.crawler.manager import CrawlManager
from app.events.emitter import EventType, default_emitter
from app.pipeline import process_crawl_results
from app.storage.repository import JSONFolkloreRepository

logger = get_logger("api.run_server")

_SSE_HEADERS = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/event-stream\r\n"
    "Cache-Control: no-cache\r\n"
    "Connection: keep-alive\r\n"
    "Access-Control-Allow-Origin: *\r\n"
    "\r\n"
).encode()


def _sse_payload(event) -> bytes:
    """Serialize a PipelineEvent as an SSE data frame."""
    data = json.loads(event.model_dump_json())
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")


class LokkathaHTTPServer:
    """Minimal async HTTP server routing to LokkathaAPIService + live SSE."""

    def __init__(
        self,
        repo: Optional[JSONFolkloreRepository] = None,
        service=None,
    ) -> None:
        self.service = service or api_service
        if repo is not None:
            self.service.repo = repo
        # task_id -> status dict, visible via GET /api/tasks
        self.tasks: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------ HTTP

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Parse one HTTP request and dispatch it. SSE requests take over the socket."""
        try:
            request_line = await asyncio.wait_for(reader.readline(), timeout=15.0)
            if not request_line:
                return
            try:
                method, raw_path, _ = request_line.decode("latin-1").strip().split(" ", 2)
            except ValueError:
                await self._write_json(writer, 400, {"error": "malformed request line"})
                return

            headers: Dict[str, str] = {}
            while True:
                line = await reader.readline()
                if line in (b"\r\n", b"\n", b""):
                    break
                key, _, value = line.decode("latin-1").partition(":")
                headers[key.strip().lower()] = value.strip()

            body = b""
            content_length = int(headers.get("content-length", "0") or 0)
            if content_length > 0:
                body = await reader.readexactly(content_length)

            if method == "GET" and urlparse(raw_path).path == "/api/events":
                await self._handle_sse(writer)
                return

            status, payload = await self._route(method, raw_path, body)
            await self._write_json(writer, status, payload)
        except asyncio.TimeoutError:
            await self._write_json(writer, 408, {"error": "request timeout"})
        except (ConnectionResetError, BrokenPipeError):
            pass
        except Exception as exc:  # never let one request kill the server
            logger.error("http_handler_error", error=str(exc), exc_info=True)
            try:
                await self._write_json(writer, 500, {"error": "internal server error"})
            except Exception:
                pass
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def _write_json(self, writer: asyncio.StreamWriter, status: int, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        reason = {200: "OK", 400: "Bad Request", 404: "Not Found", 405: "Method Not Allowed",
                  408: "Request Timeout", 500: "Internal Server Error"}.get(status, "OK")
        head = (
            f"HTTP/1.1 {status} {reason}\r\n"
            f"Content-Type: application/json; charset=utf-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"Access-Control-Allow-Origin: *\r\n"
            f"Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
            f"Access-Control-Allow-Headers: Content-Type\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        ).encode("latin-1")
        writer.write(head + body)
        await writer.drain()

    # --------------------------------------------------------------- routing

    async def _route(self, method: str, raw_path: str, body: bytes) -> Tuple[int, Any]:
        if method == "OPTIONS":
            return 200, {"ok": True}

        parsed = urlparse(raw_path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)
        data: Dict[str, Any] = {}
        if method == "POST":
            try:
                data = json.loads(body.decode("utf-8")) if body else {}
                if not isinstance(data, dict):
                    raise ValueError("body must be a JSON object")
            except (ValueError, UnicodeDecodeError) as exc:
                return 400, {"error": f"invalid JSON body: {exc}"}

        if path == "/api/health" and method == "GET":
            return 200, self.service.get_health()

        if path == "/api/sources":
            if method == "GET":
                return 200, self.service.list_sources()
            if method == "POST":
                url = data.get("url")
                if not url:
                    return 400, {"error": "missing required field: url"}
                try:
                    return 200, self.service.register_source(
                        url=url,
                        page_title=data.get("page_title"),
                        platform_name=data.get("platform_name"),
                    )
                except Exception as exc:
                    return 400, {"error": str(exc)}

        if path == "/api/folklore" and method == "GET":
            region = query.get("region", [None])[0]
            return 200, self.service.list_folklore(region=region)

        if path.startswith("/api/folklore/") and method == "GET":
            try:
                doc = self.service.get_folklore(path.split("/", 3)[3])
            except ValueError as exc:  # unsafe id (path traversal attempt)
                return 400, {"error": str(exc)}
            return (200, doc) if doc else (404, {"error": "document not found"})

        if path == "/api/tasks":
            if method == "GET":
                return 200, list(self.tasks.values())
            if method == "POST":
                return await self._start_task(data)

        if path.startswith("/api/tasks/") and method == "GET":
            parts = path.split("/")
            if len(parts) == 5 and parts[4] in ("manifest", "evidence", "results"):
                task_id, kind = parts[3], parts[4]
                loader = {
                    "manifest": self.service.get_task_manifest,
                    "evidence": self.service.get_task_evidence,
                    "results": self.service.get_task_results,
                }[kind]
                payload = loader(task_id)
                return (200, payload) if payload is not None else (404, {"error": f"no {kind} for task {task_id!r}"})

        return 404, {"error": f"no route for {method} {path}"}

    # ----------------------------------------------------------------- tasks

    async def _start_task(self, data: Dict[str, Any]) -> Tuple[int, Any]:
        url = data.get("url")
        if not url:
            return 400, {"error": "missing required field: url"}

        max_pages = data.get("max_pages", 5)
        depth = data.get("depth", 0)
        if not isinstance(max_pages, int) or max_pages < 0:
            return 400, {"error": "max_pages must be a non-negative integer"}
        if not isinstance(depth, int) or depth < 0:
            return 400, {"error": "depth must be a non-negative integer"}

        task_id = datetime.now(timezone.utc).strftime("task_%Y%m%d_%H%M%S_%f")
        task = {
            "task_id": task_id,
            "url": url,
            "max_pages": max_pages,
            "depth": depth,
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        self.tasks[task_id] = task
        asyncio.create_task(self._run_crawl(task_id, url, max_pages, depth))
        return 200, task

    async def _run_crawl(self, task_id: str, url: str, max_pages: int, depth: int) -> None:
        """Execute a real in-process crawl so SSE clients see live events."""
        task = self.tasks[task_id]
        try:
            await default_emitter.emit(
                EventType.TASK_STARTED, task_id=task_id,
                message=f"Crawl task started: {url} (max_pages={max_pages}, depth={depth})",
            )
            settings = get_settings()
            manager = CrawlManager(settings)
            results = await manager.crawl(seeds=[url], max_pages=max_pages, max_depth=depth)
            docs, evidence_records, duplicates = process_crawl_results(results, settings=settings)

            repo = JSONFolkloreRepository(base_dir=settings.storage.structured_dir)
            for doc in docs:
                repo.save(doc)
                await default_emitter.emit(
                    EventType.FOLKLORE_EXTRACTED, task_id=task_id, source_id=doc.source.source_id,
                    data={"document_id": doc.id, "title": doc.title},
                    message=f"Extracted folklore document: {doc.title}",
                )

            task.update(
                status="completed",
                completed_at=datetime.now(timezone.utc).isoformat(),
                pages_fetched=len(results),
                documents_extracted=len(docs),
                duplicates_skipped=duplicates,
                evidence_records=len(evidence_records),
            )
            await default_emitter.emit(
                EventType.TASK_COMPLETED, task_id=task_id,
                data={k: task[k] for k in ("pages_fetched", "documents_extracted", "duplicates_skipped")},
                message=f"Crawl task completed: {len(docs)} folklore documents extracted",
            )
        except Exception as exc:
            logger.error("task_crawl_failed", task_id=task_id, error=str(exc), exc_info=True)
            task.update(status="failed", error=str(exc),
                        completed_at=datetime.now(timezone.utc).isoformat())
            await default_emitter.emit(
                EventType.TASK_FAILED, task_id=task_id,
                message=f"Crawl task failed: {exc}",
            )

    # ------------------------------------------------------------------- SSE

    async def _handle_sse(self, writer: asyncio.StreamWriter) -> None:
        """Stream pipeline events until the client disconnects."""
        queue = default_emitter.subscribe()
        try:
            writer.write(_SSE_HEADERS)
            # Replay recent history so newly connected dashboards have context.
            for event in default_emitter.get_recent_events(20):
                writer.write(_sse_payload(event))
            await writer.drain()
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                    writer.write(_sse_payload(event))
                except asyncio.TimeoutError:
                    writer.write(b": keepalive\n\n")  # comment frame keeps proxies happy
                await writer.drain()
        except (ConnectionResetError, BrokenPipeError, asyncio.CancelledError):
            pass
        finally:
            default_emitter.unsubscribe(queue)


async def serve(host: str, port: int) -> None:
    server = LokkathaHTTPServer()
    tcp = await asyncio.start_server(server.handle_client, host, port)
    addr = ", ".join(str(sock.getsockname()) for sock in tcp.sockets)
    print(f"Lokkatha API server listening on http://{addr}")
    print(f"  Health:   GET  /api/health")
    print(f"  Events:   GET  /api/events   (Server-Sent Events)")
    print(f"  Start a crawl: POST /api/tasks  {{\"url\": \"https://...\", \"max_pages\": 5}}")
    async with tcp:
        await tcp.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Lokkatha API + SSE server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    args = parser.parse_args()
    try:
        asyncio.run(serve(args.host, args.port))
    except KeyboardInterrupt:
        print("\nShutting down.")


if __name__ == "__main__":
    main()
