import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

interface GlassPanelProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
  variant?: "default" | "subtle" | "glow-blue" | "glow-amber" | "interactive";
}

export const GlassPanel: React.FC<GlassPanelProps> = ({
  children,
  className,
  variant = "default",
  ...props
}) => {
  const variantStyles = {
    default: "glass-panel",
    subtle: "bg-space-900/60 backdrop-blur-md border border-white/5",
    "glow-blue": "glass-panel border-cyan-500/30 shadow-[0_0_25px_-5px_rgba(56,189,248,0.25)]",
    "glow-amber": "glass-panel border-amber-500/30 shadow-[0_0_25px_-5px_rgba(245,158,11,0.25)]",
    interactive: "glass-panel glass-panel-hover cursor-pointer",
  };

  return (
    <div
      className={twMerge(
        "rounded-xl overflow-hidden transition-all duration-300",
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
