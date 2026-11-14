# J.A.R.V.I.S. MARK XI — MASTER ARCHITECTURE SPECIFICATION

**System:** J.A.R.V.I.S. (Just A Rather Very Intelligent System)  
**Version:** MARK XI  
**Architecture Classification:** Autonomous Personal AI Operating System  
**Host Environment:** Windows 11 Home x64  
**Primary Target Profile:** Intel Core i5, 8GB System RAM, Intel UHD Graphics  
**Repository:** https://github.com/iamHeroXD/Jarvis-Hero  

---

## 1. System Topology & Tier Separation

JARVIS Mark XI implements a three-tier layered architecture designed for extreme responsiveness, non-blocking asynchronous concurrency, and hardware containment on constrained 8GB personal workstations.

```
+-----------------------------------------------------------------------------------+
|                           TIER 1: FRONTEND COMMAND HUD                            |
|  - React 18 / Vite 5 / TailwindCSS / Lucide-React                                 |
|  - Three.js WebGL Particle Core (Adaptive Bloom, 0% CPU background hibernation)   |
|  - Real-time Web Audio API Speech Synthesizer (Barge-in / ESC / SPACE hotkeys)   |
|  - Real-time Optical Gesture Tracking (MediaPipe Hands via Web Workers)           |
|  - Contextual Widgets: Schedule Planner, Chrono Timer, Weather, Desktop Overlay   |
+-----------------------------------------+-----------------------------------------+
                                          | WebSocket / HTTP JSON (Port 8765)
+-----------------------------------------v-----------------------------------------+
|                    TIER 2: BACKEND ENGINE & CANONICAL PLANES                      |
|                                                                                   |
|  +----------------------------------+  +----------------------------------------+ |
|  |  UNIFIED COMPUTER CONTROL PLANE  |  |   DATABASE-BACKED MISSION ENGINE       | |
|  |  - Windows Registry App Paths    |  |   - 14-State Machine Execution         | |
|  |  - Start Menu & Store Scanners   |  |   - ACID SQLite Task & Event Tables    | |
|  |  - Verified 5-State Verification |  |   - Idempotent Checkpoint & Recovery   | |
|  |  - Win32 EmptyWorkingSet Cleaner |  |   - Owner Approval Gatekeeper          | |
|  +----------------------------------+  +----------------------------------------+ |
|                                                                                   |
|  +----------------------------------+  +----------------------------------------+ |
|  |  VOICE & ASYNC STREAMING QUEUE   |  |   CHATGPT-TO-ANTIGRAVITY BRIDGE        | |
|  |  - google-genai SDK 3.8 Flash    |  |   - Workspace Context Inspector        | |
|  |  - Non-blocking Queue Dispatch   |  |   - Automated Engineering Prompt Gen   | |
|  |  - Sub-500ms TTFW                |  |   - Window Focus & Clipboard Handoff   | |
|  |  - en-IN / en-GB Locales         |  |   - Automated Test & Diff Verification | |
|  +----------------------------------+  +----------------------------------------+ |
|                                                                                   |
|  +----------------------------------+  +----------------------------------------+ |
|  |  RESEARCH & REPORTING ENGINE     |  |   PERSISTENT PROJECT MEMORY & BRIEFING | |
|  |  - SSRF Protection Guard         |  |   - SQLite FTS5 Full-Text Search       | |
|  |  - Multi-source DOM Parser       |  |   - Relational Projects & Decision Log | |
|  |  - Verified ReportLab PDF Gen    |  |   - Next-Day Startup Briefing Synth    | |
|  +----------------------------------+  +----------------------------------------+ |
+-----------------------------------------+-----------------------------------------+
                                          |
+-----------------------------------------v-----------------------------------------+
|                  TIER 3: NATIVE WINDOWS OS INTEGRATION LAYER                      |
|  - Windows ShellExecuteW, os.startfile, Win32 user32.dll, kernel32.dll            |
|  - psapi.dll (EmptyWorkingSet), WMI, PowerShell 7, psutil                         |
|  - File System Redirections (G:\Downloads, User Shell Folders)                    |
+-----------------------------------------------------------------------------------+
```

---

## 2. Core Subsystems

