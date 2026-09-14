import React from "react";
import { GlassPanel } from "../common/GlassPanel";
import { StatusBadge } from "../common/StatusBadge";
import { Activity, CheckCircle2, Cpu, Globe, Zap } from "lucide-react";
import { SystemStats } from "../../types/orchestration";

interface SystemStatusCardProps {
  stats: SystemStats;
}

export const SystemStatusCard: React.FC<SystemStatusCardProps> = ({ stats }) => {
  return (
    <GlassPanel className="p-4 relative group">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <h2 className="text-sm font-semibold text-slate-100 tracking-wide font-sans">
            System Status
          </h2>
        </div>
        <StatusBadge status="running" />
      </div>

      {/* 2x2 Key Metric Grid */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="p-3 rounded-xl bg-space-900/60 border border-white/5">
          <p className="text-2xl font-bold font-mono text-slate-100 tracking-tight">
            {stats.sourcesActive}
          </p>
          <p className="text-[11px] text-slate-400 mt-0.5">Sources Active</p>
        </div>

        <div className="p-3 rounded-xl bg-space-900/60 border border-white/5">
          <p className="text-2xl font-bold font-mono text-cyan-400 tracking-tight">
            {stats.tasksRunning}
          </p>
          <p className="text-[11px] text-slate-400 mt-0.5">Tasks in Progress</p>
        </div>

        <div className="p-3 rounded-xl bg-space-900/60 border border-white/5">
          <p className="text-2xl font-bold font-mono text-slate-100 tracking-tight">
            {stats.pagesProcessed.toLocaleString()}
          </p>
          <p className="text-[11px] text-slate-400 mt-0.5">Pages Processed</p>
        </div>

        <div className="p-3 rounded-xl bg-space-900/60 border border-white/5">
          <p className="text-2xl font-bold font-mono text-emerald-400 tracking-tight">
            {stats.successRate}%
          </p>
          <p className="text-[11px] text-slate-400 mt-0.5">Success Rate</p>
        </div>
      </div>

      {/* Live Sine Wave Sparkline */}
      <div className="h-9 w-full overflow-hidden rounded-lg bg-space-950/60 border border-white/5 relative flex items-center">
        <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 200 40">
          <path
            d="M 0,20 Q 25,5 50,20 T 100,20 T 150,20 T 200,20"
            fill="none"
            stroke="#38bdf8"
            strokeWidth="2"
            className="opacity-80"
          />
          <path
            d="M 0,20 Q 25,35 50,20 T 100,20 T 150,20 T 200,20"
            fill="none"
            stroke="#818cf8"
            strokeWidth="1.5"
            strokeDasharray="4 2"
            className="opacity-40"
          />
        </svg>
      </div>
    </GlassPanel>
  );
};
