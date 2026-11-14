Perform a comprehensive audit, repair, and upgrade of JARVIS as a production personal assistant for laptop control, coding assistance, and daily operations, restoring all planned and broken features across every subsystem. Deliver a single comprehensive PDF document compiling the complete PRD, system architecture, component inventory, feature matrix, verification test results, and operational guide.

Working directory: f:\Work\Jarvis- Hero
Integrity mode: development

## Requirements

### R1. Subsystem Audit and Defect Remediation
Audit all planned and implemented JARVIS subsystems—including backend services, frontend interface, speech/audio pipeline, and laptop control tools. Identify and resolve all functional defects, unhandled exceptions, and broken endpoints so that every advertised capability executes reliably.

### R2. Conversational Intelligence and Vocal Interaction
Upgrade JARVIS's dialogue management and vocal response pipeline to ensure responsive, natural conversation. The vocal interaction system must support continuous speech input, neural speech synthesis, barge-in interruption handling, and synchronized live caption display.

### R3. Autonomous Self-Code Healing and Maintenance
Implement an autonomous self-diagnosis and code repair mechanism that allows JARVIS to inspect runtime errors, locate the responsible codebase files, formulate corrective code patches, and verify those patches against automated tests.

### R4. Starburst Visuals and Desktop Interface Polish
Refine the Three.js interactive visualizer to deliver an iridescent crystal starburst light bloom matching the design specification (14 caustic petal lobes, chromatic dispersion, diamond-white singularity, diffraction spikes, sharp stardust particles, pure `#000000` void, mouse-wheel zoom from `0.2x` to `3.8x`, and state-reactive palettes). The interface must launch and operate cleanly in Chrome app mode without layout issues or console errors.

### R5. Comprehensive PRD and Documentation Single PDF
Generate a single, comprehensive, beautifully structured PDF document located in the project root. The document must integrate the complete Product Requirements Document (PRD), end-to-end system architecture, comprehensive component and library inventory, complete feature status matrix (planned, implemented, and operational status), automated verification test results, and operational runbook.

## Acceptance Criteria

### Subsystem Functionality & Stability
- [ ] All FastAPI backend endpoints and WebSocket routes in `backend/app/main.py` return valid responses or maintain stable connections without unhandled exceptions.
- [ ] Laptop controller tools (app launching, Start menu shortcut resolution, volume adjustment, battery telemetry query, file organization) execute and return successful operation status.
- [ ] The desktop frontend at `apps/desktop` compiles cleanly (`npm run build`) and is served by FastAPI at `http://127.0.0.1:8765`.

### Conversational & Vocal Interaction
- [ ] Continuous speech recognition and speech synthesis endpoints handle multi-turn dialogue without freezing or dropped sessions.
- [ ] Barge-in audio handling halts speech playback immediately when new user speech is detected.
- [ ] Live captions accurately display user speech transcripts and JARVIS vocal response text.

### Autonomous Self-Code Healing
- [ ] A dedicated self-repair test triggers an injected syntax/runtime defect, and JARVIS's self-healing routine successfully identifies the faulty file, generates a valid patch, applies the fix, and confirms tests pass.

### Visual Appearance & Interface
- [ ] The Three.js starburst canvas renders in Chrome app mode without WebGL context loss or console errors, and responds to mouse-wheel zoom between 0.2x and 3.8x.
- [ ] Visual state-reactive palette transitions trigger accurately across idle, listening, thinking, speaking, and executing states.

### Verification Test Suite
- [ ] Automated end-to-end test scripts run against the backend, laptop controller, and self-healing engine, with 100% of defined test cases passing.

### Comprehensive PRD Single PDF Deliverable
- [ ] A single PDF file (e.g., `JARVIS_Comprehensive_PRD_and_System_Guide.pdf`) is generated in the project root directory.
- [ ] The single PDF file includes: Executive Summary & System Overview, Comprehensive PRD, Architecture & Data Flow Descriptions, Component & Dependency Inventory, Complete Feature Status Matrix (all planned vs working capabilities), Automated Test Results & Verification Logs, and User Operational Runbook.
- [ ] The PDF document is valid, non-empty (>50 KB), contains all sections in a single continuous file, and renders without broken images or placeholders.
