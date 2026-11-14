# PROJECT J.A.R.V.I.S. — MARK IX
## OPEN-SOURCE INTELLIGENCE & ARCHITECTURAL BENCHMARKING REPORT

**Document Version:** 1.0.0  
**Research Target:** State-of-the-Art Personal AI Assistant Systems & Subsystems  
**Hardware Baseline Target:** Windows 11 Home x64, Intel Core i5, 7.92 GB RAM  
**Purpose:** Identify reusable architectural patterns, high-performance libraries, and strategic trade-offs for Mark IX.

---

## 1. ARCHITECTURAL COMPARISON MATRIX

| Project / Ecosystem | Primary Strength | Memory / Hardware Overhead | Mark IX Feasibility | Adoption Decision |
| :--- | :--- | :--- | :--- | :--- |
| **Pipecat** (`pipecat-ai/pipecat`) | Ultra-low latency voice pipeline (VAD + ASR + LLM + TTS streaming) | Low (~45 MB runtime) | HIGH | **ADOPT PIPELINE PATTERN:** Immediate sentence-level streaming TTS and low-latency turn-taking. |
| **Silero VAD** (`snakers4/silero-vad`) | Micro-second voice activity detection, eliminates speech tail latency | Minimal (<2 MB model) | HIGH | **INTEGRATE:** Replaces fixed 1.1s silence delays with 450-500ms adaptive cadence. |
| **faster-whisper** (`SYSTRAN/faster-whisper`) | Fast local CTranslate2 Whisper transcription | High (500 MB–1.5 GB RAM) | MEDIUM | **OPTIONAL LOCAL ENGINE:** Default to Web Speech API / Cloud STT for 0 MB RAM overhead, keep as optional toggle. |
| **Kokoro** (`hexgrad/kokoro`) | High-fidelity lightweight 82M TTS with British male voice | Moderate (150–250 MB RAM) | MEDIUM | **EVALUATE FOR OFFLINE:** Web Speech API (`en-GB George/Ryan`) is primary for zero RAM impact; SAPI as backup. |
| **PydanticAI** (`pydantic/pydantic-ai`) | Type-safe tool definitions, structured outputs, validated agent schemas | Low (<15 MB) | VERY HIGH | **ADOPT SCHEMA PATTERN:** Standardize all tool inputs, agent results, and memory records with Pydantic models. |
| **Mem0** (`mem0ai/mem0`) | Layered episodic, semantic, and procedural memory extraction | Low when SQLite-backed | HIGH | **ADOPT ARCHITECTURE:** Build lightweight SQLite FTS5 Memory Engine with automatic chat fact extraction. |
| **Browser Use** (`browser-use/browser-use`) | Multi-step agent browser automation with vision/DOM parsing | High (Spawns Chromium) | SELECTIVE | **ADOPT DETERMINISTIC FOUNDATION:** Use headless Playwright/Chrome for targeted scraping without heavy agent loops. |
| **Microsoft MarkItDown** (`microsoft/markitdown`) | Clean conversion of web pages, PDFs, and docs to markdown | Minimal (<30 MB) | VERY HIGH | **ADOPT:** Standardize document ingestion and web scraping results into clean markdown for Gemini context. |
| **Ollama / llama.cpp** | Local offline LLM inference | Very High (3.8–5.5 GB RAM) | REJECT FOR PRIMARY | **REJECT AS MANDATORY:** Running 4GB+ models on 8GB host causes extreme OOM thrashing. Cloud-first Gemini is primary. |
| **Leon AI / Personal-Jarvis** | Modular skill and command routing | Low | HIGH | **ADOPT ROUTING PATTERN:** Separation between deterministic local commands (<15ms) and deep AI reasoning. |

---

## 2. KEY ARCHITECTURAL ADOPTIONS FOR MARK IX

### A. Low-Latency Voice Streaming (Inspired by Pipecat)
- **Problem:** Traditional request-response chat waits for the complete LLM response before synthesizing audio. If the answer is 4 sentences, the user waits 5–8 seconds in silence.
- **Mark IX Implementation:**
  1. Stream tokens via WebSocket (`/api/v1/conversations/ws/chat`).
  2. Implement an incremental sentence boundary buffer in the frontend.
  3. As soon as the first sentence ends (`.`, `!`, `?`, or newline with $\ge 4$ words), dispatch it immediately to `speechSynthesis`.
  4. While sentence 1 is being spoken, sentences 2, 3, and 4 continue streaming and are queued sequentially.
  5. **Result:** Spoken response latency drops from **~6,500 ms to <650 ms**!

### B. Layered Memory Architecture (Inspired by Mem0 & Graphiti)
- **Problem:** J.A.R.V.I.S. suffered from memory amnesia. Important facts (user preferences, project details, hardware specs) were never retained across conversation sessions.
- **Mark IX Implementation:**
  1. **Working Memory:** Active conversation window (last 10 turns).
  2. **Episodic Memory:** Saved interaction milestones and major events.
  3. **Semantic Memory:** Extracted user facts (*"User's name is Rohan"*, *"Uses Windows 11"*, *"Likes mango"*, *"Developing Jarvis Hero"*).
  4. **Project Memory:** Repository locations, Git status, active branches, architecture notes.
  5. **Storage:** Stored in SQLite with Full-Text Search (FTS5) for instant sub-millisecond retrieval without requiring an expensive vector database.

### C. Real Specialist Multi-Agent System (Inspired by PydanticAI & Agno)
- **Problem:** Mark VIII specialist agents (ORACLE, NEXUS, ATHENA, ECHO) returned mock static dictionaries.
- **Mark IX Implementation:**
  1. **ORACLE (Research Specialist):** Performs live multi-source web queries via Google search, fetches page contents, extracts citations, and synthesizes structured research reports.
  2. **ATLAS (Development & Architecture Specialist):** Performs real repository inspection, file reading, AST syntax analysis, runs `pytest`, and computes Git diffs.
  3. **ECHO (Communications Specialist):** Drafts formal and informal messages, emails, and briefings with mandatory user approval before sending.
  4. **NEXUS (Business & Strategy Specialist):** Generates structured viability breakdowns, pricing analyses, and risk matrices.
  5. **ATHENA (Pedagogy & Learning Specialist):** Provides Socratic first-principles explanations, study roadmaps, and knowledge verification questions.
  6. **SENTINEL (Security & Health Specialist):** Validates URLs, scans for prompt injection and sensitive credential leaks, and monitors system limits.

### D. Zero-Overhead WebGL Optimization (Hardware Feasibility Rule)
- **Problem:** Three.js starburst core re-uploaded 8,600 vertices 60 times a second to GPU VRAM, saturating Intel integrated graphics and consuming system RAM.
- **Mark IX Implementation:**
  - Vertices are static on the GPU.
  - Scale, rotation, and harmonic breathing are driven via GPU uniforms and matrix transformations.
  - Zero buffer re-uploads per frame.
  - 3-tier Adaptive Governor: **ECO** (2,000 rays, 30 FPS, no bloom), **BALANCED** (2,800 rays, 60 FPS, tuned bloom), **TURBO** (high bloom).
