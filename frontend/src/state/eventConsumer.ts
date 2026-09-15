/**
 * Real-time event consumer architecture for Lokkatha pipeline events.
 * Consumes WebSocket, SSE, or streaming simulation events to update state.
 */

import { DataSource } from "../types/source";
import { ScrapeTask } from "../types/task";
import { ActivityLogItem, FolkloreItem, SystemStats } from "../types/orchestration";

export type PipelineEventType =
  | "source.discovered"
  | "source.connected"
  | "source.started"
  | "source.completed"
  | "source.failed"
  | "page.discovered"
  | "page.fetched"
  | "page.failed"
  | "document.extracted"
  | "evidence.created"
  | "folklore.discovered"
  | "folklore.extracted"
  | "folklore.validated"
  | "task.started"
  | "task.progress"
  | "task.completed"
  | "task.failed";

export interface PipelineEventMessage {
  event_type: PipelineEventType;
  timestamp: string;
  task_id?: string;
  source_id?: string;
  data?: Record<string, any>;
  message: string;
}

export class PipelineEventConsumer {
  private sseUrl: string;
  private eventSource: EventSource | null = null;
  private listeners: ((event: PipelineEventMessage) => void)[] = [];

  constructor(sseUrl: string = "/api/events") {
    this.sseUrl = sseUrl;
  }

  public connect(): void {
    if (typeof window === "undefined" || !window.EventSource) return;
    try {
      this.eventSource = new EventSource(this.sseUrl);
      this.eventSource.onmessage = (e) => {
        try {
          const parsed: PipelineEventMessage = JSON.parse(e.data);
          this.notifyListeners(parsed);
        } catch (err) {
          console.warn("Error parsing SSE event payload:", err);
        }
      };
      this.eventSource.onerror = () => {
        // SSE connection fallback to polling/simulation mode
      };
    } catch {
      // Offline / standalone UI fallback
    }
  }

  public subscribe(callback: (event: PipelineEventMessage) => void): () => void {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== callback);
    };
  }

  public notifyListeners(event: PipelineEventMessage): void {
    this.listeners.forEach((l) => l(event));
  }

  public disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}

export const defaultEventConsumer = new PipelineEventConsumer();
