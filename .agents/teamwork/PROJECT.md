# Project: J.A.R.V.I.S. Production Personal Assistant & Comprehensive PRD System Guide

## Architecture
- Module/package boundaries, data flow, shared interfaces:
  * Backend: FastAPI application (`backend/app/main.py`), 18 modular API routers (`backend/app/api/v1/endpoints/`), static SPA serving (`/assets` and `/{full_path:path}`), root health check (`/health`), and WebSocket server (`/api/v1/conversations/ws/chat`).
  * Laptop Control: `backend/app/tools/laptop_controller.py`, native Windows bindings via ctypes, psutil, winreg, and directory organization, hooked into fast directive parser and chat stream.
  * Conversational Intelligence: `backend/app/voice/voice_service.py` with multi-tier TTS/STT via `backend/app/ai/gemini_provider.py` (neural Gemini fallback to local Windows SAPI / speech recognition), barge-in audio interruption (`/api/v1/voice/interrupt`), and live synchronized captions.
  * Autonomous Self-Code Healing: `backend/app/evolution/self_healing.py`, closed-loop AST diagnostic capture, patch generation, syntax validation, backup/rollback, and automated test verification.
  * Desktop Frontend: `apps/desktop/` (React + TypeScript + Vite + Tailwind CSS), Three.js Starburst interactive visualizer (`ParticleCore.tsx`), state-reactive palettes, Chrome app mode launcher scripts.
  * Documentation & Single PDF Deliverable: Python ReportLab 4.4.10 generator script producing `JARVIS_Comprehensive_PRD_and_System_Guide.pdf` at the project root (>50 KB).

## Feature Inventory
Every feature from the Survey phase must appear here with its assigned milestone. No feature may be left unassigned.
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | FastAPI Backend Core & Health Check | Root `/health`, CORS, lifespan startup/shutdown, error models | M1 | Survey 1, 3 |
| 2 | REST API Endpoints (53 paths / 64 methods) | All 18 route modules across auth, memory, agent, tasks, telemetry | M1 | Survey 1, 3 |
| 3 | Laptop Controller - Start Menu Resolution | Dynamic resolution of 160+ Windows Start Menu & Desktop shortcuts | M1 | Survey 1, 3 |
| 4 | Laptop Controller - Application Launching | Process launch, window focus, safe execution | M1 | Survey 1, 3 |
| 5 | Laptop Controller - Master Volume Control | Direct Windows C-level volume adjustment via ctypes keybd_event | M1 | Survey 1, 3 |
| 6 | Laptop Controller - Battery & Hardware Telemetry | psutil battery percentage, charging state, CPU/RAM/disk metrics | M1 | Survey 1, 3 |
| 7 | Laptop Controller - Downloads File Organization | Categorized routing of downloads into documents, media, code, etc. | M1 | Survey 1, 3 |
| 8 | Laptop Controller - Fast Directive Parser | Zero-lag regex/rule directive execution (`execute_directive`) | M1 | Survey 1, 3 |
| 9 | Tool Registry Integration | Register laptop controller tools in backend tool registry | M1 | Survey 1 |
| 10 | WebSocket Directives Interception | Wire `laptop_controller.execute_directive` into `/ws/chat` stream | M1 | Survey 1 |
| 11 | Desktop Frontend Compilation & Serving | Clean `npm run build` served by FastAPI at `http://127.0.0.1:8765` | M1 | Survey 1, 2, 3 |
| 12 | Favicon Asset & Layout Fixes | Add `jarvis-icon.svg`, fix AppLayout `/dashboard` route mapping | M1 | Survey 2 |
| 13 | Pytest Configuration (`pytest.ini`) | Root pytest config (`pythonpath = .`) for bare `pytest tests/` | M1 | Survey 1, 3 |
| 14 | Neural Speech Synthesis (TTS) | Implement `synthesise_speech` on GeminiProvider with SAPI fallback | M2 | Survey 1, 2 |
| 15 | Speech Transcription (STT) | Implement `transcribe_audio` on GeminiProvider with local fallback | M2 | Survey 1, 2 |
| 16 | Continuous Speech Recognition | Robust continuous STT handling in frontend with mic error recovery | M2 | Survey 2 |
| 17 | Barge-In Interruption Handling | Instant audio playback stop on new speech across frontend & backend | M2 | Survey 2 |
| 18 | Synchronized Live Caption Display | Real-time display of user speech transcripts and JARVIS vocal replies | M2 | Survey 2 |
| 19 | Autonomous Defect Interception & Traceback | Runtime traceback parsing and faulty file location in SelfHealingEngine | M3 | Survey 1, 3 |
| 20 | AST & Diff Patch Formulation | Safe AST and pattern-based patch generation for syntax/runtime bugs | M3 | Survey 3 |
| 21 | Patch Verification & Automated Rollback | Pre-commit syntax parsing, backup creation, automated test validation | M3 | Survey 3 |
| 22 | Dedicated Self-Repair Test Suite | End-to-end defect injection tests (missing colon, zero division, etc.) | M3 | Survey 3 |
| 23 | Starburst 14 Caustic Petal Lobes | Three.js harmonic parametric caustic formula (`numLobes = 14`) | M4 | Survey 2 |
| 24 | Chromatic Dispersion | Transverse amber/cyan chromatic caustic wings with diamond spine | M4 | Survey 2 |
| 25 | Diamond-White Singularity Center | 650-point dense core with icosahedron lattice and point light | M4 | Survey 2 |
| 26 | Diffraction Spikes & Stardust Particles | 8 needle diffraction rays + 6,600 floating stardust particles | M4 | Survey 2 |
| 27 | Pure #000000 Void & Zoom Clamping | Pitch black void canvas with mouse-wheel zoom clamped to 0.2x-3.8x | M4 | Survey 2 |
| 28 | Dynamic Ray Palette State Lerping | Lerp `rayColors` in render loop across idle, listening, thinking, speaking, executing | M4 | Survey 2 |
| 29 | WebGL Context Loss Recovery | Attach `webglcontextlost` and `webglcontextrestored` event handlers | M4 | Survey 2 |
| 30 | Chrome App Mode Launcher Polish | Support multi-path Chrome, `--app`, and autoplay audio flag | M4 | Survey 2 |
| 31 | Frontend Vitest Test Suite | Vitest tests for UI components and ParticleCore visualizer | M4 | Survey 2 |
| 32 | Comprehensive PRD Document Section | Full Product Requirements Document with user stories and specs | M5 | Survey 3 |
| 33 | System Architecture & Data Flow | Visual/tabular architecture diagrams, component topologies | M5 | Survey 3 |
| 34 | Component & Dependency Inventory | Complete bill of materials across backend, frontend, tools, models | M5 | Survey 3 |
| 35 | Complete Feature Status Matrix | Exhaustive table of all 41 features with planned vs operational status | M5 | Survey 3 |
| 36 | Automated Verification Test Logs | Detailed test output logs from 100% passing backend & frontend tests | M5 | Survey 3 |
| 37 | User Operational Runbook | Step-by-step installation, launch, shortcuts, troubleshooting guide | M5 | Survey 3 |
| 38 | Single Continuous PDF Generation | Python ReportLab script generating >50 KB valid PDF at root | M5 | Survey 3 |
| 39 | E2E Test Suite - Tier 1 Feature Coverage | Opaque-box tests (>=5 per feature) verifying isolation behavior | E2E | All |
| 40 | E2E Test Suite - Tier 2 Boundary/Corner Cases | Edge case and boundary tests (>=5 per feature) | E2E | All |
| 41 | E2E Test Suite - Tier 3 Pairwise Combinations | Cross-feature combination tests covering feature interactions | E2E | All |
| 42 | E2E Test Suite - Tier 4 Real-World Scenarios | End-to-end operational scenarios (voice command -> laptop action) | E2E | All |
| 43 | Adversarial Coverage Hardening (Tier 5) | White-box adversarial testing and integrity forensics | E2E | All |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Subsystem Audit & Defect Remediation | FastAPI endpoints, laptop controller tools, WebSocket chat directive interception, tool registry, pytest.ini, frontend build/serve, favicon | none | PLANNED |
| M2 | Conversational Intelligence & Vocal Interaction | GeminiProvider voice methods (synthesise_speech, transcribe_audio), continuous STT, barge-in audio interruption, live captions | M1 contracts | PLANNED |
| M3 | Autonomous Self-Code Healing & Maintenance | SelfHealingEngine verification, error interception, AST patch formulation, rollback, dedicated self-repair test verification | M1 contracts | PLANNED |
| M4 | Starburst Visuals & Desktop Interface Polish | ParticleCore.tsx dynamic ray color state transitions, WebGL context loss recovery, Chrome app mode launcher scripts, Vitest tests | M1 contracts | PLANNED |
| M5 | Comprehensive PRD Single PDF Deliverable | ReportLab Platypus PDF generator script producing JARVIS_Comprehensive_PRD_and_System_Guide.pdf (>50 KB) at project root | M1, M2, M3, M4 | PLANNED |
| E2E | E2E Testing Track | Independent opaque-box test suite (Tiers 1-4) published via TEST_READY.md, followed by 100% test pass verification and Tier 5 adversarial hardening | M1-M4 | PLANNED |

