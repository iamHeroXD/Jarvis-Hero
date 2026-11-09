// Global application state using Zustand
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { SystemMetrics } from '../services/api';

// ── Auth Store ────────────────────────────────────────────────────────────────

interface AuthState {
  token: string | null;
  userId: number | null;
  displayName: string | null;
  isOwner: boolean;
  isAuthenticated: boolean;
  setAuth: (token: string, userId: number, displayName: string, isOwner: boolean) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      userId: null,
      displayName: null,
      isOwner: false,
      isAuthenticated: false,
      setAuth: (token, userId, displayName, isOwner) =>
        set({ token, userId, displayName, isOwner, isAuthenticated: true }),
      clearAuth: () =>
        set({ token: null, userId: null, displayName: null, isOwner: false, isAuthenticated: false }),
    }),
    {
      name: 'jarvis-auth',
      partialize: (state) => ({
        token: state.token,
        userId: state.userId,
        displayName: state.displayName,
        isOwner: state.isOwner,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);


// ── UI Store ──────────────────────────────────────────────────────────────────

type AssistantMode = 'casual' | 'focus' | 'developer' | 'business' | 'study' | 'serious' | 'quiet';

interface UIState {
  sidebarCollapsed: boolean;
  currentMode: AssistantMode;
  isListening: boolean;
  isVoiceActive: boolean;
  systemMetrics: SystemMetrics | null;
  backendOnline: boolean;
  internetAvailable: boolean;
  geminiAvailable: boolean;
  setSidebarCollapsed: (v: boolean) => void;
  setMode: (mode: AssistantMode) => void;
  setListening: (v: boolean) => void;
  setVoiceActive: (v: boolean) => void;
  setSystemMetrics: (m: SystemMetrics) => void;
  setBackendOnline: (v: boolean) => void;
  setInternetAvailable: (v: boolean) => void;
  setGeminiAvailable: (v: boolean) => void;
}

export const useUIStore = create<UIState>()((set) => ({
  sidebarCollapsed: false,
  currentMode: 'casual',
  isListening: false,
  isVoiceActive: false,
  systemMetrics: null,
  backendOnline: false,
  internetAvailable: true,
  geminiAvailable: false,
  setSidebarCollapsed: (v) => set({ sidebarCollapsed: v }),
  setMode: (mode) => set({ currentMode: mode }),
  setListening: (v) => set({ isListening: v }),
  setVoiceActive: (v) => set({ isVoiceActive: v }),
  setSystemMetrics: (m) => set({ systemMetrics: m }),
  setBackendOnline: (v) => set({ backendOnline: v }),
  setInternetAvailable: (v) => set({ internetAvailable: v }),
  setGeminiAvailable: (v) => set({ geminiAvailable: v }),
}));


// ── Chat Store ────────────────────────────────────────────────────────────────

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
  isError?: boolean;
  timestamp: Date;
  toolActivity?: string;
}

interface ChatState {
  messages: ChatMessage[];
  activeConversationId: number | null;
  isGenerating: boolean;
  toolActivity: string | null;
  addMessage: (msg: ChatMessage) => void;
  appendToLastMessage: (text: string) => void;
  setLastMessageComplete: () => void;
  setGenerating: (v: boolean) => void;
  setToolActivity: (action: string | null) => void;
  setActiveConversationId: (id: number | null) => void;
  clearMessages: () => void;
  setMessages: (msgs: ChatMessage[]) => void;
}

export const useChatStore = create<ChatState>()((set) => ({
  messages: [],
  activeConversationId: null,
  isGenerating: false,
  toolActivity: null,
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  appendToLastMessage: (text) =>
    set((s) => {
      const msgs = [...s.messages];
      if (msgs.length > 0) {
        const last = { ...msgs[msgs.length - 1] };
        last.content += text;
        msgs[msgs.length - 1] = last;
      }
      return { messages: msgs };
    }),
  setLastMessageComplete: () =>
    set((s) => {
      const msgs = [...s.messages];
      if (msgs.length > 0) {
        msgs[msgs.length - 1] = { ...msgs[msgs.length - 1], isStreaming: false };
      }
      return { messages: msgs };
    }),
  setGenerating: (v) => set({ isGenerating: v }),
  setToolActivity: (action) => set({ toolActivity: action }),
  setActiveConversationId: (id) => set({ activeConversationId: id }),
  clearMessages: () => set({ messages: [] }),
  setMessages: (msgs) => set({ messages: msgs }),
}));
