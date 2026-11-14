import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Clock, Play, Pause, RotateCcw, X, Bell } from 'lucide-react';

interface TimerWidgetProps {
  onClose: () => void;
  initialMinutes?: number;
  label?: string;
}

export default function TimerWidget({
  onClose,
  initialMinutes = 25,
  label = 'Productivity Focus Session',
}: TimerWidgetProps) {
  const [totalSeconds, setTotalSeconds] = useState<number>(initialMinutes * 60);
  const [secondsRemaining, setSecondsRemaining] = useState<number>(initialMinutes * 60);
  const [isActive, setIsActive] = useState<boolean>(true);
  const [hasFinished, setHasFinished] = useState<boolean>(false);
  const intervalRef = useRef<any>(null);

  useEffect(() => {
    if (isActive && secondsRemaining > 0) {
      intervalRef.current = setInterval(() => {
        setSecondsRemaining((prev) => {
          if (prev <= 1) {
            clearInterval(intervalRef.current);
            setIsActive(false);
            setHasFinished(true);
            triggerAudioAlarm();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isActive, secondsRemaining]);

  const triggerAudioAlarm = () => {
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioCtx) {
        const ctx = new AudioCtx();
        for (let i = 0; i < 3; i++) {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.value = 880;
          gain.gain.setValueAtTime(0.15, ctx.currentTime + i * 0.25);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.25 + 0.2);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + i * 0.25);
          osc.stop(ctx.currentTime + i * 0.25 + 0.2);
        }
      }
    } catch {}
  };

  const minutes = Math.floor(secondsRemaining / 60);
  const seconds = secondsRemaining % 60;
  const progressPercent = ((totalSeconds - secondsRemaining) / totalSeconds) * 100;

  const handleReset = () => {
    setIsActive(false);
    setHasFinished(false);
    setSecondsRemaining(totalSeconds);
  };

  const setPreset = (mins: number) => {
    setIsActive(false);
    setHasFinished(false);
    setTotalSeconds(mins * 60);
    setSecondsRemaining(mins * 60);
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, y: 20 }}
      className="fixed bottom-24 right-8 z-50 w-72 rounded-2xl bg-[#02050e]/95 border border-cyan-400/60 backdrop-blur-2xl shadow-[0_0_35px_rgba(6,182,212,0.35)] p-4 font-mono text-cyan-400 select-none"
    >
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-cyan-500/30">
        <div className="flex items-center gap-1.5 text-xs text-white font-bold">
          <Clock size={14} className="text-cyan-300" />
          <span>CHRONOMETRIC TIMER</span>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:text-rose-400 transition-colors"
          title="Close Timer"
        >
          <X size={14} />
        </button>
      </div>

      {/* Timer Label */}
      <div className="text-[11px] text-cyan-300/80 font-sans mt-2 truncate">{label}</div>

      {/* Big Digits Display */}
      <div className="py-2.5 text-center">
        <div
          className={`text-4xl font-extrabold tracking-wider ${
            hasFinished
              ? 'text-amber-400 animate-pulse'
              : isActive
              ? 'text-white'
              : 'text-cyan-200'
          }`}
        >
          {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
        </div>
        {hasFinished && (
          <div className="flex items-center justify-center gap-1 text-[11px] text-amber-300 font-bold mt-1">
            <Bell size={12} className="animate-bounce" />
            <span>SESSION COMPLETE</span>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      <div className="w-full h-1.5 bg-black/60 rounded-full overflow-hidden border border-cyan-500/30 mb-3">
        <div
          className="h-full bg-gradient-to-r from-cyan-500 to-blue-400 transition-all duration-300"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between pt-1 font-mono">
        <div className="flex items-center gap-1 text-[10px]">
          {[5, 15, 25].map((m) => (
            <button
              key={m}
              onClick={() => setPreset(m)}
              className="px-2 py-1 rounded bg-cyan-950/60 border border-cyan-500/40 text-cyan-300 hover:text-white"
            >
              {m}m
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsActive(!isActive)}
            className="p-2 rounded-xl bg-cyan-500/20 border border-cyan-400/60 text-cyan-100 hover:bg-cyan-500/30 shadow-sm transition-all"
            title={isActive ? 'Pause' : 'Start'}
          >
            {isActive ? <Pause size={13} /> : <Play size={13} />}
          </button>
          <button
            onClick={handleReset}
            className="p-2 rounded-xl bg-cyan-950/60 border border-cyan-500/40 text-cyan-300 hover:text-white transition-all"
            title="Reset"
          >
            <RotateCcw size={13} />
          </button>
        </div>
      </div>
    </motion.div>
  );
}
