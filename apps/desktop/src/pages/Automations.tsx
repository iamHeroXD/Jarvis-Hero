import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Zap,
  Play,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Plus,
  Power,
  RotateCcw,
  Sparkles,
  GitBranch,
  Shield,
} from 'lucide-react';
import { automationsApi, AutomationItem } from '../services/api';

export default function AutomationsPage() {
  const queryClient = useQueryClient();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [runLog, setRunLog] = useState<{ id: number; details: string[] } | null>(null);

  // Form state
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');
  const [triggerType, setTriggerType] = useState('time');
  const [scheduleTime, setScheduleTime] = useState('09:00');

  const { data: automations = [], isLoading } = useQuery({
    queryKey: ['automations'],
    queryFn: automationsApi.list,
  });

  const toggleMutation = useMutation({
    mutationFn: automationsApi.toggle,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automations'] });
    },
  });

  const runMutation = useMutation({
    mutationFn: automationsApi.run,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['automations'] });
      setRunLog({ id: data.automation_id, details: data.details });
    },
  });

  const createMutation = useMutation({
    mutationFn: automationsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automations'] });
      setShowCreateModal(false);
      setName('');
      setDesc('');
    },
  });

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* ── Top Header ────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-border pb-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-accent/20 border border-accent/40 flex items-center justify-center text-accent">
            <Zap size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-text-primary tracking-wide">Automations & Background Tasks</h1>
            <p className="text-xs text-text-secondary">
              Scheduled background jobs, proactive briefings, and hardware telemetry watchdogs.
            </p>
          </div>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-accent hover:bg-accent/90 text-white text-xs font-semibold shadow-glow transition-all"
        >
          <Plus size={14} /> New Automation
        </button>
      </div>

      {/* ── Execution Result Banner ────────────────────────────── */}
      <AnimatePresence>
        {runLog && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="card p-4 border border-emerald-500/40 bg-emerald-500/10"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 size={14} /> Automation Execution Succeeded
              </span>
              <button
                onClick={() => setRunLog(null)}
                className="text-text-muted hover:text-text-primary text-xs"
              >
                ✕
              </button>
            </div>
            <div className="space-y-1">
              {runLog.details.map((d, i) => (
                <div key={i} className="text-xs text-text-secondary font-mono">
                  • {d}
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Automations List ───────────────────────────────────── */}
      {isLoading ? (
        <div className="p-8 text-center text-text-muted text-xs">Loading scheduled automations...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {automations.map((auto) => (
            <div
              key={auto.id}
              className={`card p-5 border transition-all ${
                auto.is_enabled
                  ? 'border-surface-border hover:border-accent/50'
                  : 'border-surface-border/50 opacity-60'
              }`}
            >
              <div className="flex items-start justify-between gap-2 mb-3">
                <div className="flex items-center gap-2">
                  <div className={`p-2 rounded-lg ${auto.is_enabled ? 'bg-accent/20 text-accent' : 'bg-surface-3 text-text-muted'}`}>
                    <Zap size={16} />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-text-primary">{auto.name}</h3>
                    <span className="text-[10px] uppercase font-mono text-text-muted">
                      Trigger: {auto.trigger_type}
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => toggleMutation.mutate(auto.id)}
                  className={`p-1.5 rounded-lg border text-xs transition-colors ${
                    auto.is_enabled
                      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                      : 'bg-surface-3 text-text-muted border-surface-border'
                  }`}
                  title={auto.is_enabled ? 'Disable' : 'Enable'}
                >
                  <Power size={13} />
                </button>
              </div>

              <p className="text-xs text-text-secondary leading-relaxed mb-4 line-clamp-2">
                {auto.description}
              </p>

              <div className="flex items-center justify-between pt-3 border-t border-surface-border/60 text-xs">
                <span className="text-[11px] text-text-muted font-mono">
                  {auto.last_run_at
                    ? `Ran ${new Date(auto.last_run_at).toLocaleTimeString()}`
                    : 'Pending run'}
                </span>

                <button
                  onClick={() => runMutation.mutate(auto.id)}
                  disabled={runMutation.isPending}
                  className="flex items-center gap-1 px-2.5 py-1 rounded bg-surface-3 hover:bg-surface-4 text-accent border border-accent/30 text-xs font-medium transition-all"
                >
                  <Play size={11} /> Run Now
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Create Automation Modal ────────────────────────────── */}
      <AnimatePresence>
        {showCreateModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="card w-full max-w-md p-6 border border-accent/40 shadow-glow"
            >
              <div className="flex items-center justify-between mb-4 border-b border-surface-border pb-3">
                <h3 className="text-base font-bold text-text-primary flex items-center gap-2">
                  <Zap size={18} className="text-accent" /> Create New Automation
                </h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-text-muted hover:text-text-primary text-xs"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Automation Name</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Daily Evening Work Summary"
                    className="w-full input text-xs py-2 px-3 bg-surface-2 border border-surface-border rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Description</label>
                  <textarea
                    rows={2}
                    value={desc}
                    onChange={(e) => setDesc(e.target.value)}
                    placeholder="What should JARVIS do when triggered?"
                    className="w-full input text-xs py-2 px-3 bg-surface-2 border border-surface-border rounded-lg"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-text-secondary mb-1">Trigger Type</label>
                    <select
                      value={triggerType}
                      onChange={(e) => setTriggerType(e.target.value)}
                      className="w-full input text-xs py-2 px-2 bg-surface-2 border border-surface-border rounded-lg"
                    >
                      <option value="time">Time / Schedule</option>
                      <option value="command">Voice Command</option>
                      <option value="event">System Event</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-text-secondary mb-1">Schedule Time</label>
                    <input
                      type="time"
                      value={scheduleTime}
                      onChange={(e) => setScheduleTime(e.target.value)}
                      className="w-full input text-xs py-2 px-2 bg-surface-2 border border-surface-border rounded-lg font-mono"
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-surface-border">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-3 py-1.5 rounded-lg text-xs text-text-muted hover:text-text-primary"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    if (!name.trim()) return;
                    createMutation.mutate({
                      name: name.trim(),
                      description: desc.trim(),
                      trigger_type: triggerType,
                      trigger_config: { schedule: scheduleTime },
                      actions: [{ type: 'custom_task', name: name.trim() }],
                      permissions: ['system.read'],
                      is_enabled: true,
                    });
                  }}
                  disabled={!name.trim() || createMutation.isPending}
                  className="px-4 py-1.5 rounded-lg bg-accent hover:bg-accent/90 text-white text-xs font-semibold shadow-glow disabled:opacity-50"
                >
                  {createMutation.isPending ? 'Saving...' : 'Deploy Automation'}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
