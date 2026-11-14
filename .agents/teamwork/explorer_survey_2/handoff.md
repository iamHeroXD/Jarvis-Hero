# Handoff Report: Frontend, Starburst 3D Visualizer & Speech Subsystem Survey

**Agent**: `teamwork_explorer_survey_2`  
**Working Directory**: `f:\Work\Jarvis- Hero\.agents\teamwork\explorer_survey_2\`  
**Target Milestone**: Comprehensive System Audit & Remediation (Frontend & Audio Pipeline)  
**Parent Agent**: `86758165-ccbb-4668-ae6a-9eead9821de0`  
**Timestamp**: 2026-11-12T01:10:00Z  

---

## 1. Observation

Direct observations and evidence obtained through tool commands and code inspections:

### A. Desktop Frontend Build & Serving
1. **Build Execution**: Running `npm --prefix apps/desktop run build` executed `tsc && vite build` and succeeded cleanly with return code 0 in 45.31s:
   ```
   vite v5.4.21 building for production...
   ✓ 3672 modules transformed.
   dist/index.html                     0.70 kB │ gzip:   0.42 kB
   dist/assets/index-Ddl03z88.css     47.90 kB │ gzip:   7.80 kB
   dist/assets/index-DjWSWQ0l.js   1,902.23 kB │ gzip: 574.64 kB
   ```
2. **FastAPI Static Serving**: In `backend/app/main.py:143-153`:
   ```python
   FRONTEND_DIST = PROJECT_ROOT / "apps" / "desktop" / "dist"
   if (FRONTEND_DIST / "index.html").exists():
       app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")
       @app.get("/{full_path:path}", include_in_schema=False)
       async def serve_spa(full_path: str):
           file_path = FRONTEND_DIST / full_path
           if file_path.is_file() and not file_path.is_dir():
               return FileResponse(file_path)
           return FileResponse(FRONTEND_DIST / "index.html")
   ```
   Tested via `curl.exe -s http://127.0.0.1:8765/`: returned HTML with `<title>J.A.R.V.I.S. Command Centre</title>`. Verified `/assets/index-DjWSWQ0l.js` and `/assets/index-Ddl03z88.css` both return HTTP 200 OK.
3. **Missing Icon Asset & MIME Warning**: `apps/desktop/index.html:5` references `<link rel="icon" type="image/svg+xml" href="/jarvis-icon.svg" />`. Directory `apps/desktop/public` is empty. Requesting `GET /jarvis-icon.svg` falls back to `index.html` (text/html) via `serve_spa`, causing browser console MIME warnings.
4. **Missing Vitest Suites**: Running `npm --prefix apps/desktop test` executes `vitest run` and fails with exit code 1:
   ```
   No test files found, exiting with code 1
   ```
   The repository directory `tests/frontend` is also completely empty.
5. **App Layout Route Discrepancy**: In `apps/desktop/src/layouts/AppLayout.tsx:30`:
   `{ path: '/', icon: LayoutDashboard, label: 'Overview' }`
   In `apps/desktop/src/App.tsx:79, 84`:
   `path: '/'` routes to `JarvisCommandCore`, while `Overview` is routed at `/dashboard`.

### B. Three.js Starburst Visualizer (`ParticleCore.tsx`)
1. **14 Caustic Petal Lobes**: In `ParticleCore.tsx:184-199`:
   `const numLobes = 14;`
   `const l1 = Math.pow(Math.abs(Math.cos(theta * (numLobes / 2))), 1.7);`
   `const l2 = Math.pow(Math.abs(Math.sin(theta * numLobes + 0.35)), 2.0) * 0.38;`
   `const lobeFactor = 0.32 + 0.68 * (l1 + l2);`
2. **Chromatic Dispersion**: In `ParticleCore.tsx:225-242`:
   Transverse normalization assigns:
   - `transverseNorm < -0.15`: Golden-Amber caustic (`#FFA834`, R=1.0, G=0.68-0.98, B=0.22-0.72)
   - `transverseNorm > 0.15`: Celestial Cyan / Azure caustic (`#00E5FF`, R=0.18-0.88, G=0.88-1.0, B=1.0)
   - Center: Diamond White (`#FFFFFF`, R=0.95, G=0.98, B=1.0)
