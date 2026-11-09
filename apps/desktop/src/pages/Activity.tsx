import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Activity as ActivityIcon,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Bot,
  Filter,
  Search,
} from 'lucide-react';
import { activityApi, ActivityItem } from '../services/api';

export default function ActivityPage() {
  const [filterAgent, setFilterAgent] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const { data: logs = [], isLoading } = useQuery({
    queryKey: ['activityLogs'],
    queryFn: () => activityApi.list(100),
    refetchInterval: 10000,
  });

  const filteredLogs = logs.filter((log) => {
    if (filterAgent !== 'all' && log.agent_name !== filterAgent) return false;
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      return (
        log.action.toLowerCase().includes(q) ||
        (log.details && log.details.toLowerCase().includes(q)) ||
        (log.tool_id && log.tool_id.toLowerCase().includes(q))
      );
    }
    return true;
  });

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* ── Top Header ────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-border pb-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-accent/20 border border-accent/40 flex items-center justify-center text-accent">
            <ActivityIcon size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-text-primary tracking-wide">Activity & Audit Trail</h1>
            <p className="text-xs text-text-secondary">
              Immutable record of executed tools, specialist agent operations, and permission checks.
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filter actions or details..."
            className="input text-xs py-1.5 px-3 bg-surface-2 border border-surface-border rounded-lg"
          />
          <select
            value={filterAgent}
            onChange={(e) => setFilterAgent(e.target.value)}
            className="input text-xs py-1.5 px-2 bg-surface-2 border border-surface-border rounded-lg"
          >
            <option value="all">All Agents</option>
            <option value="SENTINEL">SENTINEL</option>
            <option value="ATLAS">ATLAS</option>
            <option value="ORACLE">ORACLE</option>
            <option value="JDI">JDI</option>
          </select>
        </div>
      </div>

      {/* ── Logs List ──────────────────────────────────────────── */}
      {isLoading ? (
        <div className="p-12 text-center text-xs text-text-muted">Loading audit entries...</div>
      ) : filteredLogs.length === 0 ? (
        <div className="card p-12 text-center text-xs text-text-muted">No activity records match filter.</div>
      ) : (
        <div className="space-y-2">
          {filteredLogs.map((log) => (
            <div
              key={log.id}
              className="card p-3.5 border border-surface-border hover:border-surface-border/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
            >
              <div className="flex items-start gap-3">
                <div className="mt-0.5">
                  {log.result === 'success' ? (
                    <CheckCircle2 size={16} className="text-emerald-400" />
                  ) : log.result === 'denied' ? (
                    <XCircle size={16} className="text-amber-400" />
                  ) : (
                    <AlertTriangle size={16} className="text-rose-400" />
                  )}
                </div>

                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-text-primary">{log.action}</span>
                    {log.agent_name && (
                      <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-surface-3 text-accent border border-accent/20">
                        {log.agent_name}
                      </span>
                    )}
                    {log.tool_id && (
                      <span className="font-mono text-[10px] text-text-muted">
                        [{log.tool_id}]
                      </span>
                    )}
                  </div>
                  {log.details && (
                    <p className="text-xs text-text-secondary leading-relaxed">{log.details}</p>
                  )}
                </div>
              </div>

              <div className="flex sm:flex-col items-end justify-between sm:justify-center text-right text-[11px] text-text-muted font-mono flex-shrink-0">
                <span>{new Date(log.created_at).toLocaleTimeString()}</span>
                <span className="text-[10px] text-text-muted">
                  {log.permission_level !== null ? `Perm L${log.permission_level}` : 'Passive'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
