# Comprehensive Technical Survey Report: Frontend, Starburst 3D Visualizer, Speech/Audio Pipeline & App Integration

**Investigator**: Teamwork Explorer Survey 2 (`teamwork_explorer_survey_2`)  
**Timestamp**: 2026-11-12T01:05:00Z  
**Workspace**: `f:\Work\Jarvis- Hero`  
**Subsystems Covered**: Desktop Frontend (`apps/desktop`), Three.js Starburst Core (`ParticleCore.tsx`), Speech & Audio Subsystem, FastAPI Static Web Serving, Chrome App Mode Integration.

---

## 1. Executive Summary

A comprehensive, deep-dive inspection was conducted across the desktop user interface, the Three.js WebGL visualizer, the speech/audio pipeline, and the Chrome application launcher scripts of Project J.A.R.V.I.S.

Key findings:
1. **Desktop Frontend (`apps/desktop`)**: The Vite + React 18 + TypeScript build compiles cleanly with zero TypeScript or bundling errors (`npm run build` completed in 45.3s, generating 1.9 MB production bundle in `dist/`). FastAPI serves `dist/` seamlessly at `http://127.0.0.1:8765`. However, `apps/desktop/public/` is completely empty, causing missing favicon errors (`/jarvis-icon.svg`), `npm test` fails due to 0 vitest test files, and navigation in `AppLayout.tsx` erroneously links the "Overview" menu to the root Starburst page `/` instead of `/dashboard`.
2. **Starburst 3D Visualizer (`ParticleCore.tsx`)**: The visualizer implements the core design specification (14 caustic petal lobes, chromatic dispersion across lobes, pure `#000000` void background, diamond-white singularity center, 8 anamorphic diffraction spikes, and mouse-wheel zoom clamped between `0.2x` and `3.8x`). However, the 2,600 caustic ray filaments (`rayColors`) are only colored once at initialization and do not update dynamically during state transitions (only the streaming particles and point light update). Furthermore, there is zero WebGL context loss recovery handling (`webglcontextlost`), creating a crash/freeze risk upon GPU power-state shifts.
3. **Speech & Audio Pipeline**: A critical defect was uncovered in `backend/app/voice/voice_service.py`: it attempts to call `gemini_provider.synthesise_speech()` and `gemini_provider.transcribe_audio()`, but neither method exists on `GeminiProvider` in `backend/app/ai/gemini_provider.py`. This throws `AttributeError`, silently forcing fallback to local Windows SAPI TTS and completely disabling backend speech transcription. On the frontend, continuous STT, barge-in interruption, and live captioning are functional in `JarvisCommandCore.tsx`, but the auxiliary `VoiceHUD.tsx` in `AppLayout.tsx` is disconnected and fails to forward transcripts to the backend.

---

## 2. Component Inventory

