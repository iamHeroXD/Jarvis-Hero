# J.A.R.V.I.S. MARK VIII — FORENSIC BUG REGISTER
**Audit Date:** 2026-11-13  
**Auditor:** Principal Software Architect & QA Engineering Team  
**Scope:** Full Codebase Empirical & Static Verification

---

## Severity Classification Standards
- **P0 — CRITICAL:** Application startup failure, fatal database crash, unauthenticated remote command execution, data loss.
- **P1 — HIGH:** Primary functional failure (AI reasoning failure, audio/visual breakdown, incorrect computer action, severe intent hijacking).
- **P2 — MEDIUM:** Edge-case crashes, type errors, resource leaks, permission gaps, test harness deadlocks.
- **P3 — LOW:** Usability flaws, cosmetic styling defects, missing offline asset fallbacks.

---

## Comprehensive Defect Matrix

| Bug ID | Severity | Subsystem | Defect Summary | Affected Files | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BUG-P1-01** | **P1 - HIGH** | 3D Core WebGL | Blinding white sun optical blowout caused by point light + additive cluster + low bloom threshold | `apps/desktop/src/components/jarvis-core/ParticleCore.tsx` | Identified |
| **BUG-P1-02** | **P1 - HIGH** | AI / Context | Conversational amnesia in `direct_chat`: turn history not retrieved or passed to Gemini | `backend/app/api/v1/endpoints/conversations.py`, `backend/app/ai/gemini_provider.py` | Identified |
| **BUG-P1-03** | **P1 - HIGH** | AI Provider | Severe token truncation (`max_output_tokens=140`) cutting Gemini responses mid-sentence | `backend/app/ai/gemini_provider.py` | Identified |
| **BUG-P1-04** | **P1 - HIGH** | Laptop Controller | Overly greedy substring matching in `execute_directive` swallowing common English words | `backend/app/tools/laptop_controller.py` | Identified |
| **BUG-P1-05** | **P1 - HIGH** | Workspace Bridge | Antigravity IDE missing from app launcher; compound directives misrouted to URL opener | `backend/app/tools/laptop_controller.py` | Identified |
| **BUG-P2-01** | **P2 - MEDIUM** | Tool Registry | `adjust_volume` crashes with `AttributeError` when integer/None argument is supplied | `backend/app/tools/laptop_controller.py` | Identified |
| **BUG-P2-02** | **P2 - MEDIUM** | Tool Execution | Blind shell fallback in `launch_app` invoking `start ""` on unknown queries | `backend/app/tools/laptop_controller.py` | Identified |
| **BUG-P2-03** | **P2 - MEDIUM** | Authentication | Insecure `/quick-unlock` endpoint minting owner JWTs without credentials | `backend/app/api/v1/endpoints/auth.py` | Identified |
| **BUG-P2-04** | **P2 - MEDIUM** | Database / Testing| SQLite `StaticPool` deadlock between synchronous TestClient WebSockets and async clients | `backend/app/database/session.py`, `tests/e2e/conftest.py` | Identified |
| **BUG-P3-01** | **P3 - LOW** | Optical Tracking | MediaPipe Hands scripts dynamically loaded from external CDN; fails offline | `apps/desktop/src/components/gesture-controls/GestureEngine.ts` | Identified |

---

## Detailed Bug Reports & Reproduction Steps

### BUG-P1-01: Blinding White Sun Optical Blowout in `ParticleCore.tsx`
- **Severity:** P1 (High)
- **Evidence:** User uploaded screenshot `media_1794446816099_d2e93d79.jpg` showing a blown-out, massive white sphere obscuring 60% of the screen.
- **Affected File:** `apps/desktop/src/components/jarvis-core/ParticleCore.tsx` (Lines 167-174, 205-214, 362-396, 435-436)
- **Root Cause Analysis:**
  1. `PointLight(0xffffff, 4.2, 550)` positioned at origin floodlights all additive geometries.
  2. 650 nucleus points packed into radius 1.2–6.5 with `size: 4.2`, `opacity: 0.98`, and `AdditiveBlending`. Adding 650 points in a 5px radius creates HDR luminance exceeding 50.0.
  3. 2,600 ray filaments start at $r_{\text{inner}} = 2.0$ with pure white vertex colors `[1.0, 1.0, 1.0]` under additive blending.
  4. `UnrealBloomPass(..., 1.15, 0.32, 0.22)`: Threshold of `0.22` is extremely low, causing every pixel brighter than 0.22 to bleed outward with strength `1.15`, creating a massive washed-out sun instead of the crisp, striated 14-lobe caustic ray starburst in `media_1794318286093_bfd93d21.jpg`.
- **Reproduction Instructions:**
  1. Launch frontend `npm run dev` or serve desktop build.
  2. View central canvas: center is a blinding white glow with no discernible filaments.
- **Remediation Plan:**
  - Remove PointLight or reduce intensity to 0.
  - Replace 650 nucleus particles with 20 tiny specular singularity points ($r=1.5-3.5$, size 1.6).
  - Offset ray roots to $r_{\text{inner}} = 6.0 - 10.0$ to prevent origin stacking.
  - Set `bloomPass.threshold = 0.78`, `bloomPass.strength = 0.60`, `bloomPass.radius = 0.20`.
  - Set `renderer.toneMappingExposure = 1.0`.

---

