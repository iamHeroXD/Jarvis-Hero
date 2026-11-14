# J.A.R.V.I.S. MARK XI — UNIFIED COMPUTER CONTROL PLANE

**Module:** `backend/app/tools/unified_computer_controller.py`  
**Host:** Windows 11 Home x64  
**Native Windows APIs:** Win32 (`user32.dll`, `kernel32.dll`, `psapi.dll`), `ctypes`, `psutil`, `winreg`  
**Target Version:** MARK XI  

---

## 1. Overview & Architecture

Mark XI consolidates three previously fragmented computer control scripts (`windows_controller.py`, `laptop_controller.py`, `app_launcher.py`) into one canonical engine: `unified_computer_controller.py`.

### Core Capabilities
- **Dynamic Application Discovery:**
  - Scans Windows Registry `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths` and `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths`.
  - Indexes all Start Menu `.lnk` shortcuts from User and All-Users directories.
  - Queries system `PATH` via `shutil.which`.
  - Maps common voice aliases and synonyms.
- **Verified 5-Stage Launch Pipeline:**
  1. *Binary Discovery:* Target executable, shortcut, or protocol resolved.
  2. *Process Creation:* Dispatched via `subprocess.Popen` or native `ShellExecute`.
  3. *PID Verification:* Actively polled up to 2.0s with `psutil` to verify process is alive.
  4. *Window Handle (HWND) Discovery:* Enumerates top-level visible windows via Win32 `EnumWindows`.
  5. *Window Foregrounding:* Automatically activates and restores window with `ShowWindow(SW_RESTORE)` and `SetForegroundWindow`.
- **Safe Termination:**
  - Performs graceful close signal first, waits 300ms, then terminates via `taskkill /F /IM` if unresponsive, confirming exit.
- **Virtual Input & Keystroke Automation:**
  - Unicode character typing using Win32 `SendInput` with `KEYEVENTF_UNICODE`.
  - Multi-key hotkey generation (Ctrl+C, Ctrl+V, Ctrl+Enter, Alt+Tab, Win+R).
- **Native Active Working Set Memory Optimizer:**
  - Calls `ctypes.windll.psapi.EmptyWorkingSet` across process handles.
  - Reclaims 500–600 MB of system RAM in <1.5 seconds.
- **Desktop & System Utilities:**
  - Master volume adjustments via `VK_VOLUME_UP`, `VK_VOLUME_DOWN`, and `VK_VOLUME_MUTE`.
  - Fast screen lock via `LockWorkStation`.
  - Minimize all windows via Shell COM interface.
  - User shell folder resolution (G:\Downloads, Documents, Desktop, Pictures).
  - Downloads folder categorized file reorganization.

---

## 2. Fast-Path Natural Directive Parsing (<10ms)

Directives evaluated by `unified_controller.execute_directive(text)`:
- Conversational greetings, identity queries, capabilities, time, and date.
- System diagnostics telemetry and battery status.
- "Clean RAM" / "Optimize memory" -> Active Win32 RAM purge.
- Volume commands ("volume up", "volume down", "mute").
- Window controls ("minimize all", "lock laptop", "screenshot").
- "Open antigravity and go to jarvis project and prompt it to make it better" -> Triggers Antigravity autonomous bridge.
- Application launches ("open chrome", "open spotify", "launch vscode", "open notepad").
- Application closures ("close discord", "terminate chrome").
