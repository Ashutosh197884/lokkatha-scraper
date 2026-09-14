import React from "react";
import { GlassPanel } from "../components/common/GlassPanel";
import { MetricGauge } from "../components/common/MetricGauge";
import {
  BarChart3,
  Globe2,
  Layers,
  Leaf,
  PieChart,
  ShieldAlert,
  Sparkles,
  TrendingUp,
} from "lucide-react";

export const AnalyticsView: React.FC = () => {
  return (
    <div className="flex-1 p-6 overflow-y-auto bg-space-950 text-slate-100 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold font-sans text-white flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-cyan-400" />
          Folklore Intelligence & Crawl Analytics
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Deep telemetry on Indian folklore genre distribution, linguistic coverage, and Traditional Ecological Knowledge patterns.
        </p>
      </div>

      {/* Top 4 KPI Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <GlassPanel className="p-4">
          <span className="text-xs text-slate-400">Preserved Narratives</span>
          <p className="text-2xl font-bold font-mono text-white mt-1">1,842</p>
          <span className="text-[11px] text-emerald-400 font-mono">+12% this week</span>
        </GlassPanel>

        <GlassPanel className="p-4">
          <span className="text-xs text-slate-400">Identified TEK Practices</span>
          <p className="text-2xl font-bold font-mono text-cyan-400 mt-1">486</p>
          <span className="text-[11px] text-cyan-300 font-mono">Water & Ethno-botany</span>
        </GlassPanel>

        <GlassPanel className="p-4">
          <span className="text-xs text-slate-400">Regional Dialects Mapped</span>
          <p className="text-2xl font-bold font-mono text-amber-400 mt-1">34</p>
          <span className="text-[11px] text-amber-300 font-mono">Across 18 States</span>
        </GlassPanel>

        <GlassPanel className="p-4">
          <span className="text-xs text-slate-400">LLM Verification Accuracy</span>
          <p className="text-2xl font-bold font-mono text-purple-400 mt-1">98.4%</p>
          <span className="text-[11px] text-purple-300 font-mono">Zero Hallucinations</span>
        </GlassPanel>
      </div>

      {/* Breakdown Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Genre Breakdown */}
        <GlassPanel className="p-5">
          <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2 font-sans">
            <PieChart className="w-4 h-4 text-cyan-400" />
            Folklore Genre Distribution
          </h3>
          <div className="space-y-3 font-sans text-xs">
            {[
              { label: "Folktales & Fables (Panchatantra, Jataka)", count: "42%", color: "bg-cyan-400" },
              { label: "Heroic Legends & Oral Epics (Pabuji, Alha)", count: "24%", color: "bg-indigo-400" },
              { label: "Myths & Tribal Origin Lore (Bhil, Gond)", count: "18%", color: "bg-purple-400" },
              { label: "Traditional Ecological Knowledge (TEK)", count: "11%", color: "bg-emerald-400" },
              { label: "Folk Ballads & Ritual Songs", count: "5%", color: "bg-amber-400" },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex justify-between mb-1">
                  <span className="text-slate-300">{item.label}</span>
                  <span className="font-mono text-white font-bold">{item.count}</span>
                </div>
                <div className="w-full bg-space-900 rounded-full h-2 overflow-hidden border border-white/5">
                  <div className={`h-full rounded-full ${item.color}`} style={{ width: item.count }} />
                </div>
              </div>
            ))}
          </div>
        </GlassPanel>

        {/* Traditional Ecological Knowledge Categories */}
        <GlassPanel className="p-5">
          <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2 font-sans">
            <Leaf className="w-4 h-4 text-emerald-400" />
            Traditional Ecological Knowledge (TEK) Categories
          </h3>
          <div className="space-y-3 font-sans text-xs">
            {[
              { label: "Ancestral Water Management (Johads, Baolis)", count: "38%", color: "bg-blue-400" },
              { label: "Sacred Groves & Forest Protection (Orans)", count: "26%", color: "bg-emerald-400" },
              { label: "Indigenous Ethno-botany & Healing Herbs", count: "19%", color: "bg-teal-400" },
              { label: "Wildlife Coexistence & Sacred Taboos", count: "11%", color: "bg-amber-400" },
              { label: "Monsoon & Weather Bio-indicators", count: "6%", color: "bg-indigo-400" },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex justify-between mb-1">
                  <span className="text-slate-300">{item.label}</span>
                  <span className="font-mono text-white font-bold">{item.count}</span>
                </div>
                <div className="w-full bg-space-900 rounded-full h-2 overflow-hidden border border-white/5">
                  <div className={`h-full rounded-full ${item.color}`} style={{ width: item.count }} />
                </div>
              </div>
            ))}
          </div>
        </GlassPanel>
      </div>
    </div>
  );
};
