import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Settings as SettingsIcon,
  Key,
  Volume2,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  Bot,
  Shield,
  Save,
  RefreshCw,
} from 'lucide-react';
import { settingsApi } from '../services/api';

const PERSONALITY_MODES = [
  { id: 'british_assistant', label: 'British Assistant (Default)', desc: 'Refined, calm, respectful with subtle dry wit.' },
  { id: 'focus', label: 'Deep Focus', desc: 'Minimalist, terse, no conversational filler.' },
  { id: 'developer', label: 'Senior Engineer', desc: 'Code-first, rigorous syntax, test-driven.' },
  { id: 'business', label: 'Strategic Advisor', desc: 'High-level executive clarity, ROI, risks.' },
  { id: 'study', label: 'Socratic Tutor', desc: 'Explains step-by-step from first principles.' },
  { id: 'casual', label: 'Casual Companion', desc: 'Relaxed, friendly, everyday conversational tone.' },
];

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const [apiKey, setApiKey] = useState('');
  const [testResult, setTestResult] = useState<{ status: string; message: string } | null>(null);
  const [selectedMode, setSelectedMode] = useState('british_assistant');

  // Query Gemini status
  const { data: geminiStatus, isLoading: statusLoading } = useQuery({
    queryKey: ['geminiStatus'],
    queryFn: settingsApi.getGeminiStatus,
  });

  // Query General settings
  const { data: generalSettings } = useQuery({
    queryKey: ['generalSettings'],
    queryFn: settingsApi.getGeneral,
  });

  useEffect(() => {
    if (generalSettings?.assistant_mode) {
      setSelectedMode(String(generalSettings.assistant_mode));
    }
  }, [generalSettings]);

  // Set Key mutation
  const setKeyMutation = useMutation({
    mutationFn: settingsApi.setGeminiKey,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['geminiStatus'] });
      setApiKey('');
      setTestResult({ status: 'success', message: 'API Key stored securely in Windows Credential Manager.' });
    },
    onError: (err: any) => {
      setTestResult({ status: 'error', message: err.message || 'Failed to save API key.' });
    },
  });

  // Test Key mutation
  const testMutation = useMutation({
    mutationFn: settingsApi.testGemini,
    onSuccess: (data) => {
      if (data.status === 'connected') {
        setTestResult({ status: 'success', message: `Connected to Gemini! Model: ${data.model}` });
      } else {
        setTestResult({ status: 'error', message: data.error || 'Connection test failed.' });
      }
    },
    onError: (err: any) => {
      setTestResult({ status: 'error', message: err.message || 'Connection test failed.' });
    },
  });

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6 max-w-4xl">
      {/* ── Top Header ────────────────────────────────────────── */}
      <div className="flex items-center gap-3 border-b border-surface-border pb-4">
        <div className="w-9 h-9 rounded-lg bg-accent/20 border border-accent/40 flex items-center justify-center text-accent">
          <SettingsIcon size={20} />
        </div>
        <div>
          <h1 className="text-xl font-bold text-text-primary tracking-wide">JARVIS Configuration</h1>
          <p className="text-xs text-text-secondary">
            AI model provider secrets, British persona tone, and voice subsystem parameters.
          </p>
        </div>
      </div>

      {/* ── AI Provider & Gemini Key ───────────────────────────── */}
      <div className="card p-6 border border-surface-border space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-accent/20 text-accent">
              <Key size={18} />
            </div>
            <div>
              <h2 className="text-base font-bold text-text-primary">Google Gemini Cloud AI Provider</h2>
              <p className="text-xs text-text-secondary">
                Interactions API powered by gemini-3.8-flash / gemini-4-argon with persistent interaction state.
              </p>
            </div>
          </div>

          <div>
            {geminiStatus?.configured ? (
              <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
                <CheckCircle2 size={12} /> Stored in Credential Vault
              </span>
            ) : (
              <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-mono">
                <AlertTriangle size={12} /> Key Required
              </span>
            )}
          </div>
        </div>

        {geminiStatus?.masked_key && (
          <div className="text-xs text-text-muted font-mono bg-surface-2 p-2.5 rounded-lg border border-surface-border">
            Active Vault Key: {geminiStatus.masked_key}
          </div>
        )}

        <div className="space-y-3">
          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1">
              {geminiStatus?.configured ? 'Update Gemini API Key' : 'Enter Gemini API Key'}
            </label>
            <div className="flex gap-2">
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="AIzaSy..."
                className="flex-1 input text-xs py-2 px-3 bg-surface-2 border border-surface-border rounded-lg font-mono"
              />
              <button
                onClick={() => apiKey.trim() && setKeyMutation.mutate(apiKey.trim())}
                disabled={!apiKey.trim() || setKeyMutation.isPending}
                className="px-4 py-2 rounded-lg bg-accent hover:bg-accent/90 text-white text-xs font-semibold shadow-glow flex items-center gap-1.5 disabled:opacity-50 transition-all"
              >
                <Save size={13} /> Save Key
              </button>
            </div>
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={() => testMutation.mutate()}
              disabled={testMutation.isPending || !geminiStatus?.configured}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-surface-3 hover:bg-surface-4 text-accent border border-accent/30 text-xs font-medium transition-all disabled:opacity-50"
            >
              <RefreshCw size={12} className={testMutation.isPending ? 'animate-spin' : ''} />
              Test API Connection
            </button>
            <span className="text-[11px] text-text-muted">
              Credentials are protected by Windows Credential Manager DPAPI encryption.
            </span>
          </div>

          {/* Test Alert Banner */}
          <AnimatePresence>
            {testResult && (
              <motion.div
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -5 }}
                className={`p-3 rounded-lg text-xs font-mono flex items-center justify-between border ${
                  testResult.status === 'success'
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                    : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                }`}
              >
                <span>{testResult.message}</span>
                <button onClick={() => setTestResult(null)} className="text-text-muted hover:text-text-primary text-xs ml-2">
                  ✕
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* ── Personality & Tone ─────────────────────────────────── */}
      <div className="card p-6 border border-surface-border space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-accent/20 text-accent">
            <Bot size={18} />
          </div>
          <div>
            <h2 className="text-base font-bold text-text-primary">JARVIS Persona & Communication Tone</h2>
            <p className="text-xs text-text-secondary">
              Configure conversational cadence, dryness of wit, and response conciseness.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
          {PERSONALITY_MODES.map((mode) => (
            <div
              key={mode.id}
              onClick={() => setSelectedMode(mode.id)}
              className={`p-3.5 rounded-lg border cursor-pointer transition-all ${
                selectedMode === mode.id
                  ? 'bg-surface-3 border-accent/80 shadow-sm'
                  : 'bg-surface-2 border-surface-border hover:border-surface-border/80'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-text-primary">{mode.label}</span>
                {selectedMode === mode.id && <CheckCircle2 size={14} className="text-accent" />}
              </div>
              <p className="text-[11px] text-text-secondary leading-relaxed">{mode.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Voice & Audio Subsystem ────────────────────────────── */}
      <div className="card p-6 border border-surface-border space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-accent/20 text-accent">
            <Volume2 size={18} />
          </div>
          <div>
            <h2 className="text-base font-bold text-text-primary">Voice & Speech Synthesis</h2>
            <p className="text-xs text-text-secondary">
              British masculine acoustics, wake-word detection, and natural barge-in speech interruption.
            </p>
          </div>
        </div>

        <div className="space-y-3 pt-2 text-xs">
          <div className="flex items-center justify-between p-3 rounded-lg bg-surface-2 border border-surface-border">
            <div>
              <span className="font-semibold text-text-primary block">Wake-Word Detection</span>
              <span className="text-text-muted text-[11px]">Listens locally for "Jarvis" or "Hey Jarvis"</span>
            </div>
            <span className="px-2.5 py-1 rounded bg-surface-3 text-accent font-mono">Active (Ctrl+Space fallback)</span>
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg bg-surface-2 border border-surface-border">
            <div>
              <span className="font-semibold text-text-primary block">Voice Profile</span>
              <span className="text-text-muted text-[11px]">Primary synthesis model</span>
            </div>
            <span className="px-2.5 py-1 rounded bg-surface-3 text-text-primary font-mono">British Masculine (en-GB-RyanNeural)</span>
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg bg-surface-2 border border-surface-border">
            <div>
              <span className="font-semibold text-text-primary block">Barge-In Speech Interruption</span>
              <span className="text-text-muted text-[11px]">Immediately terminates audio playback when you speak</span>
            </div>
            <span className="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400 font-mono">Enabled</span>
          </div>
        </div>
      </div>
    </div>
  );
}
