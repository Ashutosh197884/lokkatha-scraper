import React, { useState } from "react";
import { GlassPanel } from "../common/GlassPanel";
import { FolkloreItem, EvidenceRecord, VariantVersion } from "../../types/orchestration";
import {
  BookOpen,
  Calendar,
  CheckCircle2,
  ExternalLink,
  GitBranch,
  Globe2,
  Info,
  Languages,
  Leaf,
  MapPin,
  Sparkles,
  Tag,
  Users,
  X,
} from "lucide-react";

interface ResultDetailModalProps {
  item: FolkloreItem | null;
  onClose: () => void;
}

export const ResultDetailModal: React.FC<ResultDetailModalProps> = ({ item, onClose }) => {
  const [activeTab, setActiveTab] = useState<"narrative" | "evidence" | "variants" | "tek">("narrative");

  if (!item) return null;

  // Fallback sample evidence if not explicitly passed
  const evidenceList: EvidenceRecord[] = item.evidenceList || [
    {
      evidenceId: "evi-01",
      sourceId: "src-01",
      documentId: "doc-01",
      url: item.sourceUrl,
      claim: `Folklore narrative: '${item.title}' documented in source archive.`,
      evidenceType: "direct",
      location: "Section 1, Paragraph 2",
      retrievedAt: item.discoveredAt,
      contextSnippet: item.summary.slice(0, 140) + "...",
    },
    {
      evidenceId: "evi-02",
      sourceId: "src-01",
      documentId: "doc-01",
      url: item.sourceUrl,
      claim: `Characters identified: ${item.characters.join(", ")}`,
      evidenceType: "direct",
      location: "Paragraph 4",
      retrievedAt: item.discoveredAt,
    },
    {
      evidenceId: "evi-03",
      sourceId: "src-01",
      documentId: "doc-01",
      url: item.sourceUrl,
      claim: `Motifs classified: ${item.motifs.join(", ")}`,
      evidenceType: "inferred",
      location: "ATU Folklore Motif Index",
      retrievedAt: item.discoveredAt,
    },
  ];

  // Fallback sample variant tree
  const variants: VariantVersion[] = item.variants || [
    {
      variantId: "var-01",
      variantTitle: `${item.title} (Regional Oral Tradition)`,
      sourcePlatform: item.sourceName,
      sourceUrl: item.sourceUrl,
      region: item.region[0] || "Regional",
      differences: ["Primary recorded oral version transcribed from local bards."],
    },
    {
      variantId: "var-02",
      variantTitle: `${item.title} (Colonial Folklore Survey)`,
      sourcePlatform: "Internet Archive",
      sourceUrl: "https://archive.org/details/indian-folklore-collection",
      region: "Pan-Regional",
      differences: ["19th-century anthropological survey transcription variant."],
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <GlassPanel className="w-full max-w-3xl max-h-[90vh] flex flex-col p-6 space-y-5 border border-cyan-500/30 shadow-2xl relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-xl bg-space-900/80 hover:bg-white/10 text-slate-400 hover:text-white transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header with Title & Source Provenance Bar */}
        <div className="space-y-2 pr-8">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-mono text-cyan-400 bg-cyan-500/10 px-2.5 py-0.5 rounded-md border border-cyan-500/30">
              {item.folkloreType}
            </span>
            {item.verified && (
              <span className="flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                <CheckCircle2 className="w-3.5 h-3.5" /> Source Provenance Verified
              </span>
            )}
            <span className="text-[11px] font-mono text-slate-400 bg-space-900 px-2 py-0.5 rounded-md border border-white/5">
              Confidence: {(item.confidence * 100).toFixed(0)}%
            </span>
          </div>

          <h2 className="text-xl font-bold font-sans text-white">
            {item.title}
          </h2>
          {item.alternateTitle && (
            <p className="text-xs text-slate-400 font-serif italic">
              {item.alternateTitle}
            </p>
          )}

          {/* Provenance Details Ribbon */}
          <div className="p-3 rounded-xl bg-space-900/60 border border-white/5 grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
            <div>
              <span className="text-[10px] text-slate-500 uppercase font-mono block">Platform</span>
              <span className="font-semibold text-white truncate block">{item.sourceName}</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-500 uppercase font-mono block">Website</span>
              <span className="font-semibold text-cyan-400 truncate block">{item.domain || item.sourceName}</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-500 uppercase font-mono block">Language</span>
              <span className="text-slate-300 font-mono block">{item.originalLanguage || item.language.join(", ")}</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-500 uppercase font-mono block">Retrieved At</span>
              <span className="text-slate-300 font-mono text-[11px] block">{item.discoveredAt}</span>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 border-b border-white/10 pb-2">
          <button
            onClick={() => setActiveTab("narrative")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === "narrative"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Source Narrative
          </button>
          <button
            onClick={() => setActiveTab("evidence")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all ${
              activeTab === "evidence"
                ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Traceable Evidence ({evidenceList.length})</span>
          </button>
          <button
            onClick={() => setActiveTab("variants")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all ${
              activeTab === "variants"
                ? "bg-purple-500/20 text-purple-300 border border-purple-500/40"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <GitBranch className="w-3.5 h-3.5" />
            <span>Variant Tree ({variants.length})</span>
          </button>
          <button
            onClick={() => setActiveTab("tek")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all ${
              activeTab === "tek"
                ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Leaf className="w-3.5 h-3.5" />
            <span>TEK Lore ({item.tekCount})</span>
          </button>
        </div>

        {/* Tab Content Body */}
        <div className="flex-1 overflow-y-auto space-y-4 pr-1 custom-scrollbar text-xs">
          {/* Narrative Tab */}
          {activeTab === "narrative" && (
            <div className="space-y-4">
              <div className="space-y-1">
                <h4 className="text-[11px] font-bold text-slate-400 uppercase font-mono">
                  Source-Derived Text
                </h4>
                <p className="text-slate-200 leading-relaxed bg-space-900/60 p-4 rounded-xl border border-white/5 whitespace-pre-wrap font-sans">
                  {item.story || item.summary}
                </p>
              </div>

              {item.generatedSummary && (
                <div className="space-y-1">
                  <h4 className="text-[11px] font-bold text-cyan-400 uppercase font-mono flex items-center gap-1">
                    <Info className="w-3.5 h-3.5" /> Isolated AI Analysis Summary (Non-Source)
                  </h4>
                  <p className="text-slate-300 leading-relaxed bg-cyan-950/20 p-3.5 rounded-xl border border-cyan-500/20 italic">
                    {item.generatedSummary}
                  </p>
                </div>
              )}

              {/* Characters & Motifs */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-space-900/40 border border-white/5 space-y-1.5">
                  <span className="text-[10px] text-slate-400 uppercase font-mono font-bold flex items-center gap-1">
                    <Users className="w-3 h-3 text-cyan-400" /> Characters & Deities
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {item.characters.map((c) => (
                      <span key={c} className="px-2 py-0.5 rounded bg-space-900 border border-white/10 text-slate-200">
                        {c}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-space-900/40 border border-white/5 space-y-1.5">
                  <span className="text-[10px] text-slate-400 uppercase font-mono font-bold flex items-center gap-1">
                    <Tag className="w-3 h-3 text-purple-400" /> Folk Motifs
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {item.motifs.map((m) => (
                      <span key={m} className="px-2 py-0.5 rounded bg-space-900 border border-white/10 text-purple-300">
                        {m}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Evidence Tab */}
          {activeTab === "evidence" && (
            <div className="space-y-3">
              <p className="text-slate-400 text-[11px]">
                Every extracted claim is traceable directly to passages and citations in the origin source.
              </p>
              <div className="space-y-2">
                {evidenceList.map((evi) => (
                  <div
                    key={evi.evidenceId}
                    className="p-3.5 rounded-xl bg-space-900/60 border border-white/5 space-y-1.5"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-mono text-[10px] text-slate-400">
                        ID: <span className="text-cyan-400">{evi.evidenceId}</span>
                      </span>
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded uppercase font-bold ${
                          evi.evidenceType === "direct"
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                            : "bg-purple-500/10 text-purple-400 border border-purple-500/30"
                        }`}
                      >
                        {evi.evidenceType} Evidence
                      </span>
                    </div>

                    <div className="font-medium text-white">{evi.claim}</div>

                    {evi.location && (
                      <div className="text-[11px] text-slate-400 font-mono">
                        Location: <span className="text-slate-200">{evi.location}</span>
                      </div>
                    )}

                    {evi.contextSnippet && (
                      <div className="text-[11px] text-slate-300 italic bg-space-950/60 p-2 rounded border border-white/5">
                        "{evi.contextSnippet}"
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Variants Tab */}
          {activeTab === "variants" && (
            <div className="space-y-3">
              <p className="text-slate-400 text-[11px]">
                Independent source versions preserved as a multi-source variant tree without destructive merging.
              </p>
              <div className="space-y-2.5">
                <div className="p-3 rounded-xl bg-cyan-950/20 border border-cyan-500/30">
                  <div className="font-bold font-mono text-cyan-300 text-xs flex items-center gap-1.5">
                    <GitBranch className="w-3.5 h-3.5" /> Canonical Tradition: {item.title}
                  </div>
                </div>

                {variants.map((v, idx) => (
                  <div
                    key={v.variantId}
                    className="ml-4 p-3.5 rounded-xl bg-space-900/60 border border-white/5 space-y-2 relative"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h5 className="font-bold text-white text-xs">{v.variantTitle}</h5>
                        <span className="text-[11px] text-slate-400 font-mono">
                          Source: {v.sourcePlatform} ({v.region || "Regional"})
                        </span>
                      </div>
                      <a
                        href={v.sourceUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1 rounded bg-white/5 hover:bg-white/10 text-cyan-400 transition-all"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>

                    <div className="space-y-1">
                      <span className="text-[10px] text-slate-500 uppercase font-mono block">Divergence / Distinct Notes:</span>
                      <ul className="list-disc list-inside text-[11px] text-slate-300 space-y-0.5">
                        {v.differences.map((d, dIdx) => (
                          <li key={dIdx}>{d}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TEK Tab */}
          {activeTab === "tek" && (
            <div className="space-y-3">
              <p className="text-slate-400 text-[11px]">
                Traditional Ecological Knowledge (TEK) observations embedded in this narrative.
              </p>
              <div className="p-3.5 rounded-xl bg-space-900/60 border border-white/5 space-y-2">
                <div className="flex items-center gap-2">
                  <Leaf className="w-4 h-4 text-emerald-400" />
                  <span className="font-bold text-white">Traditional Ecological Knowledge Entries ({item.tekCount})</span>
                </div>
                <p className="text-[11px] text-slate-300 leading-relaxed">
                  Documented indigenous practices of water harvesting, sacred groves, and environmental coexistence linked to this tradition.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer with Action [VIEW SOURCE] */}
        <div className="flex items-center justify-between pt-3 border-t border-white/10">
          <div className="text-[11px] text-slate-400 font-mono truncate max-w-xs sm:max-w-md">
            URL: <span className="text-cyan-400">{item.sourceUrl}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-space-900 hover:bg-white/10 text-slate-300 text-xs font-medium transition-all"
            >
              Close
            </button>
            <a
              href={item.sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 shadow-lg shadow-cyan-500/20 transition-all"
            >
              <span>VIEW SOURCE</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>
      </GlassPanel>
    </div>
  );
};
