import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AppLayout from './layouts/AppLayout';
import Overview from './pages/Overview';
import Chat from './pages/Chat';
import Setup from './pages/Setup';
import LoginPage from './pages/Login';
import MissionControl from './pages/MissionControl';
import EvolutionCentre from './pages/EvolutionCentre';
import MemoryPage from './pages/MemoryPage';
import AgentsPage from './pages/Agents';
import ProjectsPage from './pages/Projects';
import TasksPage from './pages/Tasks';
import AutomationsPage from './pages/Automations';
import ActivityPage from './pages/Activity';
import SystemPage from './pages/System';
import SettingsPage from './pages/Settings';
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
    // 1. Sync stored token if available
    if (token) setToken(token);

    // 2. Check if owner is configured and attempt seamless local console unlock
    authApi.setupStatus()
      .then(async ({ owner_configured }) => {
        if (!owner_configured) {
          setNeedsSetup(true);
          setSetupChecked(true);
          return;
        }

        // If not already authenticated, attempt instant local owner unlock
        if (!isAuthenticated) {
          try {
            const res = await authApi.quickUnlock();
            setAuth(res.access_token, res.user_id, res.display_name, res.is_owner);
            setToken(res.access_token);
          } catch {
            // Fall back to showing login page
          }
        }
        setSetupChecked(true);
      })
      .catch(() => {
        // Fall back to login/app if network hiccup
        setSetupChecked(true);
      });
  }, []);

  if (!setupChecked) {
    return (
      <div className="min-h-screen w-screen bg-surface-0 flex flex-col items-center justify-center p-4">
        <div className="relative w-20 h-20 mb-4 flex items-center justify-center">
          <div className="absolute inset-0 rounded-full border border-cyan-400/40 animate-ping opacity-40" />
          <div className="absolute inset-2 rounded-full border border-accent/60 animate-spin-slow" />
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-accent to-accent-cyan flex items-center justify-center shadow-glow">
            <span className="text-white font-mono font-bold text-sm">J</span>
          </div>
        </div>
        <div className="text-accent text-xs font-mono tracking-widest uppercase animate-pulse">
          INITIALISING J.A.R.V.I.S. PROTOCOLS...
        </div>
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
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={<Navigate to="/" replace />} />
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
