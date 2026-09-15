import React from "react";
import { GlassPanel } from "../common/GlassPanel";
import { DataSource } from "../../types/source";
import {
  CheckCircle2,
  Database,
  ExternalLink,
  FileCheck2,
  FileText,
  Globe2,
  Layers,
  Sparkles,
  X,
} from "lucide-react";

interface TaskCompletionModalProps {
  isOpen: boolean;
  onClose: () => void;
  taskTitle: string;
  sourcesUsed: DataSource[];
  pagesProcessed: number;
  documentsFound: number;
  relevantDocuments: number;
  evidenceRecords: number;
  folkloreRecords: number;
  onViewLibrary?: () => void;
}

export const TaskCompletionModal: React.FC<TaskCompletionModalProps> = ({
  isOpen,
  onClose,
  taskTitle,
  sourcesUsed,
  pagesProcessed,
  documentsFound,
  relevantDocuments,
  evidenceRecords,
  folkloreRecords,
  onViewLibrary,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md animate-fadeIn">
      <GlassPanel className="w-full max-w-2xl p-6 space-y-6 border border-emerald-500/40 shadow-2xl shadow-emerald-950/50 relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-xl bg-space-900/80 hover:bg-white/10 text-slate-400 hover:text-white transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header with Emerald Pulsing Banner */}
        <div className="space-y-2 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 text-xs font-mono font-semibold tracking-wide animate-pulse">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>TASK COMPLETED</span>
          </div>
          <h2 className="text-xl font-bold font-sans text-white">
            {taskTitle}
          </h2>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Source intelligence and provenance preservation bundle successfully compiled.
          </p>
        </div>

        {/* Summary Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <div className="p-3 rounded-xl bg-space-900/70 border border-white/5 space-y-1">
            <span className="text-[10px] text-slate-400 uppercase font-mono flex items-center gap-1">
              <Globe2 className="w-3.5 h-3.5 text-cyan-400" /> Sources Used
            </span>
            <div className="text-lg font-bold font-mono text-cyan-300">
              {sourcesUsed.length}
            </div>
          </div>

          <div className="p-3 rounded-xl bg-space-900/70 border border-white/5 space-y-1">
            <span className="text-[10px] text-slate-400 uppercase font-mono flex items-center gap-1">
              <FileText className="w-3.5 h-3.5 text-blue-400" /> Pages Processed
            </span>
            <div className="text-lg font-bold font-mono text-blue-300">
              {pagesProcessed}
            </div>
          </div>

          <div className="p-3 rounded-xl bg-space-900/70 border border-white/5 space-y-1">
            <span className="text-[10px] text-slate-400 uppercase font-mono flex items-center gap-1">
              <Layers className="w-3.5 h-3.5 text-purple-400" /> Documents Found
            </span>
            <div className="text-lg font-bold font-mono text-purple-300">
              {documentsFound}
            </div>
          </div>

          <div className="p-3 rounded-xl bg-space-900/70 border border-white/5 space-y-1">
            <span className="text-[10px] text-slate-400 uppercase font-mono flex items-center gap-1">
              <FileCheck2 className="w-3.5 h-3.5 text-amber-400" /> Relevant Documents
            </span>
            <div className="text-lg font-bold font-mono text-amber-300">
              {relevantDocuments}
            </div>
          </div>

          <div className="p-3 rounded-xl bg-space-900/70 border border-white/5 space-y-1">
            <span className="text-[10px] text-slate-400 uppercase font-mono flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" /> Evidence Records
            </span>
            <div className="text-lg font-bold font-mono text-emerald-300">
              {evidenceRecords}
            </div>
          </div>

          <div className="p-3 rounded-xl bg-space-900/70 border border-white/5 space-y-1">
            <span className="text-[10px] text-slate-400 uppercase font-mono flex items-center gap-1">
              <Database className="w-3.5 h-3.5 text-rose-400" /> Folklore Records
            </span>
            <div className="text-lg font-bold font-mono text-rose-300">
              {folkloreRecords}
            </div>
          </div>
        </div>

        {/* SOURCES USED Table */}
        <div className="space-y-2">
          <h4 className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <Globe2 className="w-3.5 h-3.5 text-cyan-400" /> SOURCES USED
          </h4>
          <div className="max-h-48 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
            {sourcesUsed.map((s) => (
              <div
                key={s.id}
                className="p-3 rounded-xl bg-space-900/50 border border-white/5 flex items-center justify-between gap-3 text-xs"
              >
                <div className="space-y-0.5 min-w-0">
                  <div className="font-bold text-white truncate flex items-center gap-2">
                    <span
                      className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                      style={{ backgroundColor: s.visual.color }}
                    />
                    <span>{s.name}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-white/5 text-slate-400 font-mono">
                      {s.type}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono truncate">
                    {s.domain || s.url}
                  </div>
                </div>

                <a
                  href={s.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 font-mono text-[11px] flex items-center gap-1 border border-cyan-500/30 transition-all flex-shrink-0"
                >
                  <span>VIEW SOURCE</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-2 border-t border-white/10">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-space-900 hover:bg-white/10 text-slate-300 font-medium text-xs transition-all"
          >
            Dismiss
          </button>
          {onViewLibrary && (
            <button
              onClick={() => {
                onClose();
                onViewLibrary();
              }}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:opacity-90 text-white font-bold text-xs shadow-lg shadow-cyan-500/20 transition-all"
            >
              Explore Structured Records →
            </button>
          )}
        </div>
      </GlassPanel>
    </div>
  );
};
