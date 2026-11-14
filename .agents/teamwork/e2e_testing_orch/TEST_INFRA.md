# E2E Test Infra: JARVIS Production Personal Assistant

## Test Philosophy
- Opaque-box, requirement-driven derived from `ORIGINAL_REQUEST.md`.
- No internal code monkeypatching or private symbol dependencies; interact via HTTP REST, WebSocket, CLI directives, and public APIs.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinatorial + Real-World Workload Testing.

## Test Architecture
- Test Runner: `pytest tests/e2e/ -v`
- Test Directory: `tests/e2e/`
- Output Signal: Creates `TEST_READY.md` at project root summarizing test counts and execution command once all suites are created.

## 4-Tier Test Suite Specification

### Tier 1 — Feature Coverage (Isolation / Happy Path)
- FastAPI core & health check (`GET /health`)
- REST routes (auth, system info, memory, tasks, telemetry)
- Laptop Controller: battery status query
- Laptop Controller: shortcut resolution & app launch lookup
- Laptop Controller: master volume query & adjustment
- Laptop Controller: downloads organization dry-run
- Laptop Controller: fast directive execution
- WebSocket chat connection and directive response
- Speech pipeline: TTS synthesis endpoint (`POST /api/v1/voice/speak`)
- Speech pipeline: STT transcription endpoint (`POST /api/v1/voice/transcribe`)
- Speech pipeline: barge-in interrupt endpoint (`POST /api/v1/voice/interrupt`)
- Self-healing: diagnostic traceback parser
- Self-healing: patch applicator
- Desktop frontend static serving (`GET /` and `/assets/*`)
- Favicon asset serving (`GET /jarvis-icon.svg`)

### Tier 2 — Boundary & Corner Cases
- Empty/malformed directive strings to `execute_directive`
- Extreme volume adjustments (<0%, >100%)
- Non-existent shortcut name resolution
- Corrupted/empty audio bytes to TTS and STT endpoints
- Rapid consecutive interrupt calls to `/api/v1/voice/interrupt`
- WebSocket abrupt client disconnect and reconnect
- Self-healing with unparseable or binary files
- Non-existent routes returning 404 vs SPA fallback
- Special characters in chat messages

### Tier 3 — Cross-Feature Combinations (Pairwise)
- Chat WebSocket + Laptop Controller (send battery directive via WS, receive telemetry JSON)
- Voice synthesis + Barge-in interrupt (start speak request, trigger interrupt immediately, verify cancellation)
- Directive parser + Application launcher (execute "launch notepad", verify process lookup)
- Self-healing + Automated test runner (inject syntax defect, run heal, verify tests pass)
- Desktop SPA serving + REST API calls (simulate frontend fetching /health and /api/v1/system/info)

### Tier 4 — Real-World Application Scenarios
1. Assistant Morning Briefing: Query battery, time, and system diagnostics in one multi-turn sequence.
2. Volume Control Workflow: Turn volume up, down, mute, and query audio status.
3. Rapid Conversation with Barge-In: Simulate vocal interaction where user interrupts assistant speech mid-response.
4. Self-Healing Incident Recovery: Simulate runtime syntax error during code execution, trigger autonomous self-healing, verify zero downtime.
5. Desktop App Launch & Health Verification: Complete end-to-end boot of FastAPI server and retrieval of desktop client bundle.
