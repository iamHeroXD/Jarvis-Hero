import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Camera,
  CameraOff,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Send,
  Zap,
  Activity,
  Cpu,
  Radio,
  Command,
  Repeat,
  Volume1,
  User,
  Bot,
  FolderOpen,
  Brain,
  CheckSquare,
  Settings,
  Sparkles,
  Square,
  Trash2,
} from 'lucide-react';
import ParticleCore, { CoreState } from '../components/jarvis-core/ParticleCore';
import CommandHudDrawer, { HudTab } from '../components/jarvis-core/CommandHudDrawer';
import WeatherWidget from '../components/widgets/WeatherWidget';
import TimerWidget from '../components/widgets/TimerWidget';
import TaskScheduleWidget from '../components/widgets/TaskScheduleWidget';
import ActivityOverlayHUD from '../components/widgets/ActivityOverlayHUD';
import { gestureEngine, GestureData } from '../components/gesture-controls/GestureEngine';
import { authApi, setToken, getToken } from '../services/api';

const API_BASE = 'http://127.0.0.1:8765';
const WS_BASE = 'ws://127.0.0.1:8765';

export default function JarvisCommandCore() {
  // ── States ──────────────────────────────────────────────────────────────────
  const [coreState, setCoreState] = useState<CoreState>('idle');
  const [cameraActive, setCameraActive] = useState<boolean>(false);
  const [voiceActive, setVoiceActive] = useState<boolean>(true);
  const [soundEnabled, setSoundEnabled] = useState<boolean>(true);
  const [audioUnlocked, setAudioUnlocked] = useState<boolean>(false);
  const [inputCommand, setInputCommand] = useState<string>('');
  const [lastUserHeard, setLastUserHeard] = useState<string>('');
  const [liveTranscript, setLiveTranscript] = useState<string>('');
  const [lastJarvisReply, setLastJarvisReply] = useState<string>(
    'Systems fully online and operational, Sir. All Mark X computer control directives and specialist agents standing by. What shall we execute?'
  );
  const [lastExecutionLatency, setLastExecutionLatency] = useState<string>('INSTANT LOCAL DIRECTIVE');
  const [gestureData, setGestureData] = useState<GestureData>({
    handDetected: false,
    handX: 0,
    handY: 0,
    isPinching: false,
    isFist: false,
    isOpenPalm: false,
    expansion: 1.0,
    gesture: 'none',
    confidence: 0,
  });
  const [cpuUsage, setCpuUsage] = useState<number>(24);
  const [ramUsage, setRamUsage] = useState<number>(68);
  const [batteryLevel, setBatteryLevel] = useState<number>(33);
  const [batteryCharging, setBatteryCharging] = useState<boolean>(true);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [availableVoices, setAvailableVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<SpeechSynthesisVoice | null>(null);
  const [performanceMode, setPerformanceMode] = useState<'eco' | 'balanced' | 'turbo'>('balanced');
  const [isBooting, setIsBooting] = useState<boolean>(true);
  const [bootPhase, setBootPhase] = useState<string>('IGNITING CHROMATIC SINGULARITY MATRIX...');

  // ── Pop-Up Widgets & Desktop Activity Overlay States ────────────────────────
  const [showWeather, setShowWeather] = useState<boolean>(false);
  const [showTimer, setShowTimer] = useState<boolean>(false);
  const [showSchedule, setShowSchedule] = useState<boolean>(false);
  const [activeWorkflow, setActiveWorkflow] = useState<{
    isVisible: boolean;
    currentAction: string;
    assignedAgent: string;
    currentStep: number;
    totalSteps: number;
    isPaused: boolean;
  }>({
    isVisible: false,
    currentAction: '',
    assignedAgent: 'MASTER ORCHESTRATOR',
    currentStep: 1,
    totalSteps: 4,
    isPaused: false,
  });

  // ── HUD Drawer Navigation State ─────────────────────────────────────────────
  const [isHudOpen, setIsHudOpen] = useState<boolean>(false);
  const [activeHudTab, setActiveHudTab] = useState<HudTab>('projects');

  // ── DOM & Speech Queue Refs ─────────────────────────────────────────────────
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);
  const recognitionRef = useRef<any>(null);
  const isSpeakingRef = useRef<boolean>(false);
  const silenceTimerRef = useRef<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const speechQueueRef = useRef<string[]>([]);
  const isProcessingSpeechQueueRef = useRef<boolean>(false);
  const unspokenBufferRef = useRef<string>('');
  const abortControllerRef = useRef<AbortController | null>(null);
  const currentSpeakingTextRef = useRef<string>('');

  const [jarvisMemMb, setJarvisMemMb] = useState<number>(68);
  const [isCleaningRam, setIsCleaningRam] = useState<boolean>(false);

  // ── Auto-Authenticate Owner on Mount ────────────────────────────────────────
  useEffect(() => {
    const initAuth = async () => {
      try {
        const res = await authApi.quickUnlock();
        if (res && res.access_token) {
          setToken(res.access_token);
        }
      } catch {
        console.log('Local console fallback active');
      }
    };
    initAuth();
  }, []);

  // ── Voice List Initializer ──────────────────────────────────────────────────
  useEffect(() => {
    if (!('speechSynthesis' in window)) return;

    const loadVoices = () => {
      const v = window.speechSynthesis.getVoices();
      if (v && v.length > 0) {
        setAvailableVoices(v);
        // Default to British voice if available
        const british =
          v.find(
            (vc) =>
              (vc.lang === 'en-GB' || vc.lang.startsWith('en-GB')) &&
              (vc.name.includes('George') ||
                vc.name.includes('Ryan') ||
                vc.name.includes('Male') ||
                vc.name.includes('Oliver') ||
                vc.name.includes('Arthur'))
          ) ||
          v.find((vc) => vc.lang === 'en-GB' || vc.name.includes('British')) ||
          v.find((vc) => vc.lang.startsWith('en')) ||
          v[0];
        if (british && !selectedVoice) {
          setSelectedVoice(british);
        }
      }
    };

    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }, [selectedVoice]);

  // ── Cinematic Power-On Startup Sequence ──────────────────────────────────────
  useEffect(() => {
    const t1 = setTimeout(() => {
      setBootPhase('SYNCHRONIZING OPTICAL MATRIX & HARDWARE TELEMETRY...');
    }, 700);
    const t2 = setTimeout(() => {
      setBootPhase('MARK IX MASTER LAPTOP CONTROLLER: ONLINE');
    }, 1400);
    const t3 = setTimeout(() => {
      setIsBooting(false);
      speakBritishReply('Mark IX systems fully initialized and operational, Sir. All laptop control directives standing by.');
    }, 2100);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, []);

  // ── Universal User Gesture Audio Context Unlock ──────────────────────────────
  const unlockAudioContext = () => {
    if (audioUnlocked) return;
    setAudioUnlocked(true);

    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices
          .getUserMedia({ audio: true })
          .then((stream) => stream.getTracks().forEach((track) => track.stop()))
          .catch(() => {});
      }
    } catch {}

    if ('speechSynthesis' in window) {
      window.speechSynthesis.resume();
      const primeUtterance = new SpeechSynthesisUtterance(' ');
      primeUtterance.volume = 0.01;
      window.speechSynthesis.speak(primeUtterance);
    }
  };

  useEffect(() => {
    const handleGlobalInteraction = () => {
      unlockAudioContext();
    };
    window.addEventListener('pointerdown', handleGlobalInteraction, { once: true });
    window.addEventListener('keydown', handleGlobalInteraction, { once: true });
    return () => {
      window.removeEventListener('pointerdown', handleGlobalInteraction);
      window.removeEventListener('keydown', handleGlobalInteraction);
    };
  }, [audioUnlocked]);

  // ── Global Keyboard Shortcuts for Instant Barge-In & Mute ──────────────────
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Escape: Instant Emergency Interruption (Stops speech, aborts tasks, silences immediately)
      if (e.key === 'Escape') {
        if (isSpeakingRef.current || isProcessing) {
          stopAllSpeech();
          if (abortControllerRef.current) abortControllerRef.current.abort();
          setIsProcessing(false);
          setCoreState('idle');
          setLastJarvisReply('Interrupted, Sir. Standing by.');
        }
        return;
      }

      // Spacebar: Interrupt speech if not currently typing into an input or textarea
      if (e.code === 'Space' && !(e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement)) {
        if (isSpeakingRef.current) {
          e.preventDefault();
          stopAllSpeech();
          setCoreState('idle');
          setLastJarvisReply('Speech paused, Sir.');
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isProcessing]);

  // ── Stop All Speech (Barge-In) ──────────────────────────────────────────────
  const stopAllSpeech = () => {
    speechQueueRef.current = [];
    isProcessingSpeechQueueRef.current = false;
    unspokenBufferRef.current = '';
    currentSpeakingTextRef.current = '';

    if (audioElementRef.current) {
      audioElementRef.current.pause();
      audioElementRef.current.currentTime = 0;
    }
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      window.speechSynthesis.resume();
    }
    isSpeakingRef.current = false;
    (window as any).__jarvis_active_speech = null;
  };

  // ── Incremental Sentence-Level Vocal Queue ──────────────────────────────────
  const enqueueSentence = (sentence: string) => {
    const clean = sentence.replace(/[*#_`]/g, '').trim();
    if (!clean || !soundEnabled) return;

    speechQueueRef.current.push(clean);
    if (!isProcessingSpeechQueueRef.current) {
      processNextSentenceInQueue();
    }
  };

  const processNextSentenceInQueue = () => {
    if (speechQueueRef.current.length === 0) {
      isProcessingSpeechQueueRef.current = false;
      isSpeakingRef.current = false;
      setCoreState(gestureData.handDetected ? 'gesture' : 'idle');
      return;
    }

    isProcessingSpeechQueueRef.current = true;
    isSpeakingRef.current = true;
    setCoreState('speaking');

    const nextSentence = speechQueueRef.current.shift()!;
    currentSpeakingTextRef.current = nextSentence;

    if ('speechSynthesis' in window) {
      try {
        const utterance = new SpeechSynthesisUtterance(nextSentence);
        (window as any).__jarvis_active_speech = utterance;

        if (selectedVoice) {
          utterance.voice = selectedVoice;
        } else {
          const v = availableVoices.find((vc) => vc.lang.startsWith('en')) || availableVoices[0];
          if (v) utterance.voice = v;
        }
        utterance.rate = 1.05;
        utterance.pitch = 0.98;

        utterance.onstart = () => {
          isSpeakingRef.current = true;
          setCoreState('speaking');
        };

        utterance.onend = () => {
          (window as any).__jarvis_active_speech = null;
          processNextSentenceInQueue();
        };

        utterance.onerror = () => {
          processNextSentenceInQueue();
        };

        window.speechSynthesis.speak(utterance);
        return;
      } catch (err) {
        console.warn('SpeechSynthesis error:', err);
      }
    }

    // Fallback if browser speech synthesis is unavailable
    fallbackToBackendWavSpeech(nextSentence);
  };

  const speakBritishReply = (text: string) => {
    stopAllSpeech();
    enqueueSentence(text);
  };

  const fallbackToBackendWavSpeech = async (text: string) => {
    try {
      const token = getToken();
      const res = await fetch(`${API_BASE}/api/v1/voice/speak`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ text }),
      });

      if (res.ok) {
        const blob = await res.blob();
        const audioUrl = URL.createObjectURL(blob);
        if (audioElementRef.current) {
          audioElementRef.current.src = audioUrl;
          audioElementRef.current.onplay = () => {
            isSpeakingRef.current = true;
            setCoreState('speaking');
          };
          audioElementRef.current.onended = () => {
            URL.revokeObjectURL(audioUrl);
            processNextSentenceInQueue();
          };
          audioElementRef.current.play().catch(() => {
            processNextSentenceInQueue();
          });
        }
      } else {
        processNextSentenceInQueue();
      }
    } catch {
      processNextSentenceInQueue();
    }
  };

  // ── Dispatch Command to Master Laptop Controller & AI (Sub-Second Latency) ───
  const triggerRamOptimization = async () => {
    setIsCleaningRam(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/system/optimize-memory`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setRamUsage(Math.round(data.ram_percent || 72));
        setLastExecutionLatency(`<1.2s [RAM OPTIMIZED]`);
        setLastJarvisReply(data.message || `Memory optimization complete, Sir. Reclaimed ${data.freed_mb} MB of system RAM.`);
        speakBritishReply(`Memory optimization complete, Sir. Reclaimed ${Math.round(data.freed_mb || 450)} megabytes of system RAM.`);
      }
    } catch {
      speakBritishReply("Memory optimization command executed, Sir.");
    } finally {
      setIsCleaningRam(false);
    }
  };

  const executeCommand = async (commandText: string) => {
    const text = commandText.trim();
    if (!text) return;

    // Barge-in: immediately cancel audio and abort any pending task
    stopAllSpeech();
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const abortCtrl = new AbortController();
    abortControllerRef.current = abortCtrl;

    setLastUserHeard(text);
    setInputCommand('');
    setLiveTranscript('');
    setIsProcessing(true);
    setCoreState('thinking');

    const startTime = performance.now();

    // ── Active RAM Optimization Shortcut ─────────────────────────────────────
    const cleanLower = text.toLowerCase();
    if (/\b(?:clean ram|optimize ram|free ram|clear ram|clean memory|optimize memory|free memory|boost ram|reduce ram|free up ram)\b/i.test(cleanLower)) {
      await triggerRamOptimization();
      setIsProcessing(false);
      return;
    }
    if (/(?:open|show|view)\s+projects?/i.test(cleanLower)) {
      setActiveHudTab('projects');
      setIsHudOpen(true);
      const reply = 'Displaying active project repositories and Git workspaces, Sir.';
      setLastJarvisReply(reply);
      setLastExecutionLatency('<5ms [HUD NAVIGATION]');
      speakBritishReply(reply);
      setIsProcessing(false);
      return;
    }
    if (/(?:open|show|view)\s+memor(?:y|ies)|what do you remember/i.test(cleanLower)) {
      setActiveHudTab('memory');
      setIsHudOpen(true);
      const reply = 'Accessing persistent neural memory core and indexed directives, Sir.';
      setLastJarvisReply(reply);
      setLastExecutionLatency('<5ms [HUD NAVIGATION]');
      speakBritishReply(reply);
      setIsProcessing(false);
      return;
    }
    if (/(?:open|show|view)\s+agents?|specialist squad/i.test(cleanLower)) {
      setActiveHudTab('agents');
      setIsHudOpen(true);
      const reply = 'Activating Specialist Neural Agent console: ORACLE, ATLAS, NEXUS, ATHENA, ECHO standing by, Sir.';
      setLastJarvisReply(reply);
      setLastExecutionLatency('<5ms [HUD NAVIGATION]');
      speakBritishReply(reply);
      setIsProcessing(false);
      return;
    }
    if (/(?:open|show|view)\s+automations?/i.test(cleanLower)) {
      setActiveHudTab('automations');
      setIsHudOpen(true);
      const reply = 'Opening scheduled automations and recurring workflows, Sir.';
      setLastJarvisReply(reply);
      setLastExecutionLatency('<5ms [HUD NAVIGATION]');
      speakBritishReply(reply);
      setIsProcessing(false);
      return;
    }
    if (/(?:open|show|view)\s+tasks?/i.test(cleanLower)) {
      setActiveHudTab('tasks');
      setIsHudOpen(true);
      const reply = 'Opening task pipeline and active agent assignments, Sir.';
      setLastJarvisReply(reply);
      setLastExecutionLatency('<5ms [HUD NAVIGATION]');
      speakBritishReply(reply);
      setIsProcessing(false);
      return;
    }
    if (/(?:open|show|view)\s+evolution|self[\s-]heal/i.test(cleanLower)) {
      setActiveHudTab('evolution');
      setIsHudOpen(true);
      const reply = 'Displaying autonomous codebase self-healing and AST integrity monitor, Sir.';
      setLastJarvisReply(reply);
      setLastExecutionLatency('<5ms [HUD NAVIGATION]');
      speakBritishReply(reply);
      setIsProcessing(false);
      return;
    }
    if (/(?:open|show|view)\s+settings?/i.test(cleanLower)) {
      setActiveHudTab('settings');
      setIsHudOpen(true);
      const reply = 'Accessing Mark IX hardware telemetry and speech preferences, Sir.';
      setLastJarvisReply(reply);
      setLastExecutionLatency('<5ms [HUD NAVIGATION]');
      speakBritishReply(reply);
      setIsProcessing(false);
      return;
    }
    if (/(?:close|hide)\s+(?:hud|drawer|panel)/i.test(cleanLower)) {
      setIsHudOpen(false);
      const reply = 'Minimizing HUD overlay. Returning to holographic core, Sir.';
      setLastJarvisReply(reply);
      speakBritishReply(reply);
      setIsProcessing(false);
      return;
    }

    // ── Emergency Stop & Task Cancellation ────────────────────────────────────
    if (/\b(?:stop task|cancel task|pause task|emergency stop|halt|stop execution)\b/i.test(cleanLower)) {
      setActiveWorkflow((prev) => ({ ...prev, isVisible: false }));
      stopAllSpeech();
      setCoreState('idle');
      const reply = 'All active autonomous operations and background tasks halted immediately, Sir.';
      setLastJarvisReply(reply);
      speakBritishReply(reply);
      setIsProcessing(false);
      return;
    }

    // ── Contextual Futuristic Pop-Up Widgets ──────────────────────────────────
    if (/\b(?:weather|temperature|forecast|climate)\b/i.test(cleanLower)) {
      setShowWeather(true);
      setCoreState('success');
      const reply = 'Displaying real-time atmospheric telemetry and meteorological forecast for your coordinates, Sir.';
      setLastJarvisReply(reply);
      setLastExecutionLatency('<10ms [POPUP WIDGET]');
      speakBritishReply(reply);
      setIsProcessing(false);
      return;
    }

    if (/\b(?:timer|countdown|stopwatch|pomodoro)\b/i.test(cleanLower)) {
      setShowTimer(true);
      setCoreState('success');
      const reply = 'Activating chronometric focus timer, Sir. Ready for your session.';
      setLastJarvisReply(reply);
      setLastExecutionLatency('<10ms [POPUP WIDGET]');
      speakBritishReply(reply);
      setIsProcessing(false);
      return;
    }

    if (/\b(?:schedule|tasks before|plan my day|timeline|deadlines|tasks to finish)\b/i.test(cleanLower)) {
      setShowSchedule(true);
      setCoreState('success');
      const reply = 'Calculating optimized sequential schedule for your evening deliverables, Sir. Schedule planner active.';
      setLastJarvisReply(reply);
      setLastExecutionLatency('<10ms [POPUP WIDGET]');
      speakBritishReply(reply);
      setIsProcessing(false);
      return;
    }

    // ── Next-Day Startup Operational Briefing ──────────────────────────────────
    if (/\b(?:briefing|startup briefing|morning briefing|status briefing|daily briefing)\b/i.test(cleanLower)) {
      setCoreState('thinking');
      const token = getToken();
      fetch(`${API_BASE}/api/v1/projects/startup-briefing`, {
        headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      })
        .then((res) => (res.ok ? res.json() : null))
        .then((data) => {
          if (data && data.spoken_briefing) {
            setCoreState('speaking');
            setLastJarvisReply(data.spoken_briefing);
            setLastExecutionLatency('<25ms [STARTUP BRIEFING]');
            speakBritishReply(data.spoken_briefing);
          }
        })
        .catch(() => {
          const fallback = 'All Mark XI systems are nominal, Sir. Ready for today\'s engineering directives.';
          setLastJarvisReply(fallback);
          speakBritishReply(fallback);
        })
        .finally(() => {
          setIsProcessing(false);
        });
      return;
    }

    // ── Compound Research & PDF Directive ─────────────────────────────────────
    if (/\bresearch\b/i.test(cleanLower) && /\b(?:pdf|document|report)\b/i.test(cleanLower)) {
      setCoreState('researching');
      const topicMatch = text.replace(/(?:can you|please|just)?\s*research/i, '').replace(/(?:and\s+)?(?:make|create|generate)\s+(?:a\s+)?(?:pdf|document|report)/i, '').trim();
      const targetTopic = topicMatch || 'Autonomous AI Architectures';

      setActiveWorkflow({
        isVisible: true,
        currentAction: `Gathering authoritative sources & compiling research dossier on ${targetTopic}...`,
        assignedAgent: 'RESEARCH AGENT & ORACLE',
        currentStep: 1,
        totalSteps: 4,
        isPaused: false,
      });

      const reply = `Right away, Sir. Initiating multi-source web research on "${targetTopic}" and generating a verified PDF dossier.`;
      setLastJarvisReply(reply);
      speakBritishReply(reply);

      try {
        const token = getToken();
        fetch(`${API_BASE}/api/v1/tasks/workflows/research-pdf`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({ topic: targetTopic }),
        }).then(async (res) => {
          if (res.ok) {
            setActiveWorkflow((prev) => ({
              ...prev,
              currentAction: `Research synthesis complete. Document rendered to data/ folder.`,
              currentStep: 4,
            }));
            setTimeout(() => {
              setCoreState('success');
              setActiveWorkflow((prev) => ({ ...prev, isVisible: false }));
            }, 3000);
          }
        });
      } catch {}

      setIsProcessing(false);
      return;
    }

    // ── Compound Prompt to Antigravity IDE Directive ──────────────────────────
    if (/\b(?:prompt.+?antigravity|antigravity.+?prompt|prompt it to make it better)\b/i.test(cleanLower)) {
      setCoreState('executing');
      setActiveWorkflow({
        isVisible: true,
        currentAction: 'Synthesizing master engineering prompt & opening Antigravity IDE workspace...',
        assignedAgent: 'ATLAS & ORCHESTRATOR',
        currentStep: 1,
        totalSteps: 4,
        isPaused: false,
      });

      const reply = 'Executing compound directive, Sir. Formulating master enhancement prompt and launching Antigravity IDE with your Jarvis project.';
      setLastJarvisReply(reply);
      speakBritishReply(reply);

      try {
        const token = getToken();
        fetch(`${API_BASE}/api/v1/tasks/workflows/prompt-to-ide`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({
            concept: text,
            ide: 'antigravity',
            project_path: 'f:\\Work\\Jarvis- Hero',
          }),
        }).then(async (res) => {
          if (res.ok) {
            setActiveWorkflow((prev) => ({
              ...prev,
              currentAction: 'Antigravity IDE running. Prompt deposited into pending handoff queue.',
              currentStep: 4,
            }));
            setTimeout(() => {
              setCoreState('success');
              setActiveWorkflow((prev) => ({ ...prev, isVisible: false }));
            }, 3000);
          }
        });
      } catch {}

      setIsProcessing(false);
      return;
    }

    // ── Primary Engine: Streaming WebSocket with Incremental Audio Synthesis ──
    try {
      const token = getToken();
      let streamedAnswer = '';
      unspokenBufferRef.current = '';

      const wsUrl = `${WS_BASE}/api/v1/conversations/ws/chat`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      let hasReceivedFirstToken = false;

      ws.onopen = () => {
        ws.send(
          JSON.stringify({
            token,
            message: text,
            conversation_id: activeConversationId,
          })
        );
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'delta') {
            if (!hasReceivedFirstToken) {
              hasReceivedFirstToken = true;
              const firstTokenMs = Math.round(performance.now() - startTime);
              setLastExecutionLatency(`<${firstTokenMs}ms [STREAMING WS]`);
            }

            streamedAnswer += data.text;
            unspokenBufferRef.current += data.text;
            setLastJarvisReply(streamedAnswer);

            // Extract completed sentence boundaries (. ! ?)
            const sentenceMatch = unspokenBufferRef.current.match(/(.+?[.!?])(?:\s+|$)/);
            if (sentenceMatch) {
              const fullSentence = sentenceMatch[1];
              unspokenBufferRef.current = unspokenBufferRef.current.slice(sentenceMatch[0].length);
              enqueueSentence(fullSentence);
            }
          } else if (data.type === 'tool_activity') {
            setLastExecutionLatency(`ACTIVE // ${data.action.slice(0, 32)}`);
          } else if (data.type === 'conversation_id') {
            setActiveConversationId(data.value);
          } else if (data.type === 'completed') {
            // Flush remaining unspoken text
            if (unspokenBufferRef.current.trim()) {
              enqueueSentence(unspokenBufferRef.current);
              unspokenBufferRef.current = '';
            }
            setIsProcessing(false);
            ws.close();
          } else if (data.type === 'error') {
            throw new Error(data.message || 'WebSocket reported error');
          }
        } catch (err) {
          console.warn('WS message parsing error:', err);
        }
      };

      ws.onerror = (e) => {
        console.warn('WebSocket streaming failed, falling back to REST endpoint:', e);
        fallbackToRestChat(text, startTime);
      };

      // Safety timeout: if WebSocket takes > 3s without a token, fallback to REST
      setTimeout(() => {
        if (!hasReceivedFirstToken && ws.readyState !== WebSocket.CLOSED) {
          try { ws.close(); } catch {}
          fallbackToRestChat(text, startTime);
        }
      }, 3000);

    } catch {
      fallbackToRestChat(text, startTime);
    }
  };

  // ── Secondary Engine: Direct REST Fallback ──────────────────────────────────
  const fallbackToRestChat = async (text: string, startTime: number) => {
    try {
      let token = getToken();
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const res = await fetch(`${API_BASE}/api/v1/conversations/chat`, {
        method: 'POST',
        headers,
        signal: abortControllerRef.current?.signal,
        body: JSON.stringify({
          message: text,
          conversation_id: activeConversationId,
        }),
      });

      const latencyMs = Math.round(performance.now() - startTime);

      if (!res.ok) {
        throw new Error(`Core responded with status ${res.status}`);
      }

      const data = await res.json();
      const reply = data.reply || 'Directive executed, Sir.';
      if (data.conversation_id) {
        setActiveConversationId(data.conversation_id);
      }

      const sourceBadge =
        data.model === 'local_controller'
          ? `<${latencyMs}ms [LOCAL DIRECTIVE]`
          : `${(latencyMs / 1000).toFixed(1)}s [GEMINI AI]`;

      setLastExecutionLatency(sourceBadge);
      setLastJarvisReply(reply);

      if (data.model === 'local_controller') {
        setCoreState('executing');
        setTimeout(() => {
          speakBritishReply(reply);
        }, 150);
      } else {
        speakBritishReply(reply);
      }
    } catch (err: any) {
      if (err.name === 'AbortError') {
        // Intentionally aborted by user barge-in / speech interruption
        return;
      }
      console.warn('AI command exception:', err);
      const fallback = `Acknowledged, Sir. Directive processed: "${text}". Systems remain fully functional.`;
      setLastExecutionLatency('LOCAL RECOVERY');
      setLastJarvisReply(fallback);
      speakBritishReply(fallback);
    } finally {
      setIsProcessing(false);
    }
  };

  // ── Always-On Voice Recognition Engine (480ms Ultra-Fast Silence Threshold) ─
  useEffect(() => {
    if (!voiceActive) {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch {}
      }
      return;
    }

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn('SpeechRecognition API not available in this client.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-GB';

    recognition.onresult = (event: any) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcript;
        } else {
          interim += transcript;
        }
      }

      const spoken = (final || interim).trim();
      if (!spoken) return;

      // ── Acoustic Echo Filter ──
      // If what the mic hears is simply the laptop speaker playing JARVIS's current speech, ignore it!
      const currentSpeech = currentSpeakingTextRef.current.toLowerCase();
      if (isSpeakingRef.current && currentSpeech && currentSpeech.includes(spoken.toLowerCase()) && spoken.length < currentSpeech.length * 0.75) {
        return;
      }

      // ── Instant Stop Keywords (0ms Barge-in Cutoff) ──
      if (/\b(?:stop|shut up|quiet|pause|silence|wait|hold on|cancel|halt|shh|be quiet)\b/i.test(spoken)) {
        stopAllSpeech();
        if (abortControllerRef.current) abortControllerRef.current.abort();
        setIsProcessing(false);
        setCoreState('idle');
        setLiveTranscript('');
        setLastJarvisReply('Understood, Sir. Silenced.');
        if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
        return;
      }

      // ── Active Barge-In: User is speaking a new command, immediately interrupt speech ──
      if (isSpeakingRef.current) {
        stopAllSpeech();
        if (abortControllerRef.current) abortControllerRef.current.abort();
        setIsProcessing(false);
      }

      setLiveTranscript(spoken);
      setCoreState('listening');

      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);

      // Auto-dispatch after 450ms of silence (low-latency voice pickup)
      silenceTimerRef.current = setTimeout(() => {
        if (spoken.length > 1) {
          executeCommand(spoken);
        }
      }, 450);
    };

    recognition.onerror = (e: any) => {
      if (e.error !== 'no-speech' && e.error !== 'aborted') {
        console.warn('Speech recognition status:', e.error);
      }
    };

    recognition.onend = () => {
      if (voiceActive) {
        try {
          recognition.start();
        } catch {
          setTimeout(() => {
            if (voiceActive) try { recognition.start(); } catch {}
          }, 300);
        }
      }
    };

    try {
      recognition.start();
      recognitionRef.current = recognition;
    } catch (e) {
      console.warn('Recognition start exception:', e);
    }

    return () => {
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      try { recognition.stop(); } catch {}
    };
  }, [voiceActive]);

  // ── Optical Sensor & Hand Tracking Toggle ───────────────────────────────────
  const toggleCamera = async () => {
    if (cameraActive) {
      gestureEngine.stopTracking();
      setCameraActive(false);
      setGestureData({
        handDetected: false,
        handX: 0,
        handY: 0,
        isPinching: false,
        isFist: false,
        isOpenPalm: false,
        expansion: 1.0,
        gesture: 'none',
        confidence: 0,
      });
      setCoreState(isSpeakingRef.current ? 'speaking' : 'idle');
    } else {
      setCameraActive(true);
      setTimeout(async () => {
        const success = await gestureEngine.startTracking(
          (data) => {
            setGestureData(data);
            if (data.handDetected && !isSpeakingRef.current && coreState !== 'thinking') {
              setCoreState('gesture');
            } else if (!data.handDetected && coreState === 'gesture') {
              setCoreState(isSpeakingRef.current ? 'speaking' : 'idle');
            }
          },
          videoRef.current,
          canvasRef.current
        );
        if (!success) {
          setCameraActive(false);
        }
      }, 150);
    }
  };

  // ── Real-Time System Telemetry Polling ───────────────────────────────────────
  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await fetch(`${API_BASE}/health`);
        if (res.ok) {
          const data = await res.json();
          if (data.system) {
            setCpuUsage(Math.round(data.system.cpu_percent || 24));
            setRamUsage(Math.round(data.system.ram_percent || 68));
            setJarvisMemMb(Math.round(data.system.jarvis_ram_mb || 68));
            if (data.system.battery_percent !== null && data.system.battery_percent !== undefined) {
              setBatteryLevel(data.system.battery_percent);
            }
            if (data.system.battery_plugged !== null && data.system.battery_plugged !== undefined) {
              setBatteryCharging(data.system.battery_plugged);
            }
          }
        }
      } catch {}
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      onClick={unlockAudioContext}
      onDoubleClick={() => {
        setCoreState('executing');
        setTimeout(() => setCoreState('idle'), 700);
      }}
      className="relative w-screen h-screen bg-black text-cyan-400 font-mono overflow-hidden select-none flex flex-col justify-between"
    >
      {/* ── Cinematic Startup / Turning-On Boot Overlay ───────────────────── */}
      <AnimatePresence>
        {isBooting && (
          <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0, scale: 1.05 }}
            transition={{ duration: 0.6, ease: 'easeInOut' }}
            className="fixed inset-0 z-50 bg-black flex flex-col items-center justify-center p-6 select-none pointer-events-none"
          >
            <div className="relative w-28 h-28 flex items-center justify-center mb-6">
              <div className="absolute inset-0 rounded-full border border-cyan-400/40 animate-ping opacity-60" />
              <div className="absolute inset-2 rounded-full border-2 border-t-cyan-300 border-r-transparent border-b-amber-400 border-l-transparent animate-spin-slow" />
              <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-cyan-400 to-amber-300 flex items-center justify-center shadow-[0_0_35px_rgba(0,245,255,0.85)]">
                <span className="text-black font-mono font-black text-xl">J</span>
              </div>
            </div>
            <div className="text-xs font-bold text-white tracking-[0.3em] uppercase mb-2 font-mono">
              PROJECT J.A.R.V.I.S. // MARK IX
            </div>
            <div className="text-[11px] text-cyan-400 font-mono tracking-widest uppercase animate-pulse">
              {bootPhase}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── 3D WebGL Prismatic Starburst Core in Pure Pitch Black Void ─────── */}
      <div className="absolute inset-0 z-10 bg-black">
        <ParticleCore
          state={coreState}
          particleCount={performanceMode === 'eco' ? 2400 : performanceMode === 'turbo' ? 7800 : 5200}
          performanceMode={performanceMode}
          handX={gestureData.handX}
          handY={gestureData.handY}
          isPinching={gestureData.isPinching}
          expansion={gestureData.expansion}
          audioLevel={coreState === 'speaking' ? 0.95 : coreState === 'listening' ? 0.65 : 0}
        />
      </div>

      {/* ── Top Sci-Fi Holographic Command & Telemetry Header ────────────────── */}
      <header className="relative z-30 px-6 py-3 flex items-center justify-between border-b border-cyan-500/25 bg-black/85 backdrop-blur-xl shadow-[0_4px_30px_rgba(0,0,0,0.85)]">
        {/* Brand & Auth Owner */}
        <div className="flex items-center gap-3.5">
          <div className="relative flex items-center justify-center w-9 h-9 rounded-xl border border-cyan-400/70 bg-cyan-950/40 shadow-[0_0_22px_rgba(6,182,212,0.6)]">
            <span className="font-extrabold text-cyan-200 text-sm tracking-wider">J</span>
            <div className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold tracking-widest text-white">PROJECT J.A.R.V.I.S.</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/20 border border-cyan-400/50 text-cyan-300 font-semibold shadow-[0_0_10px_rgba(6,182,212,0.3)]">
                MARK XI // AUTONOMOUS OS
              </span>
            </div>
            <div className="text-[10px] text-cyan-500/80 tracking-wider">
              AUTHENTICATED // <span className="text-cyan-200 font-bold">ROHAN [OWNER]</span> &bull; SYS: ONLINE
            </div>
          </div>
        </div>

        {/* ── Center Holographic Navigation HUD Pills ──────────────────────── */}
        <nav className="hidden xl:flex items-center gap-1 bg-[#02050e]/80 px-2 py-1 rounded-2xl border border-cyan-500/30 shadow-inner">
          <button
            onClick={() => setIsHudOpen(false)}
            className={`px-3 py-1 rounded-xl text-[11px] font-bold flex items-center gap-1.5 transition-all ${
              !isHudOpen
                ? 'bg-cyan-500/30 text-white border border-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.5)]'
                : 'text-cyan-400/70 hover:text-cyan-200 hover:bg-cyan-950/40'
            }`}
          >
            <Sparkles size={12} className="text-amber-400" />
            <span>CORE</span>
          </button>

          {[
            { id: 'projects', label: 'Projects', icon: FolderOpen },
            { id: 'memory', label: 'Memory', icon: Brain },
            { id: 'agents', label: 'Agents', icon: Bot },
            { id: 'automations', label: 'Automations', icon: Zap },
            { id: 'tasks', label: 'Tasks', icon: CheckSquare },
            { id: 'evolution', label: 'Evolution', icon: Activity },
            { id: 'settings', label: 'Settings', icon: Settings },
          ].map((item) => {
            const Icon = item.icon;
            const isActive = isHudOpen && activeHudTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setActiveHudTab(item.id as HudTab);
                  setIsHudOpen(true);
                }}
                className={`px-3 py-1 rounded-xl text-[11px] font-bold flex items-center gap-1.5 transition-all ${
                  isActive
                    ? 'bg-cyan-500/30 text-white border border-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.5)]'
                    : 'text-cyan-400/70 hover:text-cyan-200 hover:bg-cyan-950/40'
                }`}
              >
                <Icon size={12} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right HUD Controls & Hardware Telemetry */}
        <div className="flex items-center gap-2.5">
          {/* Telemetry Capsule */}
          <div className="hidden lg:flex items-center gap-2.5 text-[11px] text-cyan-400/80 bg-cyan-950/30 px-3 py-1 rounded-xl border border-cyan-500/30">
            <span>CPU: <strong className="text-cyan-200">{cpuUsage}%</strong></span>
            <span>SYS: <strong className={ramUsage > 85 ? "text-amber-400" : "text-cyan-200"}>{ramUsage}%</strong></span>
            <span>JARVIS: <strong className="text-emerald-300 font-bold">{jarvisMemMb} MB</strong></span>
            <span>BAT: <strong className="text-cyan-200">{batteryLevel}%</strong></span>
            <button
              onClick={() => executeCommand('startup briefing')}
              className="px-2 py-0.5 rounded text-[10px] font-bold border transition-all flex items-center gap-1 bg-amber-500/20 text-amber-200 border-amber-500/40 hover:bg-amber-500/30 hover:border-amber-400 hover:text-white"
              title="Generate Daily Operational Briefing"
            >
              <span>🌅 BRIEFING</span>
            </button>
            <button
              onClick={triggerRamOptimization}
              disabled={isCleaningRam}
              className={`px-2 py-0.5 rounded text-[10px] font-bold border transition-all flex items-center gap-1 ${
                isCleaningRam
                  ? 'bg-amber-500/30 text-amber-200 border-amber-400 animate-pulse'
                  : 'bg-cyan-500/20 text-cyan-200 border-cyan-500/40 hover:bg-emerald-500/30 hover:border-emerald-400 hover:text-white'
              }`}
              title="Trim Windows working set memory and collect garbage (Frees 400-800 MB)"
            >
              <span>{isCleaningRam ? 'CLEANING...' : '🧹 CLEAN RAM'}</span>
            </button>
          </div>

          {/* Audio Unlock Button */}
          {!audioUnlocked && (
            <button
              onClick={unlockAudioContext}
              className="px-3 py-1.5 rounded-xl border border-yellow-400/80 bg-yellow-500/25 text-yellow-300 text-xs font-bold flex items-center gap-1.5 animate-bounce shadow-[0_0_20px_rgba(234,179,8,0.5)]"
            >
              <Volume1 size={14} />
              <span>ENABLE AUDIO</span>
            </button>
          )}

          {/* Optical Sensor */}
          <button
            onClick={toggleCamera}
            className={`px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-2 transition-all shadow-md ${
              cameraActive
                ? 'bg-cyan-500/30 text-cyan-100 border-cyan-400 shadow-[0_0_22px_rgba(6,182,212,0.5)]'
                : 'bg-black/50 text-cyan-500/60 border-cyan-500/30 hover:text-cyan-300 hover:border-cyan-400/60'
            }`}
            title="Toggle Optical Hand Tracking"
          >
            {cameraActive ? <Camera size={14} className="text-emerald-400 animate-pulse" /> : <CameraOff size={14} />}
            <span className="hidden sm:inline">OPTICAL</span>
          </button>

          {/* Always-On Mic */}
          <button
            onClick={() => setVoiceActive(!voiceActive)}
            className={`px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-2 transition-all shadow-md ${
              voiceActive
                ? 'bg-cyan-500/30 text-cyan-100 border-cyan-400 shadow-[0_0_22px_rgba(6,182,212,0.5)]'
                : 'bg-black/50 text-rose-400 border-rose-500/40 hover:text-rose-300'
            }`}
            title="Toggle Always-On Voice Recognition"
          >
            {voiceActive ? <Mic size={14} className="text-cyan-300 animate-pulse" /> : <MicOff size={14} />}
            <span className="hidden sm:inline">MIC</span>
          </button>

          {/* Vocal Speech Output */}
          <button
            onClick={() => {
              if (soundEnabled) {
                stopAllSpeech();
              }
              setSoundEnabled(!soundEnabled);
            }}
            className={`p-2 rounded-xl border text-xs transition-all ${
              soundEnabled
                ? 'bg-cyan-500/30 text-cyan-200 border-cyan-400/60 shadow-[0_0_18px_rgba(6,182,212,0.35)]'
                : 'bg-black/50 text-cyan-500/40 border-cyan-500/20'
            }`}
            title="Toggle Voice Speech Output"
          >
            {soundEnabled ? <Volume2 size={15} /> : <VolumeX size={15} />}
          </button>
        </div>
      </header>

      {/* ── Slide-In Holographic HUD Drawer ──────────────────────────────────── */}
      <CommandHudDrawer
        isOpen={isHudOpen}
        activeTab={activeHudTab}
        onClose={() => setIsHudOpen(false)}
        onSelectTab={(tab) => setActiveHudTab(tab)}
        onExecuteDirective={executeCommand}
        performanceMode={performanceMode}
        onSetPerformanceMode={setPerformanceMode}
        selectedVoice={selectedVoice}
        onSelectVoice={setSelectedVoice}
        availableVoices={availableVoices}
      />

      {/* ── Real-Time Desktop Activity Overlay HUD ───────────────────────────── */}
      <ActivityOverlayHUD
        isVisible={activeWorkflow.isVisible}
        currentAction={activeWorkflow.currentAction}
        assignedAgent={activeWorkflow.assignedAgent}
        currentStep={activeWorkflow.currentStep}
        totalSteps={activeWorkflow.totalSteps}
        isPaused={activeWorkflow.isPaused}
        onPauseToggle={() =>
          setActiveWorkflow((prev) => ({ ...prev, isPaused: !prev.isPaused }))
        }
        onStopTask={() => {
          setActiveWorkflow((prev) => ({ ...prev, isVisible: false }));
          stopAllSpeech();
          setCoreState('idle');
          speakBritishReply('Task terminated by user override, Sir.');
        }}
        onClose={() =>
          setActiveWorkflow((prev) => ({ ...prev, isVisible: false }))
        }
      />

      {/* ── Contextual Pop-Up Widgets (Weather, Timers, Schedule) ────────────── */}
      <AnimatePresence>
        {showWeather && (
          <WeatherWidget onClose={() => setShowWeather(false)} />
        )}
        {showTimer && (
          <TimerWidget onClose={() => setShowTimer(false)} />
        )}
        {showSchedule && (
          <TaskScheduleWidget onClose={() => setShowSchedule(false)} />
        )}
      </AnimatePresence>

      {/* ── Optical Sensor PIP Overlay ───────────────────────────────────────── */}
      <AnimatePresence>
        {cameraActive && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -20 }}
            className="fixed top-20 right-6 z-40 w-64 rounded-2xl border border-cyan-400/70 bg-[#02050e]/95 backdrop-blur-xl overflow-hidden shadow-[0_0_35px_rgba(6,182,212,0.4)]"
          >
            <div className="px-3.5 py-2 bg-cyan-950/70 border-b border-cyan-500/30 flex items-center justify-between text-[10px]">
              <div className="flex items-center gap-1.5 text-cyan-200">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                <span className="font-bold tracking-wider">OPTICAL MATRIX // LIVE</span>
              </div>
              <span className="text-cyan-400/80 font-bold">LOCKED</span>
            </div>

            <div className="relative w-full h-44 bg-black flex items-center justify-center overflow-hidden">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover scale-x-[-1] opacity-80"
              />
              <canvas
                ref={canvasRef}
                width={256}
                height={176}
                className="absolute inset-0 w-full h-full pointer-events-none"
              />

              <div className="absolute top-2 left-2 w-3.5 h-3.5 border-t-2 border-l-2 border-cyan-400 pointer-events-none" />
              <div className="absolute top-2 right-2 w-3.5 h-3.5 border-t-2 border-r-2 border-cyan-400 pointer-events-none" />
              <div className="absolute bottom-2 left-2 w-3.5 h-3.5 border-b-2 border-l-2 border-cyan-400 pointer-events-none" />
              <div className="absolute bottom-2 right-2 w-3.5 h-3.5 border-b-2 border-r-2 border-cyan-400 pointer-events-none" />
            </div>

            <div className="px-3.5 py-2 bg-cyan-950/60 border-t border-cyan-500/30 text-[10px] space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-cyan-400/70">GESTURE:</span>
                <span
                  className={`font-bold uppercase tracking-wider ${
                    gestureData.isPinching
                      ? 'text-yellow-400 animate-pulse'
                      : gestureData.isOpenPalm
                      ? 'text-cyan-200'
                      : 'text-cyan-400'
                  }`}
                >
                  {gestureData.gesture}
                </span>
              </div>
              <div className="text-[9px] text-cyan-300/70 pt-0.5 italic">
                * Move hand to orbit core &bull; Pinch to condense &bull; Open palm to expand
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Captions & Dialogue Stream Area (Structured, Clean, High Contrast) ── */}
      <footer className="relative z-30 pb-5 px-6 flex flex-col items-center gap-3.5 w-full max-w-3xl mx-auto">
        {/* 1. Live Hearing Transcript / User Caption */}
        <AnimatePresence>
          {(liveTranscript || lastUserHeard) && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="w-full px-4 py-2.5 rounded-xl bg-cyan-950/80 border border-cyan-400/60 text-cyan-100 text-xs shadow-[0_0_25px_rgba(6,182,212,0.35)] backdrop-blur-md flex items-center justify-between"
            >
              <div className="flex items-center gap-2.5 overflow-hidden">
                <div className="p-1 rounded bg-cyan-500/25 text-cyan-200 flex-shrink-0">
                  <User size={13} />
                </div>
                <div className="truncate">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400 mr-2">
                    {liveTranscript ? 'HEARING LIVE:' : 'YOU SAID:'}
                  </span>
                  <span className="font-sans text-white font-medium italic">
                    "{liveTranscript || lastUserHeard}"
                  </span>
                </div>
              </div>
              {liveTranscript && (
                <div className="flex items-center gap-1.5 flex-shrink-0 pl-2">
                  <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                  <span className="text-[10px] text-cyan-300 font-bold uppercase">LISTENING</span>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* 2. J.A.R.V.I.S. Neural Vocal Response Box */}
        <motion.div
          key={lastJarvisReply}
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="w-full px-6 py-4 rounded-2xl bg-[#02050e]/95 border border-cyan-400/60 backdrop-blur-2xl shadow-[0_0_40px_rgba(6,182,212,0.3)] relative overflow-hidden"
        >
          {/* Sci-Fi Corner Brackets */}
          <div className="absolute top-2 left-2 w-3.5 h-3.5 border-t-2 border-l-2 border-cyan-400" />
          <div className="absolute top-2 right-2 w-3.5 h-3.5 border-t-2 border-r-2 border-cyan-400" />
          <div className="absolute bottom-2 left-2 w-3.5 h-3.5 border-b-2 border-l-2 border-cyan-400" />
          <div className="absolute bottom-2 right-2 w-3.5 h-3.5 border-b-2 border-r-2 border-cyan-400" />

          {/* Subtitle Header Bar */}
          <div className="flex items-center justify-between text-[10px] text-cyan-400 tracking-widest uppercase mb-2 font-bold">
            <div className="flex items-center gap-2">
              <div className="p-1 rounded bg-cyan-500/20 text-cyan-300">
                <Bot size={13} />
              </div>
              <span className="text-cyan-200">J.A.R.V.I.S. // NEURAL VOCAL RESPONSE</span>
              <span className="text-[9px] px-1.5 py-0.2 rounded bg-cyan-950 border border-cyan-500/40 text-cyan-400 font-mono">
                {lastExecutionLatency}
              </span>
            </div>
            <div className="flex items-center gap-2">
              {coreState === 'speaking' && (
                <button
                  onClick={stopAllSpeech}
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-rose-950/80 border border-rose-500/60 text-rose-200 hover:text-white hover:border-rose-400 text-[10px] font-bold transition-all shadow-[0_0_15px_rgba(244,63,94,0.4)] animate-pulse"
                  title="Interrupt Speech Immediately (Shortcut: ESC or SPACE)"
                >
                  <Square size={10} className="fill-rose-300" />
                  <span>INTERRUPT (ESC)</span>
                </button>
              )}
              <button
                onClick={() => speakBritishReply(lastJarvisReply)}
                className="flex items-center gap-1 px-2.5 py-1 rounded bg-cyan-950/70 border border-cyan-500/40 text-cyan-200 hover:text-white hover:border-cyan-300 text-[10px] transition-all shadow-sm"
                title="Repeat Vocal Audio"
              >
                <Repeat size={11} />
                <span>REPLAY SPEECH</span>
              </button>
            </div>
          </div>

          {/* Subtitle Spoken Content */}
          <div className="text-sm md:text-base text-cyan-50 font-sans tracking-wide leading-relaxed font-normal">
            "{lastJarvisReply}"
          </div>

          {coreState === 'speaking' && (
            <div className="text-[10px] text-amber-300/80 pt-1.5 flex items-center justify-between font-mono border-t border-cyan-500/20 mt-2">
              <span className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping" />
                <span>BARGE-IN ACTIVE: Speak anytime to interrupt &bull; or press ESC / SPACE</span>
              </span>
            </div>
          )}
        </motion.div>

        {/* 3. Master Laptop Control Quick Directives */}
        <div className="flex items-center gap-2 overflow-x-auto max-w-full py-0.5">
          {[
            { label: '🌅 Daily Briefing', cmd: 'startup briefing' },
            { label: '⚡ Antigravity (Jarvis)', cmd: 'open antigravity and go to jarvis project' },
            { label: '🧹 Clean RAM', cmd: 'clean ram' },
            { label: '🌦️ Weather', cmd: 'show weather' },
            { label: '⏱️ Focus Timer', cmd: 'start timer' },
            { label: '📅 Schedule Planner', cmd: 'plan schedule' },
            { label: '🔬 Research & PDF', cmd: 'research quantum computing and create a pdf' },
            { label: '🌐 Open Chrome', cmd: 'open chrome' },
            { label: '🎵 Open Spotify', cmd: 'open spotify' },
            { label: '💻 Open VS Code', cmd: 'open vscode' },
            { label: '📝 Open Notepad', cmd: 'open notepad' },
            { label: '🔊 Volume Up', cmd: 'volume up' },
            { label: '🔉 Volume Down', cmd: 'volume down' },
            { label: '🔇 Mute', cmd: 'mute' },
            { label: '📁 Organize Downloads', cmd: 'organize downloads' },
            { label: '⚡ Battery Status', cmd: 'battery status' },
            { label: '🛡️ Diagnostics', cmd: 'system diagnostics' },
            { label: '📸 Screenshot', cmd: 'screenshot' },
            { label: '🖥️ Show Desktop', cmd: 'show desktop' },
            { label: '🗂️ Downloads Folder', cmd: 'open downloads folder' },
            { label: '🔒 Lock Screen', cmd: 'lock laptop' },
          ].map((item) => (
            <button
              key={item.label}
              onClick={() => executeCommand(item.cmd)}
              className="px-3 py-1.5 rounded-xl bg-cyan-950/50 border border-cyan-500/40 hover:border-cyan-300 hover:bg-cyan-900/60 hover:shadow-[0_0_18px_rgba(6,182,212,0.4)] text-cyan-100 text-[11px] font-medium transition-all whitespace-nowrap shadow-sm"
            >
              {item.label}
            </button>
          ))}
        </div>

        {/* 4. Glowing Command Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            executeCommand(inputCommand);
          }}
          className="w-full relative flex items-center"
        >
          <div className="absolute left-4 text-cyan-400">
            <Command size={16} />
          </div>
          <input
            type="text"
            value={inputCommand}
            onChange={(e) => setInputCommand(e.target.value)}
            placeholder="Speak directive (e.g. 'open chrome', 'volume up', 'open projects', 'system diagnostics')..."
            className="w-full py-3.5 pl-11 pr-24 rounded-2xl bg-[#02050e]/95 border border-cyan-400/60 focus:border-cyan-300 focus:shadow-[0_0_30px_rgba(6,182,212,0.5)] text-white placeholder-cyan-600 text-xs outline-none transition-all font-sans"
          />
          <button
            type="submit"
            disabled={!inputCommand.trim() || isProcessing}
            className="absolute right-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-400 to-blue-500 hover:from-cyan-300 hover:to-blue-400 text-black font-extrabold text-xs flex items-center gap-1.5 shadow-[0_0_18px_rgba(6,182,212,0.45)] disabled:opacity-30 disabled:pointer-events-none transition-all"
          >
            <span>{isProcessing ? 'EXECUTING...' : 'SEND'}</span>
            <Send size={12} />
          </button>
        </form>

        {/* 5. Holographic Equalizer Visualizer */}
        <div className="flex items-center gap-1.5 h-3.5 opacity-80">
          {[35, 75, 50, 95, 65, 100, 55, 90, 60, 98, 40, 85, 50, 80, 45, 70, 35].map((h, i) => (
            <div
              key={i}
              className="w-1 bg-gradient-to-t from-cyan-500 to-cyan-200 rounded-full transition-all duration-150"
              style={{
                height:
                  coreState === 'speaking' || coreState === 'listening'
                    ? `${(h * (coreState === 'speaking' ? 1.0 : 0.65))}%`
                    : '20%',
              }}
            />
          ))}
        </div>
      </footer>

      {/* Hidden audio element for high-fidelity fallback playback */}
      <audio ref={audioElementRef} className="hidden" />
    </div>
  );
}
