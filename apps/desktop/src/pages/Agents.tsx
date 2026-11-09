import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bot,
  Send,
  ShieldCheck,
  AlertTriangle,
  FileCode2,
  Search,
  DollarSign,
  GraduationCap,
  Mail,
  Shield,
  Sparkles,
  Terminal,
  ExternalLink,
} from 'lucide-react';
import { agentsApi, AgentInfo, AgentDispatchResult } from '../services/api';

const AGENT_META: Record<string, { icon: React.ElementType; color: string; desc: string }> = {
  ATLAS: {
    icon: FileCode2,
    color: 'from-blue-500 to-cyan-500',
    desc: 'Senior Software & Architecture Specialist. Git inspections, code testing, and verified refactoring.',
  },
  ORACLE: {
    icon: Search,
    color: 'from-purple-500 to-indigo-500',
    desc: 'Research & Source Verification Specialist. Cross-checks citations, facts, and technological claims.',
  },
  NEXUS: {
    icon: DollarSign,
    color: 'from-emerald-500 to-teal-500',
    desc: 'Business, Economics & Strategy Specialist. Pricing models, commercial viability, and pitch reviews.',
  },
  ATHENA: {
    icon: GraduationCap,
    color: 'from-amber-500 to-yellow-500',
    desc: 'Learning & Socratic Pedagogy Specialist. Breaks complex subjects into first-principles intuition.',
  },
  ECHO: {
    icon: Mail,
    color: 'from-sky-500 to-blue-500',
    desc: 'Executive Communications Specialist. Tone calibration, high-stakes correspondence, and daily summaries.',
  },
  SENTINEL: {
    icon: Shield,
    color: 'from-rose-500 to-pink-500',
    desc: 'Cybersecurity & Health Sentinel. Phishing evaluation, prompt injection scanning, and system hygiene.',
  },
  JDI: {
    icon: Sparkles,
    color: 'from-accent to-accent-cyan',
    desc: 'JARVIS Development Intelligence. Autonomous codebase self-auditing and Antigravity prompt synthesis.',
  },
};

