import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export interface AgentCursor {
  id: string;
  name: string;
  role: string;
  color: string;
  glow: string;
  x: number;
  y: number;
  targetX: number;
  targetY: number;
  isClicking: boolean;
  isTyping: boolean;
  statusText: string;
  active: boolean;
}

interface AutonomousCursorOverlayProps {
  activeTaskId?: string | null;
  coreState?: string;
}

export default function AutonomousCursorOverlay({
  activeTaskId,
  coreState,
}: AutonomousCursorOverlayProps) {
  const [cursors, setCursors] = useState<AgentCursor[]>([
    {
      id: 'atlas',
      name: 'ATLAS',
      role: 'EXECUTOR',
      color: '#06b6d4',
      glow: 'rgba(6,182,212,0.6)',
      x: 180,
      y: 220,
      targetX: 250,
      targetY: 300,
      isClicking: false,
      isTyping: false,
      statusText: 'Standby',
      active: true,
    },
    {
      id: 'oracle',
      name: 'ORACLE',
      role: 'RESEARCHER',
      color: '#c084fc',
      glow: 'rgba(192,132,252,0.6)',
      x: 750,
      y: 190,
      targetX: 820,
      targetY: 260,
      isClicking: false,
      isTyping: false,
      statusText: 'Standby',
      active: true,
    },
    {
      id: 'sentinel',
      name: 'SENTINEL',
      role: 'STORAGE GUARDIAN',
      color: '#fbbf24',
      glow: 'rgba(251,191,36,0.6)',
      x: 450,
      y: 420,
      targetX: 520,
      targetY: 380,
      isClicking: false,
      isTyping: false,
      statusText: 'Monitoring C: Storage',
      active: true,
    },
  ]);

  // Dynamic autonomous movement & behavior loop
  useEffect(() => {
    const interval = setInterval(() => {
      setCursors((prev) =>
        prev.map((c) => {
          // If task is executing, make cursors actively work
          const isBusy = coreState === 'executing' || coreState === 'researching';
          const varianceX = isBusy ? 160 : 70;
          const varianceY = isBusy ? 120 : 50;

          const newTargetX = Math.max(
            80,
            Math.min(window.innerWidth - 120, c.targetX + (Math.random() - 0.5) * varianceX)
          );
          const newTargetY = Math.max(
            80,
            Math.min(window.innerHeight - 150, c.targetY + (Math.random() - 0.5) * varianceY)
          );

          const willClick = isBusy && Math.random() > 0.65;
          const willType = isBusy && Math.random() > 0.5;

          let newStatus = c.statusText;
          if (c.id === 'sentinel') {
            newStatus = isBusy ? 'Scanning C: Drive Sectors...' : 'C: Drive Verified [4.7 GB Free]';
          } else if (c.id === 'atlas') {
            newStatus = isBusy ? 'Executing System Task...' : 'Command Core Nominal';
          } else if (c.id === 'oracle') {
            newStatus = isBusy ? 'Indexing Multi-Source DOM...' : 'Neural Memory Synced';
          }

          return {
            ...c,
            x: c.targetX,
            y: c.targetY,
            targetX: newTargetX,
            targetY: newTargetY,
            isClicking: willClick,
            isTyping: willType,
            statusText: newStatus,
          };
        })
      );
    }, 1800);

    return () => clearInterval(interval);
  }, [coreState]);

  return (
    <div className="pointer-events-none fixed inset-0 z-40 overflow-hidden">
      {cursors.map((cursor) => (
        <motion.div
          key={cursor.id}
          animate={{
            x: cursor.targetX,
            y: cursor.targetY,
          }}
          transition={{
            type: 'spring',
            damping: 24,
            stiffness: 70,
            mass: 0.8,
          }}
          className="absolute top-0 left-0 flex flex-col items-start select-none"
        >
          {/* Custom SVG Ghost Cursor Pointer */}
          <div className="relative">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              className="drop-shadow-[0_0_8px_currentColor]"
              style={{ color: cursor.color }}
            >
              <path
                d="M3 3L10.07 19.97L12.58 12.58L19.97 10.07L3 3Z"
                fill={cursor.color}
                stroke="#000"
                strokeWidth="1.5"
                strokeLinejoin="round"
              />
            </svg>

            {/* Glowing Ripple on Virtual Click */}
            <AnimatePresence>
              {cursor.isClicking && (
                <motion.div
                  initial={{ scale: 0.3, opacity: 0.9 }}
                  animate={{ scale: 2.2, opacity: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.6, ease: 'easeOut' }}
                  className="absolute -top-2 -left-2 w-7 h-7 rounded-full border-2 pointer-events-none"
                  style={{ borderColor: cursor.color, boxShadow: `0 0 15px ${cursor.glow}` }}
                />
              )}
            </AnimatePresence>
          </div>

          {/* Agent Badge & Real-Time Action Status */}
          <motion.div
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            className="ml-4 -mt-1 px-2.5 py-0.5 rounded-lg border backdrop-blur-md text-[10px] font-mono shadow-lg flex items-center gap-1.5 whitespace-nowrap bg-black/85"
            style={{
              borderColor: cursor.color,
              boxShadow: `0 0 12px ${cursor.glow}`,
            }}
          >
            <span
              className="w-1.5 h-1.5 rounded-full animate-ping"
              style={{ backgroundColor: cursor.color }}
            />
            <span className="font-extrabold tracking-wider" style={{ color: cursor.color }}>
              {cursor.name}
            </span>
            <span className="text-gray-400 text-[9px]">// {cursor.role}</span>
            <span className="text-cyan-200/90 text-[9px] italic border-l border-gray-700 pl-1.5">
              {cursor.statusText}
            </span>
          </motion.div>
        </motion.div>
      ))}
    </div>
  );
}
