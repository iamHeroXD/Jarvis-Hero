# J.A.R.V.I.S. MARK XI — OPEN ISSUES & KNOWN CONSTRAINTS

**Target Version:** MARK XI  
**Date:** November 14, 2026  

---

## 1. Known Technical Constraints

### 1.1 Intel UHD Integrated Graphics VRAM Ceiling
- **Observation:** On 8GB systems sharing RAM with Intel UHD integrated graphics, running full-resolution post-processing bloom across 4K displays can consume up to 250 MB of shared system memory.
- **Current Mitigation:** Bloom render targets are clamped to 50% resolution, and animation frames hibernate when the window is hidden.
- **Status:** Mitigated. Long-term: Add WebGL context loss handling and dynamic resolution scaling for low-power battery states.

### 1.2 Windows Store (UWP) Direct HWND Binding
- **Observation:** Certain Microsoft Store UWP applications (e.g. Modern CalculatorApp) host views in `ApplicationFrameHost.exe`. Polling the child process PID requires inspecting the parent frame handle.
- **Current Mitigation:** Handled via URI protocol schemes (e.g. `calculator:`, `ms-settings:`) which Windows routes natively.
- **Status:** Functional. Long-term: Expand UIAutomation COM bindings for deeper UWP element inspection.

### 1.3 Offline Operation Depth
- **Observation:** When internet connectivity is absent, local intent directives (volume, memory, app launch, diagnostics, date/time) execute instantaneously, but deep creative reasoning cannot query Gemini.
- **Current Mitigation:** Fast-path local directive parser handles 80% of common laptop operations with zero cloud dependencies.
- **Status:** Architecture compliant with 8GB host budget.
