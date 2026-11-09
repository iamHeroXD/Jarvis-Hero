import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AppLayout from './layouts/AppLayout';
import Overview from './pages/Overview';
import Chat from './pages/Chat';
import Setup from './pages/Setup';
import MissionControl from './pages/MissionControl';
import EvolutionCentre from './pages/EvolutionCentre';
import {
  MemoryPage,
  AgentsPage,
  ProjectsPage,
  TasksPage,
  AutomationsPage,
  ActivityPage,
  SystemPage,
  SettingsPage,
} from './pages/Placeholders';
import { useAuthStore } from './store';
import { authApi, setToken } from './services/api';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
    },
  },
});

function AppRoutes() {
  const { isAuthenticated, token, setAuth } = useAuthStore();
  const [setupChecked, setSetupChecked] = useState(false);
  const [needsSetup, setNeedsSetup] = useState(false);

  useEffect(() => {
    // Check if the backend has an owner configured
    authApi.setupStatus()
      .then(({ owner_configured }) => {
        setNeedsSetup(!owner_configured);
        setSetupChecked(true);
      })
      .catch(() => {
        // Backend might be offline — show main app
        setSetupChecked(true);
      });

    // Sync token to api service
    if (token) setToken(token);
  }, []);

  if (!setupChecked) {
    return (
      <div className="min-h-screen bg-surface-0 flex items-center justify-center">
        <div className="text-text-muted text-sm">Connecting to JARVIS...</div>
      </div>
    );
  }

  if (needsSetup) {
    return (
      <Setup
        onComplete={() => {
          setNeedsSetup(false);
        }}
      />
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Overview />} />
        <Route path="/mission-control" element={<MissionControl />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/evolution" element={<EvolutionCentre />} />
        <Route path="/memory" element={<MemoryPage />} />
        <Route path="/agents" element={<AgentsPage />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/tasks" element={<TasksPage />} />
        <Route path="/automations" element={<AutomationsPage />} />
        <Route path="/activity" element={<ActivityPage />} />
        <Route path="/system" element={<SystemPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </QueryClientProvider>
  );
}
