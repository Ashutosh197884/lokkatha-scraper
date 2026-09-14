# 🌌 Lokkatha Orchestrator Frontend (3D Solar System Command Center)

An interactive, animated solar-system-style command center for the Lokkatha Web Intelligence & Folklore Scraping System.

---

## 🚀 Tech Stack

- **Framework**: [React 19](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)
- **Build Tool**: [Vite 6](https://vitejs.dev/)
- **3D Graphics Engine**: [Three.js](https://threejs.org/) (Custom WebGL Solar Engine with procedural shaders, dynamic orbital mechanics & particle trajectories)
- **Styling**: [Tailwind CSS 3](https://tailwindcss.com/) with Glassmorphism & custom neon glows
- **Icons**: [Lucide React](https://lucide.dev/)

---

## 🪐 Architecture & Components

```text
src/
├── components/
│   ├── common/              # GlassPanel, StatusBadge, ProgressBar, MetricGauge
│   ├── dashboard/           # SystemStatusCard, CurrentTaskCard, LiveActivityFeed, ResourceMetrics, QueueOverview, DiscoveredMetricCard
│   ├── layout/              # Header, Sidebar
│   ├── orchestrator/        # SolarSystemEngine (Three.js), SolarSystemCanvas, textureUtils
│   ├── sources/             # SourceDetailDrawer, AddSourceModal
│   └── tasks/               # CreateTaskModal
├── pages/                   # OrchestratorView, SourcesView, TasksView, DataLibraryView, AnalyticsView, SettingsView
├── state/                   # Centralized orchestratorStore & real-time simulation tick loop
└── types/                   # TypeScript types for sources, tasks, and telemetry
```

---

## 🛠️ Local Development

```bash
# Install dependencies
npm install

# Start Vite development server
npm run dev

# Build production bundle
npm run build
```

---

## 🎮 Interactive Controls

- **Orbit Drag**: Hold Left Click / Touch Drag to rotate the solar system in 3D space.
- **Zoom**: Scroll wheel or pinch to zoom in/out from wide-angle to close orbit.
- **Inspect Planet**: Click any orbiting source planet to focus the camera and open the **Source Detail Drawer**.
- **Reset Camera**: Double-click anywhere or click **Reset View** in the top-left HUD.
- **Add Source**: Click `+ Add New Source` to launch a new customized data source planet into orbit.
- **Simulation Speed**: Toggle between `Paused`, `1x`, `2x`, and `5x Turbo` in the top header.
