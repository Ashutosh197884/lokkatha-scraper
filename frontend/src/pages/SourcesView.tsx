import React, { useState } from "react";
import { DataSource, SourceType } from "../types/source";
import { GlassPanel } from "../components/common/GlassPanel";
import { StatusBadge } from "../components/common/StatusBadge";
import {
  ExternalLink,
  Filter,
  Globe,
  Orbit,
  Pause,
  Play,
  Plus,
  RefreshCw,
  Search,
} from "lucide-react";

interface SourcesViewProps {
  sources: DataSource[];
  onSelectSource: (source: DataSource) => void;
  onOpenAddModal: () => void;
  onToggleStatus: (sourceId: string, status: any) => void;
}

export const SourcesView: React.FC<SourcesViewProps> = ({
  sources,
  onSelectSource,
  onOpenAddModal,
  onToggleStatus,
}) => {
  const [filterType, setFilterType] = useState<string>("all");
  const [search, setSearch] = useState("");

  const filtered = sources.filter((s) => {
    const matchesType = filterType === "all" || s.type === filterType;
    const matchesSearch =
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      s.region.toLowerCase().includes(search.toLowerCase()) ||
      s.language.toLowerCase().includes(search.toLowerCase());
    return matchesType && matchesSearch;
  });

  return (
    <div className="flex-1 p-6 overflow-y-auto bg-space-950 text-slate-100 space-y-6">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold font-sans text-white flex items-center gap-2">
            <Orbit className="w-6 h-6 text-cyan-400" />
            Connected Data Sources ({sources.length})
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Manage target websites, digital archives, and cultural repositories orbiting the core.
          </p>
        </div>

        <button
          onClick={onOpenAddModal}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-medium text-xs flex items-center gap-2 shadow-glow-cyan transition-all"
        >
          <Plus className="w-4 h-4 font-bold" />
          <span>Add New Source</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1 max-w-md relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Filter by source name, region, or language..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-space-900 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex items-center gap-2">
          {["all", "website", "api", "document_collection", "rss", "community"].map(
            (t) => (
              <button
                key={t}
                onClick={() => setFilterType(t)}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium capitalize transition-all ${
                  filterType === t
                    ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                    : "bg-space-900 text-slate-400 hover:text-slate-200 border border-white/5"
                }`}
              >
                {t.replace("_", " ")}
              </button>
            )
          )}
        </div>
      </div>

      {/* Sources Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((source) => (
          <GlassPanel
            key={source.id}
            variant="interactive"
            className="p-5 flex flex-col justify-between group"
            onClick={() => onSelectSource(source)}
          >
            <div>
              {/* Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2.5">
                  <span
                    className="w-3.5 h-3.5 rounded-full"
                    style={{
                      backgroundColor: source.visual.color,
                      boxShadow: `0 0 10px ${source.visual.glowColor}`,
                    }}
                  />
                  <h3 className="font-bold text-sm text-white font-sans group-hover:text-cyan-300 transition-colors">
                    {source.name}
                  </h3>
                </div>
                <StatusBadge status={source.status} />
              </div>

              {/* URL */}
              <a
                href={source.url}
                target="_blank"
                rel="noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="text-xs text-cyan-400 hover:underline flex items-center gap-1 mb-3"
              >
                <span className="truncate max-w-[240px]">{source.url}</span>
                <ExternalLink className="w-3 h-3 flex-shrink-0" />
              </a>

              {/* Description */}
              <p className="text-xs text-slate-400 line-clamp-2 mb-4 leading-relaxed">
                {source.description}
              </p>

              {/* Telemetry Stats */}
              <div className="grid grid-cols-3 gap-2 p-2.5 rounded-xl bg-space-900/80 border border-white/5 font-mono text-center mb-4">
                <div>
                  <span className="text-[10px] text-slate-500 block uppercase">Pages</span>
                  <span className="text-xs font-bold text-white">
                    {source.metrics.pagesProcessed}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 block uppercase">Folklore</span>
                  <span className="text-xs font-bold text-cyan-400">
                    {source.metrics.recordsFound}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 block uppercase">Rate</span>
                  <span className="text-xs font-bold text-emerald-400">
                    {source.metrics.currentRate} p/m
                  </span>
                </div>
              </div>
            </div>

            {/* Quick Action Footer */}
            <div className="flex items-center justify-between pt-3 border-t border-white/5 text-xs">
              <span className="text-slate-500 font-mono text-[11px]">
                Orbit: {source.orbit.radius} AU
              </span>

              <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                {source.status === "fetching" || source.status === "active" ? (
                  <button
                    onClick={() => onToggleStatus(source.id, "idle")}
                    className="p-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 transition-all"
                    title="Pause Crawl"
                  >
                    <Pause className="w-3.5 h-3.5" />
                  </button>
                ) : (
                  <button
                    onClick={() => onToggleStatus(source.id, "fetching")}
                    className="p-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 transition-all"
                    title="Start Crawl"
                  >
                    <Play className="w-3.5 h-3.5" />
                  </button>
                )}

                <button
                  onClick={() => onSelectSource(source)}
                  className="px-2.5 py-1 rounded-lg bg-space-900 hover:bg-white/10 text-cyan-300 font-medium text-xs border border-white/10"
                >
                  Inspect
                </button>
              </div>
            </div>
          </GlassPanel>
        ))}
      </div>
    </div>
  );
};
