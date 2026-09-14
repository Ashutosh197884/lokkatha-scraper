import React from "react";
import { GlassPanel } from "../common/GlassPanel";
import { ProgressBar } from "../common/ProgressBar";
import { ScrapeTask } from "../../types/task";
import { CheckCircle2, Circle, Feather, Loader2, Sparkles, Workflow } from "lucide-react";

interface CurrentTaskCardProps {
  task: ScrapeTask;
}

export const CurrentTaskCard: React.FC<CurrentTaskCardProps> = ({ task }) => {
  return (
    <div className="space-y-3">
      <GlassPanel className="p-4 relative">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Workflow className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-semibold text-slate-100 tracking-wide font-sans">
              Current Task
            </h2>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-mono">
            {task.status.toUpperCase()}
          </span>
        </div>

        {/* Task Title & Overall Progress */}
        <div className="mb-4">
          <div className="flex justify-between items-baseline mb-2">
            <h3 className="text-xs font-semibold text-slate-200">
              {task.title}
            </h3>
            <span className="font-mono text-cyan-400 font-bold text-sm">
              {task.progress}%
            </span>
          </div>
          <ProgressBar progress={task.progress} color="cyan" size="md" />
        </div>

        {/* Vertical Pipeline Stages */}
        <div className="space-y-2.5 my-3">
          {task.stages.map((stage) => {
            const isCompleted = stage.status === "completed";
            const isRunning = stage.status === "running";
            const isPending = stage.status === "pending";

            return (
              <div
                key={stage.id}
                className="flex items-center justify-between text-xs transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  {isCompleted && (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  )}
                  {isRunning && (
                    <div className="relative flex items-center justify-center w-4 h-4">
                      <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping absolute" />
                      <div className="w-2 h-2 rounded-full bg-cyan-400" />
                    </div>
                  )}
                  {isPending && (
                    <Circle className="w-4 h-4 text-slate-600 flex-shrink-0" />
                  )}

                  <span
                    className={`font-medium ${
                      isRunning
                        ? "text-cyan-300 font-semibold"
                        : isCompleted
                        ? "text-slate-300"
                        : "text-slate-500"
                    }`}
                  >
                    {stage.name}
                  </span>
                </div>

                <span
                  className={`font-mono text-[11px] ${
                    isCompleted
                      ? "text-slate-400"
                      : isRunning
                      ? "text-cyan-400 animate-pulse font-medium"
                      : "text-slate-600"
                  }`}
                >
                  {stage.duration || (isCompleted ? "Done" : "Pending")}
                </span>
              </div>
            );
          })}
        </div>

        {/* Current Operation Footnote */}
        <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-400">
          <span className="text-slate-500">Operation:</span>
          <span className="text-slate-300 font-mono truncate max-w-[180px]">
            {task.currentOperation}
          </span>
        </div>
      </GlassPanel>

      {/* Inspirational Quote Card matching mockup */}
      <GlassPanel variant="subtle" className="p-3.5 border-l-2 border-l-cyan-500/60">
        <div className="flex items-start gap-3">
          <Feather className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
          <p className="text-xs text-slate-300 italic leading-relaxed">
            &ldquo;Stories are like stars &mdash; scattered across the world, but connected in meaning.&rdquo;
          </p>
        </div>
      </GlassPanel>
    </div>
  );
};
