import React, { useState } from "react";
import { FolkloreItem } from "../types/orchestration";
import { GlassPanel } from "../components/common/GlassPanel";
import { ResultDetailModal } from "../components/library/ResultDetailModal";
import {
  BookMarked,
  CheckCircle2,
  Download,
  ExternalLink,
  Eye,
  Feather,
  Filter,
  GitBranch,
  Leaf,
  MapPin,
  Search,
  Sparkles,
  Tag,
  Users,
} from "lucide-react";

interface DataLibraryViewProps {
  records: FolkloreItem[];
}

export const DataLibraryView: React.FC<DataLibraryViewProps> = ({ records }) => {
  const [search, setSearch] = useState("");
  const [selectedRegion, setSelectedRegion] = useState<string>("all");
  const [activeTab, setActiveTab] = useState<"all" | "tek">("all");
  const [selectedRecord, setSelectedRecord] = useState<FolkloreItem | null>(null);

  const filtered = records.filter((rec) => {
    const matchesSearch =
      rec.title.toLowerCase().includes(search.toLowerCase()) ||
      rec.summary.toLowerCase().includes(search.toLowerCase()) ||
      rec.characters.some((c) => c.toLowerCase().includes(search.toLowerCase())) ||
      rec.motifs.some((m) => m.toLowerCase().includes(search.toLowerCase()));

    const matchesRegion =
      selectedRegion === "all" || rec.region.includes(selectedRegion);

    const matchesTek = activeTab === "all" || rec.tekCount > 0;

    return matchesSearch && matchesRegion && matchesTek;
  });

  const handleExport = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(records, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", "lokkatha_folklore_export.json");
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="flex-1 p-6 overflow-y-auto bg-space-950 text-slate-100 space-y-6 custom-scrollbar">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold font-sans text-white flex items-center gap-2">
            <BookMarked className="w-6 h-6 text-cyan-400" />
            Folklore Knowledge Repository ({records.length} Records)
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Authoritative source-derived database of Indian folklore, oral epics, variants, and Traditional Ecological Knowledge (TEK).
          </p>
        </div>

        <button
          onClick={handleExport}
          className="px-4 py-2 rounded-xl bg-space-900 hover:bg-white/10 text-white font-medium text-xs flex items-center gap-2 border border-white/10 transition-all shadow-glass"
        >
          <Download className="w-4 h-4 text-cyan-400" />
          <span>Export Provenance JSON</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1 max-w-md relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search characters, motifs, titles, or ecological knowledge..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-space-900 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-sans"
          />
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab("all")}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
              activeTab === "all"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                : "bg-space-900 text-slate-400 border border-white/5"
            }`}
          >
            All Narratives
          </button>
          <button
            onClick={() => setActiveTab("tek")}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium flex items-center gap-1.5 transition-all ${
              activeTab === "tek"
                ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                : "bg-space-900 text-slate-400 border border-white/5"
            }`}
          >
            <Leaf className="w-3.5 h-3.5" />
            <span>TEK & Ecological Lore</span>
          </button>
        </div>
      </div>

      {/* Records List */}
      <div className="space-y-4">
        {filtered.map((item) => (
          <GlassPanel
            key={item.id}
            onClick={() => setSelectedRecord(item)}
            className="p-5 space-y-4 hover:border-cyan-500/40 transition-all cursor-pointer group relative"
          >
            {/* Top row */}
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-base font-bold text-white font-sans group-hover:text-cyan-300 transition-colors">
                    {item.title}
                  </h3>
                  {item.verified && (
                    <span className="flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                      <CheckCircle2 className="w-3 h-3" /> Provenance Verified
                    </span>
                  )}
                </div>
                {item.alternateTitle && (
                  <p className="text-xs text-slate-400 font-serif italic mt-0.5">
                    {item.alternateTitle}
                  </p>
                )}
              </div>

              <div className="flex items-center gap-2">
                <span className="text-[11px] font-mono text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded-lg border border-cyan-500/30">
                  {item.folkloreType}
                </span>
                <span className="text-xs font-mono font-bold text-emerald-400 bg-space-900 px-2 py-1 rounded-lg border border-white/10">
                  {(item.confidence * 100).toFixed(0)}% Score
                </span>
              </div>
            </div>

            {/* Summary Narrative */}
            <p className="text-xs text-slate-300 leading-relaxed bg-space-900/60 p-3.5 rounded-xl border border-white/5 font-sans">
              {item.summary}
            </p>

            {/* Badges Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              {/* Characters */}
              <div className="p-2.5 rounded-xl bg-space-900/40 border border-white/5">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1 mb-1.5">
                  <Users className="w-3 h-3 text-cyan-400" /> Characters & Deities
                </span>
                <div className="flex flex-wrap gap-1">
                  {item.characters.map((c) => (
                    <span key={c} className="px-2 py-0.5 rounded bg-space-900 border border-white/10 text-[11px] text-slate-200">
                      {c}
                    </span>
                  ))}
                </div>
              </div>

              {/* Thompson Motifs */}
              <div className="p-2.5 rounded-xl bg-space-900/40 border border-white/5">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1 mb-1.5">
                  <Tag className="w-3 h-3 text-purple-400" /> Motifs & Archetypes
                </span>
                <div className="flex flex-wrap gap-1">
                  {item.motifs.map((m) => (
                    <span key={m} className="px-2 py-0.5 rounded bg-space-900 border border-white/10 text-[11px] text-purple-300">
                      {m}
                    </span>
                  ))}
                </div>
              </div>

              {/* Geography & Source */}
              <div className="p-2.5 rounded-xl bg-space-900/40 border border-white/5">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1 mb-1.5">
                  <MapPin className="w-3 h-3 text-emerald-400" /> Provenance & Region
                </span>
                <div className="space-y-1 text-[11px] text-slate-300 font-mono">
                  <div>Region: <span className="text-white">{item.region.join(", ")}</span></div>
                  <div>Platform: <span className="text-cyan-400">{item.sourceName}</span></div>
                </div>
              </div>
            </div>

            {/* Card Footer Bar */}
            <div className="flex items-center justify-between pt-1 text-[11px] text-slate-400 font-mono border-t border-white/5">
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1 text-emerald-400">
                  <Leaf className="w-3.5 h-3.5" /> {item.tekCount} TEK Records
                </span>
                <span className="flex items-center gap-1 text-purple-400">
                  <GitBranch className="w-3.5 h-3.5" /> {item.variants ? item.variants.length : 2} Variants
                </span>
              </div>

              <div className="flex items-center gap-1 text-cyan-400 group-hover:underline">
                <Eye className="w-3.5 h-3.5" />
                <span>Inspect Evidence & Source →</span>
              </div>
            </div>
          </GlassPanel>
        ))}
      </div>

      {/* Result Detail Modal */}
      <ResultDetailModal
        item={selectedRecord}
        onClose={() => setSelectedRecord(null)}
      />
    </div>
  );
};
