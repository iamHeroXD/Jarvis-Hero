# J.A.R.V.I.S. MARK XI — STRATEGIC NEXT STEPS & FUTURE EVOLUTION

**Target Version:** MARK XI -> MARK XII  
**Owner:** Rohan  

---

## 1. Immediate Post-Deployment Roadmap

1. **Active Optical Gesture Expansion:**
   - Train custom MediaPipe hand gestures for media track scrubbing and volume dial rotation in air.
2. **Multi-Display Window Snapping:**
   - Extend `unified_computer_controller` with Win32 `MoveWindow` and `SetWindowPos` to support multi-monitor layouts (e.g. "snap Antigravity to left monitor, snap Chrome to right monitor").
3. **Automated Nightly Mission Watchdog:**
   - Configure a Windows Task Scheduler trigger that calls `/api/v1/projects/startup-briefing` at 07:30 AM to prepare daily deliverables.
4. **Offline Small Language Model (SLM) Evaluation:**
   - Prototype quantized 1-bit or 2-bit SLMs (<1.2 GB RAM footprint) purely for offline conversational fallback on Intel Core i5 CPUs.
