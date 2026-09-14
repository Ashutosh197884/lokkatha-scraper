import React from "react";
import { DataSource } from "../../types/source";
import { GlassPanel } from "../common/GlassPanel";
import { StatusBadge } from "../common/StatusBadge";
import {
  Activity,
  ArrowUpRight,
  BookOpen,
  CheckCircle2,
  Clock,
  Compass,
  ExternalLink,
  Layers,
  Pause,
  Play,
  RefreshCw,
  Sliders,
  Square,
  X,
  Zap,
} from "lucide-react";

interface SourceDetailDrawerProps {
  source: DataSource | null;
  onClose: () => void;
  onToggleStatus: (sourceId: string, newStatus: any) => void;
  onViewLibrary: () => void;
}

export const SourceDetailDrawer: React.FC<SourceDetailDrawerProps> = ({
  source,
  onClose,
  onToggleStatus,
  onViewLibrary,
}) => {
  if (!source) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-96 z-50 p-4 pointer-events-none flex flex-col justify-center">
      <GlassPanel
        variant="glow-blue"
        className="w-full max-h-[92vh] overflow-y-auto pointer-events-auto p-5 relative flex flex-col justify-between border-cyan-500/40 shadow-[0_0_40px_rgba(0,0,0,0.8)] animate-in slide-in-from-right duration-300"
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-all"
        >
          <X className="w-4 h-4" />
        </button>

        <div>
          {/* Header */}
          <div className="flex items-center gap-3 mb-3">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center border shadow-lg"
              style={{
                backgroundColor: `${source.visual.color}20`,
                borderColor: `${source.visual.color}50`,
                boxShadow: `0 0 15px ${source.visual.glowColor}40`,
              }}
            >
              <span
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: source.visual.color }}
              />
            </div>
            <div>
              <h2 className="font-bold text-base text-white font-sans">
                {source.name}
              </h2>
              <a
                href={source.url}
                target="_blank"
                rel="noreferrer"
                className="text-xs text-cyan-400 hover:underline flex items-center gap-1"
              >
                <span className="truncate max-w-[190px]">{source.url}</span>
                <ExternalLink className="w-3 h-3 flex-shrink-0" />
              </a>
            </div>
          </div>

          {/* Status and Type Pills */}
          <div className="flex items-center gap-2 mb-4">
            <StatusBadge status={source.status} />
            <span className="px-2.5 py-0.5 rounded-full text-xs font-mono bg-space-900 border border-white/10 text-slate-300 capitalize">
              {source.type.replace("_", " ")}
            </span>
          </div>

          {/* Description */}
          <p className="text-xs text-slate-300 leading-relaxed mb-4 bg-space-900/60 p-3 rounded-xl border border-white/5">
            {source.description}
          </p>

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 gap-2.5 mb-4 font-mono">
            <div className="p-2.5 rounded-xl bg-space-900/80 border border-white/5">
              <span className="text-[10px] text-slate-400 uppercase">Pages Crawled</span>
              <p className="text-lg font-bold text-white mt-0.5">
                {source.metrics.pagesProcessed}
              </p>
            </div>

            <div className="p-2.5 rounded-xl bg-space-900/80 border border-white/5">
              <span className="text-[10px] text-slate-400 uppercase">Folklore Found</span>
              <p className="text-lg font-bold text-cyan-400 mt-0.5">
                {source.metrics.recordsFound}
              </p>
            </div>

            <div className="p-2.5 rounded-xl bg-space-900/80 border border-white/5">
              <span className="text-[10px] text-slate-400 uppercase">Current Rate</span>
              <p className="text-sm font-bold text-emerald-400 mt-0.5">
                {source.metrics.currentRate} p/min
              </p>
            </div>

            <div className="p-2.5 rounded-xl bg-space-900/80 border border-white/5">
              <span className="text-[10px] text-slate-400 uppercase">Last Crawled</span>
              <p className="text-xs font-semibold text-slate-300 mt-1">
                {source.metrics.lastCrawledAt || "Never"}
              </p>
            </div>
          </div>

          {/* Planetary Orbital Telemetry */}
          <div className="p-3 rounded-xl bg-space-900/40 border border-white/5 mb-4 text-xs font-mono space-y-1 text-slate-400">
            <div className="flex justify-between">
              <span>Orbit Radius:</span>
              <span className="text-slate-200">{source.orbit.radius} AU</span>
            </div>
            <div className="flex justify-between">
              <span>Orbital Speed:</span>
              <span className="text-slate-200">{source.orbit.speed.toFixed(4)} rad/s</span>
            </div>
            <div className="flex justify-between">
              <span>Axial Tilt:</span>
              <span className="text-slate-200">{source.rotation.tilt}&deg;</span>
            </div>
          </div>

          {/* Regional & Language Tags */}
          <div className="mb-4">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1.5 font-sans">
              Metadata & Region
            </span>
            <div className="flex flex-wrap gap-1.5">
              <span className="px-2 py-0.5 rounded-md bg-indigo-500/10 border border-indigo-500/30 text-[11px] text-indigo-300">
                {source.region}
              </span>
              <span className="px-2 py-0.5 rounded-md bg-purple-500/10 border border-purple-500/30 text-[11px] text-purple-300">
                {source.language}
              </span>
              {source.tags.map((t) => (
                <span
                  key={t}
                  className="px-2 py-0.5 rounded-md bg-space-900 border border-white/10 text-[11px] text-slate-400"
                >
                  #{t}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="space-y-2 pt-3 border-t border-white/10">
          <div className="grid grid-cols-2 gap-2">
            {source.status === "fetching" || source.status === "active" ? (
              <button
                onClick={() => onToggleStatus(source.id, "idle")}
                className="py-2 px-3 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 text-xs font-medium flex items-center justify-center gap-1.5 transition-all"
              >
                <Pause className="w-3.5 h-3.5" />
                <span>Pause Source</span>
              </button>
            ) : (
              <button
                onClick={() => onToggleStatus(source.id, "fetching")}
                className="py-2 px-3 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs font-medium flex items-center justify-center gap-1.5 transition-all"
              >
                <Play className="w-3.5 h-3.5" />
                <span>Start Crawl</span>
              </button>
            )}

            <button
              onClick={() => onToggleStatus(source.id, "analyzing")}
              className="py-2 px-3 rounded-xl bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 border border-blue-500/40 text-xs font-medium flex items-center justify-center gap-1.5 transition-all"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Deep Analyze</span>
            </button>
          </div>

          <button
            onClick={onViewLibrary}
            className="w-full py-2 px-3 rounded-xl bg-space-900 hover:bg-white/10 border border-white/10 text-xs text-slate-200 font-medium flex items-center justify-center gap-1.5 transition-all"
          >
            <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
            <span>View Extracted Folklore ({source.metrics.recordsFound})</span>
          </button>
        </div>
      </GlassPanel>
    </div>
  );
};
