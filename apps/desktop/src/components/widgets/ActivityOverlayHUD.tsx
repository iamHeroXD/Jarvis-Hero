import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, Square, Pause, Play, CheckCircle2, AlertTriangle, Layers, X } from 'lucide-react';

interface ActivityOverlayHUDProps {
  isVisible: boolean;
  currentAction: string;
  assignedAgent?: string;
  currentStep?: number;
  totalSteps?: number;
  isPaused?: boolean;
  onPauseToggle?: () => void;
  onStopTask?: () => void;
  onClose?: () => void;
}

export default function ActivityOverlayHUD({
  isVisible,
  currentAction,
  assignedAgent = 'MASTER ORCHESTRATOR',
  currentStep = 1,
  totalSteps = 4,
  isPaused = false,
  onPauseToggle,
  onStopTask,
  onClose,
}: ActivityOverlayHUDProps) {
  if (!isVisible) return null;

  return (
    <AnimatePresence>
      {/* Subtle Screen-Edge Cybernetic Glow */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 pointer-events-none z-40 border-2 border-cyan-400/25 shadow-[inset_0_0_50px_rgba(6,182,212,0.12)]"
      />

      {/* Floating Futuristic Activity Capsule */}
      <motion.aside
        initial={{ opacity: 0, y: -20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -20, scale: 0.95 }}
        className="fixed top-16 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 px-4 py-2 rounded-2xl bg-[#02050e]/95 border border-cyan-400/70 backdrop-blur-2xl shadow-[0_0_40px_rgba(6,182,212,0.4)] font-mono select-none"
      >
        {/* Animated Status Pulse */}
        <div className="relative flex items-center justify-center w-7 h-7 rounded-xl bg-cyan-950 border border-cyan-500/50 text-cyan-300">
          <Bot size={14} className={isPaused ? '' : 'animate-pulse text-cyan-200'} />
          {!isPaused && (
            <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          )}
        </div>

        {/* Action Details */}
        <div className="text-left">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider">
              {assignedAgent}
            </span>
            <span className="text-[9px] px-1.5 py-0.2 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-400/40">
              STEP {currentStep}/{totalSteps}
            </span>
            {isPaused && (
              <span className="text-[9px] px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-400/40 font-bold">
                PAUSED
              </span>
            )}
          </div>
          <div className="text-xs text-white font-sans font-medium truncate max-w-xs md:max-w-md">
            {currentAction}
          </div>
        </div>

        {/* Controls: Pause / Stop / Close */}
        <div className="flex items-center gap-1.5 pl-2 border-l border-cyan-500/30">
          {onPauseToggle && (
            <button
              onClick={onPauseToggle}
              className="p-1.5 rounded-lg bg-cyan-950/60 border border-cyan-500/40 text-cyan-300 hover:text-white transition-colors"
              title={isPaused ? 'Resume Workflow' : 'Pause Workflow'}
            >
              {isPaused ? <Play size={12} /> : <Pause size={12} />}
            </button>
          )}

          {onStopTask && (
            <button
              onClick={onStopTask}
              className="p-1.5 rounded-lg bg-rose-950/60 border border-rose-500/50 text-rose-300 hover:bg-rose-900/60 hover:text-white transition-colors"
              title="Emergency Stop Task"
            >
              <Square size={12} />
            </button>
          )}

          {onClose && (
            <button
              onClick={onClose}
              className="p-1 text-cyan-400/60 hover:text-white transition-colors"
              title="Minimize Overlay"
            >
              <X size={13} />
            </button>
          )}
        </div>
      </motion.aside>
    </AnimatePresence>
  );
}
