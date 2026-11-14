# J.A.R.V.I.S. MARK XI — UI SPECIFICATION & COMMAND HUD

**Module:** `apps/desktop/src/pages/JarvisCommandCore.tsx` & `apps/desktop/src/components/widgets/`  
**Framework:** React 18, Vite 5, TailwindCSS, Framer Motion, Three.js  
**Target Version:** MARK XI  

---

## 1. Visual Design Language

- **Primary Canvas:** Pitch Black `#000000` with subtle deep Navy `#02050e` backdrops.
- **Accent Holography:** Electric Cyan `#06b6d4` / `#22d3ee` with cyan glow shadows `rgba(6,182,212,0.35)`.
- **Alert States:**
  - Success / Active: Emerald `#10b981`
  - High Memory / Warning: Amber `#f59e0b`
  - Error / Interrupt: Rose `#f43f5e`
  - Neural Telemetry: Electric Violet `#8b5cf6`

---

## 2. Holographic Particle Core

- **States (11 States):** `boot`, `idle`, `listening`, `thinking`, `speaking`, `executing`, `researching`, `success`, `error`, `warning`, `hibernating`.
- **Zero-Churn Optimization:**
  - Bloom render targets scaled to 50% resolution, saving ~90MB GPU buffer memory.
  - Automatically suspends `requestAnimationFrame` when the window or tab is hidden (`document.visibilityState === 'hidden'`), dropping CPU/GPU usage to 0%.
- **Optical Gesture Integration:**
  - MediaPipe Hands tracking via dedicated Web Worker.
  - Interactive hand orbit, pinch to condense particles, and open palm to expand holographic radius.

---

## 3. Pop-Up Widgets & Productivity Tools

1. **Task Schedule Planner (`TaskScheduleWidget.tsx`):**
   - Sequential task planning with target evening deadlines.
   - Persistent `localStorage` state across app reloads.
2. **Chronometric Focus Timer (`TimerWidget.tsx`):**
   - Pomodoro and focus session timer with start/pause/reset.
   - Built-in Web Audio API alarm sound on completion.
3. **Atmospheric Weather Widget (`WeatherWidget.tsx`):**
   - Temperature, humidity, wind velocity, and condition forecasting.
4. **Desktop Activity Overlay HUD (`ActivityOverlayHUD.tsx`):**
   - Real-time display of running desktop applications, PIDs, and active RAM consumption.
   - Quick termination buttons with confirmation.
