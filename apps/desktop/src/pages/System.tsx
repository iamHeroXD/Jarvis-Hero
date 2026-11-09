import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Monitor,
  Cpu,
  HardDrive,
  Activity,
  Zap,
  Shield,
  Layers,
  Thermometer,
  Wifi,
} from 'lucide-react';
import { healthApi, governorApi, profilesApi } from '../services/api';

export default function SystemPage() {
  const queryClient = useQueryClient();

  const { data: health } = useQuery({
    queryKey: ['systemHealthFull'],
    queryFn: healthApi.get,
    refetchInterval: 3000,
  });

  const { data: governor } = useQuery({
    queryKey: ['systemGovernor'],
    queryFn: governorApi.getStatus,
    refetchInterval: 5000,
  });

  const { data: profileData } = useQuery({
    queryKey: ['systemProfile'],
    queryFn: profilesApi.current,
  });

  const setProfileMutation = useMutation({
    mutationFn: (profile: 'eco' | 'balanced' | 'performance') =>
      governorApi.setProfile(profile),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['systemGovernor'] });
    },
  });

  const switchUserMutation = useMutation({
    mutationFn: (profile: 'owner' | 'family' | 'guest') =>
      profilesApi.switch(profile),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['systemProfile'] });
    },
  });

  const metrics = health?.system;

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* ── Top Header ────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-border pb-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-accent/20 border border-accent/40 flex items-center justify-center text-accent">
            <Monitor size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-text-primary tracking-wide">System Telemetry & Governor</h1>
            <p className="text-xs text-text-secondary">
              Real-time hardware performance, RAM throttling thresholds, and profile permissions.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Backend Nominal
          </span>
        </div>
      </div>

      {/* ── Metrics Cards ──────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* CPU */}
        <div className="card p-4 border border-surface-border">
          <div className="flex items-center justify-between text-xs text-text-muted mb-2">
            <span className="flex items-center gap-1.5"><Cpu size={14} className="text-accent" /> CPU Load</span>
            <span className="font-mono text-text-primary">{metrics?.cpu_percent ?? 0}%</span>
          </div>
          <div className="w-full bg-surface-3 h-2 rounded-full overflow-hidden mb-2">
            <div
              className="bg-accent h-full transition-all duration-300"
              style={{ width: `${Math.min(100, metrics?.cpu_percent ?? 0)}%` }}
            />
          </div>
          <div className="text-[11px] text-text-muted font-mono">
            JARVIS Core: {metrics?.jarvis_cpu_percent?.toFixed(1) ?? '0.0'}%
          </div>
        </div>

        {/* RAM */}
        <div className="card p-4 border border-surface-border">
          <div className="flex items-center justify-between text-xs text-text-muted mb-2">
            <span className="flex items-center gap-1.5"><Layers size={14} className="text-cyan-400" /> RAM Usage</span>
            <span className="font-mono text-text-primary">{metrics?.ram_percent ?? 0}%</span>
          </div>
          <div className="w-full bg-surface-3 h-2 rounded-full overflow-hidden mb-2">
            <div
              className={`h-full transition-all duration-300 ${
                (metrics?.ram_percent ?? 0) > 85 ? 'bg-rose-500' : 'bg-cyan-400'
              }`}
              style={{ width: `${Math.min(100, metrics?.ram_percent ?? 0)}%` }}
            />
          </div>
          <div className="text-[11px] text-text-muted font-mono">
            {metrics?.ram_used_gb?.toFixed(1) ?? 0} GB / {metrics?.ram_total_gb?.toFixed(1) ?? 8} GB
          </div>
        </div>

        {/* Disk */}
        <div className="card p-4 border border-surface-border">
          <div className="flex items-center justify-between text-xs text-text-muted mb-2">
            <span className="flex items-center gap-1.5"><HardDrive size={14} className="text-amber-400" /> Disk Space</span>
            <span className="font-mono text-text-primary">{metrics?.disk_free_gb?.toFixed(1) ?? 0} GB Free</span>
          </div>
          <div className="w-full bg-surface-3 h-2 rounded-full overflow-hidden mb-2">
            <div
              className="bg-amber-400 h-full transition-all duration-300"
              style={{ width: `${Math.min(100, metrics?.disk_percent ?? 0)}%` }}
            />
          </div>
          <div className="text-[11px] text-text-muted font-mono">
            Used: {metrics?.disk_percent?.toFixed(1) ?? 0}%
          </div>
        </div>

        {/* Network & Uptime */}
        <div className="card p-4 border border-surface-border">
          <div className="flex items-center justify-between text-xs text-text-muted mb-2">
            <span className="flex items-center gap-1.5"><Wifi size={14} className="text-emerald-400" /> Connectivity</span>
            <span className="font-mono text-emerald-400">
              {metrics?.internet_available ? 'ONLINE' : 'LOCAL ONLY'}
            </span>
          </div>
          <div className="text-xs text-text-secondary mt-2">
            Uptime: <span className="font-mono text-text-primary">{health?.uptime_seconds ?? 0}s</span>
          </div>
          <div className="text-[11px] text-text-muted font-mono mt-1">
            Build: v{health?.version ?? '1.0.0'}
          </div>
        </div>
      </div>

      {/* ── Hardware Performance Governor ──────────────────────── */}
      <div className="card p-6 border border-surface-border space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-accent/20 text-accent">
              <Zap size={18} />
            </div>
            <div>
              <h2 className="text-base font-bold text-text-primary">Thermal & Performance Governor</h2>
              <p className="text-xs text-text-secondary">
                Prevents fan noise and thermal throttling on Intel Core i5 with integrated graphics.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {(['eco', 'balanced', 'performance'] as const).map((p) => {
              const isActive = governor?.profile === p;
              return (
                <button
                  key={p}
                  onClick={() => setProfileMutation.mutate(p)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all ${
                    isActive
                      ? 'bg-accent text-white shadow-glow'
                      : 'bg-surface-3 text-text-secondary hover:text-text-primary border border-surface-border'
                  }`}
                >
                  {p}
                </button>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-4 border-t border-surface-border text-xs">
          <div className="p-3 rounded-lg bg-surface-2 border border-surface-border">
            <span className="text-text-muted text-[11px] block uppercase">Active Profile:</span>
            <span className="font-mono font-bold text-text-primary capitalize">{governor?.profile ?? 'balanced'}</span>
          </div>
          <div className="p-3 rounded-lg bg-surface-2 border border-surface-border">
            <span className="text-text-muted text-[11px] block uppercase">3D Particle Budget:</span>
            <span className="font-mono font-bold text-text-primary">{governor?.particle_count ?? 1200} nodes</span>
          </div>
          <div className="p-3 rounded-lg bg-surface-2 border border-surface-border">
            <span className="text-text-muted text-[11px] block uppercase">Hand Tracking FPS:</span>
            <span className="font-mono font-bold text-text-primary">{governor?.camera_fps ?? 24} FPS cap</span>
          </div>
        </div>
      </div>

      {/* ── Multi-Profile Security Matrix ───────────────────────── */}
      <div className="card p-6 border border-surface-border space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-accent/20 text-accent">
              <Shield size={18} />
            </div>
            <div>
              <h2 className="text-base font-bold text-text-primary">Profile Access Boundaries</h2>
              <p className="text-xs text-text-secondary">
                Enforces strict isolation between Owner, Family, and Guest sessions.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {(['owner', 'family', 'guest'] as const).map((pr) => {
              const isCurrent = profileData?.active_profile === pr;
              return (
                <button
                  key={pr}
                  onClick={() => switchUserMutation.mutate(pr)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all ${
                    isCurrent
                      ? 'bg-accent/20 text-accent border border-accent/40 shadow-sm'
                      : 'bg-surface-3 text-text-secondary hover:text-text-primary border border-surface-border'
                  }`}
                >
                  {pr}
                </button>
              );
            })}
          </div>
        </div>

        {profileData?.permissions && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-surface-border text-xs">
            <div className="p-3 rounded bg-surface-2 border border-surface-border flex items-center justify-between">
              <span>OS Control</span>
              <span className={profileData.permissions.allow_os_control ? 'text-emerald-400' : 'text-rose-400'}>
                {profileData.permissions.allow_os_control ? '✓ Allowed' : '✗ Blocked'}
              </span>
            </div>
            <div className="p-3 rounded bg-surface-2 border border-surface-border flex items-center justify-between">
              <span>File Write</span>
              <span className={profileData.permissions.allow_file_write ? 'text-emerald-400' : 'text-rose-400'}>
                {profileData.permissions.allow_file_write ? '✓ Allowed' : '✗ Blocked'}
              </span>
            </div>
            <div className="p-3 rounded bg-surface-2 border border-surface-border flex items-center justify-between">
              <span>Memory Read</span>
              <span className={profileData.permissions.allow_memory_read ? 'text-emerald-400' : 'text-rose-400'}>
                {profileData.permissions.allow_memory_read ? '✓ Allowed' : '✗ Blocked'}
              </span>
            </div>
            <div className="p-3 rounded bg-surface-2 border border-surface-border flex items-center justify-between">
              <span>Admin Voice</span>
              <span className={profileData.permissions.allow_voice_admin ? 'text-emerald-400' : 'text-rose-400'}>
                {profileData.permissions.allow_voice_admin ? '✓ Allowed' : '✗ Blocked'}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
