import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AppLayout from './layouts/AppLayout';
import JarvisCommandCore from './pages/JarvisCommandCore';
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

    // 2. Seamless local owner auto-authentication (zero blocking, zero login screens)
    authApi.setupStatus()
      .then(async ({ owner_configured }) => {
        if (!owner_configured) {
          setNeedsSetup(true);
          setSetupChecked(true);
          return;
        }

        try {
          const res = await authApi.quickUnlock();
          if (res && res.access_token) {
            setAuth(res.access_token, res.user_id, res.display_name, res.is_owner);
            setToken(res.access_token);
          }
        } catch (e) {
          console.log('Local console seamless auth active');
        }
        setSetupChecked(true);
      })
      .catch(() => {
        setSetupChecked(true);
      });
  }, []);

  if (needsSetup) {
    return (
      <Setup
        onComplete={() => {
          setNeedsSetup(false);
        }}
      />
    );
  }

  return (
    <Routes>
      {/* ── Main Command Core: Iron Man Holographic Interface (Instant Direct Boot) ── */}
      <Route path="/" element={<JarvisCommandCore />} />
      <Route path="/login" element={<Navigate to="/" replace />} />

      {/* Auxiliary Pages */}
      <Route element={<AppLayout />}>
        <Route path="/dashboard" element={<Overview />} />
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
      <Route path="*" element={<Navigate to="/" replace />} />
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
