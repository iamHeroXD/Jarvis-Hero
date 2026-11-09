import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Cpu,
  Layers,
  HardDrive,
  Wifi,
  Sparkles,
  Zap,
  FolderKanban,
  Shield,
  Volume2,
  Bot,
  Activity,
  ArrowRight,
  Flame,
  CheckCircle2,
  AlertTriangle,
  Play,
  RotateCw,
} from 'lucide-react';
import { useUIStore, useAuthStore } from '../store';
import { healthApi, tasksApi, voiceApi, governorApi } from '../services/api';

const SPECIALIST_ROSTER = [
  { name: 'ATLAS', role: 'Dev & Git', status: 'Online', desc: 'Code inspection & test verification' },
  { name: 'ORACLE', role: 'Research', status: 'Online', desc: 'Source & factual cross-validation' },
  { name: 'NEXUS', role: 'Strategy', status: 'Online', desc: 'Business logic & model economics' },
  { name: 'ATHENA', role: 'Socratic', status: 'Online', desc: 'Pedagogical conceptual tutoring' },
  { name: 'ECHO', role: 'Comms', status: 'Online', desc: 'Executive tone & correspondence' },
  { name: 'SENTINEL', role: 'Security', status: 'Active', desc: 'Phishing & prompt injection shield' },
  { name: 'JDI', role: 'Evolution', status: 'Armed', desc: 'Antigravity self-audit engine' },
];

