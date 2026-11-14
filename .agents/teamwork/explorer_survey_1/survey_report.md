# Comprehensive Backend & Subsystem Survey Report — Project J.A.R.V.I.S.

**Surveyor**: teamwork_explorer_survey_1 (Backend Subsystem Explorer)  
**Date**: 2026-11-12T01:15:00Z  
**Target Root**: `f:\Work\Jarvis- Hero`  
**Execution Environment**: Windows 11 x64, Python 3.14.4, Node.js / Vite 5.4.21, Chrome App Mode  

---

## 1. Executive Summary

This survey provides an exhaustive forensic audit of the JARVIS backend architecture, laptop controller engines, speech/voice pipeline, autonomous self-healing subsystem, testing suite, and interface boundaries.

### Key Positives:
- **FastAPI Core Architecture**: Extremely clean, modular, and fast. Uvicorn boots in <1.2s. 53 REST paths (64 HTTP endpoints) and 1 WebSocket route are configured.
- **Laptop Controller Execution**: Ultra-fast (<15ms) Windows native execution via `ctypes.windll.user32`, `psutil`, `winreg`, and `shutil`. Verified live: indexed 128 Start Menu shortcuts, battery telemetry queried in <1ms (8% charging on AC power), system memory and CPU queried in <10ms.
- **Database & FTS5**: SQLite with `aiosqlite` and `WAL` journal mode, automated FTS5 full-text search virtual tables and triggers for memories, full relational ORM models for Users, Conversations, Messages, Memories, Projects, Tasks, Reminders, Automations, Activity Logs, and Device Sessions.
- **Frontend SPA Integration**: `apps/desktop` compiles cleanly (`npm run build` completed in 21.5s with zero TypeScript or Vite errors). The compiled bundle (`dist/index.html` and `dist/assets`) is mounted by FastAPI for zero-lag local serving at `http://127.0.0.1:8765`.
- **Existing Test Suite**: 24 tests exist in `tests/backend/` and all 24 pass when `PYTHONPATH` is set.
- **Self-Healing Subsystem**: `backend/app/evolution/self_healing.py` contains a complete AST-based diagnostic and auto-patching engine that was verified live to autonomously diagnose a `SyntaxError` and successfully repair code.

### Critical Defects & Architectural Gaps Discovered:
1. **Critical AttributeError in Speech Engine (`voice_service.py` & `gemini_provider.py`)**:
   - `voice_service.py:104` calls `await gemini_provider.transcribe_audio(...)`, and line 55 calls `await gemini_provider.synthesise_speech(...)`.
   - Neither method exists on `GeminiProvider` (`backend/app/ai/gemini_provider.py`).
   - Calling `transcribe_speech()` immediately crashes with `AttributeError: 'GeminiProvider' object has no attribute 'transcribe_audio'`.
   - There is no REST or WebSocket audio upload/transcription endpoint (e.g. `POST /api/v1/voice/transcribe`).
2. **WebSocket Directive Disconnection (`conversations.py`)**:
   - In `POST /api/v1/conversations/chat`, `laptop_controller.execute_directive(message_text)` is called at line 444, providing instant laptop control (<10ms).
   - In WebSocket chat (`/api/v1/conversations/ws/chat`), which is what the desktop frontend actually uses (`Chat.tsx`), `laptop_controller.execute_directive()` is **completely omitted**. User directives ("mute", "battery", "open chrome") sent over WebSocket bypass laptop controller and are passed to Gemini, failing if offline or unauthenticated.
3. **Disconnection Between `laptop_controller` and `tool_registry` (`tools/registry.py`)**:
   - `tool_registry.py` only registers 6 developer tools (`launch_application`, `list_files`, `read_file`, `create_file`, `run_developer_command`, `scan_url_safety`).
   - None of the laptop controller features (`adjust_volume`, `get_battery_status`, `organize_downloads`, `minimize_all_windows`, `lock_workstation`, `take_screenshot`, `empty_recycle_bin`, `open_folder`) are registered in `tool_registry`. Consequently, AI agents (ATLAS, ORACLE, orchestrator) and the `POST /api/v1/tools/execute` endpoint cannot invoke laptop controller tools.
4. **Pytest Collection Failure Without Environment Variables**:
   - Running `pytest tests/` directly fails with 4 collection errors (`ModuleNotFoundError: No module named 'backend'`) because there is no `pytest.ini` or `pyproject.toml` in the project root defining `pythonpath = ["."]`.
5. **Missing Test Coverage for High-Impact Features**:
   - No automated tests for `laptop_controller.py` (volume, battery, shortcuts, downloads organizer).
   - No automated tests for `self_healing.py` (mandatory acceptance criterion for R3).
   - No automated tests for WebSocket streaming `/api/v1/conversations/ws/chat` or voice endpoints (`/api/v1/voice/speak`, `/api/v1/voice/status`).

