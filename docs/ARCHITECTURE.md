# PROJECT J.A.R.V.I.S. — Architecture Specification

## 1. System Topology

JARVIS is engineered as a local-first, modular desktop application running on Windows 11.

### 1.1 Desktop Frontend (`apps/desktop`)
- **Framework**: Tauri 2 + React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS with custom JARVIS palette (deep charcoal `surface-0`, slate surfaces, blue/cyan accents)
- **3D Engine**: Three.js WebGL canvas rendering a real-time reactive particle core
- **Vision/Gestures**: Local camera frame processing with gesture smoothing (`GestureEngine`)
- **State Management**: Zustand store (`useAuthStore`, `useUIStore`, `useChatStore`)

### 1.2 Backend Server (`backend/app`)
- **Framework**: FastAPI (ASGI asynchronous server on `127.0.0.1:8765`)
- **Database Engine**: SQLite with `aiosqlite` async session pool and FTS5 full-text search
- **Security & Secrets**: Windows Credential Manager (`keyring`), bcrypt password hashing, HS256 JWT sessions
- **AI Integration**: Google GenAI 3.0 SDK (`google-genai`) with interactions API (`interactions.create`) and WebSocket streaming

---

## 2. Component Subsystems

### 2.1 Persona & Humour Engine 2.0 (`backend/app/personality`)
- Maintains British persona identity, vocabulary, and dry observational wit.
- Dynamically generates system instructions based on active profile and conversation mode (`casual`, `british_assistant`, `focus`, `developer`, `business`, `study`, `mentor`, `serious`, `quiet`, `security`).

### 2.2 JIEE: JARVIS Intelligence Evaluation Engine (`backend/app/guidance/jiee.py`)
- Detects correction intent from phrases such as "That's not what I meant", "You missed the point".
- Automatically parses prior conversation context and wraps the model prompt into an introspective refinement prompt without repetitive apologizing.

### 2.3 JDI: JARVIS Development Intelligence (`backend/app/evolution`)
- `auditor.py`: Real static analysis of the JARVIS codebase.
- `prompt_generator.py`: Generates structured Antigravity prompts with Problem, Evidence, Architecture, Affected Modules, Constraints, and Rollback strategy.
- `adapter.py`: Antigravity Bridge for exporting task artifacts directly to `data/evolution/`.

### 2.4 Multi-Profile Security & Sentinel (`backend/app/security`)
- Role-based separation: Owner, Family, Guest.
- URL risk heuristics: checks for raw IP hosts, brand typosquatting, high-abuse TLDs, and scam/injection patterns.

### 2.5 Hardware & Thermal Governor (`backend/app/monitoring/governor.py`)
- Real-time telemetry via `psutil`.
- Adapts 3D particle count (800 in Eco, 1500 in Balanced, 2500 in Performance) and camera framerate to maintain thermal equilibrium on Intel Core i5 with integrated graphics.
