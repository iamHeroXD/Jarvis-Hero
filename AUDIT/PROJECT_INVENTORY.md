# J.A.R.V.I.S. MARK VIII — FORENSIC PROJECT INVENTORY
**Audit Date:** 2026-11-13  
**Auditor:** Principal Software Architect & Forensic Engineering Team  
**System Specification:** Windows 11 Home x64, Intel Core i5 (4 Cores), 7.92 GB RAM, Intel Integrated Graphics  
**Target Workspaces:** `f:\Work\Jarvis- Hero`

---

## 1. Executive Summary of Inventory

A complete, exhaustive file tree walk of `f:\Work\Jarvis- Hero` was conducted. The codebase consists of:
- **Backend:** 55 Python modules across FastAPI, SQLAlchemy ORM (SQLite + WAL), Google GenAI SDK, system monitoring, security profiles, tool execution engines, and AST self-healing.
- **Frontend (`apps/desktop`):** React 18, Vite 5, TypeScript, TailwindCSS, Lucide-React, Framer Motion, and Three.js WebGL with postprocessing.
- **Desktop Packaging (`src-tauri`):** Rust 1.70+ Tauri 1.5 wrapper for native Windows windowing and system tray integration.
- **Tests (`tests/`):** 14 automated test suites comprising 218 test cases across unit, challenger, boundary, and 4-tier E2E suites.
- **Scripts & Tools (`scripts/`):** PowerShell and Batch bootstrapper scripts, ReportLab PRD generator, test execution runners.

---

## 2. Exhaustive Module Directory Catalog

### 2.1 Backend Modules (`backend/app/`)

| Module Path | Files | Primary Responsibilities | Dependencies |
| :--- | :--- | :--- | :--- |
| `backend/run.py` | 1 file (32 lines) | CLI entrypoint, Uvicorn server launcher with reload flag | `uvicorn`, `config` |
| `backend/app/main.py` | 1 file (125 lines) | FastAPI application factory, CORS setup, SPA static file mounting, lifespan handler | `fastapi`, `starlette` |
| `backend/app/core/` | 3 files (220 lines) | Global configuration (`config.py`), logging setup (`logging_config.py`), directory enforcement | `pydantic-settings`, `logging` |
| `backend/app/database/` | 2 files (123 lines) | SQLite async engine, `StaticPool`, WAL mode & FTS5 initialization (`session.py`) | `sqlalchemy`, `aiosqlite` |
| `backend/app/models/` | 2 files (310 lines) | SQLAlchemy ORM database models: User, Conversation, Message, Task, Project, Memory, Profile | `sqlalchemy.orm` |
| `backend/app/ai/` | 3 files (380 lines) | Google Gemini provider (`gemini_provider.py`) using `google-genai` SDK, fallback model router (`router.py`) | `google.genai`, `asyncio` |
| `backend/app/api/v1/` | 1 file (45 lines) | Main API v1 router aggregator | `fastapi` |
| `backend/app/api/v1/endpoints/` | 19 files (2,850 lines) | REST & WebSocket endpoints: auth, conversations, voice, health, system, tools, governor, sentinel, evolution, memory, projects, automations, tasks, profiles, settings | `fastapi`, `pydantic` |
| `backend/app/tools/` | 7 files (1,450 lines) | Master Laptop Controller (`laptop_controller.py`), registry (`registry.py`, `tool_registry.py`), file ops, app launcher, command runner | `ctypes`, `psutil`, `shutil` |
| `backend/app/security/` | 4 files (460 lines) | Authentication & JWT tokens (`auth.py`), Windows Credential Manager integration, Sentinel threat detector (`sentinel.py`), Profile isolation (`profiles.py`) | `jwt`, `passlib`, `keyring` |
| `backend/app/monitoring/` | 3 files (390 lines) | Real-time hardware telemetry (`system_monitor.py`), Hardware Governor with Eco/Balanced/Performance profiles (`governor.py`) | `psutil` |
| `backend/app/voice/` | 2 files (280 lines) | Voice service, barge-in cancellation, Windows SAPI 5 WAV speech synthesis fallback (`voice_service.py`) | `pyttsx3`, `asyncio` |
| `backend/app/evolution/` | 4 files (580 lines) | Autonomous Self-Healing AST engine (`self_healing.py`), Codebase Auditor (`auditor.py`), Prompt Generator (`prompt_generator.py`) | `ast`, `pytest`, `difflib` |
| `backend/app/tasks/` | 4 files (420 lines) | Task engine lifecycle (`task_engine.py`), Reminders scheduler (`reminders.py`), Task verification engine (`verification.py`) | `asyncio`, `datetime` |
| `backend/app/agents/` | 6 files (610 lines) | Agent orchestrator (`orchestrator.py`), Atlas (coding), Oracle (research), Specialist definitions (`specialists.py`) | `pydantic` |
| `backend/app/integrations/antigravity/` | 2 files (190 lines) | Antigravity CLI and IDE adapter (`adapter.py`), workspace launch bridge | `subprocess`, `os` |
| `backend/app/personality/` | 3 files (260 lines) | Persona engine (`persona.py`) with British elegance & dry wit, Humour engine (`humour.py`) | `random` |
| `backend/app/guidance/` | 2 files (140 lines) | JIEE (Jarvis Intelligence Evolution Engine) mismatch & correction detection (`jiee.py`) | `re` |

### 2.2 Frontend Modules (`apps/desktop/src/`)

