import React, { useEffect, useRef, useState } from "react";
import { DataSource } from "../../types/source";
import { SolarSystemEngine } from "./SolarSystemEngine";
import { StatusBadge } from "../common/StatusBadge";
import {
  Compass,
  Eye,
  Layers,
  RotateCcw,
  Sparkles,
  Zap,
} from "lucide-react";

interface SolarSystemCanvasProps {
  sources: DataSource[];
  simulationSpeed: number;
  selectedSourceId: string | null;
  onSelectSource: (source: DataSource) => void;
  onResetSelection: () => void;
  reducedMotion?: boolean;
}

export const SolarSystemCanvas: React.FC<SolarSystemCanvasProps> = ({
  sources,
  simulationSpeed,
  selectedSourceId,
  onSelectSource,
  onResetSelection,
  reducedMotion = false,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const engineRef = useRef<SolarSystemEngine | null>(null);

  // HUD Labels position state
  const [hudPositions, setHudPositions] = useState<
    Record<string, { x: number; y: number; visible: boolean }>
  >({});
  const [sunPos, setSunPos] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [showLabels, setShowLabels] = useState(true);
  const [hoveredSource, setHoveredSource] = useState<DataSource | null>(null);

  // 1. Initialize Engine on Mount
  useEffect(() => {
    if (!containerRef.current) return;

    const engine = new SolarSystemEngine(containerRef.current);
    engineRef.current = engine;
    engine.simulationSpeed = reducedMotion ? 0.2 : simulationSpeed;

    // Callbacks
    engine.onPlanetClick = (source) => {
      onSelectSource(source);
      engine.focusOnPlanet(source.id);
    };

    engine.onBackgroundClick = () => {
      onResetSelection();
      engine.resetView();
    };

    engine.onPlanetHover = (source) => {
      setHoveredSource(source);
    };

    // Resize listener
    const handleResize = () => {
      if (containerRef.current && engineRef.current) {
        engineRef.current.resize(
          containerRef.current.clientWidth,
          containerRef.current.clientHeight
        );
      }
    };
    window.addEventListener("resize", handleResize);

    // Initial sources
    engine.setSources(sources);

    // Position tracking interval for UI HUD overlay
    const interval = setInterval(() => {
      if (!engineRef.current || !showLabels) return;
      const positions: Record<string, { x: number; y: number; visible: boolean }> = {};
      for (const s of sources) {
        const p = engineRef.current.getPlanetScreenPosition(s.id);
        if (p) positions[s.id] = p;
      }
      setHudPositions(positions);
      setSunPos(engineRef.current.getSunScreenPosition());
    }, 40);

    return () => {
      clearInterval(interval);
      window.removeEventListener("resize", handleResize);
      engine.destroy();
      engineRef.current = null;
    };
  }, []);

  // 2. Update Sources when data changes
  useEffect(() => {
    if (engineRef.current) {
      engineRef.current.setSources(sources);
    }
  }, [sources]);

  // 3. Update Simulation Speed
  useEffect(() => {
    if (engineRef.current) {
      engineRef.current.simulationSpeed = reducedMotion ? 0.2 : simulationSpeed;
    }
  }, [simulationSpeed, reducedMotion]);

  // 4. Focus on selected planet if changed externally
  useEffect(() => {
    if (engineRef.current && selectedSourceId) {
      engineRef.current.focusOnPlanet(selectedSourceId);
    } else if (engineRef.current && !selectedSourceId) {
      engineRef.current.resetView();
    }
  }, [selectedSourceId]);

  return (
    <div className="relative w-full h-full min-h-[460px] flex-1 overflow-hidden bg-space-950 select-none">
      {/* 3D WebGL Canvas Container */}
      <div ref={containerRef} className="absolute inset-0 cursor-grab active:cursor-grabbing" />

      {/* Cosmic Noise & Nebula Overlay Grid */}
      <div className="absolute inset-0 cosmic-grid opacity-20 pointer-events-none" />

      {/* Floating HUD Labels for Planets */}
      {showLabels &&
        sources.map((source) => {
          const pos = hudPositions[source.id];
          if (!pos || !pos.visible) return null;
          const isSelected = selectedSourceId === source.id;
          const isHovered = hoveredSource?.id === source.id;

          return (
            <div
              key={source.id}
              style={{
                left: `${pos.x}px`,
                top: `${pos.y}px`,
                transform: "translate(-50%, -150%)",
              }}
              onClick={() => {
                onSelectSource(source);
                engineRef.current?.focusOnPlanet(source.id);
              }}
              className={`absolute pointer-events-auto cursor-pointer transition-transform duration-200 z-10 flex flex-col items-center ${
                isSelected ? "scale-110" : isHovered ? "scale-105" : "scale-95 hover:scale-100"
              }`}
            >
              {/* Badge Glass Container */}
              <div
                className={`px-2.5 py-1 rounded-lg backdrop-blur-md border text-center transition-all shadow-lg ${
                  isSelected
                    ? "bg-space-900/95 border-cyan-400 shadow-[0_0_15px_rgba(56,189,248,0.5)]"
                    : isHovered
                    ? "bg-space-900/90 border-white/30"
                    : "bg-space-900/75 border-white/10"
                }`}
              >
                <div className="flex items-center gap-1.5 justify-center">
                  <span
                    className="w-2 h-2 rounded-full flex-shrink-0"
                    style={{
                      backgroundColor: source.visual.color,
                      boxShadow: `0 0 6px ${source.visual.glowColor}`,
                    }}
                  />
                  <span className="text-[11px] font-semibold text-white whitespace-nowrap font-sans tracking-wide">
                    {source.name}
                  </span>
                </div>

                <div className="flex items-center justify-center gap-1 mt-0.5">
                  <span
                    className={`text-[9px] font-mono capitalize ${
                      source.status === "fetching"
                        ? "text-cyan-400 animate-pulse font-medium"
                        : source.status === "active"
                        ? "text-emerald-400 font-medium"
                        : source.status === "analyzing"
                        ? "text-blue-400 font-medium"
                        : source.status === "error"
                        ? "text-rose-400 font-bold"
                        : "text-slate-400"
                    }`}
                  >
                    ● {source.status}
                  </span>
                </div>
              </div>

              {/* Connecting pointer stem */}
              <div className="w-px h-3 bg-gradient-to-b from-white/30 to-transparent" />
            </div>
          );
        })}

      {/* Central Sun Core Label Overlay */}
      {sunPos.x > 0 && (
        <div
          style={{
            left: `${sunPos.x}px`,
            top: `${sunPos.y}px`,
            transform: "translate(-50%, 45px)",
          }}
          className="absolute pointer-events-none text-center z-10 select-none flex flex-col items-center"
        >
          <div className="px-3.5 py-1.5 rounded-xl bg-space-950/80 backdrop-blur-md border border-amber-500/30 shadow-[0_0_20px_rgba(245,158,11,0.3)]">
            <h2 className="text-xs font-bold font-sans text-amber-300 tracking-widest uppercase">
              Processing
            </h2>
            <p className="text-[9px] text-amber-200/70 font-mono tracking-wider">
              AI Orchestrator Core
            </p>
          </div>
        </div>
      )}

      {/* Floating Canvas Quick Controls Bar (Top Left of 3D Canvas) */}
      <div className="absolute top-4 left-4 z-20 flex items-center gap-2 bg-space-950/80 backdrop-blur-xl border border-white/10 rounded-xl p-1.5 shadow-glass">
        <button
          onClick={() => {
            onResetSelection();
            engineRef.current?.resetView();
          }}
          className="px-2.5 py-1 text-xs rounded-lg text-slate-300 hover:text-cyan-300 hover:bg-white/5 flex items-center gap-1.5 transition-all"
          title="Reset Solar System Camera View (Double Click anywhere)"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset View</span>
        </button>

        <div className="w-px h-4 bg-white/10" />

        <button
          onClick={() => setShowLabels(!showLabels)}
          className={`px-2.5 py-1 text-xs rounded-lg flex items-center gap-1.5 transition-all ${
            showLabels
              ? "text-cyan-400 bg-cyan-500/10 border border-cyan-500/30"
              : "text-slate-400 hover:text-slate-200"
          }`}
          title="Toggle Floating Source Badges"
        >
          <Eye className="w-3.5 h-3.5" />
          <span>{showLabels ? "HUD On" : "HUD Off"}</span>
        </button>
      </div>

      {/* Bottom Solar System Navigation Slogan Banner */}
      <div className="absolute bottom-3 left-1/2 transform -translate-x-1/2 z-10 pointer-events-none text-center">
        <p className="text-[11px] font-sans tracking-widest text-slate-400 font-medium">
          Connect &bull; Process &bull; Visualize &bull; Discover
        </p>
        <p className="text-[10px] text-slate-500 font-light mt-0.5">
          Turn cultural data into living knowledge.
        </p>
      </div>
    </div>
  );
};
