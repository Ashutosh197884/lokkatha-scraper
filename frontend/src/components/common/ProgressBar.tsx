import React from "react";

interface ProgressBarProps {
  progress: number; // 0 - 100
  color?: "cyan" | "emerald" | "amber" | "purple" | "blue";
  showLabel?: boolean;
  size?: "sm" | "md" | "lg";
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  color = "cyan",
  showLabel = false,
  size = "md",
}) => {
  const safeProgress = Math.max(0, Math.min(100, progress));

  const colorStyles = {
    cyan: "bg-gradient-to-r from-cyan-500 to-blue-500 shadow-[0_0_12px_rgba(56,189,248,0.5)]",
    emerald: "bg-gradient-to-r from-emerald-500 to-teal-400 shadow-[0_0_12px_rgba(16,185,129,0.5)]",
    amber: "bg-gradient-to-r from-amber-500 to-orange-500 shadow-[0_0_12px_rgba(245,158,11,0.5)]",
    purple: "bg-gradient-to-r from-purple-500 to-pink-500 shadow-[0_0_12px_rgba(168,85,247,0.5)]",
    blue: "bg-gradient-to-r from-blue-600 to-cyan-400 shadow-[0_0_12px_rgba(59,130,246,0.5)]",
  };

  const heightStyles = {
    sm: "h-1.5",
    md: "h-2.5",
    lg: "h-4",
  };

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex justify-between items-center mb-1 text-xs">
          <span className="text-slate-400">Progress</span>
          <span className="font-mono text-cyan-300 font-semibold">{safeProgress}%</span>
        </div>
      )}
      <div className={`w-full bg-space-950/80 rounded-full overflow-hidden border border-white/5 ${heightStyles[size]}`}>
        <div
          className={`h-full rounded-full transition-all duration-500 ease-out ${colorStyles[color]}`}
          style={{ width: `${safeProgress}%` }}
        />
      </div>
    </div>
  );
};
