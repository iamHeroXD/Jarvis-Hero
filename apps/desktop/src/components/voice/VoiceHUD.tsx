import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, Volume2, VolumeX, Sparkles, AlertCircle } from 'lucide-react';
import { voiceApi } from '../../services/api';
import { useUIStore } from '../../store';

export default function VoiceHUD() {
  const { isListening, setListening } = useUIStore();
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [speechTranscript, setSpeechTranscript] = useState('');
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const recognitionRef = useRef<any>(null);

  // Global hotkey Ctrl+Space to toggle listening
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.code === 'Space') {
        e.preventDefault();
        toggleListening();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isListening]);

  // Initialise Speech Recognition if supported
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-GB';

      recognition.onresult = (event: any) => {
        const text = Array.from(event.results)
          .map((res: any) => res[0].transcript)
          .join('');
        setSpeechTranscript(text);
      };

      recognition.onend = () => {
        setListening(false);
      };

      recognition.onerror = () => {
        setListening(false);
      };

      recognitionRef.current = recognition;
    }
  }, []);

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setListening(false);
    } else {
      // Barge-in: if JARVIS was speaking, stop audio immediately
      if (isPlayingAudio) {
        handleInterrupt();
      }
      setSpeechTranscript('');
      setListening(true);
      try {
        recognitionRef.current?.start();
      } catch {
        // May already be running
      }
    }
  };

  const handleInterrupt = async () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setIsPlayingAudio(false);
    try {
      await voiceApi.interrupt();
    } catch (e) {
      console.error('Failed to interrupt voice', e);
    }
  };

  return (
    <div className="fixed bottom-4 right-6 z-40 flex items-center gap-2">
      {/* ── Barge-In Stop Button (visible whenever speaking) ───── */}
      <AnimatePresence>
        {isPlayingAudio && (
          <motion.button
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            onClick={handleInterrupt}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 text-xs font-semibold hover:bg-rose-500/30 shadow-glow transition-all"
            title="Barge-In: Interrupt speech immediately"
          >
            <VolumeX size={14} className="animate-pulse" />
            <span>Interrupt Speech</span>
          </motion.button>
        )}
      </AnimatePresence>

      {/* ── Voice Listening Overlay Banner ─────────────────────── */}
      <AnimatePresence>
        {isListening && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="card px-3.5 py-1.5 border border-cyan-400/50 bg-surface-2/90 backdrop-blur-md flex items-center gap-2.5 shadow-glow"
          >
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span className="text-xs font-mono text-cyan-300">
              {speechTranscript || 'Listening for directive...'}
            </span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Push-To-Talk Toggle Button ─────────────────────────── */}
      <button
        onClick={toggleListening}
        className={`w-10 h-10 rounded-full flex items-center justify-center border transition-all shadow-md ${
          isListening
            ? 'bg-cyan-500 text-black border-cyan-300 shadow-glow animate-pulse'
            : 'bg-surface-2 text-text-secondary border-surface-border hover:text-accent hover:border-accent/40'
        }`}
        title="Toggle Voice (Ctrl + Space)"
      >
        {isListening ? <Mic size={18} /> : <MicOff size={18} />}
      </button>

      <audio ref={audioRef} onEnded={() => setIsPlayingAudio(false)} className="hidden" />
    </div>
  );
}