| File / Component Path | Primary Responsibilities | UI / UX Role |
| :--- | :--- | :--- |
| `src/main.tsx` | React 18 DOM mount point | Entrypoint |
| `src/App.tsx` | Application router, global authentication provider, layout switch | Routing & Shell |
| `src/pages/JarvisCommandCore.tsx` | Primary 100x holographic cockpit HUD: 3D Core, live hearing subtitles, vocal captions, quick directives, camera viewport | Main Cockpit HUD |
| `src/pages/Activity.tsx` | System activity and audit event stream | Diagnostics |
| `src/pages/Agents.tsx` | Specialist agent roster and active task dispatch | Agent Roster |
| `src/pages/Automations.tsx` | Scheduled cron routines and triggers | Automations |
| `src/pages/Chat.tsx` | Multi-turn streaming chat interface with markdown rendering | Secondary Chat |
| `src/pages/EvolutionCentre.tsx` | Self-healing AST patches, test audit log, and prompt proposals | JDI Dashboard |
| `src/pages/Login.tsx` | Password & Quick-Unlock authentication view | Auth |
| `src/pages/MemoryPage.tsx` | Long-term memory query, inspection, and deletion view | Memory CRUD |
| `src/pages/MissionControl.tsx` | High-level system dashboard | Legacy Overview |
| `src/pages/Overview.tsx` | Quick telemetry overview | Overview |
| `src/pages/Projects.tsx` | Registered development workspace status and Git trackers | Project Tracker |
| `src/pages/Settings.tsx` | Voice speed, audio device, AI model, and governor configuration | Settings |
| `src/pages/Setup.tsx` | First-run onboarding wizard | Onboarding |
| `src/pages/System.tsx` | Hardware telemetry charts (CPU, RAM, Disk, Battery) | Hardware Telemetry |
| `src/pages/Tasks.tsx` | Task engine status and verification tracking | Task Engine |
| `src/components/jarvis-core/ParticleCore.tsx` | Three.js WebGL particle sphere & 14-lobe caustic starburst renderer with UnrealBloomPass | Visual Singularity Core |
| `src/components/gesture-controls/GestureEngine.ts` | MediaPipe Hands client, pinch/open-palm/fist classifier, smoothing filter | Optical Tracking |
| `src/components/voice/VoiceHUD.tsx` | Audio waveform equalizer visualizer | Vocal HUD |
| `src/layouts/AppLayout.tsx` | Collapsible sidebar, header telemetry badges, navigation links | App Shell |
| `src/services/api.ts` | Axios client with JWT interceptor and typed endpoint methods | API Gateway |
| `src/store/index.ts` | Zustand global state store (auth, hardware, active conversation) | State Management |

### 2.3 Desktop Native Shell (`apps/desktop/src-tauri/`)

| File Path | Role |
| :--- | :--- |
| `tauri.conf.json` | Tauri configuration: window dimensions (1280x800), title "J.A.R.V.I.S.", permissions, tray icon |
| `src/main.rs` & `src/lib.rs` | Rust desktop entrypoint, window event handlers, system tray menu |
| `Cargo.toml` | Rust dependencies: `tauri 1.5`, `serde`, `serde_json` |

### 2.4 Test Suites (`tests/`)

| Test Suite Path | Cases | Subsystem Under Test | Status |
| :--- | :--- | :--- | :--- |
| `tests/backend/test_laptop_controller.py` | 53 | Master Laptop Controller direct methods, app map, folder resolution, native volume | 53/53 PASSED |
| `tests/backend/test_laptop_controller_stress.py` | 18 | High-concurrency volume adjustments, quick process kills, invalid input resilience | 18/18 PASSED |
| `tests/backend/test_challenger_m1.py` | 16 | Adversarial tool registry invocations, parameter boundaries, natural command swallowing | 14 Passed, 2 Failed |
| `tests/backend/test_database_and_auth.py` | 8 | Password hashing, JWT creation & verification, invalid tokens | 8/8 PASSED |
| `tests/backend/test_evolution_and_security.py` | 14 | Persona engine, humour generator, JIEE correction, Sentinel URL checker, Governor | 14/14 PASSED |
| `tests/backend/test_self_healing.py` | 3 | AST defect detection, missing colon patch, zero division patch, rollback on failure | 3/3 PASSED |
| `tests/backend/test_projects_automations_and_system.py` | 15 | Project CRUD, task scheduler, system monitor endpoints | 15/15 PASSED |
| `tests/backend/test_tools_agents_and_tasks.py` | 15 | Tool registry execution, agent task lifecycles, verification | 15/15 PASSED |
| `tests/e2e/test_tier1_features.py` | 35 | Core health, telemetry, directives, voice synthesis, self-healing, desktop SPA serving | 35/35 PASSED |
| `tests/e2e/test_tier2_boundaries.py` | 28 | Boundary inputs, empty strings, null literals, rapid interrupts, malformed WebSockets | 28/28 PASSED |
| `tests/e2e/test_tier3_pairwise.py` | 8 | Cross-feature pairwise interactions: Chat WS + Controller, SPA + REST, Self-heal + Tests | 7 Passed, 1 Lockup |
| `tests/e2e/test_tier4_scenarios.py` | 5 | Multi-turn user journeys: Morning Briefing, Volume Control, Barge-In, Incident Recovery | 5/5 PASSED |

---

## 3. Data Store & Configuration Files

- Database: SQLite 3 database at `data/db/jarvis.db` operating in WAL (`Write-Ahead Logging`) mode with `jarvis.db-shm` and `jarvis.db-wal`.
- Logs: Rotated log repository at `data/logs/jarvis.log`.
- Master PDF PRD Deliverable: `JARVIS_Comprehensive_PRD_and_System_Guide.pdf` (51,574 bytes, 17 sections).
- Build Artifacts: Compiled desktop assets at `apps/desktop/dist/` (HTML, CSS bundle, JS bundle, vector icon).