### 2.1 Unified Computer Control Plane
- **Canonical Module:** `backend/app/tools/unified_computer_controller.py`
- Replaces legacy fragmented controllers (`windows_controller.py`, `laptop_controller.py`, `app_launcher.py`) with a consolidated control plane.
- **5-State Process & Window State Verification Pipeline:**
  1. *Binary Resolution:* Dynamically verifies executable paths across verified registries, Windows Start Menu `.lnk` caches, system `PATH`, and Windows Registry (`App Paths`).
  2. *Process Creation:* Spawns target process via `subprocess.Popen` or native Win32 `ShellExecute`.
  3. *PID Verification:* Actively polls `psutil` process table up to 2.0s to confirm process is alive, responsive, and consuming valid RSS memory.
  4. *Window Enumeration:* Discovers top-level HWND using Win32 `EnumWindows` and confirms visibility via `IsWindowVisible`.
  5. *Window Foregrounding:* Calls `ShowWindow(SW_RESTORE)` and `SetForegroundWindow` to bring the application to the user's active focus.

### 2.2 Database-Backed Mission Execution Engine
- **Canonical Module:** `backend/app/tasks/mission_engine.py`
- Coordinates long-running autonomous workflows across 14 strict lifecycle states:
  `CREATED` -> `PLANNING` -> `READY` -> `RUNNING` -> `WAITING_FOR_INPUT` / `WAITING_FOR_APPROVAL` -> `VERIFYING` -> `COMPLETED`.
  Fault states include `PAUSED`, `FAILED`, `NEEDS_ATTENTION`, `CANCELLED`, and `RECOVERING`.
- All transitions and outputs are persisted within SQLite tables: `tasks`, `task_events`, and `approval_requests`.
- Enforces risk-based approval gates for actions rated `MEDIUM`, `HIGH`, or `CRITICAL`.

### 2.3 Non-Blocking Voice Streaming Bridge
- **Canonical Module:** `backend/app/ai/gemini_provider.py`
- Solves the legacy blocking iteration problem by offloading synchronous SDK network generation to a worker thread that dispatches tokens into an `asyncio.Queue` via `loop.call_soon_threadsafe`.
- Delivers tokens to client WebSockets within sub-500ms TTFW without blocking event loop concurrency.
- Supports instant cancellation on barge-in.

### 2.4 Autonomous ChatGPT-to-Antigravity Bridge
- **Canonical Module:** `backend/app/tasks/antigravity_bridge.py`
- Bridges high-level natural language instructions to IDE code operations:
  1. Inspects workspace repository structure, git branch, diff stat, and tests.
  2. Synthesizes deep, production-grade engineering instructions via Gemini.
  3. Launches Antigravity IDE and brings the project window to active focus.
  4. Injects directive markdown into `workspace/self_improvement/pending/` and syncs text to Windows Clipboard.
  5. Runs verification test commands (`pytest`, `npm test`) with bounded auto-repair loops.

### 2.5 Browser Research & SSRF Guard
- **Canonical Module:** `backend/app/tools/browser_research.py`
- Conducts multi-source internet research, extracts clean article DOM paragraphs, strips ads/scripts, and compiles high-contrast ReportLab PDF deliverables with clickable source citations.
- Enforces strict SSRF protection: blocks loopback (`127.0.0.0/8`, `::1`), private RFC1918 subnets, link-local, and cloud metadata endpoints.

### 2.6 Persistent Memory & Startup Briefing
- **Canonical Module:** `backend/app/ai/memory_manager.py` & `backend/app/api/v1/endpoints/projects.py`
- Retains semantic user facts, hardware environment variables, and architectural decisions.
- Formulates instantaneous next-day morning operational briefings highlighting active projects, recent decisions, open tasks, and system RAM availability.

---

## 3. Hardware Budget & Resource Constraints

To guarantee peak performance on 8GB host laptops:
1. **Local LLMs Prohibited:** No heavy local weights loaded into RAM or Intel UHD VRAM. All reasoning runs via high-speed cloud APIs.
2. **Win32 Active Working Set Purge:** Recovers 500–600 MB of system RAM on demand via Win32 `EmptyWorkingSet`.
3. **Particle Core GPU Throttling:** Downscales bloom render targets by 50% (saving 90MB VRAM) and terminates `requestAnimationFrame` render loops when the browser tab is hidden or minimized.
