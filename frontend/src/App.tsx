import React, { useEffect, useRef, useState } from "react";
import { DataSource } from "./types/source";
import { ScrapeTask } from "./types/task";
import {
  ActivityLogItem,
  FolkloreItem,
  QueueItem,
  ResourceMetrics,
  SystemStats,
} from "./types/orchestration";
import {
  INITIAL_ACTIVE_TASK,
  INITIAL_ACTIVITIES,
  INITIAL_FOLKLORE_RECORDS,
  INITIAL_SOURCES,
} from "./state/orchestratorStore";
import { defaultEventConsumer } from "./state/eventConsumer";
import { Header } from "./components/layout/Header";
import { Sidebar } from "./components/layout/Sidebar";
import { OrchestratorView } from "./pages/OrchestratorView";
import { SourcesView } from "./pages/SourcesView";
import { TasksView } from "./pages/TasksView";
import { DataLibraryView } from "./pages/DataLibraryView";
import { AnalyticsView } from "./pages/AnalyticsView";
import { SettingsView } from "./pages/SettingsView";
import { SourceDetailDrawer } from "./components/sources/SourceDetailDrawer";
import { AddSourceModal } from "./components/sources/AddSourceModal";
import { CreateTaskModal } from "./components/tasks/CreateTaskModal";
import { TaskCompletionModal } from "./components/tasks/TaskCompletionModal";