---

## 2. Component Inventory

| Component / File Path | Lines | Size (Bytes) | Primary Responsibility | Operational Status |
|---|---|---|---|---|
| `backend/app/main.py` | 162 | 5,617 | FastAPI entry point, lifespan, CORS, SPA static mount, global exception handler, `/health` | **Working** |
| `backend/app/core/config.py` | 125 | 5,960 | Pydantic BaseSettings, directory resolution, model names, environment configuration | **Working** |
| `backend/app/core/logging_config.py` | 64 | 2,050 | Rotating file logger & colored console logging | **Working** |
| `backend/app/database/session.py` | 124 | 4,533 | SQLAlchemy async engine, aiosqlite, WAL mode, FTS5 virtual table & triggers | **Working** |
| `backend/app/models/database_models.py` | 372 | 21,814 | SQLAlchemy declarative models: User, Conversation, Message, Memory, Project, Task, Reminder, Automation, ActivityLog, etc. | **Working** |
| `backend/app/security/auth.py` | 148 | 5,080 | Passlib bcrypt password hashing, python-jose JWT token creation & verification, Windows Credential Manager keyring storage | **Working** |
| `backend/app/security/sentinel.py` | 158 | 5,505 | Heuristic URL phishing scanner, communication social engineering detector | **Working** |
| `backend/app/security/profiles.py` | 74 | 2,543 | Owner, Family, Guest profile switching & permission matrix enforcement | **Working** |
| `backend/app/tools/laptop_controller.py` | 597 | 28,871 | Master laptop execution: app launcher, 128 shortcut indexer, ctypes volume control, battery telemetry, downloads organizer, natural directive regex parser | **Working locally; Disconnected from WebSocket & ToolRegistry** |
| `backend/app/tools/app_launcher.py` | 144 | 4,593 | Strict allowlist launcher for 5 developer applications (vscode, chrome, terminal, explorer, antigravity) | **Working** |
| `backend/app/tools/command_runner.py` | 97 | 3,406 | Allowlisted subprocess runner (git, pytest, python, npm, cargo) with argument sanitization | **Working** |
| `backend/app/tools/file_ops.py` | 157 | 5,435 | Path-confined file operations with automatic `.bak` backups and disk verification | **Working** |
| `backend/app/tools/registry.py` | 157 | 6,315 | Tool registry and Level 0-4 permission enforcement engine | **Working for 6 tools; Missing laptop controller tools** |
| `backend/app/voice/voice_service.py` | 108 | 4,474 | Speech synthesis (TTS) with SAPI fallback, STT transcription, barge-in speech interruption | **TTS Working via SAPI; STT Broken (AttributeError)** |
| `backend/app/ai/gemini_provider.py` | 220 | 7,572 | Google GenAI SDK wrapper, candidate model cascading, streaming chat | **Chat working; Missing synthesise_speech & transcribe_audio** |
| `backend/app/ai/router.py` | 170 | 5,960 | AI query router between cloud Gemini and local Ollama | **Working** |
| `backend/app/personality/persona.py` | 148 | 5,647 | PersonaEngine 2.0 system prompt builder across 7 assistant modes | **Working** |
| `backend/app/personality/humour.py` | 92 | 3,318 | Dry British wit quip generator | **Working** |
| `backend/app/guidance/jiee.py` | 82 | 2,892 | JARVIS Introspective Evaluation Engine (detects user correction intent & formulates mismatch pivot) | **Working** |
| `backend/app/evolution/self_healing.py` | 464 | 18,614 | AST traceback parser, patch formulator, backup manager, test verifier, syntax sweeper | **Working logic; Needs test coverage** |
| `backend/app/evolution/auditor.py` | 147 | 5,615 | Static code auditor checking file lengths, todo items, security risks | **Working** |
| `backend/app/evolution/prompt_generator.py` | 64 | 2,386 | Antigravity markdown task specification generator | **Working** |
| `backend/app/monitoring/system_monitor.py` | 142 | 5,583 | Background telemetry gathering (CPU, RAM, Disk, Process metrics, connectivity) | **Working** |
| `backend/app/monitoring/governor.py` | 96 | 3,422 | Hardware performance & thermal governor (eco, balanced, performance) | **Working** |
| `backend/app/tasks/task_engine.py` | 98 | 3,488 | State machine for tasks (created, planning, running, completed, etc.) | **Working** |
| `backend/app/tasks/verification.py` | 84 | 3,143 | Deterministic verification engine for file existence, process running, exit codes | **Working** |
| `backend/app/tasks/reminders.py` | 87 | 3,016 | Smart reminder management and daily tactical briefing generation | **Working** |
| `backend/app/agents/orchestrator.py` | 92 | 3,259 | Specialist agent dispatch coordinator (ATLAS, ORACLE, NEXUS, ATHENA, ECHO) | **Working** |
| `backend/app/agents/atlas.py` | 88 | 3,163 | Specialist developer agent for git, file inspections, and build status | **Working** |
| `backend/app/agents/oracle.py` | 46 | 1,586 | Specialist research agent | **Working** |
| `backend/app/api/v1/endpoints/conversations.py` | 528 | 19,209 | Conversation CRUD, WebSocket streaming chat, direct REST chat | **Working; Gap: WebSocket missing laptop directive hook** |
| `backend/app/api/v1/endpoints/voice.py` | 79 | 2,876 | Voice endpoints: `/status`, `/interrupt`, `/speak` | **Working for speak/interrupt; Missing /transcribe** |