export default function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState('ATLAS');
  const [intent, setIntent] = useState('');
  const [dispatchResult, setDispatchResult] = useState<AgentDispatchResult | null>(null);

  const { data: agents = [], isLoading } = useQuery({
    queryKey: ['agentsList'],
    queryFn: agentsApi.list,
  });

  const dispatchMutation = useMutation({
    mutationFn: agentsApi.dispatch,
    onSuccess: (res) => {
      setDispatchResult(res);
    },
  });

  const handleDispatch = () => {
    if (!intent.trim()) return;
    dispatchMutation.mutate({
      intent: intent.trim(),
      parameters: { preferred_agent: selectedAgent },
    });
  };

  const currentMeta = AGENT_META[selectedAgent] || AGENT_META.ATLAS;
  const CurrentIcon = currentMeta.icon;

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* ── Top Header ────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-border pb-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-accent/20 border border-accent/40 flex items-center justify-center text-accent">
            <Bot size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-text-primary tracking-wide">Specialist Agent Roster</h1>
            <p className="text-xs text-text-secondary">
              Coordinated multi-agent architecture operating under the central JARVIS orchestrator.
            </p>
          </div>
        </div>
      </div>

      {/* ── Agents Grid ────────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {agents.map((ag) => {
          const meta = AGENT_META[ag.name] || {
            icon: Bot,
            color: 'from-accent to-accent-cyan',
            desc: ag.role,
          };
          const Icon = meta.icon;
          const isSelected = selectedAgent === ag.name;

          return (
            <div
              key={ag.name}
              onClick={() => setSelectedAgent(ag.name)}
              className={`card p-4 border cursor-pointer transition-all ${
                isSelected
                  ? 'border-accent/80 bg-surface-3 shadow-glow'
                  : 'border-surface-border hover:border-surface-border/80'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${meta.color} flex items-center justify-center text-white shadow-sm`}>
                  <Icon size={16} />
                </div>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  {ag.status}
                </span>
              </div>
              <h3 className="text-sm font-bold text-text-primary">{ag.name}</h3>
              <p className="text-[11px] font-medium text-accent mb-1">{ag.role}</p>
              <p className="text-xs text-text-secondary leading-relaxed line-clamp-2">{meta.desc}</p>
            </div>
          );
        })}
      </div>

      {/* ── Interactive Command Dispatcher ─────────────────────── */}
      <div className="card p-6 border border-accent/30 bg-surface-2 relative">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 rounded-lg bg-surface-3 border border-surface-border text-accent">
            <CurrentIcon size={20} />
          </div>
          <div>
            <h2 className="text-base font-bold text-text-primary">
              Dispatch Mission to <span className="text-accent">{selectedAgent}</span>
            </h2>
            <p className="text-xs text-text-secondary">{currentMeta.desc}</p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1">
              Target Directive / Intent
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={intent}
                onChange={(e) => setIntent(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleDispatch()}
                placeholder={`Instruct ${selectedAgent} (e.g. ${
                  selectedAgent === 'ATLAS'
                    ? 'Inspect git status and check open tests'
                    : selectedAgent === 'ORACLE'
                    ? 'Research latest advancements in robotics edge AI'
                    : selectedAgent === 'NEXUS'
                    ? 'Review market pricing and margin model'
                    : selectedAgent === 'ATHENA'
                    ? 'Explain Kalman filter state estimation from first principles'
                    : selectedAgent === 'SENTINEL'
                    ? 'Scan suspicious URL https://accounts-google-verify.com'
                    : 'Analyze prompt requirements'
                })`}
                className="flex-1 input text-xs py-2.5 px-3 bg-surface-1 border border-surface-border rounded-lg"
              />
              <button
                onClick={handleDispatch}
                disabled={!intent.trim() || dispatchMutation.isPending}
                className="px-5 py-2.5 rounded-lg bg-accent hover:bg-accent/90 text-white text-xs font-semibold shadow-glow flex items-center gap-2 disabled:opacity-50 transition-all"
              >
                <Send size={13} />
                {dispatchMutation.isPending ? 'Executing...' : 'Dispatch'}
              </button>
            </div>
          </div>
        </div>

        {/* ── Returned Execution Findings ───────────────────────── */}
        <AnimatePresence>
          {dispatchResult && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="mt-6 pt-5 border-t border-surface-border space-y-4"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs text-accent">[{dispatchResult.agent_name}]</span>
                  <span className="text-sm font-semibold text-text-primary">Execution Report</span>
                  {dispatchResult.verified && (
                    <span className="flex items-center gap-1 text-xs text-emerald-400 font-mono">
                      <ShieldCheck size={14} /> Verified Complete
                    </span>
                  )}
                </div>
                <span className="font-mono text-xs text-text-muted">Task ID: {dispatchResult.task_id}</span>
              </div>

              <div className="p-4 rounded-lg bg-surface-1 border border-surface-border text-xs text-text-secondary leading-relaxed font-sans">
                {dispatchResult.summary}
              </div>

              {/* Findings */}
              {dispatchResult.findings && dispatchResult.findings.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-2">
                    Key Findings
                  </h4>
                  <div className="space-y-1.5">
                    {dispatchResult.findings.map((f, i) => (
                      <div
                        key={i}
                        className="p-2 rounded bg-surface-3 border border-surface-border text-xs text-text-secondary flex items-start gap-2"
                      >
                        <span className="text-accent text-[11px] font-mono">#{i + 1}</span>
                        <span>{f}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Warnings */}
              {dispatchResult.warnings && dispatchResult.warnings.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                    <AlertTriangle size={13} /> Potential Risks / Warnings
                  </h4>
                  <div className="space-y-1.5">
                    {dispatchResult.warnings.map((w, i) => (
                      <div
                        key={i}
                        className="p-2 rounded bg-amber-500/10 border border-amber-500/30 text-xs text-amber-300 flex items-start gap-2"
                      >
                        <span>•</span>
                        <span>{w}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Artifacts */}
              {dispatchResult.artifacts && dispatchResult.artifacts.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-2">
                    Generated Artifacts
                  </h4>
                  <div className="space-y-2">
                    {dispatchResult.artifacts.map((art, i) => (
                      <div key={i} className="p-3 rounded-lg bg-surface-1 border border-surface-border text-xs">
                        <div className="font-semibold text-accent mb-1">{art.title}</div>
                        {art.path && <div className="font-mono text-[10px] text-text-muted mb-2">{art.path}</div>}
                        <pre className="p-2 rounded bg-surface-3 font-mono text-[11px] text-text-secondary whitespace-pre-wrap overflow-x-auto">
                          {art.content}
                        </pre>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
