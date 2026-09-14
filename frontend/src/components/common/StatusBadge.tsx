import React from "react";
import { SourceStatus } from "../../types/source";

interface StatusBadgeProps {
  status: SourceStatus | "running" | "optimal" | "warning" | "error" | "completed" | "pending";
  showDot?: boolean;
  size?: "sm" | "md";
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  showDot = true,
  size = "md",
}) => {
  const statusConfig: Record<
    string,
    { label: string; bg: string; text: string; dot: string; glow: string }
  > = {
    active: {
      label: "Active",
      bg: "bg-emerald-500/10 border-emerald-500/30",
      text: "text-emerald-400",
      dot: "bg-emerald-400",
      glow: "shadow-[0_0_8px_rgba(52,211,153,0.6)]",
    },
    fetching: {
      label: "Fetching",
      bg: "bg-cyan-500/10 border-cyan-500/30",
      text: "text-cyan-400",
      dot: "bg-cyan-400 animate-pulse",
      glow: "shadow-[0_0_8px_rgba(56,189,248,0.7)]",
    },
    analyzing: {
      label: "Analyzing",
      bg: "bg-blue-500/10 border-blue-500/30",
      text: "text-blue-400",
      dot: "bg-blue-400 animate-pulse",
      glow: "shadow-[0_0_8px_rgba(96,165,250,0.7)]",
    },
    idle: {
      label: "Idle",
      bg: "bg-slate-500/10 border-slate-500/20",
      text: "text-slate-400",
      dot: "bg-slate-400",
      glow: "",
    },
    connecting: {
      label: "Connecting",
      bg: "bg-amber-500/10 border-amber-500/30",
      text: "text-amber-400",
      dot: "bg-amber-400 animate-ping",
      glow: "shadow-[0_0_8px_rgba(251,191,36,0.6)]",
    },
    completed: {
      label: "Completed",
      bg: "bg-teal-500/10 border-teal-500/30",
      text: "text-teal-400",
      dot: "bg-teal-400",
      glow: "shadow-[0_0_8px_rgba(45,212,191,0.6)]",
    },
    error: {
      label: "Error",
      bg: "bg-rose-500/10 border-rose-500/30",
      text: "text-rose-400",
      dot: "bg-rose-400 animate-bounce",
      glow: "shadow-[0_0_8px_rgba(244,63,94,0.7)]",
    },
    paused: {
      label: "Paused",
      bg: "bg-purple-500/10 border-purple-500/30",
      text: "text-purple-400",
      dot: "bg-purple-400",
      glow: "",
    },
    running: {
      label: "Running",
      bg: "bg-emerald-500/10 border-emerald-500/30",
      text: "text-emerald-400",
      dot: "bg-emerald-400 animate-pulse",
      glow: "shadow-[0_0_8px_rgba(52,211,153,0.6)]",
    },
    optimal: {
      label: "Optimal",
      bg: "bg-emerald-500/10 border-emerald-500/30",
      text: "text-emerald-400",
      dot: "bg-emerald-400",
      glow: "shadow-[0_0_8px_rgba(52,211,153,0.6)]",
    },
    warning: {
      label: "Warning",
      bg: "bg-amber-500/10 border-amber-500/30",
      text: "text-amber-400",
      dot: "bg-amber-400",
      glow: "",
    },
    pending: {
      label: "Pending",
      bg: "bg-slate-700/20 border-slate-700/40",
      text: "text-slate-400",
      dot: "bg-slate-500",
      glow: "",
    },
  };

  const config = statusConfig[status] || statusConfig.idle;
  const sizeClasses =
    size === "sm"
      ? "px-2 py-0.5 text-xs gap-1.5"
      : "px-2.5 py-1 text-xs font-medium gap-2";

  return (
    <span
      className={`inline-flex items-center rounded-full border ${config.bg} ${config.text} ${sizeClasses}`}
    >
      {showDot && (
        <span
          className={`w-1.5 h-1.5 rounded-full ${config.dot} ${config.glow}`}
        />
      )}
      <span className="capitalize">{config.label}</span>
    </span>
  );
};
