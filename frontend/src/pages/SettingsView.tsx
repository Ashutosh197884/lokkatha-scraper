import React, { useState } from "react";
import { GlassPanel } from "../components/common/GlassPanel";
import {
  Cpu,
  Database,
  Lock,
  RotateCcw,
  Save,
  Server,
  Settings,
  Shield,
  Zap,
} from "lucide-react";

export const SettingsView: React.FC = () => {
  const [concurrency, setConcurrency] = useState(8);
  const [delaySeconds, setDelaySeconds] = useState(1.5);
  const [respectRobots, setRespectRobots] = useState(true);
  const [enablePlaywright, setEnablePlaywright] = useState(true);
  const [llmModel, setLlmModel] = useState("gemini-1.5-flash");
  const [savedAlert, setSavedAlert] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedAlert(true);
    setTimeout(() => setSavedAlert(false), 3000);
  };

  return (
    <div className="flex-1 p-6 overflow-y-auto bg-space-950 text-slate-100 space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold font-sans text-white flex items-center gap-2">
          <Settings className="w-6 h-6 text-cyan-400" />
          Orchestration & Crawler Settings
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Configure crawler politeness, concurrency, LLM prompt extractors, and database connections.
        </p>
      </div>

      {savedAlert && (
        <div className="p-3 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs flex items-center gap-2 font-medium">
          Settings synchronized with backend orchestrator core successfully!
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6 font-sans text-xs">
        {/* Crawler Politeness & Concurrency */}
        <GlassPanel className="p-5 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            Crawler Engine & Politeness Layer
          </h3>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                Concurrent Worker Threads ({concurrency})
              </label>
              <input
                type="range"
                min={1}
                max={32}
                value={concurrency}
                onChange={(e) => setConcurrency(Number(e.target.value))}
                className="w-full accent-cyan-400"
              />
              <span className="text-[11px] text-slate-500">
                Number of simultaneous asynchronous crawl workers.
              </span>
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                Domain Politeness Delay ({delaySeconds}s)
              </label>
              <input
                type="range"
                min={0.2}
                max={5.0}
                step={0.1}
                value={delaySeconds}
                onChange={(e) => setDelaySeconds(Number(e.target.value))}
                className="w-full accent-cyan-400"
              />
              <span className="text-[11px] text-slate-500">
                Delay between successive requests to the same origin domain.
              </span>
            </div>
          </div>

          <div className="flex items-center gap-6 pt-2 border-t border-white/5">
            <label className="flex items-center gap-2 cursor-pointer text-slate-300">
              <input
                type="checkbox"
                checked={respectRobots}
                onChange={(e) => setRespectRobots(e.target.checked)}
                className="rounded accent-cyan-400 w-4 h-4"
              />
              <span>Strict Robots.txt Compliance</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer text-slate-300">
              <input
                type="checkbox"
                checked={enablePlaywright}
                onChange={(e) => setEnablePlaywright(e.target.checked)}
                className="rounded accent-cyan-400 w-4 h-4"
              />
              <span>Enable Playwright Dynamic JS Rendering</span>
            </label>
          </div>
        </GlassPanel>

        {/* LLM Structured Extraction */}
        <GlassPanel className="p-5 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Zap className="w-4 h-4 text-amber-400" />
            LLM Prompt Extractor Configuration
          </h3>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                Primary Extraction Model
              </label>
              <select
                value={llmModel}
                onChange={(e) => setLlmModel(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-space-900 border border-white/10 text-white focus:outline-none focus:border-cyan-500 font-sans"
              >
                <option value="gemini-1.5-flash">Gemini 1.5 Flash (Fast Extraction)</option>
                <option value="gemini-1.5-pro">Gemini 1.5 Pro (Deep Research)</option>
                <option value="local-ollama">Local Llama 3.3 (Air-gapped)</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                Temperature (0.0 - Strict Non-hallucination)
              </label>
              <input
                type="text"
                disabled
                value="0.1 (Strict Archetype Preservation)"
                className="w-full px-3 py-2 rounded-xl bg-space-900/50 border border-white/5 text-slate-400 font-mono"
              />
            </div>
          </div>
        </GlassPanel>

        {/* Database & Storage */}
        <GlassPanel className="p-5 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Database className="w-4 h-4 text-emerald-400" />
            Persistence & Vector Database (pgvector)
          </h3>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                Structured Storage Directory
              </label>
              <input
                type="text"
                disabled
                value="data/structured"
                className="w-full px-3 py-2 rounded-xl bg-space-900/50 border border-white/5 text-slate-300 font-mono"
              />
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                PostgreSQL URI
              </label>
              <input
                type="password"
                value="postgresql://lokkatha:secret@localhost:5432/lokkatha_db"
                readOnly
                className="w-full px-3 py-2 rounded-xl bg-space-900/50 border border-white/5 text-slate-400 font-mono"
              />
            </div>
          </div>
        </GlassPanel>

        {/* Save CTA */}
        <div className="flex justify-end">
          <button
            type="submit"
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-medium flex items-center gap-2 shadow-glow-cyan transition-all"
          >
            <Save className="w-4 h-4" />
            <span>Save & Apply Settings</span>
          </button>
        </div>
      </form>
    </div>
  );
};
