import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { CheckSquare, Square, Plus, X, Calendar, ArrowRight } from 'lucide-react';

interface TaskScheduleItem {
  id: string;
  title: string;
  timeSlot: string;
  completed: boolean;
  priority: 'high' | 'medium' | 'normal';
}

interface TaskScheduleWidgetProps {
  onClose: () => void;
  targetDeadline?: string;
}

export default function TaskScheduleWidget({
  onClose,
  targetDeadline = '08:00 PM',
}: TaskScheduleWidgetProps) {
  const [tasks, setTasks] = useState<TaskScheduleItem[]>([
    { id: '1', title: 'Complete Physics module questions', timeSlot: '04:00 PM - 05:15 PM', completed: false, priority: 'high' },
    { id: '2', title: 'Review Chemistry equations & notes', timeSlot: '05:30 PM - 06:45 PM', completed: false, priority: 'medium' },
    { id: '3', title: 'Deploy website & run validation tests', timeSlot: '07:00 PM - 07:45 PM', completed: false, priority: 'high' },
  ]);
  const [newTitle, setNewTitle] = useState<string>('');

  const toggleTask = (id: string) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t))
    );
  };

  const addTask = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    const newTask: TaskScheduleItem = {
      id: String(Date.now()),
      title: newTitle.trim(),
      timeSlot: 'Pending Allocation',
      completed: false,
      priority: 'normal',
    };
    setTasks([...tasks, newTask]);
    setNewTitle('');
  };

  const completedCount = tasks.filter((t) => t.completed).length;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, y: 20 }}
      className="fixed bottom-24 right-8 z-50 w-80 rounded-2xl bg-[#02050e]/95 border border-cyan-400/60 backdrop-blur-2xl shadow-[0_0_35px_rgba(6,182,212,0.35)] p-4 font-mono text-cyan-400 select-none"
    >
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-cyan-500/30">
        <div className="flex items-center gap-1.5 text-xs text-white font-bold">
          <Calendar size={14} className="text-cyan-300" />
          <span>SCHEDULE PLANNER // TARGET: {targetDeadline}</span>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:text-rose-400 transition-colors"
          title="Close Planner"
        >
          <X size={14} />
        </button>
      </div>

      {/* Progress pill */}
      <div className="flex items-center justify-between py-2 text-[11px] text-cyan-300/80">
        <span>Progress: {completedCount} / {tasks.length} Completed</span>
        <span className="text-[10px] text-emerald-400 font-bold">
          {Math.round((completedCount / (tasks.length || 1)) * 100)}%
        </span>
      </div>

      {/* Tasks List */}
      <div className="space-y-2 max-h-52 overflow-y-auto pr-1">
        {tasks.map((task) => (
          <div
            key={task.id}
            onClick={() => toggleTask(task.id)}
            className={`p-2.5 rounded-xl border transition-all cursor-pointer flex items-start gap-2.5 ${
              task.completed
                ? 'bg-black/40 border-cyan-500/20 opacity-60'
                : 'bg-[#030919] border-cyan-500/40 hover:border-cyan-300'
            }`}
          >
            <div className="mt-0.5 text-cyan-400">
              {task.completed ? <CheckSquare size={14} className="text-emerald-400" /> : <Square size={14} />}
            </div>
            <div className="flex-1 min-w-0">
              <div
                className={`text-xs text-white font-sans ${
                  task.completed ? 'line-through text-cyan-500' : ''
                }`}
              >
                {task.title}
              </div>
              <div className="text-[10px] text-cyan-400/70 font-mono mt-0.5 flex items-center gap-1">
                <span>{task.timeSlot}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Add Task input */}
      <form onSubmit={addTask} className="mt-3 pt-2 border-t border-cyan-500/20 flex items-center gap-1.5">
        <input
          type="text"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          placeholder="Append task item..."
          className="flex-1 py-1 px-2.5 rounded-lg bg-black border border-cyan-500/40 text-white placeholder-cyan-600 text-xs outline-none"
        />
        <button
          type="submit"
          className="p-1.5 rounded-lg bg-cyan-500/20 border border-cyan-400/50 text-cyan-100 hover:bg-cyan-500/30"
          title="Add Task"
        >
          <Plus size={13} />
        </button>
      </form>
    </motion.div>
  );
}