export const App: React.FC = () => {
  // Navigation
  const [currentView, setCurrentView] = useState<
    "orchestrator" | "sources" | "tasks" | "library" | "analytics" | "settings"
  >("orchestrator");

  // State
  const [sources, setSources] = useState<DataSource[]>(INITIAL_SOURCES);
  const [activeTask, setActiveTask] = useState<ScrapeTask>(INITIAL_ACTIVE_TASK);
  const [tasksList, setTasksList] = useState<ScrapeTask[]>([INITIAL_ACTIVE_TASK]);
  const [activities, setActivities] = useState<ActivityLogItem[]>(INITIAL_ACTIVITIES);
  const [libraryRecords, setLibraryRecords] = useState<FolkloreItem[]>(INITIAL_FOLKLORE_RECORDS);

  // Selected Planet / Source
  const [selectedSource, setSelectedSource] = useState<DataSource | null>(null);

  // Modals
  const [isAddSourceOpen, setIsAddSourceOpen] = useState(false);
  const [isCreateTaskOpen, setIsCreateTaskOpen] = useState(false);
  const [isTaskCompletedModalOpen, setIsTaskCompletedModalOpen] = useState(false);

  // Telemetry
  const [simulationSpeed, setSimulationSpeed] = useState(1);
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [reducedMotion, setReducedMotion] = useState(false);

  const [stats, setStats] = useState<SystemStats>({
    status: "running",
    sourcesActive: 8,
    tasksRunning: 4,
    pagesProcessed: 1246,
    storiesDiscovered: 1842,
    documentsFound: 1420,
    relevantDocuments: 618,
    evidenceRecords: 1940,
    successRate: 99.2,
    totalDataProcessedGb: 2.3,
  });

  const [resources, setResources] = useState<ResourceMetrics>({
    cpuUsage: 62,
    memoryUsage: 48,
    networkUsage: 71,
    storageUsage: 36,
    processingSpeed: 128,
    speedHistory: [110, 115, 122, 128, 120, 134, 128],
  });

  const [queue, setQueue] = useState<QueueItem[]>([
    { sourceId: "source-wiki", sourceName: "Wikipedia", pendingUrlsCount: 24, color: "#10b981" },
    { sourceId: "source-archive", sourceName: "Archive.org", pendingUrlsCount: 18, color: "#ef4444" },
    { sourceId: "source-cultural-sites", sourceName: "Cultural Sites", pendingUrlsCount: 31, color: "#3b82f6" },
    { sourceId: "source-folklore-repos", sourceName: "Folklore Repositories", pendingUrlsCount: 27, color: "#14b8a6" },
    { sourceId: "source-community", sourceName: "Community Submissions", pendingUrlsCount: 12, color: "#f59e0b" },
    { sourceId: "source-academic-journals", sourceName: "Academic Journals", pendingUrlsCount: 19, color: "#2563eb" },
    { sourceId: "source-news-blogs", sourceName: "News & Blogs", pendingUrlsCount: 14, color: "#f97316" },
    { sourceId: "source-gov-portals", sourceName: "Government Portals", pendingUrlsCount: 11, color: "#a855f7" },
  ]);

  // Audio Synth via Web Audio API for subtle futuristic pulses
  const audioCtxRef = useRef<AudioContext | null>(null);

  const playCosmicBeep = (freq: number = 440) => {
    if (!soundEnabled) return;
    try {
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }
      const ctx = audioCtxRef.current;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      gain.gain.setValueAtTime(0.04, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.25);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.25);
    } catch {}
  };

  // Real-time Event-driven and Simulation Loop
  useEffect(() => {
    defaultEventConsumer.connect();

    const unsubscribe = defaultEventConsumer.subscribe((evt) => {
      const timeStr = new Date().toTimeString().split(" ")[0];
      setActivities((prev) => [
        {
          id: `act-${Date.now()}`,
          timestamp: timeStr,
          sourceId: evt.source_id || "system",
          sourceName: evt.data?.platform || "Lokkatha Core",
          eventType: "fetch",
          message: evt.message,
          level: "info",
        },
        ...prev.slice(0, 24),
      ]);
    });

    return () => {
      unsubscribe();
      defaultEventConsumer.disconnect();
    };
  }, []);

  // Orchestration Simulation Tick Loop
  useEffect(() => {
    if (simulationSpeed === 0) return;

    const interval = setInterval(() => {
      // 1. Advance Active Task progress
      setActiveTask((prev) => {
        if (prev.status !== "running") return prev;
        const nextProgress = prev.progress + 1;
        const newElapsed = prev.elapsedSeconds + 1;

        // Stage progress transitions
        const updatedStages = [...prev.stages];
        if (nextProgress > 20) updatedStages[0].status = "completed";
        if (nextProgress > 50) updatedStages[1].status = "completed";
        if (nextProgress > 70) {
          updatedStages[2].status = "completed";
          updatedStages[3].status = "running";
        }
        if (nextProgress > 90) {
          updatedStages[3].status = "completed";
          updatedStages[4].status = "running";
        }

        // Trigger task completion when reaching 100%
        if (nextProgress >= 100 && prev.progress < 100) {
          updatedStages[4].status = "completed";
          setIsTaskCompletedModalOpen(true);
          playCosmicBeep(880);
          return {
            ...prev,
            progress: 100,
            status: "completed",
            elapsedSeconds: newElapsed,
            stages: updatedStages,
          };
        }

        return {
          ...prev,
          progress: nextProgress >= 100 ? 100 : nextProgress,
          elapsedSeconds: newElapsed,
          stages: updatedStages,
          pagesProcessed: prev.pagesProcessed + (Math.random() > 0.6 ? 1 : 0),
          storiesDiscovered: prev.storiesDiscovered + (Math.random() > 0.8 ? 1 : 0),
        };
      });

      // 2. Resource gauges telemetry jitter
      setResources((prev) => ({
        ...prev,
        cpuUsage: Math.min(95, Math.max(35, prev.cpuUsage + Math.floor((Math.random() - 0.5) * 6))),
        memoryUsage: Math.min(90, Math.max(40, prev.memoryUsage + Math.floor((Math.random() - 0.5) * 2))),
        networkUsage: Math.min(98, Math.max(45, prev.networkUsage + Math.floor((Math.random() - 0.5) * 8))),
        storageUsage: prev.storageUsage,
        processingSpeed: Math.min(240, Math.max(80, prev.processingSpeed + Math.floor((Math.random() - 0.5) * 10))),
      }));

      // 3. Pipeline Event Generation
      if (Math.random() < 0.35) {
        const randomSource = sources[Math.floor(Math.random() * sources.length)];
        const eventTemplates = [
          `Discovered ${Math.floor(2 + Math.random() * 8)} pages with robots compliance on ${randomSource.name}`,
          `Extracted structured narrative with direct provenance from ${randomSource.domain || randomSource.name}`,
          `Validated Traditional Ecological Knowledge (TEK) claim`,
          `Recorded canonical variant tree for oral tradition`,
          `Computed SHA-256 layer hash with zero text modification`,
        ];
        const newMsg = eventTemplates[Math.floor(Math.random() * eventTemplates.length)];
        const now = new Date();
        const timeStr = now.toTimeString().split(" ")[0];

        setActivities((prev) => [
          {
            id: `act-${Date.now()}`,
            timestamp: timeStr,
            sourceId: randomSource.id,
            sourceName: randomSource.name,
            eventType: "fetch",
            message: newMsg,
            level: "info",
          },
          ...prev.slice(0, 24),
        ]);

        // Increment stats
        setStats((prev) => ({
          ...prev,
          pagesProcessed: prev.pagesProcessed + 1,
          storiesDiscovered: prev.storiesDiscovered + (Math.random() > 0.5 ? 1 : 0),
          evidenceRecords: (prev.evidenceRecords || 1940) + (Math.random() > 0.6 ? 2 : 0),
        }));

        playCosmicBeep(520 + Math.random() * 100);
      }
    }, 1200 / simulationSpeed);

    return () => clearInterval(interval);
  }, [simulationSpeed, sources, soundEnabled]);

  // Handle Add New Source
  const handleAddSource = (newSource: DataSource) => {
    setSources((prev) => [...prev, newSource]);
    setQueue((prev) => [
      ...prev,
      {
        sourceId: newSource.id,
        sourceName: newSource.name,
        pendingUrlsCount: 15,
        color: newSource.visual.color,
      },
    ]);
    setStats((prev) => ({
      ...prev,
      sourcesActive: prev.sourcesActive + 1,
    }));
    setActivities((prev) => [
      {
        id: `act-${Date.now()}`,
        timestamp: new Date().toTimeString().split(" ")[0],
        sourceId: newSource.id,
        sourceName: newSource.name,
        eventType: "connect",
        message: `New source planet launched into orbit at ${newSource.orbit.radius} AU (${newSource.type})`,
        level: "success",
      },
      ...prev,
    ]);
    setSelectedSource(newSource);
    playCosmicBeep(880);
  };

  // Handle Launch New Task
  const handleLaunchTask = (newTask: ScrapeTask) => {
    setActiveTask(newTask);
    setTasksList((prev) => [newTask, ...prev]);
    setStats((prev) => ({
      ...prev,
      tasksRunning: prev.tasksRunning + 1,
      status: "running",
    }));
    setIsTaskCompletedModalOpen(false);
    playCosmicBeep(660);
  };

  // Toggle individual source status
  const handleToggleSourceStatus = (sourceId: string, newStatus: any) => {
    setSources((prev) =>
      prev.map((s) => (s.id === sourceId ? { ...s, status: newStatus } : s))
    );
    if (selectedSource && selectedSource.id === sourceId) {
      setSelectedSource({ ...selectedSource, status: newStatus });
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-space-950 font-sans text-slate-100 select-none">
      {/* Top Navigation Bar */}
      <Header
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        simulationSpeed={simulationSpeed}
        onSpeedChange={setSimulationSpeed}
        soundEnabled={soundEnabled}
        onSoundToggle={() => setSoundEnabled(!soundEnabled)}
        activeSourcesCount={stats.sourcesActive}
        runningTasksCount={stats.tasksRunning}
      />

      {/* Main Workspace Layout (Sidebar + Active View) */}
      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          currentView={currentView}
          onViewChange={setCurrentView}
          sourcesCount={sources.length}
          activeTasksCount={stats.tasksRunning}
        />

        {/* View Switcher */}
        {currentView === "orchestrator" && (
          <OrchestratorView
            sources={sources}
            activeTask={activeTask}
            stats={stats}
            resources={resources}
            queue={queue}
            activities={activities}
            selectedSourceId={selectedSource?.id || null}
            onSelectSource={setSelectedSource}
            onResetSelection={() => setSelectedSource(null)}
            onOpenAddSourceModal={() => setIsAddSourceOpen(true)}
            simulationSpeed={simulationSpeed}
            reducedMotion={reducedMotion}
          />
        )}

        {currentView === "sources" && (
          <SourcesView
            sources={sources}
            onSelectSource={setSelectedSource}
            onOpenAddModal={() => setIsAddSourceOpen(true)}
            onToggleStatus={handleToggleSourceStatus}
          />
        )}

        {currentView === "tasks" && (
          <TasksView
            tasks={tasksList}
            onTriggerNewTask={() => setIsCreateTaskOpen(true)}
          />
        )}

        {currentView === "library" && (
          <DataLibraryView records={libraryRecords} />
        )}

        {currentView === "analytics" && <AnalyticsView />}

        {currentView === "settings" && <SettingsView />}
      </div>

      {/* Selected Source Planet Detail Drawer */}
      <SourceDetailDrawer
        source={selectedSource}
        onClose={() => setSelectedSource(null)}
        onToggleStatus={handleToggleSourceStatus}
        onViewLibrary={() => {
          setSelectedSource(null);
          setCurrentView("library");
        }}
      />

      {/* Add New Source Planet Modal */}
      <AddSourceModal
        isOpen={isAddSourceOpen}
        onClose={() => setIsAddSourceOpen(false)}
        onAddSource={handleAddSource}
        existingSourcesCount={sources.length}
      />

      {/* Create Task Modal */}
      <CreateTaskModal
        isOpen={isCreateTaskOpen}
        onClose={() => setIsCreateTaskOpen(false)}
        sources={sources}
        onLaunchTask={handleLaunchTask}
      />

      {/* Task Completion Modal */}
      <TaskCompletionModal
        isOpen={isTaskCompletedModalOpen}
        onClose={() => setIsTaskCompletedModalOpen(false)}
        taskTitle={activeTask.title}
        sourcesUsed={sources.filter((s) => activeTask.sourceIds.includes(s.id))}
        pagesProcessed={activeTask.pagesProcessed || 128}
        documentsFound={stats.documentsFound || 1420}
        relevantDocuments={stats.relevantDocuments || 618}
        evidenceRecords={stats.evidenceRecords || 1940}
        folkloreRecords={activeTask.storiesDiscovered || 48}
        onViewLibrary={() => {
          setIsTaskCompletedModalOpen(false);
          setCurrentView("library");
        }}
      />
    </div>
  );
};
