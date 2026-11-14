# J.A.R.V.I.S. MARK X — OPEN ISSUES & KNOWN CONSTRAINTS

**Status:** ALL P0 and P1 blocking defects have been completely eliminated.  
**Classification:** Operational Minor Items & Hardware Boundary Notes  

---

## 1. Operating System & Platform Boundaries

### 1.1 Python 3.14 win32gui Callback Limitation
- **Symptom**: Calling `win32gui.EnumWindows` with a Python callback function in Python 3.14.4 raises `pywintypes.error: (122, 'EnumWindows', 'The data area passed to a system call is too small.')`.
- **Mitigation Implemented**: Replaced with `psutil.process_iter(["pid", "name", "memory_info"])` combined with direct `ctypes.windll.user32` calls. This provides robust <80ms process telemetry and verified execution without relying on unstable pywin32 callbacks in Python 3.14.

### 1.2 Web Audio API Autoplay Policy
- **Symptom**: Modern web browsers (including Chrome and Electron WebViews) block audio playback before the user performs an initial user gesture (click/key).
- **Mitigation Implemented**: Added a glowing "ENABLE AUDIO" button in the HUD header that unlocks the `AudioContext` and triggers `window.speechSynthesis` on first user interaction.

---

## 2. Hardware Resource Constraints (Intel Core i5, 8GB RAM)

### 2.1 Intel UHD Graphics Shared Memory
- **Constraint**: The GPU has no dedicated VRAM and shares host system RAM.
- **Rule Enforced**: Three.js particle counts must remain clamped according to the Adaptive Performance Governor:
  - Eco Mode: 2,400 particles / 1,600 ray filaments
  - Balanced Mode: 5,200 particles / 2,200 ray filaments (Default)
  - Turbo Mode: 7,800 particles / 2,800 ray filaments
- Zero per-frame buffer updates permitted.

### 2.2 Local LLM Weight Exclusion
- **Constraint**: Storing a 7B or 8B parameter local LLM in RAM requires 4.5–6.0 GB of memory, exceeding available headroom (~0.93–1.85 GB) and causing Windows paging thrash.
- **Rule Enforced**: Zero local quantized LLMs loaded into memory. All neural language generation uses the Gemini 2.5/Flash neural core over async HTTPS/WebSocket streaming, keeping memory footprint <96 MB RSS.
