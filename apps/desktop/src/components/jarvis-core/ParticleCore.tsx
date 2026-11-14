import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';

export type CoreState =
  | 'idle'
  | 'listening'
  | 'processing'
  | 'thinking'
  | 'speaking'
  | 'executing'
  | 'researching'
  | 'waiting_for_approval'
  | 'error'
  | 'recovering'
  | 'success'
  | 'gesture'
  | 'warning';

interface ParticleCoreProps {
  state?: CoreState;
  particleCount?: number;
  handX?: number;
  handY?: number;
  isPinching?: boolean;
  expansion?: number;
  audioLevel?: number;
  performanceMode?: 'eco' | 'balanced' | 'turbo';
}

interface PaletteColors {
  core: THREE.Color;
  primary: THREE.Color;
  secondary: THREE.Color;
  fringe: THREE.Color;
}

const STATE_PALETTES: Record<CoreState, PaletteColors> = {
  idle: {
    core: new THREE.Color(1.0, 1.0, 1.0),
    primary: new THREE.Color(0.0, 0.94, 1.0),      // Electric Cyan
    secondary: new THREE.Color(1.0, 0.72, 0.22),   // Golden Amber
    fringe: new THREE.Color(0.65, 0.38, 1.0),      // Prismatic Violet
  },
  listening: {
    core: new THREE.Color(1.0, 1.0, 1.0),
    primary: new THREE.Color(0.2, 0.75, 1.0),      // Azure Sky
    secondary: new THREE.Color(0.0, 0.96, 1.0),    // Electric Cyan
    fringe: new THREE.Color(0.55, 0.92, 1.0),      // Ice Blue
  },
  processing: {
    core: new THREE.Color(0.95, 1.0, 1.0),
    primary: new THREE.Color(0.0, 0.88, 1.0),      // High-frequency Cyan
    secondary: new THREE.Color(0.2, 0.55, 1.0),    // Cobalt Ray
    fringe: new THREE.Color(0.4, 0.85, 1.0),       // Glacial Cyan
  },
  thinking: {
    core: new THREE.Color(1.0, 0.92, 1.0),
    primary: new THREE.Color(0.75, 0.42, 1.0),     // Quantum Violet
    secondary: new THREE.Color(0.96, 0.32, 0.75),  // Magenta Pink
    fringe: new THREE.Color(0.52, 0.18, 0.95),     // Deep Amethyst
  },
  speaking: {
    core: new THREE.Color(1.0, 1.0, 1.0),
    primary: new THREE.Color(1.0, 0.82, 0.28),     // Solar Gold
    secondary: new THREE.Color(0.25, 0.92, 1.0),   // Cyan Harmonic
    fringe: new THREE.Color(1.0, 0.42, 0.12),      // Solar Flare Coral
  },
  gesture: {
    core: new THREE.Color(1.0, 1.0, 0.92),
    primary: new THREE.Color(0.98, 0.74, 0.16),    // Amber Gold
    secondary: new THREE.Color(1.0, 0.54, 0.1),    // Warm Orange
    fringe: new THREE.Color(1.0, 0.92, 0.42),      // Pale Gold
  },
  executing: {
    core: new THREE.Color(0.92, 1.0, 0.95),
    primary: new THREE.Color(0.06, 0.88, 0.52),    // Matrix Emerald
    secondary: new THREE.Color(0.2, 0.96, 0.76),   // Mint Green
    fringe: new THREE.Color(0.0, 0.96, 1.0),       // Cyan Flare
  },
  researching: {
    core: new THREE.Color(0.95, 0.95, 1.0),
    primary: new THREE.Color(0.12, 0.48, 1.0),     // Deep Sapphire
    secondary: new THREE.Color(0.0, 0.92, 0.95),   // Aquamarine
    fringe: new THREE.Color(0.45, 0.22, 1.0),      // Royal Violet
  },
  waiting_for_approval: {
    core: new THREE.Color(1.0, 0.98, 0.9),
    primary: new THREE.Color(1.0, 0.72, 0.0),      // Safety Amber
    secondary: new THREE.Color(1.0, 0.45, 0.05),   // Incandescent Orange
    fringe: new THREE.Color(1.0, 0.85, 0.3),       // Radiant Gold
  },
  error: {
    core: new THREE.Color(1.0, 0.92, 0.92),
    primary: new THREE.Color(0.96, 0.22, 0.22),    // Ruby Red
    secondary: new THREE.Color(1.0, 0.42, 0.15),   // Flare Coral
    fringe: new THREE.Color(0.85, 0.08, 0.25),     // Crimson
  },
  warning: {
    core: new THREE.Color(1.0, 0.92, 0.92),
    primary: new THREE.Color(0.96, 0.24, 0.24),    // Ruby Red
    secondary: new THREE.Color(0.98, 0.58, 0.1),   // Amber
    fringe: new THREE.Color(1.0, 0.18, 0.38),      // Crimson
  },
  recovering: {
    core: new THREE.Color(0.95, 1.0, 0.98),
    primary: new THREE.Color(0.35, 0.75, 1.0),     // Restorative Cyan
    secondary: new THREE.Color(0.2, 0.92, 0.65),   // Healing Mint
    fringe: new THREE.Color(0.65, 0.45, 1.0),      // Soft Amethyst
  },
  success: {
    core: new THREE.Color(1.0, 1.0, 1.0),
    primary: new THREE.Color(0.0, 1.0, 0.65),      // Emerald Brilliance
    secondary: new THREE.Color(0.0, 0.92, 1.0),    // Electric Cyan
    fringe: new THREE.Color(0.75, 1.0, 0.45),      // Aurora Lime
  },
};

