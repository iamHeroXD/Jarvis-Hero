import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FolderKanban,
  GitBranch,
  GitCommit,
  CheckCircle2,
  Clock,
  Plus,
  ExternalLink,
  Code2,
  FileText,
  Tag,
  Target,
  AlertCircle,
  FolderOpen,
} from 'lucide-react';
import { projectsApi, Project, ProjectNote } from '../services/api';

export default function ProjectsPage() {
  const queryClient = useQueryClient();
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showNoteModal, setShowNoteModal] = useState(false);

  // Form states
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high' | 'critical'>('high');
  const [localPath, setLocalPath] = useState('');
  const [repoUrl, setRepoUrl] = useState('');
  const [goalInput, setGoalInput] = useState('');
  const [goals, setGoals] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [tags, setTags] = useState<string[]>([]);

  // Note form state
  const [noteContent, setNoteContent] = useState('');
  const [noteType, setNoteType] = useState<'note' | 'decision' | 'blocker' | 'milestone'>('note');

  // Query projects
  const { data: projects = [], isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: projectsApi.list,
  });

  const selectedProject = projects.find((p) => p.id === selectedProjectId) || projects[0] || null;

  // Query Git status for selected project
  const { data: gitStatus } = useQuery({
    queryKey: ['projectGit', selectedProject?.id],
    queryFn: () => (selectedProject ? projectsApi.gitStatus(selectedProject.id) : null),
    enabled: !!selectedProject,
    refetchInterval: 15000,
  });

  // Query Notes for selected project
  const { data: notes = [] } = useQuery({
    queryKey: ['projectNotes', selectedProject?.id],
    queryFn: () => (selectedProject ? projectsApi.listNotes(selectedProject.id) : []),
    enabled: !!selectedProject,
  });

  // Create Project mutation
  const createMutation = useMutation({
    mutationFn: projectsApi.create,
    onSuccess: (newProj) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setSelectedProjectId(newProj.id);
      setShowCreateModal(false);
      setName('');
      setDescription('');
      setGoals([]);
      setTags([]);
    },
  });

  // Add Note mutation
  const addNoteMutation = useMutation({
    mutationFn: (data: { content: string; note_type: string }) =>
      projectsApi.addNote(selectedProject!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projectNotes', selectedProject?.id] });
      setShowNoteModal(false);
      setNoteContent('');
    },
  });

  const handleAddGoal = () => {
    if (goalInput.trim()) {
      setGoals([...goals, goalInput.trim()]);
      setGoalInput('');
    }
  };

  const handleAddTag = () => {
    if (tagInput.trim()) {
      setTags([...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  return (
    <div className="flex-1 overflow-hidden flex flex-col md:flex-row">
      {/* ── Left Sidebar: Project List ─────────────────────────── */}
      <div className="w-full md:w-80 border-r border-surface-border bg-surface-1 flex flex-col flex-shrink-0">
        <div className="p-4 border-b border-surface-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FolderKanban size={18} className="text-accent" />
            <span className="font-semibold text-sm text-text-primary">Projects & Workspaces</span>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="p-1.5 rounded-lg bg-accent/20 hover:bg-accent/30 text-accent border border-accent/40 text-xs transition-colors"
            title="Create Project"
          >
            <Plus size={14} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {isLoading ? (
            <div className="text-center text-xs text-text-muted py-6">Loading projects...</div>
          ) : projects.length === 0 ? (
            <div className="text-center text-xs text-text-muted py-6">No projects tracked.</div>
          ) : (
            projects.map((proj) => {
              const isSelected = selectedProject?.id === proj.id;
              return (
                <div
                  key={proj.id}
                  onClick={() => setSelectedProjectId(proj.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-surface-3 border-accent/60 shadow-sm'
                      : 'bg-surface-2 border-surface-border hover:border-surface-border/80'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="font-semibold text-xs text-text-primary truncate">{proj.name}</h3>
                    <span
                      className={`text-[10px] uppercase font-mono px-1.5 py-0.5 rounded ${
                        proj.priority === 'critical'
                          ? 'bg-rose-500/20 text-rose-400'
                          : proj.priority === 'high'
                          ? 'bg-amber-500/20 text-amber-400'
                          : 'bg-cyan-500/20 text-cyan-400'
                      }`}
                    >
                      {proj.priority}
                    </span>
                  </div>
                  <p className="text-[11px] text-text-secondary line-clamp-2 mb-2">{proj.description}</p>
                  <div className="flex items-center gap-2 text-[10px] text-text-muted">
                    <span className="flex items-center gap-1 font-mono">
                      <Target size={10} /> {proj.goals?.length || 0} goals
                    </span>
                    {proj.local_path && (
                      <span className="flex items-center gap-1 text-emerald-400">
                        <FolderOpen size={10} /> Local
                      </span>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* ── Main View: Selected Project Details ────────────────── */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {selectedProject ? (
          <>
            {/* Header Card */}
            <div className="card p-6 border border-surface-border">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                <div>
                  <div className="flex items-center gap-3">
                    <h2 className="text-lg font-bold text-text-primary">{selectedProject.name}</h2>
                    <span className="px-2 py-0.5 rounded text-xs bg-accent/20 text-accent border border-accent/30 uppercase font-mono">
                      {selectedProject.status}
                    </span>
                  </div>
                  <p className="text-xs text-text-secondary mt-1 max-w-2xl">{selectedProject.description}</p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setShowNoteModal(true)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-3 hover:bg-surface-4 text-accent border border-accent/30 text-xs font-medium transition-all"
                  >
                    <Plus size={13} /> Add Note / Decision
                  </button>
                </div>
              </div>

              {/* Workspace and Git Bar */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-3 border-t border-surface-border/60">
                <div className="bg-surface-2 p-3 rounded-lg border border-surface-border text-xs">
                  <span className="text-text-muted text-[11px] block uppercase tracking-wider mb-1">
                    Workspace Path:
                  </span>
                  <div className="font-mono text-text-primary truncate">
                    {selectedProject.local_path || 'No local directory linked'}
                  </div>
                </div>

                <div className="bg-surface-2 p-3 rounded-lg border border-surface-border text-xs flex items-center justify-between">
                  <div>
                    <span className="text-text-muted text-[11px] block uppercase tracking-wider mb-1">
                      Repository Git Status:
                    </span>
                    {gitStatus?.is_git ? (
                      <div className="flex items-center gap-2 font-mono">
                        <GitBranch size={13} className="text-accent" />
                        <span className="text-text-primary">{gitStatus.branch}</span>
                        {gitStatus.clean ? (
                          <span className="text-emerald-400 text-[11px] font-sans">✓ Clean</span>
                        ) : (
                          <span className="text-amber-400 text-[11px] font-sans">● Changes pending</span>
                        )}
                      </div>
                    ) : (
                      <span className="text-text-muted text-[11px]">Git tracking not configured</span>
                    )}
                  </div>
                  {selectedProject.repository_url && (
                    <a
                      href={selectedProject.repository_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-text-muted hover:text-accent p-1.5 rounded hover:bg-surface-3 transition-colors"
                      title="Open Remote Repository"
                    >
                      <ExternalLink size={14} />
                    </a>
                  )}
                </div>
              </div>
            </div>

            {/* Goals & Deliverables */}
            <div className="card p-5 border border-surface-border">
              <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-2 mb-3">
                <Target size={14} className="text-accent" /> Project Goals & Objectives
              </h3>
              {selectedProject.goals && selectedProject.goals.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {selectedProject.goals.map((g, i) => (
                    <div
                      key={i}
                      className="flex items-center gap-2.5 p-2 rounded bg-surface-2 border border-surface-border text-xs text-text-secondary font-mono"
                    >
                      <CheckCircle2 size={13} className="text-accent flex-shrink-0" />
                      <span>{g}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-text-muted">No specific milestones entered yet.</p>
              )}
            </div>

            {/* Notes & Decisions Log */}
            <div className="card p-5 border border-surface-border">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
                  <FileText size={14} className="text-accent" /> Architectural Log & Decisions
                </h3>
                <span className="text-[11px] text-text-muted font-mono">{notes.length} entries</span>
              </div>

              {notes.length === 0 ? (
                <p className="text-xs text-text-muted">No notes recorded for this workspace.</p>
              ) : (
                <div className="space-y-3">
                  {notes.map((n) => (
                    <div key={n.id} className="p-3 rounded-lg bg-surface-2 border border-surface-border text-xs">
                      <div className="flex items-center justify-between mb-1.5">
                        <span
                          className={`text-[10px] font-mono uppercase px-1.5 py-0.5 rounded ${
                            n.note_type === 'decision'
                              ? 'bg-accent/20 text-accent'
                              : n.note_type === 'blocker'
                              ? 'bg-rose-500/20 text-rose-400'
                              : n.note_type === 'milestone'
                              ? 'bg-emerald-500/20 text-emerald-400'
                              : 'bg-surface-3 text-text-secondary'
                          }`}
                        >
                          {n.note_type}
                        </span>
                        <span className="text-[10px] text-text-muted font-mono">
                          {new Date(n.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-text-secondary leading-relaxed">{n.content}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="card p-12 text-center text-text-muted text-xs">Select or create a project.</div>
        )}
      </div>

      {/* ── Create Project Modal ───────────────────────────────── */}
      <AnimatePresence>
        {showCreateModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="card w-full max-w-lg p-6 border border-accent/40 shadow-glow"
            >
              <div className="flex items-center justify-between mb-4 border-b border-surface-border pb-3">
                <h3 className="text-base font-bold text-text-primary flex items-center gap-2">
                  <FolderKanban size={18} className="text-accent" /> Register New Workspace Project
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
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Project Name</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. RCN Core Robotics Framework"
                    className="w-full input text-xs py-2 px-3 bg-surface-2 border border-surface-border rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Description</label>
                  <textarea
                    rows={2}
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="High-level mission and overview..."
                    className="w-full input text-xs py-2 px-3 bg-surface-2 border border-surface-border rounded-lg"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-text-secondary mb-1">Priority</label>
                    <select
                      value={priority}
                      onChange={(e) => setPriority(e.target.value as any)}
                      className="w-full input text-xs py-2 px-2 bg-surface-2 border border-surface-border rounded-lg"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-text-secondary mb-1">Local Workspace Path</label>
                    <input
                      type="text"
                      value={localPath}
                      onChange={(e) => setLocalPath(e.target.value)}
                      placeholder="f:\Work\Project-Dir"
                      className="w-full input text-xs py-2 px-2 bg-surface-2 border border-surface-border rounded-lg font-mono"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Repository URL</label>
                  <input
                    type="text"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    placeholder="https://github.com/owner/repo"
                    className="w-full input text-xs py-2 px-3 bg-surface-2 border border-surface-border rounded-lg font-mono"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Goals & Milestones</label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={goalInput}
                      onChange={(e) => setGoalInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleAddGoal()}
                      placeholder="Add milestone..."
                      className="flex-1 input text-xs py-1.5 px-2 bg-surface-2 border border-surface-border rounded-lg"
                    />
                    <button
                      onClick={handleAddGoal}
                      className="px-2.5 py-1.5 rounded-lg bg-surface-3 hover:bg-surface-4 text-xs font-medium text-text-primary border border-surface-border"
                    >
                      Add
                    </button>
                  </div>
                  {goals.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {goals.map((g, i) => (
                        <div key={i} className="text-xs text-text-secondary bg-surface-2 px-2 py-1 rounded flex justify-between">
                          <span>{g}</span>
                          <button onClick={() => setGoals(goals.filter((_, idx) => idx !== i))} className="text-rose-400">✕</button>
                        </div>
                      ))}
                    </div>
                  )}
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
                      description: description.trim(),
                      priority,
                      local_path: localPath.trim() || null,
                      repository_url: repoUrl.trim() || null,
                      goals,
                      tags,
                    });
                  }}
                  disabled={!name.trim() || createMutation.isPending}
                  className="px-4 py-1.5 rounded-lg bg-accent hover:bg-accent/90 text-white text-xs font-semibold shadow-glow disabled:opacity-50"
                >
                  {createMutation.isPending ? 'Saving...' : 'Register Workspace'}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ── Add Note Modal ─────────────────────────────────────── */}
      <AnimatePresence>
        {showNoteModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="card w-full max-w-md p-6 border border-accent/40 shadow-glow"
            >
              <div className="flex items-center justify-between mb-4 border-b border-surface-border pb-3">
                <h3 className="text-base font-bold text-text-primary flex items-center gap-2">
                  <FileText size={18} className="text-accent" /> Log Project Note
                </h3>
                <button
                  onClick={() => setShowNoteModal(false)}
                  className="text-text-muted hover:text-text-primary text-xs"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Entry Type</label>
                  <select
                    value={noteType}
                    onChange={(e) => setNoteType(e.target.value as any)}
                    className="w-full input text-xs py-2 px-2 bg-surface-2 border border-surface-border rounded-lg"
                  >
                    <option value="note">General Note</option>
                    <option value="decision">Architectural Decision</option>
                    <option value="blocker">Blocker / Issue</option>
                    <option value="milestone">Milestone Accomplished</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Content</label>
                  <textarea
                    rows={4}
                    value={noteContent}
                    onChange={(e) => setNoteContent(e.target.value)}
                    placeholder="Record critical rationale, findings, or blocker details..."
                    className="w-full input text-xs py-2 px-3 bg-surface-2 border border-surface-border rounded-lg"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-surface-border">
                <button
                  onClick={() => setShowNoteModal(false)}
                  className="px-3 py-1.5 rounded-lg text-xs text-text-muted hover:text-text-primary"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    if (!noteContent.trim()) return;
                    addNoteMutation.mutate({ content: noteContent.trim(), note_type: noteType });
                  }}
                  disabled={!noteContent.trim() || addNoteMutation.isPending}
                  className="px-4 py-1.5 rounded-lg bg-accent hover:bg-accent/90 text-white text-xs font-semibold shadow-glow disabled:opacity-50"
                >
                  {addNoteMutation.isPending ? 'Logging...' : 'Save Entry'}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
