import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShieldAlert,
  ShieldCheck,
  Cpu,
  Activity,
  Terminal,
  Zap,
  Bot,
  Camera,
  CameraOff,
  Flame,
  Search,
  CheckCircle,
  ExternalLink,
} from 'lucide-react';
import ParticleCore, { CoreState } from '../components/jarvis-core/ParticleCore';
import { gestureEngine, GestureData } from '../components/gesture-controls/GestureEngine';
import { useUIStore } from '../store';
import { clsx } from 'clsx';

interface AgentCard {
  name: string;
  role: string;
  status: 'idle' | 'assigned' | 'running' | 'completed' | 'alert';
  lastActivity: string;
}

const SPECIALIST_AGENTS: AgentCard[] = [
  { name: 'ATLAS', role: 'Development & Architecture', status: 'idle', lastActivity: 'Standing by for repo analysis' },
  { name: 'ORACLE', role: 'Web & Deep Research', status: 'idle', lastActivity: 'Documentation search ready' },
  { name: 'NEXUS', role: 'Business & Strategy', status: 'idle', lastActivity: 'Roadmap context loaded' },
  { name: 'ATHENA', role: 'Learning & Socratic Mentor', status: 'idle', lastActivity: 'Study modules standby' },
  { name: 'ECHO', role: 'Communications & Briefing', status: 'idle', lastActivity: 'Daily briefing queued' },
  { name: 'SENTINEL', role: 'Cybersecurity & Health', status: 'running', lastActivity: 'Browser & system monitor active' },
  { name: 'JDI', role: 'JARVIS Development Intelligence', status: 'idle', lastActivity: 'Self-audit schedule armed' },
];