export default function OverviewPage() {
  const navigate = useNavigate();
  const { systemMetrics, backendOnline, internetAvailable, currentMode } = useUIStore();
  const { displayName } = useAuthStore();
  const [time, setTime] = useState(new Date());
  const [briefingText, setBriefingText] = useState<string | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [loadingBriefing, setLoadingBriefing] = useState(false);

  // Live clock
  useEffect(() => {
    const interval = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  const greeting = (() => {
    const hour = time.getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  })();

  const handleFetchBriefing = async () => {
    setLoadingBriefing(true);
    try {
      const res = await tasksApi.getBriefing();
      setBriefingText(res.briefing);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingBriefing(false);
    }
  };

  const handlePlayBriefingVoice = async () => {
    if (!briefingText) return;
    setIsSpeaking(true);
    try {
      const blob = await voiceApi.speak(briefingText);
      if (blob) {
        const audio = new Audio(URL.createObjectURL(blob));
        audio.onended = () => setIsSpeaking(false);
        audio.onerror = () => setIsSpeaking(false);
        await audio.play();
      } else {
        setIsSpeaking(false);
      }
    } catch {
      setIsSpeaking(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* ── Top Hero HUD ───────────────────────────────────────── */}
      <div className="card p-6 border border-accent/40 bg-gradient-to-r from-surface-2 via-surface-1 to-surface-2 relative overflow-hidden shadow-glow">
        <div className="absolute top-0 right-0 w-96 h-96 bg-accent/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping" />
              <span className="text-xs font-mono font-bold text-accent uppercase tracking-widest">
                SYSTEM STATUS: OPTIMAL &bull; AUTHENTICATED
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-text-primary tracking-wide">
              {greeting}, {displayName || 'Rohan'}.
            </h1>
            <p className="text-xs text-text-secondary mt-1 font-sans max-w-xl">
              Systems are online. Your RCN workspace, specialist agents, and Sentinel security monitor are ready for command.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleFetchBriefing}
              disabled={loadingBriefing}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-surface-3 hover:bg-surface-4 text-accent border border-accent/40 text-xs font-semibold shadow-sm transition-all"
            >
              <Sparkles size={14} className={loadingBriefing ? 'animate-spin' : ''} />
              <span>{loadingBriefing ? 'Synthesizing...' : 'Tactical Briefing'}</span>
            </button>

            <button
              onClick={() => navigate('/mission-control')}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-accent to-accent-cyan hover:from-accent/90 hover:to-accent-cyan/90 text-white text-xs font-bold shadow-glow transition-all"
            >
              <Flame size={15} />
              <span>Mission Control</span>
              <ArrowRight size={14} />
            </button>
          </div>
        </div>

        {/* Live Date/Time Bar */}
        <div className="mt-4 pt-4 border-t border-surface-border/60 flex flex-wrap items-center justify-between gap-2 text-xs font-mono text-text-muted">
          <span>{format(time, 'EEEE, d MMMM yyyy')} &bull; {format(time, 'HH:mm:ss')}</span>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" /> Backend Online (127.0.0.1:8765)
            </span>
            <span className="text-text-muted">|</span>
            <span className="text-accent uppercase">Mode: {currentMode}</span>
          </div>
        </div>
      </div>

      {/* ── Tactical Briefing Card (if expanded) ───────────────── */}
      <AnimatePresence>
        {briefingText && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="card p-5 border-l-4 border-accent relative bg-gradient-to-r from-accent/10 to-transparent"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-bold text-accent uppercase tracking-wider flex items-center gap-2">
                <Sparkles size={14} /> Morning Tactical Briefing
              </h3>
              <div className="flex items-center gap-2">
                <button
                  onClick={handlePlayBriefingVoice}
                  disabled={isSpeaking}
                  className="flex items-center gap-1 text-xs px-2.5 py-1 rounded bg-surface-3 hover:bg-surface-4 text-text-primary border border-surface-border transition-colors"
                >
                  <Volume2 size={13} className={isSpeaking ? 'text-accent animate-pulse' : ''} />
                  {isSpeaking ? 'Speaking (en-GB)...' : 'Play Speech'}
                </button>
                <button onClick={() => setBriefingText(null)} className="text-xs text-text-muted hover:text-text-primary">
                  Dismiss
                </button>
              </div>
            </div>
            <p className="text-xs text-text-secondary leading-relaxed font-sans whitespace-pre-line">
              {briefingText}
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Real-Time Hardware Telemetry ───────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* CPU */}
        <div className="card p-4 border border-surface-border">
          <div className="flex items-center justify-between text-xs text-text-muted mb-2">
            <span className="flex items-center gap-1.5 font-semibold">
              <Cpu size={14} className="text-accent" /> Intel Core i5
            </span>
            <span className="font-mono text-text-primary font-bold">{systemMetrics?.cpu_percent.toFixed(0) ?? 0}%</span>
          </div>
          <div className="w-full bg-surface-3 h-2 rounded-full overflow-hidden mb-2">
            <div
              className="bg-accent h-full transition-all duration-300"
              style={{ width: `${Math.min(100, systemMetrics?.cpu_percent ?? 0)}%` }}
            />
          </div>
          <div className="text-[11px] text-text-muted font-mono">
            JARVIS CPU: {systemMetrics?.jarvis_cpu_percent.toFixed(1) ?? '0.0'}%
          </div>
        </div>

        {/* RAM */}
        <div className="card p-4 border border-surface-border">
          <div className="flex items-center justify-between text-xs text-text-muted mb-2">
            <span className="flex items-center gap-1.5 font-semibold">
              <Layers size={14} className="text-cyan-400" /> RAM Footprint
            </span>
            <span className="font-mono text-text-primary font-bold">{systemMetrics?.ram_percent.toFixed(0) ?? 0}%</span>
          </div>
          <div className="w-full bg-surface-3 h-2 rounded-full overflow-hidden mb-2">
            <div
              className={`h-full transition-all duration-300 ${
                (systemMetrics?.ram_percent ?? 0) > 85 ? 'bg-rose-500' : 'bg-cyan-400'
              }`}
              style={{ width: `${Math.min(100, systemMetrics?.ram_percent ?? 0)}%` }}
            />
          </div>
          <div className="text-[11px] text-text-muted font-mono">
            {systemMetrics?.ram_used_gb.toFixed(1) ?? 0} / {systemMetrics?.ram_total_gb.toFixed(1) ?? 8} GB (JARVIS: {systemMetrics?.jarvis_ram_mb.toFixed(0) ?? 0} MB)
          </div>
        </div>

        {/* Disk */}
        <div className="card p-4 border border-surface-border">
          <div className="flex items-center justify-between text-xs text-text-muted mb-2">
            <span className="flex items-center gap-1.5 font-semibold">
              <HardDrive size={14} className="text-amber-400" /> SSD Storage
            </span>
            <span className="font-mono text-text-primary font-bold">{systemMetrics?.disk_free_gb.toFixed(1) ?? 0} GB Free</span>
          </div>
          <div className="w-full bg-surface-3 h-2 rounded-full overflow-hidden mb-2">
            <div
              className="bg-amber-400 h-full transition-all duration-300"
              style={{ width: `${Math.min(100, systemMetrics?.disk_percent ?? 0)}%` }}
            />
          </div>
          <div className="text-[11px] text-text-muted font-mono">
            Used: {systemMetrics?.disk_percent.toFixed(1) ?? 0}%
          </div>
        </div>

        {/* AI & Sentinel Network */}
        <div className="card p-4 border border-surface-border">
          <div className="flex items-center justify-between text-xs text-text-muted mb-2">
            <span className="flex items-center gap-1.5 font-semibold">
              <Shield size={14} className="text-emerald-400" /> Sentinel Defense
            </span>
            <span className="font-mono text-emerald-400 font-bold">ARMED</span>
          </div>
          <div className="text-xs text-text-secondary mt-1 font-mono">
            Phishing / Typosquat: Active
          </div>
          <div className="text-[11px] text-text-muted mt-1 font-mono">
            AI: Google Gemini Interactions
          </div>
        </div>
      </div>

      {/* ── Quick Command Grid ─────────────────────────────────── */}
      <div>
        <h2 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-3 flex items-center gap-2">
          <Zap size={14} className="text-accent" /> Operations Quick Access
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <button
            onClick={() => navigate('/mission-control')}
            className="p-3.5 rounded-xl card border border-surface-border hover:border-accent/60 flex flex-col items-center text-center gap-2 group transition-all"
          >
            <div className="w-8 h-8 rounded-lg bg-accent/20 text-accent flex items-center justify-center group-hover:scale-110 transition-transform">
              <Flame size={16} />
            </div>
            <span className="text-xs font-bold text-text-primary">3D Core</span>
            <span className="text-[10px] text-text-muted">Holographic HUD</span>
          </button>

          <button
            onClick={() => navigate('/chat')}
            className="p-3.5 rounded-xl card border border-surface-border hover:border-accent/60 flex flex-col items-center text-center gap-2 group transition-all"
          >
            <div className="w-8 h-8 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Bot size={16} />
            </div>
            <span className="text-xs font-bold text-text-primary">Chat Stream</span>
            <span className="text-[10px] text-text-muted">JIEE Self-Correction</span>
          </button>

          <button
            onClick={() => navigate('/projects')}
            className="p-3.5 rounded-xl card border border-surface-border hover:border-accent/60 flex flex-col items-center text-center gap-2 group transition-all"
          >
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center group-hover:scale-110 transition-transform">
              <FolderKanban size={16} />
            </div>
            <span className="text-xs font-bold text-text-primary">RCN Workspace</span>
            <span className="text-[10px] text-text-muted">Git & Tasks</span>
          </button>

          <button
            onClick={() => navigate('/agents')}
            className="p-3.5 rounded-xl card border border-surface-border hover:border-accent/60 flex flex-col items-center text-center gap-2 group transition-all"
          >
            <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Activity size={16} />
            </div>
            <span className="text-xs font-bold text-text-primary">Specialists</span>
            <span className="text-[10px] text-text-muted">ATLAS, ORACLE, JDI</span>
          </button>

          <button
            onClick={() => navigate('/tasks')}
            className="p-3.5 rounded-xl card border border-surface-border hover:border-accent/60 flex flex-col items-center text-center gap-2 group transition-all"
          >
            <div className="w-8 h-8 rounded-lg bg-rose-500/20 text-rose-400 flex items-center justify-center group-hover:scale-110 transition-transform">
              <CheckCircle2 size={16} />
            </div>
            <span className="text-xs font-bold text-text-primary">Task Engine</span>
            <span className="text-[10px] text-text-muted">Verified Execution</span>
          </button>

          <button
            onClick={() => navigate('/evolution')}
            className="p-3.5 rounded-xl card border border-surface-border hover:border-accent/60 flex flex-col items-center text-center gap-2 group transition-all"
          >
            <div className="w-8 h-8 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Sparkles size={16} />
            </div>
            <span className="text-xs font-bold text-text-primary">Evolution</span>
            <span className="text-[10px] text-text-muted">Antigravity Audit</span>
          </button>
        </div>
      </div>

      {/* ── Specialist Agent Radar ─────────────────────────────── */}
      <div className="card p-5 border border-surface-border">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
            <Bot size={14} className="text-accent" /> Specialist Agent Architecture
          </h2>
          <span className="text-[11px] text-text-muted font-mono">7 Coordinated Agents Active</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {SPECIALIST_ROSTER.map((ag) => (
            <div
              key={ag.name}
              onClick={() => navigate('/agents')}
              className="p-3 rounded-lg bg-surface-2 border border-surface-border hover:border-accent/40 cursor-pointer transition-all"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-text-primary">{ag.name}</span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-400">
                  {ag.status}
                </span>
              </div>
              <p className="text-[11px] text-accent font-medium mb-0.5">{ag.role}</p>
              <p className="text-[10px] text-text-muted line-clamp-1">{ag.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
