# Scope: Milestone 1 — Subsystem Audit & Defect Remediation

## Architecture & Code Boundaries
- Backend Core: `backend/app/main.py`, `backend/app/api/v1/endpoints/conversations.py`
- Tools & Integrations: `backend/app/tools/laptop_controller.py`, `backend/app/tools/tool_registry.py`
- Tests & Configuration: `pytest.ini`, `tests/backend/test_laptop_controller.py`
- Desktop Frontend: `apps/desktop/public/jarvis-icon.svg`, `apps/desktop/src/layouts/AppLayout.tsx`

## Features & Deliverables
1. Root `pytest.ini`:
   - Create `pytest.ini` at project root with `[pytest]\npythonpath = .` and testpaths `tests` so that running `pytest` out-of-the-box succeeds without setting manual environment variables.
2. WebSocket Chat Laptop Directives Interception:
   - In `backend/app/api/v1/endpoints/conversations.py` (`websocket_chat` function), intercept incoming user messages with `laptop_controller.execute_directive(message_text)` (matching `direct_chat` logic at line 444).
   - If a directive matches (battery, volume, launch app, time, etc.), send the directive response directly over the WebSocket to the frontend and store in conversation history, preventing unnecessary Gemini fallback.
3. Tool Registry Integration:
   - Formally register `laptop_controller` tools in `backend/app/tools/tool_registry.py` so that autonomous agent execution and system tool queries can discover and invoke laptop control capabilities.
4. Laptop Controller Unit Test Suite:
   - Create `tests/backend/test_laptop_controller.py` verifying Start menu shortcut resolution, volume key event triggering, battery status retrieval, download organization, and directive parsing.
5. Favicon Asset & Layout Route Fix:
   - Create `apps/desktop/public/jarvis-icon.svg` (JARVIS-themed SVG arc reactor icon) so `/jarvis-icon.svg` returns valid image/svg+xml instead of falling back to SPA HTML.
   - In `apps/desktop/src/layouts/AppLayout.tsx`, change Overview navigation path from `'/'` to `'/dashboard'` to match route definition in `App.tsx`.
6. Frontend Build & Static Serving Verification:
   - Verify `npm run build` succeeds cleanly in `apps/desktop`.
   - Verify FastAPI serves the updated frontend cleanly at `http://127.0.0.1:8765`.
   - Run backend test suite to ensure 100% pass rate.

## Pass Criteria
- `pytest` runs and passes 100% of tests.
- `laptop_controller.execute_directive` is called inside `websocket_chat`.
- `apps/desktop/public/jarvis-icon.svg` exists and is served.
- `npm run build` exits 0.