### BUG-P1-02: Conversational Amnesia Between Turns in Direct Chat
- **Severity:** P1 (High)
- **Evidence:** User feedback: "doesnt remember last talked what". User requests are answered without memory of earlier turns in the conversation.
- **Affected Files:** `backend/app/api/v1/endpoints/conversations.py` (Lines 492-500), `backend/app/ai/gemini_provider.py` (Lines 93-149)
- **Root Cause Analysis:**
  - `direct_chat` endpoint creates or finds `Conversation`, inserts the user's current message, but executes:
    `gemini_provider.chat(message=message_text, system_instruction=system_prompt, model=settings.primary_model)`
  - It NEVER queried preceding turns from `Message` table!
  - `gemini_provider.chat` only took `message: str` and passed a single string to `client.models.generate_content(contents=message)`.
- **Reproduction Instructions:**
  1. Post `{"message": "My favorite color is cyan"}` to `/api/v1/conversations/chat`.
  2. Post `{"message": "What is my favorite color?", "conversation_id": <id>}` to `/api/v1/conversations/chat`.
  3. AI has no knowledge of turn 1 and responds with generic speculation.
- **Remediation Plan:**
  - In `direct_chat`, query the last 10 messages from `Message` where `conversation_id == convo.id`.
  - Construct a structured `history` payload `[{"role": m.role, "text": m.content}, ...]`.
  - In `gemini_provider.py`, accept `history` and construct a multi-turn `contents` array with `types.Content(role=..., parts=[...])`.

---

### BUG-P1-03: Arbitrary Token Truncation in Gemini Provider
- **Severity:** P1 (High)
- **Evidence:** SQLite database shows truncated assistant messages: `[186] assistant (gemini): You're very welcome,`, `[188] assistant (gemini): Be direct, honest`, `[198] assistant (gemini): Formulate Response`.
- **Affected File:** `backend/app/ai/gemini_provider.py` (Line 116)
- **Root Cause Analysis:**
  - `max_output_tokens` was hardcoded to `140` tokens (~20-30 words). When Gemini generated punctuation or thinking tokens, the response cut off mid-clause.
- **Reproduction Instructions:**
  1. Submit query: "Explain how neural networks learn weights and biases."
  2. Observe response cuts off mid-sentence after 140 tokens.
- **Remediation Plan:**
  - Increase `max_output_tokens` to `1024` in `GenerateContentConfig`.
  - Update system instruction to ensure complete, natural sentences.

---

### BUG-P1-04: Greedy Substring Matching in `execute_directive`
- **Severity:** P1 (High)
- **Evidence:** `tests/backend/test_challenger_m1.py::test_adversarial_non_directive_swallowing` failed:
  - `"How do I update my database?"` -> swallowed by `'date'`
  - `"What is the time complexity of quicksort?"` -> swallowed by `'time'`
  - `"We need to validate the hypothesis"` -> swallowed by `'date'`
  - `"What is your daily commute like?"` -> swallowed by `'mute'`
- **Affected File:** `backend/app/tools/laptop_controller.py` (Lines 559-601)
- **Root Cause Analysis:**
  - Checked `any(w in text for w in ["date", "time", "mute"])`.
  - `"date"` matches `"update"`, `"validate"`, `"candidate"`.
  - `"time"` matches `"spacetime"`, `"time complexity"`.
  - `"mute"` matches `"commute"`.
- **Reproduction Instructions:**
  1. Call `laptop_controller.execute_directive("How do I update my database?")`.
  2. Notice it immediately returns `Today is Friday, November 13, 2026, Sir.` instead of returning `None` to route to Gemini!
- **Remediation Plan:**
  - Replace naive `in` substring checks with exact regex word boundary patterns (`\b`).

---

### BUG-P1-05: Antigravity IDE Missing from Application Launcher & Workspace Bridge
- **Severity:** P1 (High)
- **Evidence:** User said: "open antigravity and go to jarvis project and prompt it to make it better and smth else etc etc but it doesnt do anything".
- **Affected File:** `backend/app/tools/laptop_controller.py`
- **Root Cause Analysis:**
  - `antigravity` was not indexed in `LaptopController.app_map`.
  - When user said `"open antigravity and go to jarvis project"`, `url_match` regex matched `go to jarvis` and attempted to launch a web browser to `https://jarvis`!
- **Reproduction Instructions:**
  1. Call `laptop_controller.execute_directive("open antigravity and go to jarvis project")`.
  2. Observe browser attempting to open `https://jarvis`.
- **Remediation Plan:**
  - Add `antigravity` to `self.app_map` with verified path `C:\Users\Rohan\AppData\Local\Programs\Antigravity IDE\Antigravity IDE.exe`.
  - Implement `open_project_in_ide` to launch Antigravity IDE with `f:\Work\Jarvis- Hero`.
  - Restrict URL regex to require standard TLDs (`.com`, `.org`, etc.) or `http`.

---

### BUG-P2-01: `adjust_volume` Crash on Non-String Parameter
- **Severity:** P2 (Medium)
- **Evidence:** `tests/backend/test_challenger_m1.py::test_tool_registry_invalid_argument_types` crashed with `AttributeError: 'int' object has no attribute 'lower'`.
- **Affected File:** `backend/app/tools/laptop_controller.py` (Line 338)
- **Root Cause Analysis:**
  - `action.lower().strip()` fails when caller passes integer or non-string object.
- **Remediation Plan:**
  - Safely cast `action`: `action = str(action or "").lower().strip()`.
