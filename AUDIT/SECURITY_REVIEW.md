# J.A.R.V.I.S. MARK VIII — FORENSIC SECURITY REVIEW
**Audit Date:** 2026-11-13  
**Auditor:** Principal Security Engineer & Forensic Review Team  
**System Target:** Windows 11 Home x64, Localhost API (127.0.0.1:8765)

---

## 1. Threat Model & Attack Surface

J.A.R.V.I.S. Mark VIII exposes a local HTTP/WebSocket API listening on `127.0.0.1:8765`.
Because the application possesses system privileges (application launching, file system manipulation, master volume, and code compilation), the local boundary is critical:
- **Local Process Privilege Escalation:** Any unprivileged process or browser script on the host machine attempting to communicate with `127.0.0.1:8765`.
- **Cross-Origin Resource Sharing (CORS):** Malicious websites visited by the user executing JavaScript targeting `http://127.0.0.1:8765`.
- **Indirect Prompt Injection:** Untrusted web content, repositories, or external text ingested by Gemini containing malicious system directives.

---

## 2. Key Security Findings & Vulnerabilities

### SEC-01 (HIGH): Unprotected `/quick-unlock` Endpoint
- **Location:** `backend/app/api/v1/endpoints/auth.py` (Lines 201-221)
- **Vulnerability:** The endpoint issues a full `owner` JWT token without requiring password, biometric check, or session nonce.
- **Risk:** Any process running on the host or any malicious web page executing a cross-origin POST request (if CORS is permissive) can obtain an owner JWT and gain full authority over the laptop.
- **Remediation Priority:** HIGH. Replace with Windows DPAPI-backed token generation or restrict to a transient startup token passed via Tauri / CLI IPC.

### SEC-02 (HIGH): Overly Permissive CORS Policy
- **Location:** `backend/app/main.py` (Lines 37-45)
- **Vulnerability:** `allow_origins=["*"]` allows any web page loaded in any browser on the laptop to send requests to the local backend.
- **Risk:** Cross-Site Request Forgery (CSRF) / Drive-by local API execution from untrusted websites.
- **Remediation Priority:** HIGH. Restrict CORS origins strictly to `["http://localhost:5173", "http://127.0.0.1:5173", "tauri://localhost", "http://127.0.0.1:8765"]`.

### SEC-03 (MEDIUM): Fallback Shell Execution in `launch_app`
- **Location:** `backend/app/tools/laptop_controller.py` (Line 232)
- **Vulnerability:** Fallback `subprocess.Popen(f'start "" "{q}"', shell=True)` passed arbitrary unvalidated strings to `cmd.exe`.
- **Risk:** Argument injection or unexpected Windows protocol execution if unvetted input reaches `launch_app`.
- **Remediation Priority:** MEDIUM. Fixed in Milestone 1 by removing blind shell dispatch and requiring verified executable paths or explicit URL protocols.

### SEC-04 (MEDIUM): External CDN Script Injection Risk for MediaPipe
- **Location:** `apps/desktop/src/components/gesture-controls/GestureEngine.ts` (Lines 112-140)
- **Vulnerability:** Dynamically loads script tags from `https://cdn.jsdelivr.net/npm/@mediapipe/hands`.
- **Risk:** If CDN is compromised or DNS is poisoned, arbitrary remote JavaScript executes inside the desktop client context.
- **Remediation Priority:** MEDIUM. Bundle MediaPipe Hands libraries locally in `apps/desktop/public/vendor/`.

### SEC-05 (LOW): API Key Protection in Windows Credential Manager
- **Location:** `backend/app/security/auth.py` (Lines 94-149)
- **Evaluation:** Secure implementation. Gemini API key is stored in Windows Credential Manager via `keyring` under service `JARVIS`. The raw key is never returned to the frontend and never printed in logs (`logger.info("Storing Gemini API key in Windows Credential Manager.")`).

---

## 3. Subsystem Security Checklist

| Subsystem | Requirement | Implementation Status | Evidence / Verification |
| :--- | :--- | :--- | :--- |
| **Authentication** | Password hashing with bcrypt | **SECURE** | Uses `bcrypt.hashpw` with salt; tested in `test_database_and_auth.py` |
| **Token Handling** | Signed JWT with expiration | **SECURE** | Uses HS256 with 60-min TTL; tested in `test_invalid_jwt` |
| **Credentials** | OS-backed credential store | **SECURE** | Windows Credential Manager (`keyring`) |
| **Camera Access** | Opt-in, visible indicator | **SECURE** | Camera is off by default, live HUD border & indicator when active |
| **Audio Capture** | Barge-in cancellation | **SECURE** | Immediate speech synthesis & audio track cancellation |
| **Local Directives** | Typed whitelist execution | **FORTIFIED** | Restricted to allowlisted apps & native Win32 virtual keys |
| **Self-Healing** | No blind source overwrites | **FORTIFIED** | `.bak` safety clone, syntax check, and pytest validation with rollback |
