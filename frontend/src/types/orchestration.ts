import { SourceType } from "./source";

export interface EvidenceRecord {
  evidenceId: string;
  sourceId: string;
  documentId: string;
  url: string;
  claim: string;
  evidenceType: "direct" | "inferred" | "generated";
  location?: string;
  retrievedAt: string;
  contextSnippet?: string;
}

export interface VariantVersion {
  variantId: string;
  variantTitle: string;
  sourcePlatform: string;
  sourceUrl: string;
  region?: string;
  language?: string;
  differences: string[];
}

export interface FolkloreItem {
  id: string;
  title: string;
  alternateTitle?: string;
  folkloreType: string;
  region: string[];
  language: string[];
  originalLanguage?: string;
  sourceName: string;
  sourceUrl: string;
  sourceType?: SourceType;
  domain?: string;
  author?: string | null;
  publishedAt?: string | null;
  discoveredAt: string;
  confidence: number;
  summary: string;
  story?: string;
  generatedSummary?: string;
  characters: string[];
  locations?: string[];
  motifs: string[];
  tekCount: number;
  evidenceCount?: number;
  evidenceList?: EvidenceRecord[];
  variants?: VariantVersion[];
  verified: boolean;
}

export interface ActivityLogItem {
  id: string;
  timestamp: string;
  sourceId: string;
  sourceName: string;
  eventType: "fetch" | "extract" | "validate" | "store" | "connect" | "queue" | "error";
  message: string;
  level: "info" | "success" | "warning" | "error";
}

export interface QueueItem {
  sourceId: string;
  sourceName: string;
  pendingUrlsCount: number;
  color: string;
}

export interface SystemStats {
  status: "idle" | "running" | "paused" | "completed";
  sourcesActive: number;
  tasksRunning: number;
  pagesProcessed: number;
  storiesDiscovered: number;
  documentsFound?: number;
  relevantDocuments?: number;
  evidenceRecords?: number;
  successRate: number;
  totalDataProcessedGb: number;
}

export interface ResourceMetrics {
  cpuUsage: number;
  memoryUsage: number;
  networkUsage: number;
  storageUsage: number;
  processingSpeed: number; // records per minute
  speedHistory: number[];
}