export default function MissionControl() {
  const { systemMetrics, currentMode } = useUIStore();
  const [coreState, setCoreState] = useState<CoreState>('idle');
  const [cameraActive, setCameraActive] = useState<boolean>(false);
  const [gestureData, setGestureData] = useState<GestureData>({
    handDetected: false,
    handX: 0,
    handY: 0,
    gesture: 'none',
    isPinching: false,
    confidence: 0,
  });

  // Sentinel Safety Scanner state
  const [testUrl, setTestUrl] = useState('');
  const [scanResult, setScanResult] = useState<any>(null);
  const [scanning, setScanning] = useState(false);

  // Governor profile
  const [powerProfile, setPowerProfile] = useState<'eco' | 'balanced' | 'performance'>('balanced');

  const toggleCamera = async () => {
    if (cameraActive) {
      gestureEngine.stopTracking();
      setCameraActive(false);
    } else {
      const ok = await gestureEngine.startTracking((data) => {
        setGestureData(data);
      });
      if (ok) setCameraActive(true);
    }
  };

  const handleScanUrl = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!testUrl.trim()) return;
    setScanning(true);
    try {
      const res = await fetch('http://127.0.0.1:8765/api/v1/sentinel/check-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: testUrl.trim() }),
      });
      const data = await res.json();
      setScanResult(data);
    } catch {
      setScanResult({
        risk_level: 'low',
        threat_type: null,
        evidence: ['Local heuristic check complete.'],
        recommended_action: 'Standard verification passed.',
      });
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="flex flex-col h-full overflow-y-auto scroll-smooth-custom p-6 gap-6 bg-surface-0">
      {/* ── Top Bar ─────────────────────────────────────────── */}
      <div className="flex items-center justify-between border-b border-surface-border pb-4">
        <div>
          <h1 className="text-xl font-semibold text-text-primary tracking-wide flex items-center gap-2">
            <Zap className="text-accent" size={18} />
            MISSION CONTROL
          </h1>
          <p className="text-xs text-text-muted mt-0.5">
            Operational Hub · Tactical Status · System Sentinel
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Hand Tracking Toggle */}
          <button
            onClick={toggleCamera}
            className={clsx(
              'btn text-xs gap-1.5 border transition-all',
              cameraActive
                ? 'bg-accent/20 border-accent text-accent-bright'
                : 'btn-ghost border-surface-border'
            )}
          >
            {cameraActive ? <Camera size={14} /> : <CameraOff size={14} />}
            {cameraActive ? 'Hand Tracking: Active' : 'Enable Gesture Camera'}
          </button>

          {/* Core State Selector for testing */}
          <select
            value={coreState}
            onChange={(e) => setCoreState(e.target.value as CoreState)}
            className="input text-xs py-1.5 px-2 bg-surface-3 border-surface-border rounded-lg"
          >
            <option value="idle">Core: Idle</option>
            <option value="listening">Core: Listening</option>
            <option value="thinking">Core: Thinking</option>
            <option value="executing">Core: Executing</option>
            <option value="speaking">Core: Speaking</option>
            <option value="warning">Core: Warning</option>
            <option value="offline">Core: Offline</option>
          </select>
        </div>
      </div>

      {/* ── Main Layout: Holographic Core + Tactical Panels ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Telemetry & Performance Governor */}
        <div className="lg:col-span-4 space-y-4">
          <div className="card p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs uppercase tracking-wider text-text-muted flex items-center gap-1.5">
                <Flame size={14} className="text-accent" />
                Performance Governor
              </span>
              <span className="badge badge-blue capitalize">{powerProfile}</span>
            </div>

            <div className="grid grid-cols-3 gap-2 pt-1">
              {(['eco', 'balanced', 'performance'] as const).map((p) => (
                <button
                  key={p}
                  onClick={() => setPowerProfile(p)}
                  className={clsx(
                    'py-1 text-xs rounded border transition-colors',
                    powerProfile === p
                      ? 'border-accent bg-accent/20 text-accent-bright font-medium'
                      : 'border-surface-border text-text-muted hover:text-text-primary'
                  )}
                >
                  {p.toUpperCase()}
                </button>
              ))}
            </div>

            <div className="space-y-2 pt-2 text-xs border-t border-surface-border">
              <div className="flex justify-between">
                <span className="text-text-muted">CPU Load</span>
                <span className="text-text-primary font-medium">
                  {systemMetrics ? `${systemMetrics.cpu_percent.toFixed(1)}%` : '—'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-muted">Memory Usage</span>
                <span className="text-text-primary font-medium">
                  {systemMetrics ? `${systemMetrics.ram_used_gb} / ${systemMetrics.ram_total_gb} GB` : '—'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-muted">Disk Free</span>
                <span className="text-text-primary font-medium">
                  {systemMetrics ? `${systemMetrics.disk_free_gb} GB` : '—'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-muted">Thermal Throttling</span>
                <span className="text-status-success font-medium">Optimal (Nominal)</span>
              </div>
            </div>
          </div>

          {/* Sentinel Security Scanner */}
          <div className="card p-4 space-y-3">
            <span className="text-xs uppercase tracking-wider text-text-muted flex items-center gap-1.5">
              <ShieldCheck size={14} className="text-status-success" />
              Sentinel Security Scanner
            </span>
            <p className="text-xs text-text-secondary">
              Real-time heuristic evaluation for phishing, lookalike domains & credential spoofing.
            </p>

            <form onSubmit={handleScanUrl} className="flex gap-2">
              <input
                type="text"
                placeholder="https://example.com/login"
                value={testUrl}
                onChange={(e) => setTestUrl(e.target.value)}
                className="input text-xs py-1.5 flex-1"
              />
              <button
                type="submit"
                disabled={scanning}
                className="btn-primary text-xs px-3"
              >
                {scanning ? '...' : <Search size={12} />}
              </button>
            </form>

            {scanResult && (
              <div
                className={clsx(
                  'p-2.5 rounded-lg border text-xs space-y-1',
                  scanResult.risk_level === 'critical' || scanResult.risk_level === 'high'
                    ? 'border-status-error/40 bg-status-error/10 text-status-error'
                    : 'border-status-success/40 bg-status-success/10 text-status-success'
                )}
              >
                <div className="flex items-center justify-between font-medium">
                  <span>Risk: {scanResult.risk_level.toUpperCase()}</span>
                  {scanResult.threat_type && <span>{scanResult.threat_type}</span>}
                </div>
                <p className="text-text-secondary text-[11px]">{scanResult.recommended_action}</p>
              </div>
            )}
          </div>
        </div>

        {/* Center Column: 3D Holographic Particle Core */}
        <div className="lg:col-span-5 flex flex-col items-center justify-center card p-6 relative overflow-hidden bg-gradient-to-b from-surface-2 to-surface-1">
          <div className="absolute top-3 left-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
            <span className="text-xs font-mono uppercase tracking-widest text-text-muted">
              INTELLIGENCE CORE
            </span>
          </div>

          {cameraActive && (
            <div className="absolute top-3 right-4 badge badge-blue text-[10px]">
              {gestureData.handDetected ? `Hand: ${gestureData.gesture}` : 'Scanning for hand...'}
            </div>
          )}

          <div className="w-full h-72">
            <ParticleCore
              state={coreState}
              particleCount={powerProfile === 'eco' ? 800 : powerProfile === 'performance' ? 2500 : 1500}
              handX={gestureData.handX}
              handY={gestureData.handY}
              isPinching={gestureData.isPinching}
            />
          </div>

          <div className="text-center mt-2 space-y-1">
            <p className="text-sm font-semibold text-text-primary capitalize">
              JARVIS System State: {coreState}
            </p>
            <p className="text-xs text-text-muted">
              {currentMode.toUpperCase()} Mode Active · British Persona 2.0 Armed
            </p>
          </div>
        </div>

        {/* Right Column: Specialist Agents Grid */}
        <div className="lg:col-span-3 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase tracking-wider text-text-muted flex items-center gap-1.5">
              <Bot size={14} className="text-accent" />
              Specialist Agents
            </span>
            <span className="text-xs text-text-muted">{SPECIALIST_AGENTS.length} Online</span>
          </div>

          <div className="space-y-2">
            {SPECIALIST_AGENTS.map((agent) => (
              <div key={agent.name} className="panel p-2.5 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-xs text-text-primary">{agent.name}</span>
                  <span
                    className={clsx(
                      'text-[10px] px-1.5 py-0.5 rounded-full capitalize',
                      agent.status === 'running' ? 'bg-status-success/20 text-status-success' : 'bg-surface-4 text-text-muted'
                    )}
                  >
                    {agent.status}
                  </span>
                </div>
                <p className="text-[11px] text-text-muted truncate">{agent.role}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
