import React from "react";

interface MetricGaugeProps {
  label: string;
  value: number; // 0 - 100
  color: string;
  unit?: string;
  size?: number;
}

export const MetricGauge: React.FC<MetricGaugeProps> = ({
  label,
  value,
  color,
  unit = "%",
  size = 72,
}) => {
  const strokeWidth = 6;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg className="w-full h-full transform -rotate-90">
          {/* Background circle track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="rgba(255, 255, 255, 0.08)"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Animated filled circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            fill="transparent"
            style={{
              transition: "stroke-dashoffset 0.8s ease-in-out",
              filter: `drop-shadow(0 0 6px ${color}80)`,
            }}
          />
        </svg>
        {/* Center percentage value */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xs font-bold font-mono text-slate-100">
            {value}{unit}
          </span>
        </div>
      </div>
      <span className="mt-1.5 text-[11px] font-medium text-slate-400 uppercase tracking-wider">
        {label}
      </span>
    </div>
  );
};
