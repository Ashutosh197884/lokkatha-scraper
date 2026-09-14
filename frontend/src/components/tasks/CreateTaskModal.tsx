import React, { useState } from "react";
import { ScrapeTask } from "../../types/task";
import { DataSource } from "../../types/source";
import { GlassPanel } from "../common/GlassPanel";
import { Plus, Workflow, X } from "lucide-react";

interface CreateTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  sources: DataSource[];
  onLaunchTask: (task: ScrapeTask) => void;
}

export const CreateTaskModal: React.FC<CreateTaskModalProps> = ({
  isOpen,
  onClose,
  sources,
  onLaunchTask,
}) => {
  if (!isOpen) return null;

  const [title, setTitle] = useState("");
  const [region, setRegion] = useState("Rajasthan");
  const [selectedSources, setSelectedSources] = useState<string[]>(
    sources.slice(0, 3).map((s) => s.id)
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || selectedSources.length === 0) return;

    const newTask: ScrapeTask = {
      id: `task-${Date.now()}`,
      title: title.trim(),
      targetRegion: region.trim(),
      sourceIds: selectedSources,
      status: "running",
      progress: 5,
      stages: [
        {
          id: "stage-connect",
          name: "Connecting to sources",
          status: "running",
          duration: "Active...",
          message: "Establishing socket pool and verifying domain robots policies",
        },
        {
          id: "stage-fetch",
          name: "Fetching pages",
          status: "pending",
          duration: "Pending",
        },
        {
          id: "stage-parse",
          name: "Parsing content",
          status: "pending",
          duration: "Pending",
        },
        {
          id: "stage-extract",
          name: "Extracting entities & TEK",
          status: "pending",
          duration: "Pending",
        },
        {
          id: "stage-store",
          name: "Storing in database",
          status: "pending",
          duration: "Pending",
        },
      ],
      currentStageIndex: 0,
      startTime: new Date().toLocaleTimeString(),
      elapsedSeconds: 0,
      pagesProcessed: 0,
      storiesDiscovered: 0,
      currentSource: sources.find((s) => s.id === selectedSources[0])?.name || "Multiple Sources",
      currentOperation: "Initializing connection frontier...",
      errorCount: 0,
    };

    onLaunchTask(newTask);
    onClose();
  };

  const toggleSource = (id: string) => {
    if (selectedSources.includes(id)) {
      setSelectedSources(selectedSources.filter((s) => s !== id));
    } else {
      setSelectedSources([...selectedSources, id]);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-in fade-in duration-200">
      <GlassPanel
        variant="glow-blue"
        className="w-full max-w-lg max-h-[90vh] overflow-y-auto p-6 relative shadow-2xl border-cyan-500/40"
      >
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-all"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
            <Workflow className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white font-sans">
              Launch Scraping & Extraction Job
            </h2>
            <p className="text-xs text-slate-400">
              Orchestrate a targeted cultural crawl across selected orbiting source planets.
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs font-sans">
          <div>
            <label className="block text-slate-300 font-semibold mb-1">
              Job Title *
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Scraping Mithila Folk Tales & Madhubani Lore"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-space-900 border border-white/10 text-white focus:outline-none focus:border-cyan-500 font-sans"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">
              Target Cultural Region / State
            </label>
            <input
              type="text"
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              placeholder="e.g. Bihar, Mithilanchal"
              className="w-full px-3 py-2 rounded-xl bg-space-900 border border-white/10 text-white focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-2">
              Select Data Sources ({selectedSources.length} selected)
            </label>
            <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto pr-1">
              {sources.map((s) => {
                const isChecked = selectedSources.includes(s.id);
                return (
                  <button
                    type="button"
                    key={s.id}
                    onClick={() => toggleSource(s.id)}
                    className={`flex items-center gap-2 p-2 rounded-xl border text-left transition-all ${
                      isChecked
                        ? "bg-space-900 border-cyan-400 text-white"
                        : "bg-space-900/40 border-white/5 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <span
                      className="w-3 h-3 rounded-full flex-shrink-0"
                      style={{ backgroundColor: s.visual.color }}
                    />
                    <span className="text-xs font-medium truncate">{s.name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-white/10">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-space-900 hover:bg-white/10 text-slate-300 font-medium transition-all"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-medium flex items-center gap-2 shadow-glow-cyan transition-all"
            >
              <Plus className="w-4 h-4 font-bold" />
              <span>Launch Orchestration Job</span>
            </button>
          </div>
        </form>
      </GlassPanel>
    </div>
  );
};