---

## 3. Feature Status & Verification Against Acceptance Criteria

### R1. Subsystem Audit and Defect Remediation
- **FastAPI Endpoints**: 53 REST paths, 64 HTTP methods, 1 WebSocket route. All endpoints handle parameters with Pydantic validation.
- **Global Error Handling**: `app.exception_handler(Exception)` catches unhandled errors and returns JSON 500 without crashing the server.
- **Defects Identified**:
  - `voice_service.transcribe_speech()` raises `AttributeError: 'GeminiProvider' object has no attribute 'transcribe_audio'`.
  - `voice_service.synthesize_british_speech()` fails on Gemini TTS attempt due to missing `synthesise_speech`, then succeeds on SAPI fallback.
  - WebSocket `/ws/chat` does not evaluate laptop control directives.

### R2. Conversational Intelligence and Vocal Interaction
- **Speech Synthesis (TTS)**: `POST /api/v1/voice/speak` produces valid WAV bytes via Windows SAPI fallback (`SAPI.SpVoice`). Tested directly: generates 195,584 bytes of clean WAV audio.
- **Barge-in Interruption**: `POST /api/v1/voice/interrupt` successfully resets `is_speaking = False` and cancels active playback task.
- **Speech-to-Text (STT)**: Broken at backend level due to missing `transcribe_audio` method on `GeminiProvider`. Desktop frontend currently falls back to browser `webkitSpeechRecognition`.

### R3. Autonomous Self-Code Healing and Maintenance
- **SelfHealingEngine**: Contains `diagnose_traceback`, `formulate_patch`, `apply_patch`, `rollback`, `verify_patch`, and `diagnose_and_repair`.
- **Verification Performed**: Created a test script injecting a `SyntaxError` (missing colon on `def broken_fn()`). `SelfHealingEngine` correctly parsed the traceback, formulated an AST-safe patch appending `:`, applied the patch, verified syntax, and returned success in 3.4ms.
- **Defect**: No automated test in `tests/` currently exercises this functionality.

### R4. Starburst Visuals and Desktop Interface Polish
- **Frontend Compilation**: `apps/desktop` compiles cleanly via `npm run build` with zero errors.
- **FastAPI Serving**: `FRONTEND_DIST` is mounted at `/assets` and `/{full_path:path}` serves `index.html`.
- **Launcher Scripts**: `scripts/start_jarvis.ps1` boots backend and launches Chrome in `--app=http://127.0.0.1:8765` mode.

### R5. Comprehensive PRD and Documentation Single PDF
- **ReportLab**: `reportlab 4.4.10` is installed and ready in Python environment for single-PDF generation.

---

## 4. Root Causes of Defects

### Defect 1: AttributeError in `VoiceService.transcribe_speech`
- **Location**: `backend/app/voice/voice_service.py:104`
- **Code**:
  ```python
  async def transcribe_speech(self, audio_data: bytes, mime_type: str = "audio/wav") -> str | None:
      return await gemini_provider.transcribe_audio(audio_data=audio_data, mime_type=mime_type)
  ```
- **Root Cause**: `gemini_provider.py` does not define `transcribe_audio` or `synthesise_speech`.
- **Fix**: Implement `transcribe_audio` in `gemini_provider.py` using `google-genai` audio input (`client.models.generate_content`) or fallback to `SpeechRecognition` library (which is already installed in the pip environment). Also implement `synthesise_speech` using `edge-tts` (already installed: `edge-tts 7.3.1`) or Gemini TTS.

### Defect 2: WebSocket Chat Bypasses Laptop Directives
- **Location**: `backend/app/api/v1/endpoints/conversations.py:182-356`
- **Root Cause**: The WebSocket endpoint handles user messages by directly invoking `jiee` and `gemini_provider.stream_chat()`. It never calls `laptop_controller.execute_directive(message_text)` like `POST /chat` does at line 444.
- **Impact**: When the desktop UI sends a command over WebSocket (e.g. "mute", "battery", "open chrome"), it is ignored by the laptop controller and routed to Gemini chat.
- **Fix**: In `websocket_chat`, before streaming AI responses, check `directive_res = laptop_controller.execute_directive(message_text)`. If matched, stream the result as a delta, emit `tool_activity`, and complete immediately with zero latency (<10ms).

