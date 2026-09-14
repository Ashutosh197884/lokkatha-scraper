import React from "react";
import { GlassPanel } from "../common/GlassPanel";
import { ArrowUpRight, Plus, Sparkles } from "lucide-react";

interface DiscoveredMetricCardProps {
  totalDiscovered: number;
  onOpenAddSourceModal: () => void;
}

export const DiscoveredMetricCard: React.FC<DiscoveredMetricCardProps> = ({
  totalDiscovered,
  onOpenAddSourceModal,
}) => {
  return (
    <GlassPanel className="p-4 flex flex-col justify-between h-full relative overflow-hidden group">
      {/* Background glow orb */}
      <div className="absolute -top-12 -right-12 w-28 h-28 bg-indigo-500/20 rounded-full blur-2xl pointer-events-none group-hover:bg-cyan-500/30 transition-all duration-500" />

      {/* Metric Title & Value */}
      <div>
        <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
          Total Discovered
        </span>
        <div className="flex items-baseline gap-2 mt-1">
          <p className="text-2xl font-bold font-mono text-white tracking-tight">
            {totalDiscovered.toLocaleString()}
          </p>
          <div className="flex items-center text-[11px] font-semibold text-emerald-400 font-mono">
            <ArrowUpRight className="w-3 h-3 mr-0.5" />
            +12% <span className="text-slate-500 font-normal ml-1">vs last hr</span>
          </div>
        </div>
      </div>

      {/* Sparkline Gradient Area */}
      <div className="h-10 my-2 w-full">
        <svg className="w-full h-full" viewBox="0 0 160 40" preserveAspectRatio="none">
          <defs>
            <linearGradient id="purpleGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#818cf8" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#818cf8" stopOpacity="0.0" />
            </linearGradient>
          </defs>
          <path
            d="M 0,35 Q 30,30 60,20 T 120,10 T 160,5 L 160,40 L 0,40 Z"
            fill="url(#purpleGrad)"
          />
          <path
            d="M 0,35 Q 30,30 60,20 T 120,10 T 160,5"
            fill="none"
            stroke="#a855f7"
            strokeWidth="2"
          />
        </svg>
      </div>

      {/* Add New Source Button matching mockup */}
      <button
        onClick={onOpenAddSourceModal}
        className="w-full py-2.5 px-3 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-medium text-xs flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(79,70,229,0.4)] hover:shadow-[0_0_25px_rgba(56,189,248,0.6)] transition-all duration-300 transform active:scale-95"
      >
        <Plus className="w-4 h-4 font-bold" />
        <span>Add New Source</span>
      </button>
    </GlassPanel>
  );
};
