// API service layer — communicates with JARVIS backend
// All requests go to 127.0.0.1:8765

const BASE_URL = 'http://127.0.0.1:8765';
const API_URL = `${BASE_URL}/api/v1`;

// ── Token management ──────────────────────────────────────────────────────────

let _token: string | null = null;

export function setToken(token: string | null) {
  _token = token;
  if (token) {
    localStorage.setItem('jarvis_token', token);
  } else {
    localStorage.removeItem('jarvis_token');
  }
}

export function getToken(): string | null {
  if (_token) return _token;
  _token = localStorage.getItem('jarvis_token');
  return _token;
}

function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}


// ── HTTP helpers ──────────────────────────────────────────────────────────────

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
      ...(options.headers as Record<string, string> || {}),
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: response.statusText }));
    throw new ApiError(response.status, errorData.detail || errorData.message || 'Request failed');
  }

  return response.json();
}

function get<T>(path: string): Promise<T> {
  return request<T>(path, { method: 'GET' });
}

function post<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    body: body ? JSON.stringify(body) : undefined,
  });
}

function patch<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(path, {
    method: 'PATCH',
    body: body ? JSON.stringify(body) : undefined,
  });
}

function del<T>(path: string): Promise<T> {
  return request<T>(path, { method: 'DELETE' });
}


// ── Error type ────────────────────────────────────────────────────────────────

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}


// ── Health ────────────────────────────────────────────────────────────────────

export interface HealthStatus {
  status: string;
  version: string;
  uptime_seconds: number;
  system: SystemMetrics;
  components: Record<string, string>;
  mode: string;
}

export interface SystemMetrics {
  timestamp: string;
  cpu_percent: number;
  ram_percent: number;
  ram_used_gb: number;
  ram_total_gb: number;
  disk_percent: number;
  disk_free_gb: number;
  jarvis_cpu_percent: number;
  jarvis_ram_mb: number;
  internet_available: boolean;
}

export const healthApi = {
  get: () => get<HealthStatus>('/health'),
  metrics: () => get<SystemMetrics>('/system/metrics'),
};


// ── Auth ──────────────────────────────────────────────────────────────────────

export interface AuthToken {
  access_token: string;
  token_type: string;
  user_id: number;
  display_name: string;
  is_owner: boolean;
}

export interface SetupStatus {
  owner_configured: boolean;
  owner_username: string | null;
}

export const authApi = {
  setupStatus: () => get<SetupStatus>('/auth/setup-status'),

  setup: (username: string, displayName: string, password: string) =>
    post<AuthToken>('/auth/setup', {
      username,
      display_name: displayName,
      password,
    }),

  login: async (username: string, password: string): Promise<AuthToken> => {
    // OAuth2 form encoding
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString(),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new ApiError(response.status, err.detail || 'Login failed');
    }

    return response.json();
  },

  me: () => get<{ id: number; username: string; display_name: string; is_owner: boolean }>('/auth/me'),
  quickUnlock: () => post<AuthToken>('/auth/quick-unlock'),
};


// ── Conversations ─────────────────────────────────────────────────────────────