### Defect 3: Missing Laptop Control Tools in `ToolRegistry`
- **Location**: `backend/app/tools/registry.py:40-89`
- **Root Cause**: `ToolRegistry` only exposes 6 file/command tools. It has no bindings to `laptop_controller` methods (`adjust_volume`, `get_battery_status`, `organize_downloads`, `minimize_all_windows`, `lock_workstation`, `take_screenshot`, `empty_recycle_bin`).
- **Fix**: Register `laptop_controller` methods in `ToolRegistry` with appropriate permission levels (Level 0 for telemetry, Level 1 for volume/apps, Level 2 for file operations).

### Defect 4: Pytest ModuleNotFoundError on Collection
- **Location**: Project root execution of `pytest tests/`
- **Root Cause**: Pytest does not automatically include the current working directory in `sys.path` on Windows without a configuration file.
- **Fix**: Add a `pyproject.toml` or `pytest.ini` at the project root:
  ```ini
  [pytest]
  pythonpath = .
  asyncio_mode = strict
  ```

---

## 5. Dependency List & Environment Compatibility

### Python Packages (Verified Installed in Python 3.14.4):
- **Web & Framework**: `fastapi 0.141.1`, `uvicorn 0.40.0`, `starlette 0.52.1`, `pydantic 2.13.5`, `pydantic-settings 2.15.0`, `httpx 0.28.1`, `websockets 17.1`
- **AI & Speech**: `google-genai 3.0.0`, `edge-tts 7.3.1`, `SpeechRecognition 3.17.0`, `soundfile 0.14.0`, `librosa 1.0.0`, `scipy 1.18.1`, `numpy 2.5.2`
- **Database & Storage**: `aiosqlite 0.22.1`, `SQLAlchemy 2.1.2`, `alembic 1.20.1`
- **Security & System**: `keyring 25.7.0`, `passlib 1.7.4`, `bcrypt 5.0.0`, `python-jose 3.5.0`, `psutil 7.2.2`, `pywin32 312`, `watchdog 7.1.0`
- **Documentation & PDF**: `reportlab 4.4.10`, `markdown-it-py 4.2.0`, `pillow 12.2.0`
- **Testing**: `pytest 9.1.1`, `pytest-asyncio 1.4.0`

### Windows API Integrations (Verified Operational):
- `winreg`: Resolves user shell folders (`Downloads`, `Documents`, `Desktop`, `Pictures`). Successfully resolved `G:\Downloads`.
- `ctypes.windll.user32.keybd_event`: Native virtual keystrokes for volume up (`0xAF`), volume down (`0xAE`), mute (`0xAD`).
- `ctypes.windll.user32.LockWorkStation`: Instant workstation lock.
- `SAPI.SpVoice` via `win32com.client`: Offline British voice synthesis fallback.
- `psutil.sensors_battery()`: Real-time AC/battery telemetry.

---

## 6. Technical Recommendations for Milestones

1. **Milestone 1 — Core Fixes & Integration**:
   - Create `pytest.ini` with `pythonpath = .` so all tests execute cleanly without environment overrides.
   - Implement `synthesise_speech` and `transcribe_audio` in `gemini_provider.py` with multi-tier fallbacks (Edge TTS / Gemini TTS / SAPI, and Gemini Audio / SpeechRecognition).
   - Hook `laptop_controller.execute_directive` into `websocket_chat` in `conversations.py`.
   - Register laptop controller tools in `tool_registry.py` and add dedicated controller endpoints if required.
2. **Milestone 2 — Test Suite Expansion & Autonomous Healing Verification**:
   - Add `tests/backend/test_laptop_controller.py` covering volume, battery, shortcut resolution, and directive execution.
   - Add `tests/backend/test_self_healing.py` executing an injected error test with automated self-repair verification (satisfying Acceptance Criteria R3).
   - Add `tests/backend/test_voice_and_websocket.py` testing TTS audio bytes generation and WebSocket directive messaging.
3. **Milestone 3 — Visualizer & Desktop Polish**:
   - Verify Starburst Three.js canvas in Chrome app mode with zoom (0.2x to 3.8x) and palette states.
4. **Milestone 4 — Comprehensive PRD & Single PDF Generator**:
   - Author a standalone Python script using `reportlab` to compile the complete PRD, system architecture, feature status matrix, test results, and operational runbook into a single PDF deliverable (`JARVIS_Comprehensive_PRD_and_System_Guide.pdf` >50 KB) in the project root.
