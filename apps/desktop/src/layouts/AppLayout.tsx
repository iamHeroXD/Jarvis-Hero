import React, { useEffect } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  MessageSquare,
  Brain,
  Bot,
  FolderKanban,
  CheckSquare,
  Zap,
  Activity,
  Monitor,
  Settings,
  Mic,
  MicOff,
  Wifi,
  WifiOff,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Flame,
} from 'lucide-react';
import { useUIStore, useAuthStore } from '../store';
import { healthApi } from '../services/api';
import VoiceHUD from '../components/voice/VoiceHUD';
import { clsx } from 'clsx';

const NAV_ITEMS = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Overview' },
  { path: '/mission-control', icon: Flame, label: 'Mission Control' },
  { path: '/chat', icon: MessageSquare, label: 'Chat' },
  { path: '/evolution', icon: Sparkles, label: 'Evolution Centre' },
  { path: '/memory', icon: Brain, label: 'Memory' },
  { path: '/agents', icon: Bot, label: 'Agents' },
  { path: '/projects', icon: FolderKanban, label: 'Projects' },
  { path: '/tasks', icon: CheckSquare, label: 'Tasks' },
  { path: '/automations', icon: Zap, label: 'Automations' },
  { path: '/activity', icon: Activity, label: 'Activity' },
  { path: '/system', icon: Monitor, label: 'System' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export default function AppLayout() {
  const {
    sidebarCollapsed,
    setSidebarCollapsed,
    isListening,
    backendOnline,
    internetAvailable,
    geminiAvailable,
    setBackendOnline,
    setInternetAvailable,
    setSystemMetrics,
  } = useUIStore();
  const { displayName } = useAuthStore();

  // Poll backend health every 15s
  useEffect(() => {
    const poll = async () => {
      try {
        const health = await healthApi.get();
        setBackendOnline(true);
        setInternetAvailable(health.system.internet_available);
        setSystemMetrics(health.system);
      } catch {
        setBackendOnline(false);
      }
    };

    poll();
    const interval = setInterval(poll, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-surface-0">
      {/* ── Sidebar ───────────────────────────────────────── */}
      <motion.aside
        animate={{ width: sidebarCollapsed ? 64 : 220 }}
        transition={{ duration: 0.2, ease: 'easeInOut' }}
        className="flex flex-col bg-surface-1 border-r border-surface-border flex-shrink-0"
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 py-5 border-b border-surface-border">
          <div className="relative flex-shrink-0">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-accent-cyan flex items-center justify-center">
              <span className="text-white font-bold text-xs">J</span>
            </div>
            {isListening && (
              <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-accent-cyan animate-pulse" />
            )}
          </div>
          <AnimatePresence>
            {!sidebarCollapsed && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.15 }}
              >
                <span className="font-semibold text-sm text-text-primary tracking-wide">JARVIS</span>
                <p className="text-xs text-text-muted">{displayName || 'Owner'}</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto scroll-smooth-custom">
          {NAV_ITEMS.map(({ path, icon: Icon, label }) => (
            <NavLink
              key={path}
              to={path}
              end={path === '/'}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-2.5 py-2 rounded-lg cursor-pointer',
                  'text-sm font-medium transition-all duration-150',
                  'focus:outline-none',
                  isActive
                    ? 'bg-surface-4 text-text-primary border border-surface-border'
                    : 'text-text-secondary hover:text-text-primary hover:bg-surface-4'
                )
              }
              title={sidebarCollapsed ? label : undefined}
            >
              <Icon size={16} className="flex-shrink-0" />
              <AnimatePresence>
                {!sidebarCollapsed && (
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.1 }}
                  >
                    {label}
                  </motion.span>
                )}
              </AnimatePresence>
            </NavLink>
          ))}
        </nav>

        {/* Status Bar */}
        <div className="border-t border-surface-border px-3 py-3 space-y-2">
          <StatusRow
            icon={backendOnline ? <Wifi size={12} /> : <WifiOff size={12} />}
            label="Backend"
            status={backendOnline ? 'online' : 'offline'}
            collapsed={sidebarCollapsed}
          />
          <StatusRow
            icon={internetAvailable ? <Wifi size={12} /> : <WifiOff size={12} />}
            label="Internet"
            status={internetAvailable ? 'online' : 'offline'}
            collapsed={sidebarCollapsed}
          />
          <StatusRow
            icon={isListening ? <Mic size={12} /> : <MicOff size={12} />}
            label="Voice"
            status={isListening ? 'active' : 'muted'}
            collapsed={sidebarCollapsed}
          />
        </div>

        {/* Collapse toggle */}
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="flex items-center justify-center py-3 border-t border-surface-border text-text-muted hover:text-text-secondary transition-colors"
        >
          {sidebarCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
      </motion.aside>

      {/* ── Main Content ──────────────────────────────────── */}
      <main className="flex-1 overflow-hidden flex flex-col relative">
        <Outlet />
        <VoiceHUD />
      </main>
    </div>
  );
}

function StatusRow({
  icon,
  label,
  status,
  collapsed,
}: {
  icon: React.ReactNode;
  label: string;
  status: 'online' | 'offline' | 'active' | 'muted' | 'warning';
  collapsed: boolean;
}) {
  const dotClass = {
    online: 'bg-status-success',
    active: 'bg-accent-cyan',
    offline: 'bg-status-error',
    muted: 'bg-text-muted',
    warning: 'bg-status-warning',
  }[status];

  return (
    <div className="flex items-center gap-2 text-xs text-text-muted">
      <div className={clsx('w-1.5 h-1.5 rounded-full flex-shrink-0', dotClass)} />
      {!collapsed && (
        <>
          <span className="flex items-center gap-1 text-text-muted">
            {icon} {label}
          </span>
        </>
      )}
    </div>
  );
}
