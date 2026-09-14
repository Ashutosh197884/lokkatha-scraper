import React from "react";
import {
  Bell,
  FastForward,
  Flame,
  Globe,
  Maximize2,
  Moon,
  Pause,
  Play,
  Search,
  Volume2,
  VolumeX,
} from "lucide-react";

interface HeaderProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  simulationSpeed: number;
  onSpeedChange: (speed: number) => void;
  soundEnabled: boolean;
  onSoundToggle: () => void;
  activeSourcesCount: number;
  runningTasksCount: number;
}

export const Header: React.FC<HeaderProps> = ({
  searchQuery,
  onSearchChange,
  simulationSpeed,
  onSpeedChange,
  soundEnabled,
  onSoundToggle,
  activeSourcesCount,
  runningTasksCount,
}) => {
  return (
    <header className="h-16 px-6 border-b border-white/10 bg-space-950/80 backdrop-blur-xl flex items-center justify-between z-30 relative select-none">
      {/* Left: Branding & Subtitle */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500/20 via-orange-500/30 to-amber-300/20 border border-amber-500/40 shadow-[0_0_20px_rgba(245,158,11,0.3)]">
            <Flame className="w-5 h-5 text-amber-400 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-bold text-lg text-white tracking-wide font-sans flex items-center gap-1.5">
                Lokkatha <span className="text-cyan-400 font-semibold">Orchestrator</span>
              </h1>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-mono">
                v1.0.0
              </span>
            </div>
            <p className="text-xs text-slate-400 font-light">
              Multiple Sources. One Intelligent Flow.
            </p>
          </div>
        </div>
      </div>

      {/* Center: Live Search Bar */}
      <div className="flex-1 max-w-md mx-8">
        <div className="relative">
          <Search className="absolute left-3.5 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search sources, tasks, entities, folklore records..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full bg-space-900/90 text-sm text-slate-100 placeholder-slate-500 pl-10 pr-4 py-2 rounded-xl border border-white/10 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all font-sans"
          />
        </div>
      </div>

      {/* Right Controls: Sim Speed, Sound, Alerts, User */}
      <div className="flex items-center gap-3">
        {/* Simulation Speed Controls */}
        <div className="flex items-center bg-space-900/90 border border-white/10 rounded-xl p-1 gap-1">
          <button
            onClick={() => onSpeedChange(simulationSpeed === 0 ? 1 : 0)}
            className={`px-2.5 py-1 text-xs rounded-lg font-medium flex items-center gap-1 transition-all ${
              simulationSpeed === 0
                ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                : "text-slate-400 hover:text-slate-200"
            }`}
            title={simulationSpeed === 0 ? "Resume Simulation" : "Pause Simulation"}
          >
            {simulationSpeed === 0 ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
            {simulationSpeed === 0 ? "Paused" : "Live"}
          </button>
          
          <button
            onClick={() => onSpeedChange(1)}
            className={`px-2 py-1 text-xs rounded-lg font-mono font-medium transition-all ${
              simulationSpeed === 1
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            1x
          </button>
          
          <button
            onClick={() => onSpeedChange(2)}
            className={`px-2 py-1 text-xs rounded-lg font-mono font-medium transition-all ${
              simulationSpeed === 2
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            2x
          </button>

          <button
            onClick={() => onSpeedChange(5)}
            className={`px-2 py-1 text-xs rounded-lg font-mono font-medium transition-all ${
              simulationSpeed === 5
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <FastForward className="w-3 h-3 inline mr-0.5" /> 5x
          </button>
        </div>

        {/* Audio Toggle */}
        <button
          onClick={onSoundToggle}
          className="p-2 rounded-xl border border-white/10 bg-space-900/80 text-slate-400 hover:text-cyan-300 hover:border-cyan-500/30 transition-all"
          title={soundEnabled ? "Mute Cosmic Audio" : "Enable Ambient Pulse Audio"}
        >
          {soundEnabled ? <Volume2 className="w-4 h-4 text-cyan-400" /> : <VolumeX className="w-4 h-4" />}
        </button>

        {/* Fullscreen Toggle */}
        <button
          onClick={() => {
            if (!document.fullscreenElement) {
              document.documentElement.requestFullscreen();
            } else {
              document.exitFullscreen();
            }
          }}
          className="p-2 rounded-xl border border-white/10 bg-space-900/80 text-slate-400 hover:text-cyan-300 hover:border-cyan-500/30 transition-all"
          title="Toggle Fullscreen"
        >
          <Maximize2 className="w-4 h-4" />
        </button>

        {/* Notifications */}
        <button
          className="relative p-2 rounded-xl border border-white/10 bg-space-900/80 text-slate-400 hover:text-amber-300 hover:border-amber-500/30 transition-all"
          title="System Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-amber-400 animate-pulse shadow-[0_0_8px_rgba(251,191,36,0.8)]" />
        </button>

        {/* User Profile */}
        <div className="flex items-center gap-2.5 pl-3 border-l border-white/10">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-600 to-indigo-600 border border-cyan-400/40 flex items-center justify-center font-bold text-xs text-white shadow-glow-cyan">
            LK
          </div>
          <div className="hidden lg:block text-left">
            <p className="text-xs font-semibold text-slate-200">Admin</p>
            <p className="text-[10px] text-emerald-400 font-mono">System Online</p>
          </div>
        </div>
      </div>
    </header>
  );
};
