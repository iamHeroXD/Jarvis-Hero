# J.A.R.V.I.S. MARK XI — PERSISTENT PROJECT MEMORY & STARTUP BRIEFING

**Modules:** `backend/app/ai/memory_manager.py`, `backend/app/api/v1/endpoints/projects.py`  
**Storage:** SQLite 3 with FTS5 Full-Text Virtual Tables & Relational Schema  
**Target Version:** MARK XI  

---

## 1. Relational Project & Decision Model

JARVIS Mark XI tracks engineering projects and decisions using structured tables in `data/db/jarvis.db`:
- `projects`: Tracks repository URL, local path, status (`active`, `paused`, `completed`), priority, JSON goals, and deadlines.
- `project_notes`: Records timestamped architectural notes, decisions, blockers, and milestones.
- `memories`: Stores user identity, personal preferences, hardware configuration, and explicit conversation directives.
- `memories_fts`: SQLite FTS5 virtual table synchronized via database triggers for sub-millisecond keyword and context retrieval.

---

## 2. Next-Day Startup Operational Briefing

Accessed via `GET /api/v1/projects/startup-briefing`:
1. Aggregates all active projects and their outstanding goals.
2. Retrieves recent decisions and blockers from `project_notes`.
3. Gathers open high-priority tasks from `tasks`.
4. Inspects real-time hardware telemetry (RAM %, available GB, CPU %, battery %).
5. Formulates a synthesized vocal briefing and structured JSON response:
   - Greeting ("Good morning, Rohan")
   - Summary of active projects and operations
   - Recommended first action of the day
   - Complete vocal text ready for text-to-speech audio playback

---

## 3. UI Integration

- Command HUD features a `[🌅 BRIEFING]` button in the top telemetry header.
- Quick directive button `[🌅 Daily Briefing]` triggers briefing on one click.
- Voice directive "startup briefing" or "morning briefing" delivers immediate spoken briefing.
