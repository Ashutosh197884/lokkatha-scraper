export type TaskStageStatus = "pending" | "running" | "completed" | "failed";

export interface TaskStage {
  id: string;
  name: string;
  status: TaskStageStatus;
  duration?: string;
  message?: string;
}

export interface ScrapeTask {
  id: string;
  title: string;
  description?: string;
  targetRegion: string;
  sourceIds: string[];
  status: "idle" | "running" | "paused" | "completed" | "failed";
  progress: number; // 0 to 100
  stages: TaskStage[];
  currentStageIndex: number;
  startTime: string;
  elapsedSeconds: number;
  pagesProcessed: number;
  storiesDiscovered: number;
  currentSource: string;
  currentOperation: string;
  errorCount: number;
}
