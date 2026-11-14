# CHANGELOG — PROJECT J.A.R.V.I.S.

## [0.9.0] - 2026-11-13 — PROJECT J.A.R.V.I.S. MARK IX
### Transformed
- **Zero-Churn GPU Matrix Transforms in Three.js**: Completely eliminated per-frame CPU vertex loops updating GPU buffers (240 buffer uploads/sec -> 0 bytes/frame). Saved >350 MB RAM and eliminated iGPU memory thrashing on Windows 11 Home (Intel Core i5, 8 GB RAM).
- **Sub-Second Voice AI Pipeline (<600ms Latency)**: Replaced blocking synchronous HTTP requests with WebSocket streaming (`/ws/chat`), incremental sentence-level speech chunking via Web Speech API queue, and reduced silence detection from 1,100ms to 480ms.
- **Specialist Neural Agent Squad with Real Intelligence**: Replaced mock dictionaries with live Gemini neural synthesis across ORACLE (deep technical dossiers), ATLAS (git/testing execution), NEXUS (commercial viability & risk modeling), ATHENA (Socratic first-principles reasoning), and ECHO (executive comms).
- **Layered Long-Term Memory Engine**: Automated fact/preference/directive extraction into SQLite with FTS5 search and prompt injection across multi-turn sessions.
- **Holographic Command HUD Navigation Drawer**: Slide-in glassmorphic drawer overlaying the 3D core without unmounting the Three.js canvas; instant access to Projects, Memory, Agents, Automations, Tasks, Evolution, and Settings via UI pills or voice triggers.
- **Adaptive Performance Governor**: Three hardware performance tiers (`eco`, `balanced`, `turbo`) for dynamic memory and particle scaling.
- **Master Technical Specification PDF**: Generated comprehensive multi-page reference document `JARVIS_MARK_IX_MASTER_SPECIFICATION_AND_AUDIT.pdf`.

## [0.8.0] - 2026-11-12 — PROJECT J.A.R.V.I.S. MARK VIII
### Added
- **Visual Prismatic Particle Caustics**: 14 harmonic caustic petal lobes, fine striations, chromatic dispersion, 25-point diamond core, and tight specular bloom threshold (0.76).
- **Direct Windows Native Laptop Control**: Native Win32 ctypes keystroke volume adjustments (0.17ms), lock workstation, Start Menu cache, and downloads categorization.
- **Antigravity IDE Bridge**: Dedicated launcher loading `f:\Work\Jarvis- Hero` directly into Antigravity IDE on voice command.
- **Multi-Turn Conversational Memory**: 10-turn message history serialization passed into official google.genai SDK.

## [0.2.0] - 2026-11-09
### Added
- **Mission Control Dashboard**: Futuristic personal command centre with real-time telemetry, agent modules, and power profile controls.
- **3D Holographic Particle Core**: Three.js WebGL particle sphere responsive to core state (`idle`, `listening`, `thinking`, `executing`, `speaking`, `warning`, `offline`) and hand position.
- **Hand Tracking & Gesture Engine**: Privacy-first webcam gesture interaction with instant stream teardown and local in-memory frame processing.
- **Personality 2.0 & British Humour Engine**: British masculine persona with dry wit, situational quips, and 10 dynamic modes (Casual, British Assistant, Focus, Developer, Business, Study, Mentor, Serious, Quiet, Security).
- **JIEE (JARVIS Intelligence Evaluation Engine)**: Automatic mismatch analysis and response auto-pivot when user issues corrections ("That's not what I meant", "You missed the point").
- **JDI (JARVIS Development Intelligence) & Evolution Centre**: Real codebase static analysis auditor, structured Antigravity prompt generator, and artifact exporter (`data/evolution/`).
- **Sentinel Cybersecurity Engine**: Real-time URL reputation analysis for phishing, typosquatting, raw IP hosts, high-abuse TLDs, and scam/prompt-injection detection.
- **Hardware Performance & Thermal Governor**: Dynamic load-based throttling for Intel Core i5 and 8 GB RAM laptop (Eco, Balanced, Performance).
- **Multi-Profile System**: Owner (Rohan), Family Member (Work), and Guest isolation.
- **Automated Test Suite**: 12 comprehensive pytest unit and integration tests passing at 100%.

## [0.1.0] - 2026-11-09
### Added
- Phase 0 Environment Audit and hardware discovery.
- Tauri 2 desktop shell scaffolded with React 18, TypeScript, and Tailwind CSS.
- Python FastAPI backend with SQLite + aiosqlite and FTS5 full-text memory search.
- Google GenAI 3.0 SDK integration with interactions API and WebSocket streaming.
- Windows Credential Manager integration for secure API key storage.
