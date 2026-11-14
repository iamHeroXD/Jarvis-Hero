# J.A.R.V.I.S. MARK XI — MISSION EXECUTION ENGINE SPECIFICATION

**Module:** `backend/app/tasks/mission_engine.py`  
**Storage Engine:** SQLite 3 (WAL mode) with SQLAlchemy Async ORM  
**Target Version:** MARK XI  
**Owner:** Rohan  

---

## 1. State Machine Definition

The Mark XI Mission Execution Engine governs multi-step compound automation tasks through a strict 14-state lifecycle:

```
                   +-------------+
                   |   CREATED   |
                   +------+------+
                          |
                          v
                   +-------------+
                   |  PLANNING   |<------------+
                   +------+------+             |
                          |                    |
                          v                    |
                   +-------------+             |
                   |    READY    |             |
                   +------+------+             |
                          |                    |
                          v                    |
       +------------>  RUNNING   <---------+   |
       |                  |                |   |
       |       +----------+----------+     |   |
       |       |                     |     |   |
       |       v                     v     |   |
       |  +-----------+       +---------+  |   |
       |  | WAITING_  |       | WAITING |  |   |
       |  | FOR_INPUT |       | _FOR_   |  |   |
       |  +----+------+       | APPROVAL|  |   |
       |       |              +----+----+  |   |
       |       +----+     +--------+       |   |
       |            |     |                |   |
       |            v     v                |   |
       |          +---------+              |   |
       +----------+VERIFYING|              |   |
                  +----+----+              |   |
                       |                   |   |
        +--------------+--------------+    |   |
        |              |              |    |   |
        v              v              v    |   |
   +---------+   +------------+  +----+----+   |
   |COMPLETED|   | RECOVERING |  |  FAILED |---+
   +---------+   +-----+------+  +---------+
                       |              ^
                       +--------------+
```

### Complete State Dictionary

| State | Description | Exit Conditions |
| :--- | :--- | :--- |
| `CREATED` | Mission payload received and recorded in SQLite database. | Moves to `PLANNING` or `READY`. |
| `PLANNING` | Neural engine synthesizing concrete steps and validating preconditions. | Moves to `READY`, `WAITING_FOR_INPUT`, or `FAILED`. |
| `READY` | Preconditions verified; ready for sequential step dispatch. | Moves to `RUNNING` or `PAUSED`. |
| `RUNNING` | Active step execution in progress across native tools or APIs. | Dispatches to verification, approval, or pause. |
| `WAITING_FOR_INPUT` | Mission paused waiting for clarification answers from Rohan. | Resumes to `PLANNING` or `RUNNING`. |
| `WAITING_FOR_APPROVAL` | High/critical risk step paused waiting for explicit human authorization. | Resumes to `RUNNING` upon approval, or cancels. |
| `VERIFYING` | Post-step or post-mission validation checks (tests, DOM, process status). | Moves to `COMPLETED` or `RECOVERING`. |
| `COMPLETED` | All steps executed and verified; artifacts saved to database. | Terminal success state. |
| `PAUSED` | User initiated temporary halt of mission execution. | Resumes to `RUNNING` on command. |
| `FAILED` | Unrecoverable error encountered or retry limits exhausted. | Terminal failure state unless manual recovery initiated. |
| `NEEDS_ATTENTION` | Mission completed with non-fatal anomalies or warnings. | Awaiting owner review. |
| `CANCELLED` | Explicit cancellation by owner or watchdog supervisor. | Terminal state. |
| `RECOVERING` | Automatic self-healing, rollback, or bounded retry in progress. | Resumes to `RUNNING` or transitions to `FAILED`. |

---

## 2. Persistence Model & Checkpointing

Missions and step checkpoints are stored across three core relational tables:
1. `tasks`: Master record with UUID, title, status, priority, JSON plan, evidence, and error log.
2. `task_events`: Immutable audit trail recording timestamps, from-state, to-state, and descriptive event logs.
3. `approval_requests`: Authorization records for sensitive actions (risk level, permission level, status, decision timestamp).

### Automated Crash Recovery
Upon restart, `mission_engine` inspects SQLite for tasks marked `running` or `recovering`. It checks the last completed step index, validates that disk artifacts match expectations, and resumes the mission from the unexecuted step without duplicate execution.

---

## 3. Supported Step Action Handlers

1. `directive`: Fast-path local directive execution via `unified_controller` (<10ms).
2. `app_launch`: Verified 5-stage application launch and foreground activation.
3. `command`: Asynchronous subprocess execution with timeout and output capture.
4. `research`: Multi-source internet research with clean DOM extraction.
5. `pdf_export`: High-contrast ReportLab PDF generation with clickable source links.
6. `ide_handoff`: Handoff directive generation and injection into Antigravity IDE.
7. `verify`: File existence, process alive, or test suite execution validation.