export interface Conversation {
  id: number;
  title: string;
  mode: string;
  is_pinned: boolean;
  ai_provider: string;
  model_name: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface Message {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  ai_provider: string | null;
  model_name: string | null;
  is_error: boolean;
  created_at: string;
}

export const conversationsApi = {
  list: () => get<Conversation[]>('/conversations'),
  create: (title?: string, mode?: string) =>
    post<Conversation>('/conversations', { title, mode }),
  getMessages: (id: number) => get<Message[]>(`/conversations/${id}/messages`),
  togglePin: (id: number) => patch<{ is_pinned: boolean }>(`/conversations/${id}/pin`),
  delete: (id: number) => del<void>(`/conversations/${id}`),
};


// ── Memory ────────────────────────────────────────────────────────────────────

export interface Memory {
  id: number;
  category: string;
  title: string;
  content: string;
  source_type: string;
  is_pinned: boolean;
  is_sensitive: boolean;
  tags: string;
  created_at: string;
  updated_at: string;
}

export const memoryApi = {
  list: (category?: string) =>
    get<Memory[]>(`/memory${category ? `?category=${category}` : ''}`),
  search: (q: string) => get<Memory[]>(`/memory/search?q=${encodeURIComponent(q)}`),
  create: (data: {
    category: string;
    title: string;
    content: string;
    tags?: string[];
    is_sensitive?: boolean;
  }) => post<Memory>('/memory', data),
  update: (id: number, data: Partial<Memory>) => patch<Memory>(`/memory/${id}`, data),
  delete: (id: number) => del<void>(`/memory/${id}`),
  deleteCategory: (category: string) => del<void>(`/memory/category/${category}`),
};


// ── Settings ──────────────────────────────────────────────────────────────────

export const settingsApi = {
  getGeminiStatus: () =>
    get<{ configured: boolean; masked_key?: string }>('/settings/ai/gemini'),
  setGeminiKey: (apiKey: string) =>
    post<{ message: string }>('/settings/ai/gemini', { api_key: apiKey }),
  testGemini: () =>
    post<{ status: string; model?: string; error?: string }>('/settings/ai/gemini/test'),
  getGeneral: () => get<Record<string, unknown>>('/settings/general'),
};


// ── Projects ──────────────────────────────────────────────────────────────────

export interface Project {
  id: number;
  user_id: number;
  name: string;
  description: string;
  status: 'active' | 'paused' | 'completed' | 'archived';
  priority: 'low' | 'medium' | 'high' | 'critical';
  repository_url: string | null;
  local_path: string | null;
  goals: string[];
  tags: string[];
  deadline: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectGitStatus {
  is_git: boolean;
  path?: string;
  branch?: string;
  has_changes?: boolean;
  status_output?: string;
  clean?: boolean;
  message?: string;
}

export interface ProjectNote {
  id: number;
  project_id: number;
  content: string;
  note_type: 'note' | 'decision' | 'blocker' | 'milestone';
  created_at: string;
}

export const projectsApi = {
  list: () => get<Project[]>('/projects'),
  get: (id: number) => get<Project>(`/projects/${id}`),
  create: (data: Partial<Project>) => post<Project>('/projects', data),
  update: (id: number, data: Partial<Project>) => patch<Project>(`/projects/${id}`, data),
  delete: (id: number) => del<void>(`/projects/${id}`),
  gitStatus: (id: number) => get<ProjectGitStatus>(`/projects/${id}/git-status`),
  listNotes: (id: number) => get<ProjectNote[]>(`/projects/${id}/notes`),
  addNote: (id: number, data: { content: string; note_type?: string }) =>
    post<ProjectNote>(`/projects/${id}/notes`, data),
};


// ── Tasks & Reminders ─────────────────────────────────────────────────────────

export interface TaskItem {
  task_id: string;
  title: string;
  description: string;
  state: 'created' | 'planning' | 'awaiting_approval' | 'running' | 'verifying' | 'completed' | 'failed' | 'needs_attention';
  assigned_agent: string;
  permission_level: number;
  requires_approval: boolean;
  plan: string[];
  evidence: string[];
  errors: string[];
  verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface ReminderItem {
  reminder_id: string;
  title: string;
  due_at: string;
  body: string;
  recurrence: string | null;
  is_completed: boolean;
  speak_aloud: boolean;
}

export const tasksApi = {
  list: () => get<TaskItem[]>('/tasks'),
  create: (data: {
    title: string;
    description?: string;
    assigned_agent?: string;
    permission_level?: number;
    requires_approval?: boolean;
    plan?: string[];
  }) => post<TaskItem>('/tasks', data),
  listReminders: () => get<ReminderItem[]>('/tasks/reminders'),
  createReminder: (data: {
    title: string;
    due_at: string;
    body?: string;
    recurrence?: string | null;
    speak_aloud?: boolean;
  }) => post<ReminderItem>('/tasks/reminders', data),
  completeReminder: (reminderId: string) =>
    patch<{ status: string; reminder_id: string }>(`/tasks/reminders/${reminderId}/complete`),
  getBriefing: () => get<{ briefing: string }>('/tasks/briefing'),
};


// ── Specialist Agents ─────────────────────────────────────────────────────────

export interface AgentInfo {
  name: string;
  role: string;
  status: string;
}

export interface AgentDispatchResult {
  agent_name: string;
  task_id: string;
  status: string;
  summary: string;
  findings: string[];
  warnings: string[];
  artifacts: Array<{ title: string; content: string; path?: string }>;
  requires_approval: boolean;
  verified: boolean;
}

export const agentsApi = {
  list: () => get<AgentInfo[]>('/agents'),
  dispatch: (data: { intent: string; parameters?: Record<string, unknown>; task_id?: string }) =>
    post<AgentDispatchResult>('/agents/dispatch', data),
};


// ── Voice Service ─────────────────────────────────────────────────────────────

export interface VoiceStatus {
  voice_enabled: boolean;
  wake_word: string;
  wake_word_active: boolean;
  is_speaking: boolean;
  tts_engine: string;
}

export const voiceApi = {
  getStatus: () => get<VoiceStatus>('/voice/status'),
  interrupt: () => post<{ status: string; is_speaking: boolean }>('/voice/interrupt'),
  speak: async (text: string): Promise<Blob | null> => {
    const res = await fetch(`${API_URL}/voice/speak`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(),
      },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) return null;
    const contentType = res.headers.get('content-type') || '';
    if (contentType.includes('audio')) {
      return res.blob();
    }
    return null;
  },
};


// ── Sentinel & Profiles & Governor ────────────────────────────────────────────

export interface SecurityAssessment {
  risk_score: number;
  risk_level: 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  reasons: string[];
  safe_action_recommended: string;
  target: string;
}

export interface GovernorStatus {
  profile: string;
  throttled: boolean;
  particle_count: number;
  camera_fps: number;
  metrics: {
    cpu_percent: number;
    ram_percent: number;
    disk_percent: number;
  };
}

export const sentinelApi = {
  checkUrl: (url: string) => post<SecurityAssessment>('/sentinel/check-url', { url }),
  scanText: (text: string) => post<SecurityAssessment>('/sentinel/scan-text', { text }),
};

export const governorApi = {
  getStatus: () => get<GovernorStatus>('/governor/status'),
  setProfile: (profile: 'eco' | 'balanced' | 'performance') =>
    post<{ message: string; state: GovernorStatus }>('/governor/set-profile', { profile }),
};

export const profilesApi = {
  current: () =>
    get<{
      active_profile: string;
      permissions: {
        profile_name: string;
        allow_os_control: boolean;
        allow_file_write: boolean;
        allow_terminal: boolean;
        allow_settings_change: boolean;
        allow_memory_read: boolean;
        allow_memory_write: boolean;
        allow_voice_admin: boolean;
      };
    }>('/profiles/current'),
  switch: (profile: 'owner' | 'family' | 'guest') =>
    post<{ message: string; active_profile: string }>('/profiles/switch', { profile }),
};


// ── Automations ───────────────────────────────────────────────────────────────

export interface AutomationItem {
  id: number;
  user_id: number;
  name: string;
  description: string;
  trigger_type: string;
  trigger_config: Record<string, unknown>;
  conditions: Array<Record<string, unknown>>;
  actions: Array<Record<string, unknown>>;
  permissions: string[];
  is_enabled: boolean;
  last_run_at: string | null;
  last_run_status: string | null;
  created_at: string;
}

export const automationsApi = {
  list: () => get<AutomationItem[]>('/automations'),
  create: (data: Partial<AutomationItem>) => post<AutomationItem>('/automations', data),
  toggle: (id: number) => patch<AutomationItem>(`/automations/${id}/toggle`),
  run: (id: number) =>
    post<{ status: string; automation_id: number; name: string; executed_at: string; details: string[] }>(
      `/automations/${id}/run`,
    ),
  delete: (id: number) => del<void>(`/automations/${id}`),
};


// ── Activity Log ──────────────────────────────────────────────────────────────

export interface ActivityItem {
  id: number;
  user_id: number | null;
  task_id: number | null;
  agent_name: string | null;
  tool_id: string | null;
  action: string;
  permission_level: number | null;
  approval_given: boolean | null;
  result: string;
  details: string;
  created_at: string;
}

export const activityApi = {
  list: (limit = 50) => get<ActivityItem[]>(`/activity?limit=${limit}`),
};


// ── System ────────────────────────────────────────────────────────────────────

export const systemApi = {
  getMetrics: () => get<SystemMetrics>('/system/metrics'),
};


// ── WebSocket Chat ────────────────────────────────────────────────────────────

export type StreamEvent =
  | { type: 'delta'; text: string }
  | { type: 'tool_activity'; action: string }
  | { type: 'completed'; message_id: number; interaction_id: string; conversation_id: number }
  | { type: 'conversation_id'; value: number }
  | { type: 'error'; message: string };

export function createChatWebSocket(
  onEvent: (event: StreamEvent) => void,
  onClose?: () => void,
): WebSocket {
  const ws = new WebSocket('ws://127.0.0.1:8765/api/v1/conversations/ws/chat');

  ws.onmessage = (e) => {
    try {
      const event = JSON.parse(e.data) as StreamEvent;
      onEvent(event);
    } catch {
      // Ignore parse errors
    }
  };

  ws.onclose = () => {
    onClose?.();
  };

  ws.onerror = (e) => {
    console.error('WebSocket error', e);
    onEvent({ type: 'error', message: 'Connection lost. Reconnecting...' });
  };

  return ws;
}
