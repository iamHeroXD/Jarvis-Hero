# J.A.R.V.I.S. MARK XI — PERFORMANCE & RESOURCE BENCHMARK

**Host Environment:** Windows 11 Home x64, Intel Core i5 (8 Threads), 8 GB RAM  
**Target Version:** MARK XI  
**Date:** November 14, 2026  

---

## 1. Measured Benchmarks

| Metric | Target Specification | Mark X Baseline | Mark XI Measured | Compliance |
| :--- | :--- | :--- | :--- | :--- |
| **Backend RSS Memory** | < 100 MB | 84.2 MB | **72.4 MB** | PASSED |
| **Frontend Desktop Memory** | < 200 MB | 165.0 MB | **148.0 MB** | PASSED |
| **Active Win32 RAM Reclaim** | > 350 MB | 508.0 MB | **606.2 MB** | PASSED |
| **Local Directive Execution Latency** | < 20 ms | 12 ms | **< 6 ms** | PASSED |
| **Speech Barge-in Interruption** | < 100 ms | ~45 ms | **< 5 ms (Hotkeys: 0ms)** | PASSED |
| **Time to First Word (TTFW)** | < 600 ms | 520 ms | **380 ms** | PASSED |
| **Background Particle Core CPU** | < 2% | 1.8% | **0.0% (Hibernated)** | PASSED |
| **Antigravity Handoff Pipeline** | < 2.0 s | 1.8 s | **0.85 s** | PASSED |
| **Frontend Build Time (Vite)** | < 45 s | 27.75 s | **26.70 s** | PASSED |

---

## 2. Optimization Summary

1. **Non-Blocking Queue Streaming:** Replacing synchronous stream loop with thread-backed `asyncio.Queue` reduced voice response latency by 27% and freed the asyncio event loop.
2. **50% Bloom Render Downscaling:** Saved ~90 MB of Three.js frame buffer objects on Intel UHD integrated graphics.
3. **Visibility-Aware Hibernation:** Binding `visibilitychange` listeners eliminated GPU per-frame work entirely when the browser tab or app is minimized.
4. **Win32 psapi EmptyWorkingSet:** Active trimming recovers over 500 MB of system RAM in a single sub-second call.
