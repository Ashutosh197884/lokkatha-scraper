import React from "react";
import { GlassPanel } from "../common/GlassPanel";
import { MetricGauge } from "../common/MetricGauge";
import { ResourceMetrics as ResourceMetricsType } from "../../types/orchestration";
import { Cpu } from "lucide-react";

interface ResourceMetricsProps {
  resources: ResourceMetricsType;
}

export const ResourceMetrics: React.FC<ResourceMetricsProps> = ({ resources }) => {
  return (
    <GlassPanel className="p-4 flex flex-col justify-between h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider font-sans">
            Resource Utilization
          </h2>
        </div>
      </div>

      {/* 4 Circular Donut Gauges */}
      <div className="grid grid-cols-4 gap-2 my-2">
        <MetricGauge label="CPU" value={resources.cpuUsage} color="#f59e0b" size={64} />
        <MetricGauge label="Memory" value={resources.memoryUsage} color="#38bdf8" size={64} />
        <MetricGauge label="Network" value={resources.networkUsage} color="#a855f7" size={64} />
        <MetricGauge label="Storage" value={resources.storageUsage} color="#10b981" size={64} />
      </div>

      {/* Processing Speed Sparkline & Metric */}
      <div className="pt-2 border-t border-white/5 flex items-center justify-between text-xs">
        <span className="text-[11px] text-slate-400">Processing Speed</span>
        <div className="flex items-center gap-3">
          {/* Mini line wave */}
          <div className="w-20 h-4">
            <svg className="w-full h-full" viewBox="0 0 80 20" preserveAspectRatio="none">
              <path
                d="M 0,10 Q 15,2 30,10 T 60,10 T 80,6"
                fill="none"
                stroke="#38bdf8"
                strokeWidth="1.5"
              />
            </svg>
          </div>
          <span className="font-mono text-cyan-300 font-bold text-xs">
            {resources.processingSpeed} pages/min
          </span>
        </div>
      </div>
    </GlassPanel>
  );
};
