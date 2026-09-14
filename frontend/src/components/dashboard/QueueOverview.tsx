import React from "react";
import { GlassPanel } from "../common/GlassPanel";
import { QueueItem } from "../../types/orchestration";
import { ListOrdered } from "lucide-react";

interface QueueOverviewProps {
  queue: QueueItem[];
  onSelectSource?: (sourceId: string) => void;
}

export const QueueOverview: React.FC<QueueOverviewProps> = ({
  queue,
  onSelectSource,
}) => {
  return (
    <GlassPanel className="p-4 flex flex-col justify-between h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <ListOrdered className="w-4 h-4 text-cyan-400" />
          <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider font-sans">
            Queue Overview
          </h2>
        </div>
      </div>

      {/* Queue breakdown per source */}
      <div className="space-y-1.5 overflow-y-auto max-h-[140px] pr-1">
        {queue.map((item) => (
          <div
            key={item.sourceId}
            onClick={() => onSelectSource?.(item.sourceId)}
            className="flex items-center justify-between text-xs py-1 px-1.5 rounded hover:bg-white/5 cursor-pointer transition-colors"
          >
            <div className="flex items-center gap-2">
              <span
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ backgroundColor: item.color }}
              />
              <span className="text-slate-300 font-medium truncate max-w-[120px]">
                {item.sourceName}
              </span>
            </div>
            <span className="font-mono text-slate-400 text-xs font-semibold">
              {item.pendingUrlsCount}
            </span>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
};
