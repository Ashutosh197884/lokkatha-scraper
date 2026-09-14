import React from "react";
import { GlassPanel } from "../common/GlassPanel";
import { ActivityLogItem } from "../../types/orchestration";
import { Radio } from "lucide-react";

interface LiveActivityFeedProps {
  activities: ActivityLogItem[];
  onSourceSelect?: (sourceId: string) => void;
}

export const LiveActivityFeed: React.FC<LiveActivityFeedProps> = ({
  activities,
  onSourceSelect,
}) => {
  return (
    <GlassPanel className="p-4 flex flex-col h-full">
      {/* Header with Live Indicator */}
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-white/5">
        <div className="flex items-center gap-2">
          <div className="relative flex items-center justify-center">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping absolute" />
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
          </div>
          <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider font-sans">
            Live Activity
          </h2>
        </div>
        <span className="text-[10px] font-mono text-slate-400">Stream Online</span>
      </div>

      {/* Activity Log List */}
      <div className="space-y-2 overflow-y-auto pr-1 flex-1 max-h-[160px] font-mono text-xs">
        {activities.map((item) => (
          <div
            key={item.id}
            className="flex items-start gap-2.5 hover:bg-white/5 p-1 rounded transition-colors group cursor-pointer"
            onClick={() => item.sourceId && onSourceSelect?.(item.sourceId)}
          >
            <span className="text-slate-500 text-[11px] whitespace-nowrap">
              {item.timestamp}
            </span>

            <span className="text-cyan-400 font-semibold whitespace-nowrap group-hover:underline">
              [{item.sourceName}]
            </span>

            <span className="text-slate-300 truncate text-[11px]">
              {item.message}
            </span>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
};