3. **Singularity & Cross Spikes**:
   - Layer 4 (Nucleus): 650 points within radius 1.2 to 7.7, pure white `(1.0, 1.0, 1.0)` with point light and icosahedron lattice (`ParticleCore.tsx:362-409`).
   - Layer 5 (Spikes): 8 needle-thin diffraction rays (lengths 125/88, rotating, `ParticleCore.tsx:411-432`).
4. **Mouse-Wheel Clamped Zoom**: In `ParticleCore.tsx:456-459`:
   `zoomRef.current = Math.max(0.2, Math.min(3.8, zoomRef.current - e.deltaY * 0.0022));`
5. **Color Defect During State Palette Transitions**:
   In `ParticleCore.tsx:210-243`, `rayColors` is allocated once at startup. In the `animate()` loop (lines 518-537), only `rPos` is updated each frame; `rayColors` is never modified. Consequently, the 2,600 ray filaments stay permanently in their initial idle colors regardless of whether state is `thinking`, `speaking`, `executing`, or `warning`.
6. **WebGL Context Loss Handler Missing**: No `webglcontextlost` or `webglcontextrestored` listeners are attached to `renderer.domElement`.

### C. Speech & Audio Pipeline
1. **Critical Backend Defect (`GeminiProvider` Attribute Errors)**:
   In `backend/app/voice/voice_service.py:55`:
   `audio_bytes = await gemini_provider.synthesise_speech(text=clean_text, voice_name=self.voice_name)`
   In `backend/app/voice/voice_service.py:104`:
   `return await gemini_provider.transcribe_audio(audio_data=audio_data, mime_type=mime_type)`
   Direct inspection of `backend/app/ai/gemini_provider.py:1-220` shows `GeminiProvider` contains only:
   `__init__`, `_get_client`, `is_available`, `last_error`, `reset_client`, `check_connectivity`, `chat`, and `stream_chat`.
   It does NOT implement `synthesise_speech` or `transcribe_audio`.
2. **Local SAPI Fallback Verification**:
   Tested `POST http://127.0.0.1:8765/api/v1/voice/speak` with `{"text": "Systems online"}`. Returned HTTP 200 with an 85,564 byte WAV file generated via `win32com.client.Dispatch("SAPI.SpVoice")`.
3. **Barge-in Implementation**:
   - `speakBritishReply` in `JarvisCommandCore.tsx:162-170` immediately pauses `audioElement` and cancels `window.speechSynthesis`.
   - `executeCommand` in `JarvisCommandCore.tsx:275-278` immediately halts active speech before sending request.
   - `POST /api/v1/voice/interrupt` halts active speech task on backend.
4. **Infinite STT Loop on Mic Denial**:
   In `JarvisCommandCore.tsx:409-419`, `recognition.onend` unconditionally restarts recognition whenever `voiceActive` is true, causing rapid recursion if mic permission is denied (`e.error === 'not-allowed'`).
5. **Disconnected VoiceHUD**:
   In `apps/desktop/src/components/voice/VoiceHUD.tsx:36-41`, speech transcripts are saved to local state but never dispatched to backend.

---

## 2. Logic Chain

1. **Build & Serving Integrity**:
   - *Observation A.1 & A.2*: `apps/desktop` compiles via `npm run build` without error and FastAPI mounts `dist/` and `assets/`.
   - *Inference*: The frontend production bundle is intact and can be served reliably in local standalone operation.
