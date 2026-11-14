## 2026-11-12T01:20:33Z
You are test_writer_e2e. Your working directory is f:\Work\Jarvis- Hero\.agents\teamwork\test_writer_e2e\

MANDATORY FIRST STEP:
Read f:\Work\Jarvis- Hero\.agents\teamwork\ORIGINAL_REQUEST.md in full before starting work.
Also read:
- f:\Work\Jarvis- Hero\.agents\teamwork\e2e_testing_orch\TEST_INFRA.md
- f:\Work\Jarvis- Hero\.agents\teamwork\PROJECT.md
- f:\Work\Jarvis- Hero\.agents\teamwork\explorer_survey_1\survey_report.md
- f:\Work\Jarvis- Hero\.agents\teamwork\spec_miner_survey_3\spec_report.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

EXCLUSIVE FILE OWNERSHIP:
You own and may create ONLY these files:
- `tests/e2e/__init__.py`
- `tests/e2e/conftest.py`
- `tests/e2e/test_tier1_features.py`
- `tests/e2e/test_tier2_boundaries.py`
- `tests/e2e/test_tier3_pairwise.py`
- `tests/e2e/test_tier4_scenarios.py`
- `TEST_READY.md` (at project root `f:\Work\Jarvis- Hero\TEST_READY.md`)
DO NOT modify any implementation code in `backend/` or `apps/`.

TASKS TO EXECUTE:
1. Create `tests/e2e/conftest.py`:
   - Set up async client fixtures using `httpx.AsyncClient(app=app, base_url="http://test")` or Starlette `TestClient` for synchronous calls.
   - Set up test environment variables if needed.
2. Create `tests/e2e/test_tier1_features.py` (Tier 1: Feature Coverage):
   - >=5 test cases per feature area (FastAPI health & routes, laptop tools, directive execution, voice endpoints, self-healing traceback & AST formulation, desktop static assets).
3. Create `tests/e2e/test_tier2_boundaries.py` (Tier 2: Boundary & Corner Cases):
   - Edge cases, empty inputs, extreme volume levels, non-existent shortcuts, rapid interrupts, invalid audio bytes, 404 paths.
4. Create `tests/e2e/test_tier3_pairwise.py` (Tier 3: Cross-Feature Combinations):
   - Pairwise tests: Chat WebSocket + Laptop Controller, Voice + Interrupt, Directive + App lookup, Self-healing + Test execution.
5. Create `tests/e2e/test_tier4_scenarios.py` (Tier 4: Real-World Scenarios):
   - 5 comprehensive workflow tests:
     1. Morning Briefing Workflow
     2. Volume Control Workflow
     3. Vocal Barge-In Workflow
     4. Self-Healing Incident Recovery Workflow
     5. Desktop App Serving & Health Verification Workflow
6. Run the test suite:
   - Run `pytest tests/e2e/ -v` and verify test suite status.
   - If voice endpoints (M2) currently return 500/AttributeError before M2 worker completes, handle expected responses or mock gracefully so the test harness functions properly.
7. Create `TEST_READY.md` at project root (`f:\Work\Jarvis- Hero\TEST_READY.md`) with the template:
   - Test Runner command: `pytest tests/e2e/ -v`
   - Coverage Summary table (Tiers 1-4 counts)
   - Feature Checklist
8. Write `f:\Work\Jarvis- Hero\.agents\teamwork\test_writer_e2e\handoff.md` with:
   Observation, Logic Chain, Caveats, Conclusion, Verification Method.
9. Send completion message to orchestrator (`86758165-ccbb-4668-ae6a-9eead9821de0`).
