import React from "react";
import {
  Activity,
  BarChart3,
  BookMarked,
  Compass,
  Database,
  Layers,
  Moon,
  Orbit,
  Server,
  Settings,
  ShieldCheck,
  Workflow,
} from "lucide-react";

interface SidebarProps {
  currentView: string;
  onViewChange: (view: any) => void;
  sourcesCount: number;
  activeTasksCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentView,
  onViewChange,
  sourcesCount,
  activeTasksCount,
}) => {
  const navItems = [
    {
      id: "orchestrator",
      label: "Orchestrator",
      icon: Orbit,
      badge: "LIVE",
      badgeColor: "bg-cyan-500/20 text-cyan-300 border-cyan-500/40",
    },
    {
      id: "sources",
      label: "Sources",
      icon: Database,
      badge: sourcesCount.toString(),
      badgeColor: "bg-slate-800 text-slate-300 border-slate-700",
    },
    {
      id: "tasks",
      label: "Tasks",
      icon: Workflow,
      badge: activeTasksCount.toString(),
      badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/40",
    },
    {
      id: "library",
      label: "Data Library",
      icon: BookMarked,
      badge: "1.8K",
      badgeColor: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
    },
    {
      id: "analytics",
      label: "Analytics",
      icon: BarChart3,
    },
    {
      id: "settings",
      label: "Settings",
      icon: Settings,
    },
  ];

  return (
    <aside className="w-64 h-[calc(100vh-4rem)] border-r border-white/10 bg-space-950/70 backdrop-blur-xl flex flex-col justify-between p-4 z-20 select-none">
      {/* Navigation list */}
      <div className="space-y-1.5">
        <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-500 font-mono">
          Command Center
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-sm font-medium transition-all duration-200 group ${
                isActive
                  ? "bg-gradient-to-r from-indigo-900/40 via-cyan-900/30 to-transparent text-white border border-cyan-500/40 shadow-[0_0_20px_-5px_rgba(56,189,248,0.3)]"
                  : "text-slate-400 hover:text-slate-100 hover:bg-white/5 border border-transparent"
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon
                  className={`w-4 h-4 transition-transform duration-200 group-hover:scale-110 ${
                    isActive ? "text-cyan-400" : "text-slate-400 group-hover:text-cyan-300"
                  }`}
                />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span
                  className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full border ${item.badgeColor}`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Bottom Footer Info */}
      <div className="space-y-3 pt-4 border-t border-white/10">
        {/* Quote pill */}
        <div className="p-3 rounded-xl bg-space-900/80 border border-white/5 text-[11px] text-slate-400 italic">
          &ldquo;Every story revolves around a bigger universe.&rdquo;
        </div>

        {/* System security status */}
        <div className="flex items-center justify-between px-2 text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span className="text-[11px] font-medium">Core Security Active</span>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 font-semibold">99.8%</span>
        </div>
      </div>
    </aside>
  );
};
