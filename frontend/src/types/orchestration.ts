import { DataSource } from "./source";
import { ScrapeTask } from "./task";

export interface ResourceMetrics {
  cpuUsage: number;     // 0 - 100
  memoryUsage: number;  // 0 - 100
  networkUsage: number; // 0 - 100
  storageUsage: number; // 0 - 100
  processingSpeed: number; // pages / min
  speedHistory: number[];  // last 20 ticks for sparkline
}

export interface SystemStats {
  status: "optimal" | "running" | "warning" | "error" | "paused";
  sourcesActive: number;
  tasksRunning: number;
  pagesProcessed: number;
  storiesDiscovered: number;
  successRate: number;
  totalDataProcessedGb: number;
}

export interface ActivityLogItem {
  id: string;
  timestamp: string;
  sourceId?: string;
  sourceName: string;
  eventType: "fetch" | "extract" | "validate" | "store" | "error" | "connect" | "queue";
  message: string;
  level: "info" | "success" | "warning" | "error";
  details?: Record<string, any>;
}

export interface QueueItem {
  sourceId: string;
  sourceName: string;
  pendingUrlsCount: number;
  color: string;
}

export interface FolkloreItem {
  id: string;
  title: string;
  alternateTitle?: string;
  folkloreType: string;
  region: string[];
  language: string[];
  sourceName: string;
  sourceUrl: string;
  discoveredAt: string;
  confidence: number;
  summary: string;
  characters: string[];
  motifs: string[];
  tekCount: number;
  verified: boolean;
}

export interface BackendEvent {
  event: string;
  timestamp: string;
  sourceId?: string;
  url?: string;
  pagesProcessed?: number;
  storiesDiscovered?: number;
  data?: any;
}