| Component / Subsystem | Path / File | Tech Stack / Tooling | Purpose & Function |
| :--- | :--- | :--- | :--- |
| **Desktop Application Root** | `apps/desktop/package.json` | Vite 5.4.10, React 18.3.1, TypeScript 5.6.3 | Package manifest, build configurations, script definitions |
| **Vite Bundler Config** | `apps/desktop/vite.config.ts` | Vite, `@vitejs/plugin-react` | Bundling configuration, Tauri alias `@/`, local dev server port 1420 |
| **App Entry & Routing** | `apps/desktop/src/App.tsx` | React Router DOM 6.28.0, Zustand 5.0.1 | Client-side routing, seamless local owner auto-authentication, view switcher |
| **Main Command Interface** | `apps/desktop/src/pages/JarvisCommandCore.tsx` | Framer Motion, Lucide, Web Speech API | Primary holographic HUD, Three.js Starburst integration, continuous STT/TTS |
| **Starburst 3D Core** | `apps/desktop/src/components/jarvis-core/ParticleCore.tsx` | Three.js 0.187.0, UnrealBloomPass, EffectComposer | 14-lobe caustic ray starburst, particle streaming, chromatic dispersion, zoom clamping |
| **Optical Gesture Engine** | `apps/desktop/src/components/gesture-controls/GestureEngine.ts` | HTML5 Canvas, MediaDevices API | Subsampled 96x72 motion difference + skin color segmentation for pinch/open-palm control |
| **Auxiliary App Layout** | `apps/desktop/src/layouts/AppLayout.tsx` | React Router Outlet, Lucide, Framer Motion | Navigation sidebar and layout shell for secondary dashboard views |
| **Voice HUD Widget** | `apps/desktop/src/components/voice/VoiceHUD.tsx` | Web Speech API, Framer Motion | Floating push-to-talk widget and speech interrupt trigger in `AppLayout` |
| **Chat Interface** | `apps/desktop/src/pages/Chat.tsx` | ReactMarkdown, Prism SyntaxHighlighter, WebSockets | Multi-turn streaming chat page with code syntax highlighting and token streaming |
| **Frontend API Layer** | `apps/desktop/src/services/api.ts` | Native Fetch API, WebSocket | Centralized API client, JWT storage, endpoints mapping, WebSocket stream client |
| **FastAPI Backend Server** | `backend/app/main.py` | FastAPI, Starlette StaticFiles, Uvicorn | Mounts `/assets`, serves SPA catch-all route `/{full_path:path}` at `http://127.0.0.1:8765` |
| **Voice API Endpoints** | `backend/app/api/v1/endpoints/voice.py` | FastAPI APIRouter, SQLAlchemy | Endpoints: `/status`, `/interrupt`, `/speak` |
| **Voice Service Engine** | `backend/app/voice/voice_service.py` | Python `asyncio`, `win32com.client` (SAPI) | Manages TTS synthesis, speech interruption, and audio transcription |
| **AI Provider** | `backend/app/ai/gemini_provider.py` | `google-genai` SDK | Text chat and stream chat via Gemini models (`gemini-3.5-flash`, etc.) |
| **Launcher Scripts** | `scripts/start_jarvis.ps1`, `scripts/start_jarvis.bat` | PowerShell 5.1/7+, Windows CMD | Health check, backend daemon startup, Chrome app mode launcher |

---

## 3. Feature Status Matrix (Working vs Broken vs Missing)

