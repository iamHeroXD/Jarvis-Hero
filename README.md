# PROJECT J.A.R.V.I.S.
### Just A Rather Very Intelligent System — Private Personal AI Command Centre

[![Platform](https://img.shields.io/badge/Platform-Windows%2011-blue)](https://microsoft.com/windows)
[![Frontend](https://img.shields.io/badge/Frontend-Tauri%202%20%2B%20React%20%2B%20TS-cyan)](https://tauri.app)
[![Backend](https://img.shields.io/badge/Backend-Python%20FastAPI-green)](https://fastapi.tiangolo.com)
[![AI Engine](https://img.shields.io/badge/AI-Google%20Gemini%20API%20(google--genai%203.0)-purple)](https://ai.google.dev)
[![3D Engine](https://img.shields.io/badge/3D-Three.js%20Particle%20Core-orange)](https://threejs.org)

JARVIS is a private, local-first, voice-enabled personal AI assistant and computer operator engineered for desktop environments. Designed with an original Iron Man-inspired command centre aesthetic, JARVIS incorporates British persona intelligence, dry wit, real-time system monitoring, long-term memory, self-evolution intelligence (JDI), and a webcam-based hand-gesture interface.

---

## Architecture Overview

```text
                  USER
                    |
      VOICE / HANDS / TEXT INPUT
                    |
                    v
    JARVIS MISSION CONTROL (Tauri 2 + React)
        |                       |
        v                       v
 3D PARTICLE CORE       HAND TRACKING ENGINE
 (Three.js WebGL)      (Local Gesture Engine)
                    |
                    v
          JARVIS BACKEND API
           (FastAPI / Python)
                    |
         +----------+----------+
         |                     |
         v                     v
   AI ROUTER             LOCAL SERVICES
   - Gemini (Cloud)      - Memory (SQLite FTS5)
   - Ollama (Offline)    - Sentinel (Cybersecurity)
         |               - Performance Governor
         |               - JDI (Self-Evolution)
         v               - JIEE (Response Pivot)
   SPECIALIST AGENTS
   [ATLAS, ORACLE, NEXUS, ATHENA, ECHO, SENTINEL, JDI]
                    |
                    v
             PERMISSION LAYER
                    |
                    v
             TASK EXECUTION & VERIFICATION
```

---

## Key Features

1. **Mission Control & 3D Holographic Core**
   - High-fidelity Three.js particle sphere responsive to status (`idle`, `listening`, `thinking`, `executing`, `speaking`, `warning`).
   - Adapts particle density dynamically based on system load.

2. **Webcam Hand-Tracking & Gestures**
   - Privacy-first: disabled by default, runs purely in local memory with zero external transmission.
   - Detects hand position and pinch states to manipulate the 3D intelligence core.

3. **Personality 2.0 & Humour Engine**
   - British masculine voice and persona with dry observational wit.
   - 10 operational modes: Casual, British Assistant, Focus, Developer, Business, Study, Mentor, Serious, Quiet, Security.

4. **JIEE (JARVIS Intelligence Evaluation Engine)**
   - Introspective self-critique: when the owner indicates dissatisfaction ("That's not what I meant", "You missed the point"), JIEE analyzes the prior mismatch and auto-pivots to a superior response.

5. **JDI (JARVIS Development Intelligence) & Evolution Centre**
   - Automated static code auditing of the JARVIS repository for performance, test coverage, and security vulnerabilities.
   - Generates structured Google Antigravity prompts with problem context, constraints, and rollback plans.

6. **Family & Multi-Profile Security**
   - Strict profile separation between **Owner** (Rohan), **Family Member** (Work), and **Guest**.
   - Private memory, credentials, and system settings remain inaccessible to non-owner profiles.

7. **Sentinel Cybersecurity & Browser Safety**
   - Real-time phishing, lookalike domain, and typosquatting detection.
   - Social engineering and prompt injection scanning on incoming messages and documents.

8. **Thermal & Hardware Governor**
   - Engineered specifically for Intel Core i5 and 8 GB RAM constraints.
   - Switches between Eco, Balanced, and Performance profiles to avoid thermal throttling.

---

## Quick Start

### 1. Start Backend Service
```powershell
# From project root
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8765
```

### 2. Start Desktop Frontend
```powershell
cd apps/desktop
npm run dev
```

### 3. Run Automated Tests
```powershell
$env:PYTHONPATH = "f:\Work\Jarvis- Hero"
pytest tests/ -v
```

---

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — System design & component contracts
- [`docs/SECURITY.md`](docs/SECURITY.md) — Threat models, permission tiers & profile separation
- [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md) — Formal specification requirements
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — Development milestones & phased delivery
- [`docs/TESTING.md`](docs/TESTING.md) — Automated test suite & test procedures
