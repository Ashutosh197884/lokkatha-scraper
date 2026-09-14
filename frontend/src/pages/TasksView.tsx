import React from "react";
import { ScrapeTask } from "../types/task";
import { GlassPanel } from "../components/common/GlassPanel";
import { ProgressBar } from "../components/common/ProgressBar";
import {
  CheckCircle2,
  Clock,
  Layers,
  Play,
  Plus,
  RotateCcw,
  Sparkles,
  Workflow,
} from "lucide-react";

interface TasksViewProps {
  tasks: ScrapeTask[];
  onTriggerNewTask: () => void;
}

export const TasksView: React.FC<TasksViewProps> = ({ tasks, onTriggerNewTask }) => {
  return (
    <div className="flex-1 p-6 overflow-y-auto bg-space-950 text-slate-100 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold font-sans text-white flex items-center gap-2">
            <Workflow className="w-6 h-6 text-cyan-400" />
            Scraping & Extraction Tasks ({tasks.length})
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Monitor real-time pipeline progress, multistage folklore extraction, and data ingestion jobs.
          </p>
        </div>

        <button
          onClick={onTriggerNewTask}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-medium text-xs flex items-center gap-2 shadow-glow-cyan transition-all"
        >
          <Plus className="w-4 h-4 font-bold" />
          <span>Launch New Scraping Job</span>
        </button>
      </div>

      {/* Tasks List */}
      <div className="space-y-4">
        {tasks.map((task) => (
          <GlassPanel key={task.id} className="p-5 relative space-y-4">
            {/* Top row */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                  <Workflow className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white font-sans">
                    {task.title}
                  </h3>
                  <p className="text-xs text-slate-400">
                    Target Region: <span className="text-slate-200">{task.targetRegion}</span>
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span className="text-xs font-mono px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 capitalize">
                  ● {task.status}
                </span>
                <span className="text-sm font-mono font-bold text-white">
                  {task.progress}%
                </span>
              </div>
            </div>

            {/* Progress Bar */}
            <ProgressBar progress={task.progress} color="cyan" size="md" />

            {/* Stages Grid */}
            <div className="grid grid-cols-5 gap-2 pt-2 border-t border-white/5 text-xs">
              {task.stages.map((stg, i) => (
                <div
                  key={stg.id}
                  className={`p-2.5 rounded-xl border ${
                    stg.status === "completed"
                      ? "bg-emerald-500/5 border-emerald-500/20 text-slate-300"
                      : stg.status === "running"
                      ? "bg-cyan-500/10 border-cyan-500/40 text-cyan-300 shadow-[0_0_12px_rgba(56,189,248,0.2)]"
                      : "bg-space-900/40 border-white/5 text-slate-500"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono text-[10px]">0{i + 1}</span>
                    {stg.status === "completed" ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    ) : stg.status === "running" ? (
                      <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                    ) : null}
                  </div>
                  <p className="font-semibold text-xs truncate">{stg.name}</p>
                  <span className="text-[10px] font-mono opacity-80 block mt-1">
                    {stg.duration || "Pending"}
                  </span>
                </div>
              ))}
            </div>

            {/* Bottom stats row */}
            <div className="flex items-center justify-between text-xs text-slate-400 font-mono pt-1">
              <div>
                Pages Processed: <span className="text-white font-bold">{task.pagesProcessed}</span> | Stories Discovered: <span className="text-cyan-400 font-bold">{task.storiesDiscovered}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-slate-500" />
                <span>Elapsed: {Math.floor(task.elapsedSeconds / 60)}m {task.elapsedSeconds % 60}s</span>
              </div>
            </div>
          </GlassPanel>
        ))}
      </div>
    </div>
  );
};
