# J.A.R.V.I.S. MARK XI — CHANGELOG & MIGRATION RECORD

**Release:** MARK XI (Autonomous Personal AI Operating System)  
**Baseline:** MARK X  
**Date:** November 14, 2026  

---

## Added

- **Unified Computer Control Plane (`unified_computer_controller.py`):**
  - Consolidated `windows_controller.py`, `laptop_controller.py`, and `app_launcher.py`.
  - Added dynamic Windows Start Menu and Registry `App Paths` discovery.
  - Implemented 5-state process and window verification pipeline (resolve -> spawn -> poll PID -> find HWND -> foreground focus).
  - Added Win32 `SendInput` Unicode typing and multi-key hotkey automation.
- **Database-Backed Mission Execution Engine (`mission_engine.py`):**
  - Full 14-state machine: `CREATED`, `PLANNING`, `READY`, `RUNNING`, `WAITING_FOR_INPUT`, `WAITING_FOR_APPROVAL`, `VERIFYING`, `COMPLETED`, `PAUSED`, `FAILED`, `NEEDS_ATTENTION`, `CANCELLED`, `RECOVERING`.
  - Checkpointed execution in SQLite `tasks`, `task_events`, and `approval_requests`.
  - Automatic restart recovery from last valid step.
- **Autonomous ChatGPT-to-Antigravity Bridge (`antigravity_bridge.py`):**
  - Automated workspace context inspection (git branch, diff stat, tech stack).
  - Production-grade engineering instruction synthesis via Gemini.
  - Automatic Antigravity IDE launching, window focus activation, and directive handoff injection into `.antigravity/` / `workspace/self_improvement/pending/` and Windows Clipboard.
- **SSRF Security Guard (`browser_research.py`):**
  - Added `is_ssrf_safe_url()` validating URL scheme and rejecting loopback, RFC 1918 private subnets, link-local, and metadata endpoints.
- **Next-Day Startup Operational Briefing (`projects.py`):**
  - Added `GET /api/v1/projects/startup-briefing` summarizing active projects, open decisions, pending tasks, and hardware telemetry.
  - Added `[🌅 BRIEFING]` button to Command HUD and quick directive triggers.
- **Persistent Productivity Widgets:**
  - Added `localStorage` persistence to `TaskScheduleWidget.tsx`.

## Changed

- **Non-Blocking Gemini Streaming Bridge (`gemini_provider.py`):**
  - Replaced synchronous `for chunk in stream:` iteration with a worker-thread feeding an `asyncio.Queue`, eliminating event loop blocking and accelerating TTFW to sub-500ms.
- **Command HUD Branding:**
  - Updated header branding to `MARK XI // AUTONOMOUS OS`.
- **FastAPI Routing Bug Fix:**
  - Positioned static `/startup-briefing` before dynamic `/{project_id}` to prevent 422 integer casting errors.

## Fixed

- **Startup Race Condition (`ERR_CONNECTION_REFUSED`):**
  - Removed broken `get_current_user_optional` import in `system.py`.
  - Replaced arbitrary script wait timer with active health polling loop (`curl.exe http://127.0.0.1:8765/health`).
- **RAM Bloat on 8GB Workstations:**
  - Integrated native Win32 `EmptyWorkingSet` memory cleaner recovering 500–600 MB of system RAM on demand.
  - Downscaled Three.js bloom post-processing render targets by 50% and added background tab hibernation.