## Interface Contracts
### Backend ↔ Frontend
- REST API: `http://127.0.0.1:8765/api/v1/`
- WebSocket Chat: `ws://127.0.0.1:8765/api/v1/conversations/ws/chat` (accepts user message JSON, executes directives via `laptop_controller`, streams response tokens)
- Static Files: `GET /` and `GET /{full_path:path}` serves `apps/desktop/dist/`
- Favicon: `GET /jarvis-icon.svg` served from `apps/desktop/public/jarvis-icon.svg`
- Voice Interrupt: `POST /api/v1/voice/interrupt` halts active audio playback

### Backend ↔ GeminiProvider
- `synthesise_speech(text: str, voice_name: str) -> bytes`: returns WAV audio bytes
- `transcribe_audio(audio_data: bytes, mime_type: str) -> str`: returns transcribed text string

### Laptop Controller ↔ Core Backend
- `laptop_controller.execute_directive(text: str) -> dict | None`: executed on all incoming chat and voice messages before LLM fallback

## Code Layout
- `backend/app/main.py`: FastAPI server setup, mounts, SPA router
- `backend/app/api/v1/endpoints/`: REST and WebSocket endpoint routers
- `backend/app/tools/laptop_controller.py`: Laptop control, shortcuts, volume, battery, downloads
- `backend/app/ai/gemini_provider.py`: Gemini client, chat, voice synthesis & transcription
- `backend/app/voice/voice_service.py`: Voice service orchestration, SAPI fallback, audio endpoints
- `backend/app/evolution/self_healing.py`: SelfHealingEngine, AST diagnosis, patch formulation
- `apps/desktop/src/components/jarvis-core/ParticleCore.tsx`: Three.js Starburst interactive visualizer
- `apps/desktop/public/`: Static frontend assets (favicon, icons)
- `scripts/`: Launcher scripts (`start_jarvis.ps1`, `start_jarvis.bat`)
- `tests/`: Automated pytest test suites
- `JARVIS_Comprehensive_PRD_and_System_Guide.pdf`: Root deliverable
