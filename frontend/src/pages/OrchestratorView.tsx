import React from "react";
import { DataSource } from "../types/source";
import { ScrapeTask } from "../types/task";
import {
  ActivityLogItem,
  QueueItem,
  ResourceMetrics as ResourceMetricsType,
  SystemStats,
} from "../types/orchestration";
import { SolarSystemCanvas } from "../components/orchestrator/SolarSystemCanvas";
import { SystemStatusCard } from "../components/dashboard/SystemStatusCard";
import { CurrentTaskCard } from "../components/dashboard/CurrentTaskCard";
import { LiveActivityFeed } from "../components/dashboard/LiveActivityFeed";
import { ResourceMetrics } from "../components/dashboard/ResourceMetrics";
import { QueueOverview } from "../components/dashboard/QueueOverview";
import { DiscoveredMetricCard } from "../components/dashboard/DiscoveredMetricCard";

interface OrchestratorViewProps {
  sources: DataSource[];
  activeTask: ScrapeTask;
  stats: SystemStats;
  resources: ResourceMetricsType;
  queue: QueueItem[];
  activities: ActivityLogItem[];
  selectedSourceId: string | null;
  onSelectSource: (source: DataSource) => void;
  onResetSelection: () => void;
  onOpenAddSourceModal: () => void;
  simulationSpeed: number;
  reducedMotion: boolean;
}

export const OrchestratorView: React.FC<OrchestratorViewProps> = ({
  sources,
  activeTask,
  stats,
  resources,
  queue,
  activities,
  selectedSourceId,
  onSelectSource,
  onResetSelection,
  onOpenAddSourceModal,
  simulationSpeed,
  reducedMotion,
}) => {
  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-4rem)] overflow-hidden bg-space-950 p-3 gap-3">
      {/* Top Main Section: Solar System Center + Right Task Panels */}
      <div className="flex-1 flex gap-3 min-h-0">
        {/* Center: Interactive 3D Solar System Canvas */}
        <div className="flex-1 rounded-2xl overflow-hidden border border-white/10 relative shadow-2xl bg-space-950 flex flex-col">
          <SolarSystemCanvas
            sources={sources}
            simulationSpeed={simulationSpeed}
            selectedSourceId={selectedSourceId}
            onSelectSource={onSelectSource}
            onResetSelection={onResetSelection}
            reducedMotion={reducedMotion}
          />
        </div>

        {/* Right Side Status Panels */}
        <div className="w-80 flex flex-col gap-3 overflow-y-auto pr-0.5 select-none">
          <SystemStatusCard stats={stats} />
          <CurrentTaskCard task={activeTask} />
        </div>
      </div>

      {/* Bottom Telemetry & Activity Panels Grid (Matching mockup image 2) */}
      <div className="h-56 grid grid-cols-1 md:grid-cols-4 gap-3 select-none flex-shrink-0">
        {/* 1. Live Activity Feed */}
        <div className="h-full">
          <LiveActivityFeed
            activities={activities}
            onSourceSelect={(id) => {
              const s = sources.find((src) => src.id === id);
              if (s) onSelectSource(s);
            }}
          />
        </div>

        {/* 2. Resource Utilization Gauges */}
        <div className="h-full">
          <ResourceMetrics resources={resources} />
        </div>

        {/* 3. Queue Overview */}
        <div className="h-full">
          <QueueOverview
            queue={queue}
            onSelectSource={(id) => {
              const s = sources.find((src) => src.id === id);
              if (s) onSelectSource(s);
            }}
          />
        </div>

        {/* 4. Total Discovered & Add Source CTA */}
        <div className="h-full">
          <DiscoveredMetricCard
            totalDiscovered={stats.storiesDiscovered}
            onOpenAddSourceModal={onOpenAddSourceModal}
          />
        </div>
      </div>
    </div>
  );
};
