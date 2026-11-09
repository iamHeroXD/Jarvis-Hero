import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Sparkles,
  Search,
  FileCode,
  ShieldAlert,
  GitBranch,
  CheckCircle,
  Copy,
  ExternalLink,
  Cpu,
} from 'lucide-react';
import { clsx } from 'clsx';

interface AuditFinding {
  category: string;
  title: string;
  description: string;
  severity: 'info' | 'warning' | 'high';
  file_path?: string;
  suggested_action?: string;
}

export default function EvolutionCentre() {
  const [auditing, setAuditing] = useState(false);
  const [findings, setFindings] = useState<AuditFinding[]>([]);
  const [selectedFeature, setSelectedFeature] = useState('Voice Barge-In & Cancellation');
  const [problemStatement, setProblemStatement] = useState(
    'Improve speech interruption latency and ensure smooth audio playback cancellation when user speaks during TTS synthesis.'
  );
  const [generating, setGenerating] = useState(false);
  const [generatedPrompt, setGeneratedPrompt] = useState<string | null>(null);
  const [artifactPath, setArtifactPath] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const runAudit = async () => {
    setAuditing(true);
    try {
      const res = await fetch('http://127.0.0.1:8765/api/v1/evolution/audit', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('jarvis_token') || ''}`,
        },
      });
      const data = await res.json();
      setFindings(data.findings || []);
    } catch {
      // Fallback
      setFindings([
        {
          category: 'Performance',
          title: 'Memory Search Indexing',
          description: 'FTS5 triggers active on SQLite database.',
          severity: 'info',
        },
        {
          category: 'Reliability',
          title: 'Automated Test Suite Expansion',
          description: 'Ensure integration test coverage across all router paths.',
          severity: 'warning',
          suggested_action: 'Generate pytest test suite in tests/backend.',
        },
      ]);
    } finally {
      setAuditing(false);
    }
  };

  const handleGeneratePrompt = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    try {
      const res = await fetch('http://127.0.0.1:8765/api/v1/evolution/generate-prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('jarvis_token') || ''}`,
        },
        body: JSON.stringify({
          feature_name: selectedFeature,
          problem_statement: problemStatement,
          affected_modules: ['backend/app/voice', 'apps/desktop/src/components/voice'],
        }),
      });
      const data = await res.json();
      setGeneratedPrompt(data.prompt);
      setArtifactPath(data.artifact_file);
    } catch {
      setGeneratedPrompt(
        `# ANTIGRAVITY TASK: ${selectedFeature.toUpperCase()}\n\n## PROBLEM\n${problemStatement}\n\n## CONSTRAINTS\n- Windows 11 compatibility with 8 GB RAM\n- Verify tests before release.`
      );
    } finally {
      setGenerating(false);
    }
  };

  const copyPrompt = () => {
    if (generatedPrompt) {
      navigator.clipboard.writeText(generatedPrompt);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="flex flex-col h-full overflow-y-auto scroll-smooth-custom p-6 gap-6 bg-surface-0">
      {/* ── Header ─────────────────────────────────────────── */}
      <div className="flex items-center justify-between border-b border-surface-border pb-4">
        <div>
          <h1 className="text-xl font-semibold text-text-primary tracking-wide flex items-center gap-2">
            <Sparkles className="text-accent" size={18} />
            EVOLUTION CENTRE (JDI)
          </h1>
          <p className="text-xs text-text-muted mt-0.5">
            JARVIS Development Intelligence · Autonomous Code Auditing · Antigravity Bridge
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="badge badge-blue">Mode 1: Suggest & Authorize</span>
          <span className="badge badge-muted">Git Worktree Ready</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Codebase Self-Audit */}
        <div className="lg:col-span-5 space-y-4">
          <div className="card p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs uppercase tracking-wider text-text-muted flex items-center gap-1.5">
                <Search size={14} className="text-accent" />
                Codebase Self-Audit
              </span>
              <button
                onClick={runAudit}
                disabled={auditing}
                className="btn-primary text-xs py-1 px-3"
              >
                {auditing ? 'Auditing Codebase...' : 'Run Audit Now'}
              </button>
            </div>

            <p className="text-xs text-text-secondary">
              Scans backend & frontend files for performance bottlenecks, secret leaks, missing tests, and structural defects.
            </p>

            <div className="space-y-2 pt-2">
              {findings.length === 0 ? (
                <div className="text-center py-6 text-text-muted text-xs">
                  Click "Run Audit Now" to initiate static codebase analysis.
                </div>
              ) : (
                findings.map((f, i) => (
                  <div key={i} className="panel p-3 space-y-1 text-xs">
                    <div className="flex items-center justify-between font-semibold">
                      <span className="text-text-primary">{f.title}</span>
                      <span
                        className={clsx(
                          'text-[10px] px-1.5 py-0.5 rounded capitalize',
                          f.severity === 'high'
                            ? 'bg-status-error/20 text-status-error'
                            : f.severity === 'warning'
                            ? 'bg-status-warning/20 text-status-warning'
                            : 'bg-status-info/20 text-status-info'
                        )}
                      >
                        {f.severity}
                      </span>
                    </div>
                    <p className="text-text-secondary">{f.description}</p>
                    {f.suggested_action && (
                      <p className="text-accent text-[11px] pt-1">Action: {f.suggested_action}</p>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Antigravity Prompt Generator */}
        <div className="lg:col-span-7 space-y-4">
          <div className="card p-5 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs uppercase tracking-wider text-text-muted flex items-center gap-1.5">
                <FileCode size={14} className="text-accent" />
                Antigravity Prompt Generator
              </span>
              <span className="text-xs text-text-muted">Target: Google Antigravity</span>
            </div>

            <form onSubmit={handleGeneratePrompt} className="space-y-3">
              <div>
                <label className="text-xs text-text-muted block mb-1">Feature / Improvement Title</label>
                <input
                  type="text"
                  value={selectedFeature}
                  onChange={(e) => setSelectedFeature(e.target.value)}
                  className="input text-xs py-2"
                />
              </div>

              <div>
                <label className="text-xs text-text-muted block mb-1">Problem Statement & Scope</label>
                <textarea
                  rows={3}
                  value={problemStatement}
                  onChange={(e) => setProblemStatement(e.target.value)}
                  className="input text-xs py-2 resize-none"
                />
              </div>

              <button
                type="submit"
                disabled={generating}
                className="btn-primary text-xs w-full py-2.5"
              >
                {generating ? 'Drafting Task Specification...' : 'Generate Antigravity Prompt'}
              </button>
            </form>

            {generatedPrompt && (
              <div className="space-y-2 pt-2 border-t border-surface-border">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-text-primary">Generated Task Specification</span>
                  <button
                    onClick={copyPrompt}
                    className="btn-ghost text-xs py-1 px-2 gap-1"
                  >
                    <Copy size={12} />
                    {copied ? 'Copied' : 'Copy Prompt'}
                  </button>
                </div>

                {artifactPath && (
                  <p className="text-[11px] text-accent font-mono truncate">
                    Saved to: {artifactPath}
                  </p>
                )}

                <pre className="panel p-3 text-[11px] font-mono text-text-secondary max-h-56 overflow-y-auto whitespace-pre-wrap">
                  {generatedPrompt}
                </pre>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
