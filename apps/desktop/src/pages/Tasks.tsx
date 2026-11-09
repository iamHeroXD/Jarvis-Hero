import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  CheckSquare,
  Clock,
  Plus,
  Play,
  ShieldCheck,
  AlertTriangle,
  Bot,
  Volume2,
  RefreshCw,
  Sparkles,
  Calendar,
  CheckCircle2,
  XCircle,
  FileText,
} from 'lucide-react';
import { tasksApi, voiceApi, TaskItem, ReminderItem } from '../services/api';

const AGENT_OPTIONS = ['JARVIS', 'ATLAS', 'ORACLE', 'NEXUS', 'ATHENA', 'ECHO', 'SENTINEL', 'JDI'];

export default function TasksPage() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'tasks' | 'reminders'>('tasks');
  const [showNewTaskModal, setShowNewTaskModal] = useState(false);
  const [showNewReminderModal, setShowNewReminderModal] = useState(false);
  const [briefingText, setBriefingText] = useState<string | null>(null);
  const [isSpeakingBriefing, setIsSpeakingBriefing] = useState(false);

  // New task form state
  const [taskTitle, setTaskTitle] = useState('');
  const [taskDescription, setTaskDescription] = useState('');
  const [taskAgent, setTaskAgent] = useState('ATLAS');
  const [taskPermLevel, setTaskPermLevel] = useState(1);
  const [taskApproval, setTaskApproval] = useState(false);
  const [taskPlanStep, setTaskPlanStep] = useState('');
  const [taskPlan, setTaskPlan] = useState<string[]>([
    'Inspect target repository or environment',
    'Execute operations with rollback protection',
    'Verify on-disk evidence and test results',
  ]);

  // New reminder form state
  const [remTitle, setRemTitle] = useState('');
  const [remDueAt, setRemDueAt] = useState('');
  const [remBody, setRemBody] = useState('');
  const [remRecurrence, setRemRecurrence] = useState('');
  const [remSpeak, setRemSpeak] = useState(true);

  // Queries
  const { data: tasks = [], isLoading: tasksLoading, refetch: refetchTasks } = useQuery({
    queryKey: ['tasks'],
    queryFn: tasksApi.list,
    refetchInterval: 5000,
  });

  const { data: reminders = [], isLoading: remLoading, refetch: refetchReminders } = useQuery({
    queryKey: ['reminders'],
    queryFn: tasksApi.listReminders,
    refetchInterval: 10000,
  });

  // Task creation mutation
  const createTaskMutation = useMutation({
    mutationFn: tasksApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      setShowNewTaskModal(false);
      setTaskTitle('');
      setTaskDescription('');
    },
  });

  // Reminder creation mutation
  const createReminderMutation = useMutation({
    mutationFn: tasksApi.createReminder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reminders'] });
      setShowNewReminderModal(false);
      setRemTitle('');
      setRemDueAt('');
      setRemBody('');
    },
  });

  // Complete reminder mutation
  const completeReminderMutation = useMutation({
    mutationFn: tasksApi.completeReminder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reminders'] });
    },
  });

  // Briefing action
  const handleFetchBriefing = async () => {
    try {
      const res = await tasksApi.getBriefing();
      setBriefingText(res.briefing);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSpeakBriefing = async () => {
    if (!briefingText) return;
    setIsSpeakingBriefing(true);
    try {
      const blob = await voiceApi.speak(briefingText);
      if (blob) {
        const audio = new Audio(URL.createObjectURL(blob));
        audio.onended = () => setIsSpeakingBriefing(false);
        audio.onerror = () => setIsSpeakingBriefing(false);
        await audio.play();
      } else {
        setIsSpeakingBriefing(false);
      }
    } catch {
      setIsSpeakingBriefing(false);
    }
  };

  const handleAddPlanStep = () => {
    if (taskPlanStep.trim()) {
      setTaskPlan([...taskPlan, taskPlanStep.trim()]);
      setTaskPlanStep('');
    }
  };

  const getStatusBadge = (state: TaskItem['state']) => {
    switch (state) {
      case 'completed':
        return <span className="px-2 py-0.5 rounded text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono">COMPLETED</span>;
      case 'running':
        return <span className="px-2 py-0.5 rounded text-xs bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 animate-pulse font-mono">RUNNING</span>;
      case 'verifying':
        return <span className="px-2 py-0.5 rounded text-xs bg-amber-500/20 text-amber-400 border border-amber-500/30 font-mono">VERIFYING</span>;
      case 'awaiting_approval':
        return <span className="px-2 py-0.5 rounded text-xs bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 font-mono">APPROVAL NEEDED</span>;
      case 'failed':
        return <span className="px-2 py-0.5 rounded text-xs bg-rose-500/20 text-rose-400 border border-rose-500/30 font-mono">FAILED</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-xs bg-surface-3 text-text-secondary border border-surface-border font-mono">{state.toUpperCase()}</span>;
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* ── Top Header ────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-border pb-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-accent/20 border border-accent/40 flex items-center justify-center text-accent">
              <CheckSquare size={20} />
            </div>
            <div>
              <h1 className="text-xl font-bold text-text-primary tracking-wide">Tasks & Operations Engine</h1>
              <p className="text-xs text-text-secondary">
                Autonomous task lifecycle, state machine verification, and tactical reminders.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleFetchBriefing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-3 hover:bg-surface-4 text-accent border border-accent/30 text-xs font-medium transition-all"
          >
            <Sparkles size={14} /> Tactical Briefing
          </button>
          <button
            onClick={() => {
              if (activeTab === 'tasks') setShowNewTaskModal(true);
              else setShowNewReminderModal(true);
            }}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-accent hover:bg-accent/90 text-white text-xs font-semibold shadow-glow transition-all"
          >
            <Plus size={14} /> {activeTab === 'tasks' ? 'New Task' : 'New Reminder'}
          </button>
        </div>
      </div>

      {/* ── Tactical Briefing Card (if fetched) ────────────────── */}
      <AnimatePresence>
        {briefingText && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="card p-5 border-l-4 border-accent relative bg-gradient-to-r from-accent/10 to-transparent"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-accent animate-ping" />
                <h3 className="text-sm font-semibold text-accent uppercase tracking-wider">Tactical Briefing Overview</h3>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleSpeakBriefing}
                  disabled={isSpeakingBriefing}
                  className="flex items-center gap-1 text-xs px-2.5 py-1 rounded bg-surface-3 hover:bg-surface-4 text-text-primary border border-surface-border transition-colors"
                >
                  <Volume2 size={13} className={isSpeakingBriefing ? 'text-accent animate-pulse' : ''} />
                  {isSpeakingBriefing ? 'Speaking...' : 'Play Audio'}
                </button>
                <button
                  onClick={() => setBriefingText(null)}
                  className="text-xs text-text-muted hover:text-text-primary"
                >
                  Dismiss
                </button>
              </div>
            </div>
            <p className="text-sm text-text-secondary leading-relaxed font-sans whitespace-pre-line">{briefingText}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── View Switcher Tabs ─────────────────────────────────── */}
      <div className="flex items-center gap-2 border-b border-surface-border pb-2">
        <button
          onClick={() => setActiveTab('tasks')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold tracking-wide transition-all ${
            activeTab === 'tasks'
              ? 'bg-accent/20 text-accent border border-accent/40 shadow-sm'
              : 'text-text-secondary hover:text-text-primary'
          }`}
        >
          <CheckSquare size={14} /> Active Tasks ({tasks.length})
        </button>
        <button
          onClick={() => setActiveTab('reminders')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold tracking-wide transition-all ${
            activeTab === 'reminders'
              ? 'bg-accent/20 text-accent border border-accent/40 shadow-sm'
              : 'text-text-secondary hover:text-text-primary'
          }`}
        >
          <Clock size={14} /> Smart Reminders ({reminders.filter((r) => !r.is_completed).length})
        </button>
      </div>

      {/* ── Content Area ───────────────────────────────────────── */}
      {activeTab === 'tasks' ? (
        <div className="space-y-4">
          {tasksLoading ? (
            <div className="p-8 text-center text-text-muted text-xs">Loading operational tasks...</div>
          ) : tasks.length === 0 ? (
            <div className="card p-10 text-center border-dashed border-surface-border">
              <Bot size={36} className="mx-auto text-text-muted mb-3 opacity-60" />
              <h3 className="text-sm font-semibold text-text-primary">No Active Tasks</h3>
              <p className="text-xs text-text-secondary mt-1">
                Dispatch an autonomous task to ATLAS, ORACLE, or JDI to get started.
              </p>
              <button
                onClick={() => setShowNewTaskModal(true)}
                className="mt-4 px-3 py-1.5 rounded-lg bg-surface-3 hover:bg-surface-4 text-accent text-xs font-medium border border-accent/30 inline-flex items-center gap-1.5"
              >
                <Plus size={13} /> Create First Task
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {tasks.map((task) => (
                <div key={task.task_id} className="card p-5 border border-surface-border hover:border-accent/40 transition-all">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-xs text-text-muted">[{task.task_id.slice(0, 8)}]</span>
                      <h3 className="text-sm font-semibold text-text-primary">{task.title}</h3>
                      {getStatusBadge(task.state)}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-text-muted">
                      <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-surface-3 border border-surface-border">
                        <Bot size={12} className="text-accent" /> {task.assigned_agent}
                      </span>
                      <span className="px-2 py-0.5 rounded bg-surface-3 border border-surface-border font-mono">
                        L{task.permission_level}
                      </span>
                      {task.verified && (
                        <span className="flex items-center gap-1 text-emerald-400 font-mono">
                          <ShieldCheck size={13} /> Verified
                        </span>
                      )}
                    </div>
                  </div>

                  {task.description && (
                    <p className="text-xs text-text-secondary mb-3 leading-relaxed">{task.description}</p>
                  )}

                  {/* Plan Steps */}
                  {task.plan && task.plan.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-surface-border/50">
                      <div className="text-[11px] font-semibold text-text-muted uppercase tracking-wider mb-2">
                        Execution Plan:
                      </div>
                      <div className="space-y-1.5">
                        {task.plan.map((step, idx) => (
                          <div key={idx} className="flex items-start gap-2 text-xs text-text-secondary font-mono">
                            <span className="text-accent text-[11px]">{idx + 1}.</span>
                            <span>{step}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Evidence list */}
                  {task.evidence && task.evidence.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-surface-border/50">
                      <div className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider mb-1 flex items-center gap-1">
                        <ShieldCheck size={12} /> Verified Evidence
                      </div>
                      <div className="space-y-1">
                        {task.evidence.map((ev, idx) => (
                          <div key={idx} className="text-xs text-text-muted bg-surface-3/50 px-2 py-1 rounded border border-surface-border/40 font-mono">
                            {ev}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {remLoading ? (
            <div className="p-8 text-center text-text-muted text-xs">Loading scheduled reminders...</div>
          ) : reminders.length === 0 ? (
            <div className="card p-10 text-center border-dashed border-surface-border">
              <Clock size={36} className="mx-auto text-text-muted mb-3 opacity-60" />
              <h3 className="text-sm font-semibold text-text-primary">No Reminders Scheduled</h3>
              <p className="text-xs text-text-secondary mt-1">
                Ask JARVIS to remind you to finish chemistry records, inspect repositories, or prepare reports.
              </p>
              <button
                onClick={() => setShowNewReminderModal(true)}
                className="mt-4 px-3 py-1.5 rounded-lg bg-surface-3 hover:bg-surface-4 text-accent text-xs font-medium border border-accent/30 inline-flex items-center gap-1.5"
              >
                <Plus size={13} /> Schedule Reminder
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {reminders.map((rem) => (
                <div
                  key={rem.reminder_id}
                  className={`card p-4 border transition-all ${
                    rem.is_completed
                      ? 'border-surface-border opacity-60'
                      : 'border-surface-border hover:border-accent/40'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div className="flex items-center gap-2">
                      {rem.is_completed ? (
                        <CheckCircle2 size={16} className="text-emerald-400 flex-shrink-0" />
                      ) : (
                        <Clock size={16} className="text-accent flex-shrink-0" />
                      )}
                      <h4
                        className={`text-sm font-semibold ${
                          rem.is_completed ? 'line-through text-text-muted' : 'text-text-primary'
                        }`}
                      >
                        {rem.title}
                      </h4>
                    </div>
                    {!rem.is_completed && (
                      <button
                        onClick={() => completeReminderMutation.mutate(rem.reminder_id)}
                        className="px-2 py-1 rounded bg-surface-3 hover:bg-surface-4 text-emerald-400 hover:text-emerald-300 border border-emerald-500/30 text-xs font-medium transition-colors"
                      >
                        Mark Done
                      </button>
                    )}
                  </div>

                  {rem.body && <p className="text-xs text-text-secondary mb-3">{rem.body}</p>}

                  <div className="flex items-center justify-between text-[11px] text-text-muted pt-2 border-t border-surface-border/50">
                    <span className="flex items-center gap-1 font-mono">
                      <Calendar size={11} /> {new Date(rem.due_at).toLocaleString()}
                    </span>
                    {rem.recurrence && (
                      <span className="px-1.5 py-0.5 rounded bg-surface-3 border border-surface-border font-mono">
                        {rem.recurrence}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── New Task Modal ─────────────────────────────────────── */}
      <AnimatePresence>
        {showNewTaskModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="card w-full max-w-lg p-6 border border-accent/40 shadow-glow"
            >
              <div className="flex items-center justify-between mb-4 border-b border-surface-border pb-3">
                <h3 className="text-base font-bold text-text-primary flex items-center gap-2">
                  <Bot size={18} className="text-accent" /> Create Managed Autonomous Task
                </h3>
                <button
                  onClick={() => setShowNewTaskModal(false)}
                  className="text-text-muted hover:text-text-primary text-xs"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Task Title</label>
                  <input
                    type="text"
                    value={taskTitle}
                    onChange={(e) => setTaskTitle(e.target.value)}
                    placeholder="e.g. Inspect RCN repository and run test suite"
                    className="w-full input text-xs py-2 px-3 bg-surface-2 border border-surface-border rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Description</label>
                  <textarea
                    rows={2}
                    value={taskDescription}
                    onChange={(e) => setTaskDescription(e.target.value)}
                    placeholder="Detailed intent and success criteria..."
                    className="w-full input text-xs py-2 px-3 bg-surface-2 border border-surface-border rounded-lg"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-text-secondary mb-1">Specialist Agent</label>
                    <select
                      value={taskAgent}
                      onChange={(e) => setTaskAgent(e.target.value)}
                      className="w-full input text-xs py-2 px-2 bg-surface-2 border border-surface-border rounded-lg"
                    >
                      {AGENT_OPTIONS.map((a) => (
                        <option key={a} value={a}>
                          {a}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-text-secondary mb-1">Permission Level</label>
                    <select
                      value={taskPermLevel}
                      onChange={(e) => setTaskPermLevel(Number(e.target.value))}
                      className="w-full input text-xs py-2 px-2 bg-surface-2 border border-surface-border rounded-lg"
                    >
                      <option value={0}>L0: Info / Passive</option>
                      <option value={1}>L1: Read-Only Workspace</option>
                      <option value={2}>L2: Workspace Modification</option>
                      <option value={3}>L3: Developer Tool Runner</option>
                      <option value={4}>L4: System Administrative</option>
                    </select>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="reqApp"
                    checked={taskApproval}
                    onChange={(e) => setTaskApproval(e.target.checked)}
                    className="rounded bg-surface-2 border-surface-border text-accent focus:ring-0"
                  />
                  <label htmlFor="reqApp" className="text-xs text-text-secondary cursor-pointer">
                    Require explicit confirmation before execution
                  </label>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Plan Steps</label>
                  <div className="space-y-1 mb-2">
                    {taskPlan.map((s, i) => (
                      <div key={i} className="text-xs text-text-muted flex items-center justify-between bg-surface-2 px-2 py-1 rounded">
                        <span>{i + 1}. {s}</span>
                        <button
                          onClick={() => setTaskPlan(taskPlan.filter((_, idx) => idx !== i))}
                          className="text-rose-400 hover:text-rose-300 text-[10px]"
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={taskPlanStep}
                      onChange={(e) => setTaskPlanStep(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleAddPlanStep()}
                      placeholder="Add plan step..."
                      className="flex-1 input text-xs py-1.5 px-2 bg-surface-2 border border-surface-border rounded-lg"
                    />
                    <button
                      onClick={handleAddPlanStep}
                      className="px-2.5 py-1.5 rounded-lg bg-surface-3 hover:bg-surface-4 text-xs font-medium text-text-primary border border-surface-border"
                    >
                      Add
                    </button>
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-surface-border">
                <button
                  onClick={() => setShowNewTaskModal(false)}
                  className="px-3 py-1.5 rounded-lg text-xs text-text-muted hover:text-text-primary"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    if (!taskTitle.trim()) return;
                    createTaskMutation.mutate({
                      title: taskTitle.trim(),
                      description: taskDescription.trim(),
                      assigned_agent: taskAgent,
                      permission_level: taskPermLevel,
                      requires_approval: taskApproval,
                      plan: taskPlan,
                    });
                  }}
                  disabled={!taskTitle.trim() || createTaskMutation.isPending}
                  className="px-4 py-1.5 rounded-lg bg-accent hover:bg-accent/90 text-white text-xs font-semibold shadow-glow disabled:opacity-50"
                >
                  {createTaskMutation.isPending ? 'Scheduling...' : 'Launch Task'}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ── New Reminder Modal ─────────────────────────────────── */}
      <AnimatePresence>
        {showNewReminderModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="card w-full max-w-md p-6 border border-accent/40 shadow-glow"
            >
              <div className="flex items-center justify-between mb-4 border-b border-surface-border pb-3">
                <h3 className="text-base font-bold text-text-primary flex items-center gap-2">
                  <Clock size={18} className="text-accent" /> Schedule Smart Reminder
                </h3>
                <button
                  onClick={() => setShowNewReminderModal(false)}
                  className="text-text-muted hover:text-text-primary text-xs"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Title</label>
                  <input
                    type="text"
                    value={remTitle}
                    onChange={(e) => setRemTitle(e.target.value)}
                    placeholder="e.g. Complete chemistry record experiment writeup"
                    className="w-full input text-xs py-2 px-3 bg-surface-2 border border-surface-border rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Due Date & Time</label>
                  <input
                    type="datetime-local"
                    value={remDueAt}
                    onChange={(e) => setRemDueAt(e.target.value)}
                    className="w-full input text-xs py-2 px-3 bg-surface-2 border border-surface-border rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Context / Notes</label>
                  <textarea
                    rows={2}
                    value={remBody}
                    onChange={(e) => setRemBody(e.target.value)}
                    placeholder="Optional notes or details..."
                    className="w-full input text-xs py-2 px-3 bg-surface-2 border border-surface-border rounded-lg"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="speakRem"
                    checked={remSpeak}
                    onChange={(e) => setRemSpeak(e.target.checked)}
                    className="rounded bg-surface-2 border-surface-border text-accent focus:ring-0"
                  />
                  <label htmlFor="speakRem" className="text-xs text-text-secondary cursor-pointer">
                    Speak aloud with British voice when due
                  </label>
                </div>
              </div>

              <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-surface-border">
                <button
                  onClick={() => setShowNewReminderModal(false)}
                  className="px-3 py-1.5 rounded-lg text-xs text-text-muted hover:text-text-primary"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    if (!remTitle.trim() || !remDueAt) return;
                    createReminderMutation.mutate({
                      title: remTitle.trim(),
                      due_at: remDueAt,
                      body: remBody.trim(),
                      recurrence: remRecurrence || null,
                      speak_aloud: remSpeak,
                    });
                  }}
                  disabled={!remTitle.trim() || !remDueAt || createReminderMutation.isPending}
                  className="px-4 py-1.5 rounded-lg bg-accent hover:bg-accent/90 text-white text-xs font-semibold shadow-glow disabled:opacity-50"
                >
                  {createReminderMutation.isPending ? 'Scheduling...' : 'Set Reminder'}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
