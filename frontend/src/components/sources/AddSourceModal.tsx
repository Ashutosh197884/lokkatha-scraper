import React, { useState } from "react";
import { DataSource, PlanetTextureTheme, SourceType } from "../../types/source";
import { GlassPanel } from "../common/GlassPanel";
import { Globe, Orbit, Plus, Sparkles, X } from "lucide-react";

interface AddSourceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAddSource: (newSource: DataSource) => void;
  existingSourcesCount: number;
}

export const AddSourceModal: React.FC<AddSourceModalProps> = ({
  isOpen,
  onClose,
  onAddSource,
  existingSourcesCount,
}) => {
  if (!isOpen) return null;

  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [type, setType] = useState<SourceType>("website");
  const [region, setRegion] = useState("Rajasthan");
  const [language, setLanguage] = useState("hi, raj");
  const [category, setCategory] = useState("Cultural Archive");
  const [description, setDescription] = useState("");
  const [maxPages, setMaxPages] = useState(250);
  const [maxDepth, setMaxDepth] = useState(3);
  const [theme, setTheme] = useState<PlanetTextureTheme>("emerald-gas");
  const [tags, setTags] = useState("folktales, oral-traditions, tek");

  const themePalette: Record<
    PlanetTextureTheme,
    { label: string; color: string; glow: string }
  > = {
    "emerald-gas": { label: "Emerald Gas", color: "#10b981", glow: "#34d399" },
    "deep-ocean": { label: "Deep Ocean", color: "#38bdf8", glow: "#60a5fa" },
    "crimson-ringed": { label: "Crimson Rings", color: "#ef4444", glow: "#f87171" },
    "terrestrial-earth": { label: "Terrestrial Earth", color: "#3b82f6", glow: "#60a5fa" },
    "golden-dune": { label: "Golden Dunes", color: "#f59e0b", glow: "#fbbf24" },
    "amethyst-ice": { label: "Amethyst Ice", color: "#a855f7", glow: "#c084fc" },
    "electric-azure": { label: "Electric Azure", color: "#2563eb", glow: "#3b82f6" },
    "sandstone-canyon": { label: "Sandstone Canyon", color: "#f97316", glow: "#fb923c" },
    "toxic-neon": { label: "Toxic Neon", color: "#14b8a6", glow: "#2dd4bf" },
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !url.trim()) return;

    const baseRadius = 140 + existingSourcesCount * 42;
    const randomAngle = Math.random() * Math.PI * 2;
    const speed = 0.003 / (1 + existingSourcesCount * 0.15);
    const selectedVisual = themePalette[theme];

    const newSource: DataSource = {
      id: `source-${Date.now()}`,
      name: name.trim(),
      url: url.trim(),
      type,
      status: "connecting",
      region: region.trim() || "National",
      language: language.trim() || "Multilingual",
      category: category.trim() || "Folklore Archive",
      description:
        description.trim() ||
        `Structured crawling and continuous data discovery source for ${name}.`,
      orbit: {
        radius: baseRadius,
        angle: randomAngle,
        speed: Math.max(0.0006, speed),
        inclination: (Math.random() - 0.5) * 0.2,
        eccentricity: 0.96 + Math.random() * 0.08,
      },
      rotation: {
        speed: 0.008 + Math.random() * 0.008,
        tilt: Math.floor(5 + Math.random() * 25),
      },
      visual: {
        color: selectedVisual.color,
        glowColor: selectedVisual.glow,
        radius: 4.8 + Math.random() * 1.6,
        theme,
        hasRings: theme === "crimson-ringed" || Math.random() > 0.7,
      },
      metrics: {
        pagesProcessed: 0,
        recordsFound: 0,
        errorsCount: 0,
        latencyMs: 120,
        currentRate: 0,
        lastCrawledAt: "Just now",
        successRate: 100,
      },
      tags: tags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean),
      maxPages,
      maxDepth,
      crawlFrequency: "Daily",
    };

    onAddSource(newSource);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-in fade-in duration-200">
      <GlassPanel
        variant="glow-blue"
        className="w-full max-w-xl max-h-[90vh] overflow-y-auto p-6 relative shadow-2xl border-cyan-500/40"
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Title */}
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shadow-glow-cyan">
            <Orbit className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white font-sans">
              Add New Source Planet
            </h2>
            <p className="text-xs text-slate-400">
              Integrate a new cultural data stream into the solar system orchestration core.
            </p>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4 text-xs font-sans">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                Source Name *
              </label>
              <input
                type="text"
                required
                placeholder="e.g. IGNCA Janapada Sampada"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-space-900 border border-white/10 text-white focus:outline-none focus:border-cyan-500 font-sans"
              />
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                Target URL *
              </label>
              <input
                type="url"
                required
                placeholder="https://example.gov.in/folklore"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-space-900 border border-white/10 text-white focus:outline-none focus:border-cyan-500 font-sans"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                Source Type
              </label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value as SourceType)}
                className="w-full px-3 py-2 rounded-xl bg-space-900 border border-white/10 text-white focus:outline-none focus:border-cyan-500 capitalize"
              >
                <option value="website">Website</option>
                <option value="sitemap">Sitemap</option>
                <option value="rss">RSS / Feed</option>
                <option value="api">API Endpoint</option>
                <option value="document_collection">Document Collection</option>
                <option value="community">Community</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                Region / State
              </label>
              <input
                type="text"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                placeholder="e.g. Rajasthan, Marwar"
                className="w-full px-3 py-2 rounded-xl bg-space-900 border border-white/10 text-white focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                Language(s)
              </label>
              <input
                type="text"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                placeholder="e.g. hi, raj, en"
                className="w-full px-3 py-2 rounded-xl bg-space-900 border border-white/10 text-white focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                Max Pages ({maxPages})
              </label>
              <input
                type="range"
                min={20}
                max={1000}
                step={20}
                value={maxPages}
                onChange={(e) => setMaxPages(Number(e.target.value))}
                className="w-full accent-cyan-400"
              />
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                Crawl Depth ({maxDepth})
              </label>
              <input
                type="range"
                min={1}
                max={5}
                value={maxDepth}
                onChange={(e) => setMaxDepth(Number(e.target.value))}
                className="w-full accent-cyan-400"
              />
            </div>
          </div>

          {/* Planet Theme Selector */}
          <div>
            <label className="block text-slate-300 font-semibold mb-2">
              Planet Visual Appearance
            </label>
            <div className="grid grid-cols-3 gap-2">
              {Object.entries(themePalette).map(([tKey, tVal]) => (
                <button
                  type="button"
                  key={tKey}
                  onClick={() => setTheme(tKey as PlanetTextureTheme)}
                  className={`flex items-center gap-2 p-2 rounded-xl border transition-all text-left ${
                    theme === tKey
                      ? "bg-space-900 border-cyan-400 shadow-glow-cyan text-white"
                      : "bg-space-900/40 border-white/5 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <span
                    className="w-3.5 h-3.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: tVal.color }}
                  />
                  <span className="text-[11px] font-medium truncate">
                    {tVal.label}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">
              Tags (comma-separated)
            </label>
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="folktales, panchatantra, water-management"
              className="w-full px-3 py-2 rounded-xl bg-space-900 border border-white/10 text-white focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Buttons */}
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
              <span>Launch Planet into Orbit</span>
            </button>
          </div>
        </form>
      </GlassPanel>
    </div>
  );
};
