export type SourceStatus =
  | "idle"
  | "connecting"
  | "active"
  | "fetching"
  | "analyzing"
  | "completed"
  | "error"
  | "paused"
  | "disconnected";

export type SourceType =
  | "WEB_PAGE"
  | "BLOG"
  | "NEWS"
  | "WIKI"
  | "DIGITAL_LIBRARY"
  | "ARCHIVE"
  | "ACADEMIC_PAPER"
  | "RESEARCH_REPOSITORY"
  | "GOVERNMENT_DOCUMENT"
  | "MUSEUM"
  | "UNIVERSITY"
  | "BOOK_METADATA"
  | "PDF"
  | "PUBLIC_DATASET"
  | "API"
  | "RSS"
  | "XML"
  | "SITEMAP"
  | "COMMUNITY_ARCHIVE"
  | "ORAL_HISTORY_ARCHIVE"
  | "CULTURAL_DATABASE"
  | "website"
  | "document_collection"
  | "community"; // legacy fallbacks

export type PlanetTextureTheme =
  | "emerald-gas"
  | "deep-ocean"
  | "crimson-ringed"
  | "terrestrial-earth"
  | "golden-dune"
  | "amethyst-ice"
  | "electric-azure"
  | "sandstone-canyon"
  | "toxic-neon";

export interface SourceOrbit {
  radius: number;          // Distance from central Sun
  angle: number;           // Current orbital radian angle
  speed: number;           // Orbital speed
  inclination: number;     // Vertical plane inclination angle in radians
  eccentricity?: number;   // Slight ellipse eccentricity
}

export interface SourceRotation {
  speed: number;           // Axial rotation speed
  tilt: number;            // Axial tilt in degrees
}

export interface SourceMetrics {
  pagesProcessed: number;
  recordsFound: number;
  errorsCount: number;
  latencyMs: number;
  currentRate: number;     // Pages per minute
  lastCrawledAt?: string;
  successRate: number;     // percentage 0 - 100
}

export interface SourceVisual {
  color: string;
  glowColor: string;
  ringColor?: string;
  hasRings?: boolean;
  ringRadius?: number;
  radius: number;          // Planet sphere scale
  theme: PlanetTextureTheme;
  iconName?: string;
}

export interface DataSource {
  id: string;
  name: string;
  url: string;
  domain?: string;
  platformName?: string;
  type: SourceType;
  status: SourceStatus;
  region: string;
  language: string;
  category: string;
  description: string;
  orbit: SourceOrbit;
  rotation: SourceRotation;
  visual: SourceVisual;
  metrics: SourceMetrics;
  tags: string[];
  maxPages: number;
  maxDepth: number;
  crawlFrequency: string;
  lastError?: string;
  pulseActive?: boolean;
}
