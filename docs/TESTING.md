# PROJECT J.A.R.V.I.S. Automated Testing Suite

## Overview

Project J.A.R.V.I.S. features a comprehensive, multi-layer automated test suite that validates every subsystem from database integrity and cryptographic token handling to autonomous multi-agent task execution and Sentinel security analysis.

---

## Test Inventory (24 Automated Tests)

### 1. Database & Authentication (`tests/backend/test_database_and_auth.py`)
- `test_password_hashing`: Validates standard salted bcrypt hashing with truncation protection for passwords.
- `test_jwt_generation_and_validation`: Tests access token creation, subject string encoding, and expiration claims.
- `test_invalid_jwt`: Verifies cryptographic rejection of tampered tokens, invalid signatures, and malformed headers.

### 2. Evolution, Security & Personality (`tests/backend/test_evolution_and_security.py`)
- `test_persona_engine_generation`: Tests British masculine persona system prompts across all 10 operational modes.
- `test_humour_engine`: Tests situational dry wit quips based on high load, repetitive commands, and user corrections.
- `test_jiee_mismatch_detection`: Verifies the JARVIS Intelligence Evaluation Engine detects owner dissatisfaction ("That's not what I meant") and generates prompt pivots.
- `test_sentinel_url_safety`: Tests detection of lookalike typosquatting and phishing domains (`accounts-google-verify.com`).
- `test_sentinel_communication_scan`: Tests detection of social engineering coercion and prompt injection strings.
- `test_performance_governor`: Tests adaptive hardware throttling on Intel Core i5 dual-core and 8 GB RAM constraints.
- `test_codebase_auditor`: Tests static repository auditing for missing tests, hardcoded paths, and TODO items.
- `test_prompt_generator`: Tests structured Google Antigravity prompt synthesis.
- `test_profile_permissions`: Verifies strict permission isolation between Owner, Family, and Guest profiles.

### 3. Tools, Agents & Task Engine (`tests/backend/test_tools_agents_and_tasks.py`)
- `test_approved_app_launcher`: Tests allowlisted application launching with process validation.
- `test_file_operations_with_verification`: Tests workspace-bounded file reading, writing with automatic rollback backups, and existence verification.
- `test_allowlisted_command_runner`: Tests developer command execution (`git`, `pytest`, `npm`, `cargo`) without raw shell escalation.
- `test_tool_registry_and_permissions`: Tests Level 0–4 permission enforcement and mandatory confirmation requirements.
- `test_agent_orchestrator_dispatch`: Tests intent routing to ATLAS (software dev) and ORACLE (research & citations).
- `test_task_engine_state_machine`: Tests task lifecycle transitions (`CREATED` -> `RUNNING` -> `VERIFYING` -> `COMPLETED`).
- `test_smart_reminders_and_briefing`: Tests scheduled reminders and tactical daily briefing generation.
- `test_voice_service_barge_in`: Tests British TTS synthesis and immediate barge-in interruption.

### 4. Projects, Automations & System (`tests/backend/test_projects_automations_and_system.py`)
- `test_projects_lifecycle_and_git_status`: Tests project listing with default seeding (RCN, Clearly AI), workspace Git inspection, and notes/decisions logging.
- `test_automations_lifecycle`: Tests scheduled automations, manual run triggers, and state toggles.
- `test_activity_log`: Tests immutable security audit trails and tool action logging.
- `test_system_and_governor`: Tests live psutil metrics endpoint and governor profile switching to Eco mode.

---

## Executing the Test Suite

Run all tests via PowerShell:
```powershell
$env:PYTHONPATH = "f:\Work\Jarvis- Hero"
pytest tests/ -v
```

Or execute the provided runner script:
```powershell
.\scripts\run_tests.ps1
```