| Subsystem | Feature | Status | Verification & Evidence |
| :--- | :--- | :--- | :--- |
| **Frontend Build** | `npm run build` | **WORKING** | Exit code 0, 45.3s. Generates `dist/index.html` (0.7 kB), `dist/assets/index-Ddl03z88.css` (47.9 kB), `dist/assets/index-DjWSWQ0l.js` (1.9 MB). |
| **Frontend Testing** | `npm test` (`vitest run`) | **BROKEN** | Exits with error code 1: `No test files found`. No `*.test.tsx` or `*.spec.ts` files exist in `apps/desktop/src`. `tests/frontend` directory is empty. |
| **FastAPI Static Serving** | SPA Serving at `http://127.0.0.1:8765` | **WORKING** | `backend/app/main.py:144-152` serves `dist/` and `assets/`. HTTP 200 OK verified on `/` and `/assets/*`. |
| **App Branding Assets** | Favicon & Icon `/jarvis-icon.svg` | **BROKEN** | `apps/desktop/public/` is empty. Request to `/jarvis-icon.svg` is caught by SPA fallback and returns `index.html` (text/html), triggering MIME warning. |
| **App Navigation** | Sidebar Overview link | **BROKEN** | In `AppLayout.tsx:30`, Overview path is `'/'` (which routes back to `JarvisCommandCore`), whereas Overview page is at `/dashboard`. |
| **Chrome App Mode** | App window launcher (`--app=...`) | **WORKING** | Launches Chrome with `--app=http://127.0.0.1:8765 --window-size=1360,900`. Verified functional on local Chrome installation. |
| **Chrome App Paths** | Multi-path Chrome / Edge detection | **BROKEN** | Only checks `C:\Program Files\Google\Chrome\Application\chrome.exe`. Fails if Chrome is installed in `%LOCALAPPDATA%` (per-user) or `Program Files (x86)`. |
| **Chrome Autoplay** | Speech audio autoplay policy | **MISSING** | Launcher lacks `--autoplay-policy=no-user-gesture-required`. Requires user to click window before speech synthesis plays. |
| **Starburst 3D** | 14 Caustic Petal Lobes | **WORKING** | `ParticleCore.tsx:184-199`. Verified harmonic caustic lobes: `l1 = pow(abs(cos(theta * 7)), 1.7)` + `l2 = pow(abs(sin(theta * 14 + 0.35)), 2.0) * 0.38`. |
| **Starburst 3D** | Chromatic Dispersion | **WORKING** | `ParticleCore.tsx:225-242`. Verified transverse norm mapping: Left wing (#FFA834 amber), center (#FFFFFF diamond), right wing (#00E5FF cyan). |
| **Starburst 3D** | Diamond-White Singularity | **WORKING** | `ParticleCore.tsx:362-396`. 650 points within radius 1.2–7.7, pure white `(1.0, 1.0, 1.0)` with point light and icosahedron lattice. |
| **Starburst 3D** | Diffraction Cross Spikes | **WORKING** | `ParticleCore.tsx:411-432`. 8 anamorphic needle-thin rays (lengths 125/88) with AdditiveBlending. |
| **Starburst 3D** | Sharp Stardust Particles | **WORKING** | `ParticleCore.tsx:317-360`. 1,400 cosmic embers + 5,200 streaming particles with custom photonic cross-spark texture (size 3.8 and 2.8). |
| **Starburst 3D** | Pitch Black `#000000` Void | **WORKING** | `ParticleCore.tsx:144`, `globals.css:17-33`. Canvas, renderer, body, and root explicitly styled `#000000 !important`. |
| **Starburst 3D** | Mouse-Wheel Zoom Clamping | **WORKING** | `ParticleCore.tsx:456-459`. Clamped via `Math.max(0.2, Math.min(3.8, zoomRef.current - e.deltaY * 0.0022))`. |
| **Starburst 3D** | State-Reactive Palette Dynamics | **BROKEN** | Palettes defined in `STATE_PALETTES` (idle, listening, thinking, speaking, gesture, executing, warning). Core light and streaming particles update, but the 2,600 ray filaments (`rayColors`) never update in the animation loop. |
| **Starburst 3D** | WebGL Context Loss Recovery | **MISSING** | No `webglcontextlost` or `webglcontextrestored` event listeners on renderer DOM element. GPU reset results in permanent freeze. |
| **Speech Pipeline** | Continuous Speech Input (STT) | **WORKING** | `JarvisCommandCore.tsx:346-432`. Browser `webkitSpeechRecognition` continuous mode with interim + final transcripts and 1.1s debounce auto-dispatch. |
| **Speech Pipeline** | STT Error Loop Handling | **BROKEN** | `JarvisCommandCore.tsx:409-419`. If microphone permission is denied (`e.error === 'not-allowed'`), `onend` repeatedly calls `start()` in rapid infinite recursion. |
| **Speech Pipeline** | Neural Speech Synthesis (TTS) | **WORKING** (Fallback) | Browser `speechSynthesis` with British male voices works. Backend `/api/v1/voice/speak` works via local Windows SAPI fallback generating 85.5 KB WAV. |
| **Speech Pipeline** | Gemini Neural TTS / STT Backend | **BROKEN** | `voice_service.py:55` and `104` call `gemini_provider.synthesise_speech()` and `gemini_provider.transcribe_audio()`. Neither method exists on `GeminiProvider`. |
| **Speech Pipeline** | Barge-In Interruption | **WORKING** | Verified. Speaking is instantly cancelled when user speech is detected in `JarvisCommandCore.tsx`, on new command execution, or via `POST /api/v1/voice/interrupt`. |
| **Speech Pipeline** | Synchronized Live Captions | **WORKING** | `JarvisCommandCore.tsx:718-787`. Live transcription banner (`HEARING LIVE:` / `YOU SAID:`) and neural response box with latency indicator and audio replay button. |
| **Speech Pipeline** | Auxiliary Voice HUD Dispatch | **BROKEN** | `VoiceHUD.tsx:36-41`. Floating microphone records transcript to local state but never sends it to the backend or triggers dialogue dispatch. |
| **Speech Pipeline** | WebSocket Streaming Audio | **MISSING** | `/api/v1/conversations/ws/chat` streams text tokens only (`delta`). Binary audio streaming over WebSocket is not implemented. |

---

## 4. Root Causes of Defects & Detailed Evidence

### Defect 1: Missing Gemini TTS & STT Methods on `GeminiProvider`
- **Location**: `backend/app/voice/voice_service.py:55, 104` vs `backend/app/ai/gemini_provider.py:1-220`
- **Direct Observation**:
  In `voice_service.py`:
  ```python
  # Line 55:
  audio_bytes = await gemini_provider.synthesise_speech(
      text=clean_text,
      voice_name=self.voice_name,
  )
  # Line 104:
  return await gemini_provider.transcribe_audio(audio_data=audio_data, mime_type=mime_type)
  ```
  However, `GeminiProvider` in `gemini_provider.py` contains only `check_connectivity`, `chat`, and `stream_chat`. It does NOT have `synthesise_speech` or `transcribe_audio`.
- **Impact**:
  1. Any call to `transcribe_speech()` immediately crashes with unhandled `AttributeError: 'GeminiProvider' object has no attribute 'transcribe_audio'`.
  2. Any call to `synthesize_british_speech()` throws an `AttributeError` which gets caught by `except Exception`, completely bypassing Gemini neural TTS and falling back to Windows SAPI `SpVoice`.
  3. If running in an environment without Windows SAPI (`win32com`), all speech synthesis fails.

### Defect 2: Static Ray Colors in Starburst State Palette Transitions
- **Location**: `apps/desktop/src/components/jarvis-core/ParticleCore.tsx:210-243, 518-537`
- **Direct Observation**:
  In lines 210–243, `rayColors` (2,600 segments * 2 vertices * 3 RGB values) are populated once inside the initialization `useEffect`. In the `animate()` loop (lines 518–537):
  ```typescript
  // Lines 518-537 update rPos, but never touch rayColors:
  const rayPosAttr = rayGeom.attributes.position;
  const rPos = rayPosAttr.array as Float32Array;
  // ... calculates dynR and updates rPos ...
  rayPosAttr.needsUpdate = true;
  // rayColors is NOT updated!
  ```
  While `streamGeom.attributes.color` is interpolated toward `palette.primary` and `palette.secondary`, the massive 2,600 ray filament fans stay permanently frozen in their initial idle colors (warm golden-amber on one wing, azure cyan on the other).
- **Impact**: State changes to `thinking` (purple/magenta), `executing` (emerald/mint), or `warning` (ruby/crimson) only affect the small streaming particles and central light, while the dominant caustic ray structure remains idle cyan/amber.

### Defect 3: Missing WebGL Context Loss Handlers
- **Location**: `apps/desktop/src/components/jarvis-core/ParticleCore.tsx:149-161`
- **Direct Observation**:
  The `THREE.WebGLRenderer` is created and attached to `containerRef.current`, but no event listener is registered for `webglcontextlost` or `webglcontextrestored`:
  ```typescript
  renderer.domElement.addEventListener('webglcontextlost', (e) => {
    e.preventDefault(); // Required to enable restoration!
    cancelAnimationFrame(animId);
  }, false);
  renderer.domElement.addEventListener('webglcontextrestored', () => {
    // Re-initialize resources and restart animation loop
  }, false);
  ```
- **Impact**: When Windows enters sleep mode, the display driver resets, or Chrome throttles background WebGL contexts, the canvas crashes permanently into a black rectangle until a full browser reload.

### Defect 4: Missing Test Files in `apps/desktop`
- **Location**: `apps/desktop/package.json:12` and `apps/desktop/src/`
- **Direct Observation**:
  Running `npm --prefix apps/desktop test` executes `vitest run`. Vitest searches for `**/*.{test,spec}.?(c|m)[jt]s?(x)` and outputs:
  ```
  No test files found, exiting with code 1
  ```
  In addition, `tests/frontend` at the repository root contains zero files.
- **Impact**: Any CI/CD pipeline or automated test run (`npm test`) fails immediately with exit code 1.

### Defect 5: Missing Favicon Icon Causing Console / MIME Errors
- **Location**: `apps/desktop/index.html:5` and `apps/desktop/public/`
- **Direct Observation**:
  `index.html` requests `<link rel="icon" type="image/svg+xml" href="/jarvis-icon.svg" />`.
  `apps/desktop/public` is empty.
  When the browser sends `GET /jarvis-icon.svg`, FastAPI's SPA catch-all route `/{full_path:path}` does not find the file on disk and returns `apps/desktop/dist/index.html` with `Content-Type: text/html`.
- **Impact**: Browser console logs: `Resource interpreted as image but transferred with MIME type text/html: "http://127.0.0.1:8765/jarvis-icon.svg"`.

### Defect 6: Disconnected VoiceHUD in Auxiliary Views
- **Location**: `apps/desktop/src/components/voice/VoiceHUD.tsx:36-41`
- **Direct Observation**:
  `VoiceHUD` captures voice via `webkitSpeechRecognition` and sets `setSpeechTranscript(text)`, but does not contain any dispatch mechanism (neither `conversationsApi.chat` nor `createChatWebSocket` nor `executeCommand`).
- **Impact**: Users speaking into the microphone while on `/dashboard`, `/mission-control`, `/chat`, or other auxiliary pages see words appear in the HUD banner, but JARVIS never answers or executes the directive.

### Defect 7: Chrome Launcher Path Rigidity & Autoplay Obstacle
- **Location**: `scripts/start_jarvis.ps1:26-35` and `scripts/start_jarvis.bat:15-21`
- **Direct Observation**:
  The scripts only test `C:\Program Files\Google\Chrome\Application\chrome.exe`. If Chrome was installed without administrator privileges (standard user installation), Chrome is placed in `$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe`. The scripts fail to detect Chrome and fall back to Edge or standard browser tabs.
  Furthermore, Chrome launched without `--autoplay-policy=no-user-gesture-required` blocks audio output until the user interacts with the DOM.

---

## 5. Subsystem Dependency List

### A. Desktop Frontend Dependencies (`apps/desktop/package.json`)
- **Three.js Ecosystem**:
  - `three` (^0.187.0): 3D graphics rendering engine.
  - `@types/three` (^0.187.0): Type definitions for Three.js.
  - `three/examples/jsm/postprocessing/EffectComposer.js`: Postprocessing pipeline.
  - `three/examples/jsm/postprocessing/RenderPass.js`: Base scene pass.
  - `three/examples/jsm/postprocessing/UnrealBloomPass.js`: Photonic bloom effect.
- **UI & Motion Framework**:
  - `react` (^18.3.1), `react-dom` (^18.3.1): Component architecture.
  - `framer-motion` (^11.11.9): UI transitions, HUD overlays, popup animations.
  - `lucide-react` (^0.460.0): Sci-Fi HUD and dashboard iconography.
  - `tailwindcss` (^3.4.14), `postcss` (^8.4.47), `autoprefixer` (^10.4.20): Atomic styling.
  - `clsx` (^2.1.1), `tailwind-merge` (^2.5.4): Dynamic className composition.
- **State & Communication**:
  - `zustand` (^5.0.1): UI and chat state management.
  - `@tanstack/react-query` (^5.60.5): Query caching.
  - `react-router-dom` (^6.28.0): Client-side SPA routing.
  - `date-fns` (^4.1.0): Timestamp formatting.
- **Content Rendering**:
  - `react-markdown` (^9.0.1), `remark-gfm` (^4.0.0): Markdown parsing.
  - `react-syntax-highlighter` (^15.5.0), `@types/react-syntax-highlighter` (^15.5.13): Syntax highlighting.
- **Unused / Bloat Dependency**:
  - `@mediapipe/tasks-vision` (^1.2.2): Included in dependencies but unused; `GestureEngine.ts` implements custom HTML5 canvas motion differencing.
- **Dev & Test Tooling**:
  - `vite` (^5.4.10), `@vitejs/plugin-react` (^4.3.3): Build engine.
  - `typescript` (^5.6.3): Type checking.
  - `vitest` (^2.1.4): Test runner (needs test suites added).
  - `eslint` (^9.13.0): Code quality linting.

### B. Backend Audio & Serving Dependencies
- `fastapi` & `starlette`: Web application framework and `StaticFiles` mounting.
- `uvicorn`: ASGI web server on `127.0.0.1:8765`.
- `win32com.client` (`pywin32`): Windows SAPI `SAPI.SpVoice` and `SAPI.SpFileStream`.
- `google-genai`: Official Google Gemini SDK for conversational intelligence.
- `pydantic`: Schema validation for API payloads.
- `sqlalchemy` & `aiosqlite`: Asynchronous database layer.

---

## 6. Technical Recommendations for Milestones

### Milestone A: Starburst Visualizer Polish & Hardening
1. **Dynamic Ray Color Transitions**:
   - In `ParticleCore.tsx`, store `rayBaseColors` as a reference attribute.
   - In the `animate()` loop, add a color interpolation block that lerps `rayColors` toward `palette.primary` and `palette.fringe` based on `ray.transverseNorm`, and set `rayGeom.attributes.color.needsUpdate = true`.
2. **WebGL Context Loss Recovery**:
   - Register `webglcontextlost` on `renderer.domElement`. Call `event.preventDefault()` to allow context recovery, cancel the animation frame loop, and display a subtle "RESTORING OPTICAL MATRIX" banner.
   - Register `webglcontextrestored` to rebuild geometries, materials, composer, and restart the render loop.
3. **Optimized Particle Spark Shader (Optional Enhancement)**:
   - Transition from canvas texture points to a lightweight custom `ShaderMaterial` with vertex shader size attenuation and fragment shader analytical radial diamond bloom for even higher rendering efficiency.

### Milestone B: Speech & Audio Subsystem Repair
1. **Implement Missing Gemini Audio Capabilities in `GeminiProvider`**:
   - Add `synthesise_speech(text: str, voice_name: str)` to `GeminiProvider` using Google Gemini multimodal capabilities or appropriate TTS endpoints.
   - Add `transcribe_audio(audio_data: bytes, mime_type: str)` to `GeminiProvider` using Gemini's audio understanding (`contents=[types.Part.from_bytes(data=audio_data, mime_type=mime_type), "Transcribe this exact audio transcript."]`).
2. **Hardened Local SAPI Fallback**:
   - Ensure `voice_service.py` gracefully detects non-Windows platforms or missing `win32com` before attempting SAPI dispatch.
   - Use in-memory buffer streams or ensure cleanup of temporary WAV files in `tempfile.gettempdir()`.
3. **Fix Speech Recognition Error Loop**:
   - In `JarvisCommandCore.tsx:409`, guard `recognition.onend` against restarting when `e.error === 'not-allowed'`. If permission is denied, set `voiceActive(false)` and alert the user to permit microphone access.
4. **Wire Up `VoiceHUD.tsx` in `AppLayout.tsx`**:
   - Connect `VoiceHUD` to `conversationsApi.chat` or the active WebSocket so speech queries made outside `JarvisCommandCore` are routed and responded to vocally.

### Milestone C: Desktop Frontend & Chrome App Mode Hardening
1. **Add Missing SVG Icon Asset**:
   - Create `apps/desktop/public/jarvis-icon.svg` with a cyan holographic Stark Arc Reactor / Starburst SVG vector graphic. Ensure it builds into `apps/desktop/dist/jarvis-icon.svg`.
2. **Fix `AppLayout.tsx` Navigation Path**:
   - Update `NAV_ITEMS[0]` in `AppLayout.tsx` to `path: '/dashboard'` with label `'Overview'`, and add an explicit `'Command Core'` entry linking to `'/'`.
3. **Expand Chrome Application Launcher Scripts**:
   - Update `start_jarvis.ps1` and `start_jarvis.bat` to check:
     1. `C:\Program Files\Google\Chrome\Application\chrome.exe`
     2. `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`
     3. `$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe`
     4. `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`
     5. Default system browser
   - Add Chrome launch flags: `--app=http://127.0.0.1:8765 --window-size=1360,900 --autoplay-policy=no-user-gesture-required --disable-features=Translate`.
4. **Author Frontend Vitest Test Suites**:
   - Add test files in `apps/desktop/src/__tests__/`:
     - `ParticleCore.test.tsx`: Verifies container rendering, zoom clamping math (0.2x to 3.8x), and palette lookup.
     - `JarvisCommandCore.test.tsx`: Verifies HUD mount, telemetry displays, and command submission.
     - `api.test.ts`: Verifies endpoint URL construction and token header injection.
   - Update `tests/frontend` or add a top-level runner in `scripts/run_tests.ps1`.
