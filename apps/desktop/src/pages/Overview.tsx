import { useEffect, useState } from 'react';
import { format } from 'date-fns';
import { motion } from 'framer-motion';
import {
  Cpu,
  MemoryStick,
  HardDrive,
  Wifi,
  WifiOff,
  Mic,
  Bot,
  CheckCircle,
  AlertCircle,
  Clock,
  Zap,
} from 'lucide-react';
import { useUIStore, useAuthStore } from '../store';
import { healthApi } from '../services/api';
import { clsx } from 'clsx';

export default function OverviewPage() {
  const { systemMetrics, backendOnline, internetAvailable, geminiAvailable, currentMode } = useUIStore();
  const { displayName } = useAuthStore();
  const [time, setTime] = useState(new Date());
  const [health, setHealth] = useState<Record<string, string>>({});

  // Live clock
  useEffect(() => {
    const interval = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  // Initial health load
  useEffect(() => {
    healthApi.get().then((h) => setHealth(h.components)).catch(() => {});
  }, []);

  const greeting = (() => {
    const hour = time.getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  })();

  return (
    <div className="flex flex-col h-full overflow-y-auto scroll-smooth-custom p-6 gap-6">
      {/* ── Header ─────────────────────────────────────────────── */}
      <div className="flex items-start justify-between">
        <div>
          <motion.h1
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-2xl font-semibold text-text-primary"
          >
            {greeting}{displayName ? `, ${displayName}` : ''}.
          </motion.h1>
          <p className="text-text-secondary mt-1 text-sm">
            {format(time, 'EEEE, d MMMM yyyy')} · {format(time, 'HH:mm:ss')}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className={clsx(
            'badge',
            backendOnline ? 'badge-green' : 'badge-red'
          )}>
            {backendOnline ? '● Systems online' : '● Backend offline'}
          </span>
          <span className={clsx(
            'badge',
            internetAvailable ? 'badge-blue' : 'badge-orange'
          )}>
            {internetAvailable ? 'Online' : 'Offline'}
          </span>
          <span className="badge badge-muted capitalize">{currentMode} mode</span>
        </div>
      </div>

      {/* ── Status Grid ────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatusCard
          icon={<Cpu size={16} />}
          label="CPU"
          value={systemMetrics ? `${systemMetrics.cpu_percent.toFixed(0)}%` : '—'}
          subValue={systemMetrics ? 'i5-7200U' : undefined}
          status={
            !systemMetrics ? 'muted'
            : systemMetrics.cpu_percent > 80 ? 'warning'
            : 'ok'
          }
        />
        <StatusCard
          icon={<MemoryStick size={16} />}
          label="RAM"
          value={systemMetrics ? `${systemMetrics.ram_percent.toFixed(0)}%` : '—'}
          subValue={systemMetrics ? `${systemMetrics.ram_used_gb}/${systemMetrics.ram_total_gb} GB` : undefined}
          status={
            !systemMetrics ? 'muted'
            : systemMetrics.ram_percent > 85 ? 'error'
            : systemMetrics.ram_percent > 70 ? 'warning'
            : 'ok'
          }
        />
        <StatusCard
          icon={<HardDrive size={16} />}
          label="Disk Free"
          value={systemMetrics ? `${systemMetrics.disk_free_gb} GB` : '—'}
          subValue={systemMetrics ? `${(100 - systemMetrics.disk_percent).toFixed(0)}% available` : undefined}
          status={
            !systemMetrics ? 'muted'
            : systemMetrics.disk_free_gb < 2 ? 'error'
            : systemMetrics.disk_free_gb < 5 ? 'warning'
            : 'ok'
          }
        />
        <StatusCard
          icon={internetAvailable ? <Wifi size={16} /> : <WifiOff size={16} />}
          label="Connectivity"
          value={internetAvailable ? 'Online' : 'Offline'}
          subValue={internetAvailable ? 'Gemini available' : 'Local mode only'}
          status={internetAvailable ? 'ok' : 'warning'}
        />
      </div>

      {/* ── Component Health ───────────────────────────────────── */}
      <div className="card p-5">
        <h2 className="text-sm font-medium text-text-secondary uppercase tracking-wider mb-4">
          Component Status
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {Object.entries(health).map(([component, status]) => (
            <ComponentStatus key={component} name={component} status={status} />
          ))}
        </div>
      </div>

      {/* ── JARVIS Process ─────────────────────────────────────── */}
      {systemMetrics && (
        <div className="card p-5">
          <h2 className="text-sm font-medium text-text-secondary uppercase tracking-wider mb-4">
            JARVIS Process
          </h2>
          <div className="flex gap-6 text-sm">
            <div>
              <span className="text-text-muted">CPU usage</span>
              <p className="text-text-primary font-medium mt-1">
                {systemMetrics.jarvis_cpu_percent.toFixed(1)}%
              </p>
            </div>
            <div>
              <span className="text-text-muted">Memory</span>
              <p className="text-text-primary font-medium mt-1">
                {systemMetrics.jarvis_ram_mb.toFixed(0)} MB
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ── Quick Actions ──────────────────────────────────────── */}
      <div className="card p-5">
        <h2 className="text-sm font-medium text-text-secondary uppercase tracking-wider mb-4">
          Quick Actions
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <QuickAction icon={<Bot size={16} />} label="Start Chat" href="/chat" />
          <QuickAction icon={<Mic size={16} />} label="Voice Mode" onClick={() => {}} />
          <QuickAction icon={<Zap size={16} />} label="Automations" href="/automations" />
          <QuickAction icon={<Clock size={16} />} label="Set Reminder" href="/tasks" />
        </div>
      </div>

      {/* ── Info Banner ────────────────────────────────────────── */}
      <div className="panel p-4 flex items-start gap-3">
        <AlertCircle size={16} className="text-accent mt-0.5 flex-shrink-0" />
        <div className="text-sm text-text-secondary">
          <span className="text-text-primary font-medium">Phase 1 — Core Application</span>
          {' '}— Backend, database, navigation, and system monitoring are operational.
          Configure your Gemini API key in <span className="text-accent">Settings → AI</span> to enable AI conversation.
          Voice and agent features arrive in later phases.
        </div>
      </div>
    </div>
  );
}

// ── Sub-components ────────────────────────────────────────────────────────────

function StatusCard({
  icon,
  label,
  value,
  subValue,
  status,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  subValue?: string;
  status: 'ok' | 'warning' | 'error' | 'muted';
}) {
  const statusColour = {
    ok: 'text-status-success',
    warning: 'text-status-warning',
    error: 'text-status-error',
    muted: 'text-text-muted',
  }[status];

  return (
    <div className="card p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-text-muted text-xs uppercase tracking-wider">{label}</span>
        <span className={clsx('text-xs', statusColour)}>{icon}</span>
      </div>
      <p className="text-xl font-semibold text-text-primary">{value}</p>
      {subValue && <p className="text-xs text-text-muted mt-1">{subValue}</p>}
    </div>
  );
}

function ComponentStatus({ name, status }: { name: string; status: string }) {
  const isOk = status === 'online' || status === 'connected';
  const isWarning = status === 'not_checked' || status === 'not_initialised';
  const isOff = status === 'disabled' || status === 'offline';

  return (
    <div className="flex items-center gap-2 text-sm">
      {isOk ? (
        <CheckCircle size={12} className="text-status-success flex-shrink-0" />
      ) : isWarning ? (
        <Clock size={12} className="text-status-warning flex-shrink-0" />
      ) : (
        <AlertCircle size={12} className="text-text-muted flex-shrink-0" />
      )}
      <span className="text-text-secondary capitalize">
        {name.replace(/_/g, ' ')}
      </span>
      <span className={clsx(
        'ml-auto text-xs',
        isOk ? 'text-status-success' : isWarning ? 'text-status-warning' : 'text-text-muted'
      )}>
        {status}
      </span>
    </div>
  );
}

function QuickAction({
  icon,
  label,
  href,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  href?: string;
  onClick?: () => void;
}) {
  const content = (
    <div className="panel p-3 flex items-center gap-2 cursor-pointer hover:bg-surface-4 transition-colors text-sm text-text-secondary hover:text-text-primary">
      {icon}
      <span>{label}</span>
    </div>
  );

  if (href) {
    return <a href={href}>{content}</a>;
  }
  return <button onClick={onClick} className="text-left">{content}</button>;
}