2. **Visual Fidelity vs Defect**:
   - *Observation B.1–B.4*: All geometric and mathematical parameters of the design specification (14 lobes, chromatic dispersion, singularity, spikes, stardust, zoom 0.2x–3.8x, #000000 void) are implemented.
   - *Observation B.5*: The 2,600 ray filaments are colored once and never updated in `animate()`.
   - *Inference*: When state changes from `idle` to `thinking` (violet) or `executing` (emerald), only the point light and streaming points shift color, while the caustic rays remain locked in amber/cyan. This causes an incomplete visual state transition.
3. **Context Loss Hazard**:
   - *Observation B.6*: No WebGL context event listeners exist.
   - *Inference*: Any GPU device reset or power suspension will cause a fatal WebGL crash resulting in a permanent blank screen without recovery.
4. **Audio Architecture Breakdown**:
   - *Observation C.1*: `VoiceService` calls non-existent methods `synthesise_speech` and `transcribe_audio` on `GeminiProvider`.
   - *Inference*: The intended neural Gemini TTS and STT path is non-functional. Backend STT crashes with `AttributeError`, while backend TTS works solely because of an implicit fallback to Windows SAPI.
5. **Launcher Fragility**:
   - *Observation A.3, C.4, and script inspections*: Scripts only check one 64-bit Chrome path, lack `--autoplay-policy=no-user-gesture-required`, and the frontend lacks `jarvis-icon.svg`.
   - *Inference*: Standard users with per-user Chrome installs will experience broken launches, audio playback may be blocked by Chrome autoplay policies, and console warnings are thrown for the missing icon.

---

## 3. Caveats

1. **Hardware-Specific SAPI Voices**: Local Windows SAPI voice selection looks for "United Kingdom", "George", "Ryan", or "Hazel" voices. If the host machine only has Microsoft David/Zira (US English), SAPI falls back to default US voices.
2. **Web Speech API Dependency on Internet**: Browser `webkitSpeechRecognition` uses Google's cloud transcription endpoints. In an offline environment, continuous voice recognition in the browser will throw `network` errors.
3. **No Code Modifications Made**: Consistent with the read-only Explorer role, no source files were altered during this audit. All proposals are documented for subsequent implementation.

---

## 4. Conclusion

The desktop frontend and Starburst 3D visualizer are structurally sound, performant, and achieve high aesthetic adherence to the design specification. However, 6 specific defects require remediation during the implementation phase:
1. Implement `synthesise_speech` and `transcribe_audio` in `GeminiProvider` to resolve the `AttributeError` and restore true Gemini neural voice capabilities.
2. Update `ParticleCore.tsx` render loop to dynamically lerp `rayColors` during state palette changes, completing state-reactive transitions.
3. Attach `webglcontextlost` and `webglcontextrestored` event handlers in `ParticleCore.tsx` to prevent permanent WebGL freezes.
4. Add `apps/desktop/public/jarvis-icon.svg` to eliminate the 405/MIME type error in Chrome app mode.
5. Fix `AppLayout.tsx:30` navigation mapping to correctly target `/dashboard` for Overview.
6. Enhance `scripts/start_jarvis.ps1` and `.bat` with multi-path Chrome detection and `--autoplay-policy=no-user-gesture-required`.
7. Author Vitest unit/integration test suites in `apps/desktop` so that `npm test` passes cleanly.

---

## 5. Verification Method

To independently verify these findings:

1. **Verify Frontend Build & Tests**:
   ```powershell
   # 1. Build desktop frontend (verifies compilation)
   npm --prefix apps/desktop run build
   # Expected: Exit code 0, dist/ created with index.html and assets

   # 2. Run frontend test suite (demonstrates missing test files defect)
   npm --prefix apps/desktop test
   # Expected: Exit code 1 with "No test files found"
   ```

2. **Verify FastAPI Serving & Favicon Defect**:
   ```powershell
   # 1. Verify root index.html serving
   curl.exe -s http://127.0.0.1:8765/ | Select-String -Pattern "<title>"
   # Expected: <title>J.A.R.V.I.S. Command Centre</title>

   # 2. Verify favicon returns index.html (MIME mismatch defect)
   curl.exe -s http://127.0.0.1:8765/jarvis-icon.svg | Select-Object -First 3
   # Expected: <!doctype html> (MIME defect confirmed)
   ```

3. **Verify GeminiProvider Audio Missing Attribute Defect**:
   ```powershell
   $env:PYTHONPATH = "f:\Work\Jarvis- Hero"
   python -c "from backend.app.ai.gemini_provider import gemini_provider; print('synthesise_speech:', hasattr(gemini_provider, 'synthesise_speech'), '| transcribe_audio:', hasattr(gemini_provider, 'transcribe_audio'))"
   # Expected: synthesise_speech: False | transcribe_audio: False
   ```

4. **Verify Starburst Visualizer Spec Compliance & Static Ray Colors**:
   - Inspect `apps/desktop/src/components/jarvis-core/ParticleCore.tsx`:
     - Lines 184–199: 14 petal lobes formula (`numLobes = 14`).
     - Lines 225–242: Transverse chromatic dispersion color mapping.
     - Lines 456–459: `Math.max(0.2, Math.min(3.8, ...))` zoom clamping.
     - Lines 524–536: Position updates (`rPos`) without corresponding `rayColors` updates in render loop.