/**
 * Creates ultra-sharp diamond photonic spark texture.
 * Ensures individual particles sparkle cleanly without blending into a flat white blob.
 */
function createPhotonicSparkTexture(): THREE.CanvasTexture {
  const size = 64;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d')!;

  const center = size / 2;
  const grad = ctx.createRadialGradient(center, center, 0, center, center, center);
  grad.addColorStop(0.0, 'rgba(255, 255, 255, 1.0)');
  grad.addColorStop(0.18, 'rgba(255, 255, 255, 0.95)');
  grad.addColorStop(0.42, 'rgba(255, 255, 255, 0.45)');
  grad.addColorStop(0.72, 'rgba(255, 255, 255, 0.1)');
  grad.addColorStop(1.0, 'rgba(0, 0, 0, 0.0)');

  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, size, size);

  // Cross diffraction highlight
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.65)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(center, 4);
  ctx.lineTo(center, size - 4);
  ctx.moveTo(4, center);
  ctx.lineTo(size - 4, center);
  ctx.stroke();

  const texture = new THREE.CanvasTexture(canvas);
  texture.generateMipmaps = false;
  texture.minFilter = THREE.LinearFilter;
  return texture;
}

export default function ParticleCore({
  state = 'idle',
  particleCount = 5200,
  handX = 0,
  handY = 0,
  isPinching = false,
  expansion = 1.0,
  audioLevel = 0,
  performanceMode = 'balanced',
}: ParticleCoreProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  const handXRef = useRef(handX);
  const handYRef = useRef(handY);
  const isPinchingRef = useRef(isPinching);
  const expansionRef = useRef(expansion);
  const audioLevelRef = useRef(audioLevel);
  const stateRef = useRef(state);
  const zoomRef = useRef(1.0);
  const mouseDragRef = useRef({ isDown: false, lastX: 0, lastY: 0, rotX: 0, rotY: 0 });

  useEffect(() => { handXRef.current = handX; }, [handX]);
  useEffect(() => { handYRef.current = handY; }, [handY]);
  useEffect(() => { isPinchingRef.current = isPinching; }, [isPinching]);
  useEffect(() => { expansionRef.current = expansion; }, [expansion]);
  useEffect(() => { audioLevelRef.current = audioLevel; }, [audioLevel]);
  useEffect(() => { stateRef.current = state; }, [state]);

  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;
    const width = container.clientWidth || window.innerWidth;
    const height = container.clientHeight || window.innerHeight;

    // ── 1. WebGL Scene & Camera Setup (Pure Pitch Black Void) ──────────────────
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000000);

    const camera = new THREE.PerspectiveCamera(46, width / height, 0.1, 3000);
    camera.position.z = 240;

    const renderer = new THREE.WebGLRenderer({
      alpha: false,
      antialias: performanceMode === 'turbo',
      powerPreference: 'high-performance',
    });
    renderer.setSize(width, height);
    // Dynamic memory-budget pixel ratio (conserves shared RAM on Intel integrated GPU)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, performanceMode === 'eco' ? 0.85 : performanceMode === 'balanced' ? 1.25 : 1.5));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;

    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // ── 2. Cinematic Balanced Postprocessing Bloom (Downsampled to 1/2 for 75% less FBO RAM) ──
    const composer = new EffectComposer(renderer);
    const renderPass = new RenderPass(scene, camera);
    composer.addPass(renderPass);

    const bloomStrength = performanceMode === 'eco' ? 0.22 : performanceMode === 'turbo' ? 0.65 : 0.48;
    const bloomPass = new UnrealBloomPass(
      new THREE.Vector2(Math.floor(width / 2), Math.floor(height / 2)),
      bloomStrength, // Controlled bloom strength (no giant white sun washout)
      0.22, // Tight specular halo radius
      0.76  // High threshold so only intense specular sparks bloom softly
    );
    composer.addPass(bloomPass);

    const sparkTex = createPhotonicSparkTexture();

    // ── 3. Layer 1: Prismatic Striated Ray Filaments (14 Optical Lobe Fans) ───
    const rayCount = performanceMode === 'eco' ? 1600 : performanceMode === 'turbo' ? 2800 : 2200;
    const rayGeom = new THREE.BufferGeometry();
    const rayPositions = new Float32Array(rayCount * 2 * 3);
    const rayColors = new Float32Array(rayCount * 2 * 3);
    const rayBaseAngles: { theta: number; phi: number; lobeFactor: number; lenMult: number; transverseNorm: number }[] = [];

    const numLobes = 14; // 14 organic prismatic starburst petals (matching reference image)
    for (let r = 0; r < rayCount; r++) {
      const baseTheta = (r / rayCount) * Math.PI * 2;
      const jitter = (Math.random() - 0.5) * 0.025;
      const theta = baseTheta + jitter;
      const phi = ((Math.random() - 0.5) * 0.35) * Math.PI;

      // Harmonic 14-lobe caustic shape calculation
      const lobeWidth = (Math.PI * 2) / numLobes;
      const lobeCenter = Math.round(theta / lobeWidth) * lobeWidth;
      const deltaTheta = theta - lobeCenter;
      const transverseNorm = Math.max(-1.0, Math.min(1.0, deltaTheta / (lobeWidth * 0.5)));

      // Caustic bell envelope with delicate striation ripples
      const lobeEnv = Math.exp(-Math.pow(transverseNorm * 1.6, 2));
      const harmonicFlare = Math.pow(Math.abs(Math.cos(theta * (numLobes / 2))), 1.8);
      const lobeFactor = 0.28 + 0.72 * (0.65 * lobeEnv + 0.35 * harmonicFlare);
      const lenMult = 0.88 + Math.random() * 0.24;

      rayBaseAngles.push({ theta, phi, lobeFactor, lenMult, transverseNorm });

      // Core root vertex: offset from center (r = 5.0 to 11.0) to prevent additive white burnout
      const rInner = 5.0 + Math.random() * 6.0;
      rayPositions[r * 6] = rInner * Math.cos(theta) * Math.cos(phi);
      rayPositions[r * 6 + 1] = rInner * Math.sin(theta) * Math.cos(phi);
      rayPositions[r * 6 + 2] = rInner * Math.sin(phi);

      // Core root color: Soft translucent Diamond White / Ice Blue
      rayColors[r * 6] = 0.88;
      rayColors[r * 6 + 1] = 0.94;
      rayColors[r * 6 + 2] = 1.0;

      // Outer ray tip
      const baseOuterR = 92 * lobeFactor * lenMult;
      rayPositions[r * 6 + 3] = baseOuterR * Math.cos(theta) * Math.cos(phi);
      rayPositions[r * 6 + 4] = baseOuterR * Math.sin(theta) * Math.cos(phi);
      rayPositions[r * 6 + 5] = baseOuterR * Math.sin(phi);

      // Chromatic dispersion across transverse width of each petal lobe:
      // Left wing: Warm Golden-Amber (#FFA834 / #FF9020)
      // Center: Brilliant Diamond White (#FFFFFF)
      // Right wing: Electric Cyan / Iridescent Azure (#00E5FF / #70A1FF)
      if (transverseNorm < -0.15) {
        // Golden Amber Caustic
        const t = Math.abs(transverseNorm);
        rayColors[r * 6 + 3] = 1.0;
        rayColors[r * 6 + 4] = 0.65 + (1.0 - t) * 0.28;
        rayColors[r * 6 + 5] = 0.20 + (1.0 - t) * 0.45;
      } else if (transverseNorm > 0.15) {
        // Celestial Cyan / Azure Caustic
        const t = Math.abs(transverseNorm);
        rayColors[r * 6 + 3] = 0.15 + (1.0 - t) * 0.65;
        rayColors[r * 6 + 4] = 0.85 + (1.0 - t) * 0.15;
        rayColors[r * 6 + 5] = 1.0;
      } else {
        // Core White Spine
        rayColors[r * 6 + 3] = 1.0;
        rayColors[r * 6 + 4] = 1.0;
        rayColors[r * 6 + 5] = 1.0;
      }
    }

    rayGeom.setAttribute('position', new THREE.BufferAttribute(rayPositions, 3));
    rayGeom.setAttribute('color', new THREE.BufferAttribute(rayColors, 3));

    const rayMat = new THREE.LineBasicMaterial({
      vertexColors: true,
      transparent: true,
      opacity: 0.48, // Silky translucent filaments (no blinding additive glare)
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    const starburstRays = new THREE.LineSegments(rayGeom, rayMat);
    scene.add(starburstRays);

    // ── 4. Layer 2: Distinct Photonic Streaming Sparks ───────────────
    const streamCount = performanceMode === 'eco' ? 1400 : performanceMode === 'turbo' ? 4200 : 2400;
    const streamGeom = new THREE.BufferGeometry();
    const streamPositions = new Float32Array(streamCount * 3);
    const streamColors = new Float32Array(streamCount * 3);

    for (let i = 0; i < streamCount; i++) {
      const rayIdx = Math.floor(Math.random() * rayCount);
      const progress = 0.05 + Math.random() * 0.95;
      const offset = (Math.random() - 0.5) * 1.8;

      const ray = rayBaseAngles[rayIdx];
      const maxR = 92 * ray.lobeFactor * ray.lenMult;
      const curR = progress * maxR;

      streamPositions[i * 3] = (curR + offset) * Math.cos(ray.theta) * Math.cos(ray.phi);
      streamPositions[i * 3 + 1] = (curR + offset) * Math.sin(ray.theta) * Math.cos(ray.phi);
      streamPositions[i * 3 + 2] = curR * Math.sin(ray.phi);

      // Chromatic color mapping matching reference image caustics
      if (progress < 0.18) {
        streamColors[i * 3] = 1.0;
        streamColors[i * 3 + 1] = 1.0;
        streamColors[i * 3 + 2] = 1.0;
      } else if (ray.transverseNorm < -0.15) {
        streamColors[i * 3] = 1.0;
        streamColors[i * 3 + 1] = 0.70;
        streamColors[i * 3 + 2] = 0.22;
      } else if (ray.transverseNorm > 0.15) {
        streamColors[i * 3] = 0.15;
        streamColors[i * 3 + 1] = 0.88;
        streamColors[i * 3 + 2] = 1.0;
      } else {
        streamColors[i * 3] = 0.94;
        streamColors[i * 3 + 1] = 0.98;
        streamColors[i * 3 + 2] = 1.0;
      }
    }

    streamGeom.setAttribute('position', new THREE.BufferAttribute(streamPositions, 3));
    streamGeom.setAttribute('color', new THREE.BufferAttribute(streamColors, 3));

    const streamMat = new THREE.PointsMaterial({
      size: 2.2, // Crisp, needle-sharp photonic points
      map: sparkTex,
      vertexColors: true,
      transparent: true,
      opacity: 0.82,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    const streamPoints = new THREE.Points(streamGeom, streamMat);
    scene.add(streamPoints);

    // ── 5. Layer 3: Ambient Cosmic Stardust Cloud ────
    const dustCount = performanceMode === 'eco' ? 400 : performanceMode === 'turbo' ? 1200 : 750;
    const dustGeom = new THREE.BufferGeometry();
    const dustPos = new Float32Array(dustCount * 3);
    const dustColors = new Float32Array(dustCount * 3);

    for (let d = 0; d < dustCount; d++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = (Math.random() - 0.5) * Math.PI * 0.75;
      const radius = 55 + Math.random() * 80;

      dustPos[d * 3] = radius * Math.cos(theta) * Math.cos(phi);
      dustPos[d * 3 + 1] = radius * Math.sin(theta) * Math.cos(phi);
      dustPos[d * 3 + 2] = radius * Math.sin(phi);

      const isWarm = Math.random() > 0.5;
      if (isWarm) {
        dustColors[d * 3] = 1.0;
        dustColors[d * 3 + 1] = 0.72;
        dustColors[d * 3 + 2] = 0.30;
      } else {
        dustColors[d * 3] = 0.22;
        dustColors[d * 3 + 1] = 0.88;
        dustColors[d * 3 + 2] = 1.0;
      }
    }

    dustGeom.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
    dustGeom.setAttribute('color', new THREE.BufferAttribute(dustColors, 3));

    const dustMat = new THREE.PointsMaterial({
      size: 1.8,
      map: sparkTex,
      vertexColors: true,
      transparent: true,
      opacity: 0.55,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    const dustPoints = new THREE.Points(dustGeom, dustMat);
    scene.add(dustPoints);

    // ── 6. Layer 4: Compact Specular Singularity (Only 25 Tiny Sparks) ────────
    const nucCount = 25; // Compact star core (eliminates the 650-point nuclear white sun)
    const nucGeom = new THREE.BufferGeometry();
    const nucPos = new Float32Array(nucCount * 3);
    const nucColors = new Float32Array(nucCount * 3);

    for (let n = 0; n < nucCount; n++) {
      const u = Math.random();
      const v = Math.random();
      const th = u * 2.0 * Math.PI;
      const ph = Math.acos(2.0 * v - 1.0);
      const r = Math.cbrt(Math.random()) * 2.5 + 0.4;

      nucPos[n * 3] = r * Math.sin(ph) * Math.cos(th);
      nucPos[n * 3 + 1] = r * Math.sin(ph) * Math.sin(th);
      nucPos[n * 3 + 2] = r * Math.cos(ph);

      nucColors[n * 3] = 1.0;
      nucColors[n * 3 + 1] = 1.0;
      nucColors[n * 3 + 2] = 1.0;
    }

    nucGeom.setAttribute('position', new THREE.BufferAttribute(nucPos, 3));
    nucGeom.setAttribute('color', new THREE.BufferAttribute(nucColors, 3));

    const nucMat = new THREE.PointsMaterial({
      size: 2.0, // Tiny diamond specular core
      map: sparkTex,
      vertexColors: true,
      transparent: true,
      opacity: 0.90,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    const nucPoints = new THREE.Points(nucGeom, nucMat);
    scene.add(nucPoints);

    // Subtle Holographic Lattice Accent
    const latticeGeom = new THREE.IcosahedronGeometry(4.5, 1);
    const latticeMat = new THREE.MeshBasicMaterial({
      color: 0x00f5ff,
      wireframe: true,
      transparent: true,
      opacity: 0.12,
      blending: THREE.AdditiveBlending,
    });
    const nucleusLattice = new THREE.Mesh(latticeGeom, latticeMat);
    scene.add(nucleusLattice);

    // ── 7. Layer 5: Optical Lens Diffraction Cross Spikes ──────────────────────
    const spikeCount = 6;
    const spikeGeom = new THREE.BufferGeometry();
    const spikePos = new Float32Array(spikeCount * 2 * 3);
    for (let s = 0; s < spikeCount; s++) {
      const ang = (s / spikeCount) * Math.PI;
      const len = s % 2 === 0 ? 110 : 75;
      spikePos[s * 6] = -len * Math.cos(ang);
      spikePos[s * 6 + 1] = -len * Math.sin(ang);
      spikePos[s * 6 + 2] = 0;
      spikePos[s * 6 + 3] = len * Math.cos(ang);
      spikePos[s * 6 + 4] = len * Math.sin(ang);
      spikePos[s * 6 + 5] = 0;
    }
    spikeGeom.setAttribute('position', new THREE.BufferAttribute(spikePos, 3));
    const spikeMat = new THREE.LineBasicMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 0.28,
      blending: THREE.AdditiveBlending,
    });
    const diffractionSpikes = new THREE.LineSegments(spikeGeom, spikeMat);
    scene.add(diffractionSpikes);

    // ── 8. Fast & Silky Zoom, Drag & Expand Controls ──────────────────────────
    const onMouseDown = (e: MouseEvent) => {
      mouseDragRef.current.isDown = true;
      mouseDragRef.current.lastX = e.clientX;
      mouseDragRef.current.lastY = e.clientY;
    };
    const onMouseMove = (e: MouseEvent) => {
      if (!mouseDragRef.current.isDown) return;
      const dx = e.clientX - mouseDragRef.current.lastX;
      const dy = e.clientY - mouseDragRef.current.lastY;
      mouseDragRef.current.rotY += dx * 0.007;
      mouseDragRef.current.rotX += dy * 0.007;
      mouseDragRef.current.lastX = e.clientX;
      mouseDragRef.current.lastY = e.clientY;
    };
    const onMouseUp = () => {
      mouseDragRef.current.isDown = false;
    };
    const onWheel = (e: WheelEvent) => {
      // Fast, ultra-smooth zooming (0.2x to 3.8x)
      zoomRef.current = Math.max(0.2, Math.min(3.8, zoomRef.current - e.deltaY * 0.0022));
    };

    window.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    window.addEventListener('wheel', onWheel, { passive: true });

    // ── 9. 60 FPS Render Loop: Power-On Startup, Harmonics & Reactive Colors ──
    const clock = new THREE.Clock();
    let currentScale = 0.01; // Starts collapsed for cinematic startup sequence
    let targetRotX = 0;
    let targetRotY = 0;
    let animId = 0;
    const startTime = performance.now();

    let isWindowVisible = !document.hidden;
    const onVisibilityChange = () => {
      isWindowVisible = !document.hidden;
    };
    document.addEventListener('visibilitychange', onVisibilityChange);

    const animate = () => {
      animId = requestAnimationFrame(animate);
      if (!isWindowVisible) return; // 0% CPU & 0 GPU memory bandwidth when minimized or backgrounded
      const elapsed = clock.getElapsedTime();
      const bootSeconds = (performance.now() - startTime) / 1000;

      // ── Startup / Turning-On Ignition Sequence (First 1.8s) ──
      const bootProgress = Math.min(1.0, bootSeconds / 1.7);
      const bootEasing = Math.pow(bootProgress, 3); // Cubic explosion

      const curState = stateRef.current;
      const curHandX = handXRef.current;
      const curHandY = handYRef.current;
      const curPinch = isPinchingRef.current;
      const curExp = expansionRef.current;
      const curAudio = audioLevelRef.current;
      const mDrag = mouseDragRef.current;
      const palette = STATE_PALETTES[curState] || STATE_PALETTES.idle;

      // Update dynamic colors based on state
      latticeMat.color.copy(palette.primary);

      // ── Rotation: Optical Hand Following + Fluid Inertia ──
      if (curHandX !== 0 || curHandY !== 0) {
        targetRotY += curHandX * 0.075;
        targetRotX += curHandY * 0.055;
      } else {
        const spinSpeed =
          curState === 'thinking' || curState === 'processing'
            ? 0.045
            : curState === 'researching'
            ? 0.032
            : curState === 'waiting_for_approval'
            ? 0.004
            : curState === 'success'
            ? 0.055
            : 0.007;
        targetRotY += spinSpeed + mDrag.rotY * 0.02;
        targetRotX = Math.sin(elapsed * 0.35) * 0.12 + mDrag.rotX * 0.02;
      }

      starburstRays.rotation.y = THREE.MathUtils.lerp(starburstRays.rotation.y, targetRotY, 0.12);
      starburstRays.rotation.x = THREE.MathUtils.lerp(starburstRays.rotation.x, targetRotX, 0.12);
      streamPoints.rotation.y = starburstRays.rotation.y;
      streamPoints.rotation.x = starburstRays.rotation.x;
      dustPoints.rotation.y = starburstRays.rotation.y * 0.6;
      dustPoints.rotation.x = starburstRays.rotation.x * 0.6;

      nucleusLattice.rotation.x = elapsed * 0.65;
      nucleusLattice.rotation.y = elapsed * 0.8;
      diffractionSpikes.rotation.z = elapsed * 0.05;

      // ── Optical Harmonic Dynamics (100% GPU Matrix Transforms — Zero Buffer Churn) ──
      const waveSpeed =
        curState === 'speaking'
          ? 8.5
          : curState === 'thinking' || curState === 'processing'
          ? 6.0
          : curState === 'waiting_for_approval'
          ? 1.8
          : curState === 'success'
          ? 12.0
          : 2.0;
      const wave = Math.sin(elapsed * waveSpeed) * 0.04;
      const audioExpansion = curState === 'speaking' ? (curAudio * 0.22) : curState === 'listening' ? (curAudio * 0.12) : 0;
      const dynamicScaleMod = 1.0 + wave + audioExpansion;

      // Independent multi-layer rotation on the GPU
      const spinMult =
        curState === 'speaking'
          ? 1.6
          : curState === 'thinking' || curState === 'processing'
          ? 2.5
          : curState === 'researching'
          ? 1.8
          : 1.0;
      streamPoints.rotation.z += 0.002 * spinMult;
      streamPoints.rotation.y = starburstRays.rotation.y + elapsed * 0.02 * spinMult;
      dustPoints.rotation.y += 0.001 * spinMult;
      dustPoints.rotation.x = Math.sin(elapsed * 0.2) * 0.08;

      // ── Dynamic Scale: Startup + Zoom + Hand Pinch/Expansion + Voice Pulse ──
      let desiredScale = curPinch ? 0.35 : (curExp * zoomRef.current);
      if (curState === 'speaking') {
        desiredScale *= 1.0 + Math.sin(elapsed * 15.0) * 0.12 + curAudio * 0.35;
      } else if (curState === 'listening') {
        desiredScale *= 1.0 + Math.sin(elapsed * 9.0) * 0.08;
      } else if (curState === 'thinking' || curState === 'processing' || curState === 'researching') {
        desiredScale *= 1.0 + Math.sin(elapsed * 12.0) * 0.06;
      } else if (curState === 'waiting_for_approval') {
        desiredScale *= 1.0 + Math.sin(elapsed * 3.0) * 0.12; // Inhalation breathing
      } else if (curState === 'success') {
        desiredScale *= 1.15 + Math.sin(elapsed * 18.0) * 0.04; // Celebratory bloom
      }

      desiredScale *= bootEasing; // Power-on growth

      currentScale = THREE.MathUtils.lerp(currentScale, desiredScale, 0.14);
      const finalScale = currentScale * dynamicScaleMod;

      starburstRays.scale.setScalar(finalScale);
      streamPoints.scale.setScalar(finalScale * 1.02);
      dustPoints.scale.setScalar(finalScale * 1.06);
      nucPoints.scale.setScalar(finalScale);
      nucleusLattice.scale.setScalar(finalScale);
      diffractionSpikes.scale.setScalar(finalScale);

      // ── Camera Position Offset Following Hand in 3D ──
      const targetPosX = (curHandX !== 0 || curHandY !== 0) ? curHandX * 60 : 0;
      const targetPosY = (curHandX !== 0 || curHandY !== 0) ? -curHandY * 48 : 0;

      scene.position.x = THREE.MathUtils.lerp(scene.position.x, targetPosX, 0.12);
      scene.position.y = THREE.MathUtils.lerp(scene.position.y, targetPosY, 0.12);

      composer.render();
    };

    animate();

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth || window.innerWidth;
      const h = container.clientHeight || window.innerHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
      composer.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animId);
      document.removeEventListener('visibilitychange', onVisibilityChange);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      window.removeEventListener('wheel', onWheel);
      renderer.dispose();
      composer.dispose();
      rayGeom.dispose();
      streamGeom.dispose();
      dustGeom.dispose();
      nucGeom.dispose();
      spikeGeom.dispose();
      latticeGeom.dispose();
      rayMat.dispose();
      streamMat.dispose();
      dustMat.dispose();
      nucMat.dispose();
      spikeMat.dispose();
      latticeMat.dispose();
      sparkTex.dispose();
    };
  }, [particleCount, performanceMode]);

  return (
    <div
      ref={containerRef}
      className="absolute inset-0 w-full h-full select-none overflow-hidden cursor-grab active:cursor-grabbing bg-black"
    />
  );
}
