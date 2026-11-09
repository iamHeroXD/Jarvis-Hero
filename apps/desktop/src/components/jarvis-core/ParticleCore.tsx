import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export type CoreState = 'idle' | 'listening' | 'thinking' | 'executing' | 'speaking' | 'warning' | 'offline';

interface ParticleCoreProps {
  state?: CoreState;
  particleCount?: number;
  handX?: number; // Normalized -1 to 1 from hand tracking
  handY?: number;
  isPinching?: boolean;
}

const STATE_COLORS: Record<CoreState, { primary: number; secondary: number }> = {
  idle: { primary: 0x3b82f6, secondary: 0x06b6d4 },        // Blue / Cyan
  listening: { primary: 0x06b6d4, secondary: 0x38bdf8 },   // Cyan pulse
  thinking: { primary: 0xa855f7, secondary: 0x6366f1 },    // Violet / Indigo
  executing: { primary: 0x10b981, secondary: 0x059669 },   // Emerald green
  speaking: { primary: 0x60a5fa, secondary: 0x93c5fd },    // Soft luminous blue
  warning: { primary: 0xf59e0b, secondary: 0xef4444 },     // Amber / Red
  offline: { primary: 0x64748b, secondary: 0x475569 },     // Slate grey
};

export default function ParticleCore({
  state = 'idle',
  particleCount = 1500,
  handX = 0,
  handY = 0,
  isPinching = false,
}: ParticleCoreProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const particlesRef = useRef<THREE.Points | null>(null);
  const frameIdRef = useRef<number>(0);

  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;
    const width = container.clientWidth || 360;
    const height = container.clientHeight || 360;

    // 1. Scene & Camera
    const scene = new THREE.Scene();
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
    camera.position.z = 180;

    // 2. Renderer with low-power optimizations for Intel HD Graphics
    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: false,
      powerPreference: 'low-power',
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    container.innerHTML = '';
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // 3. Spherical particle geometry
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const radius = 65;
    const primaryColor = new THREE.Color(STATE_COLORS[state].primary);
    const secondaryColor = new THREE.Color(STATE_COLORS[state].secondary);

    for (let i = 0; i < particleCount; i++) {
      // Golden spiral distribution on sphere surface
      const phi = Math.acos(1 - 2 * (i + 0.5) / particleCount);
      const theta = Math.PI * (1 + 5 ** 0.5) * i;

      const jitter = (Math.random() - 0.5) * 8;
      const r = radius + jitter;

      positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = r * Math.cos(phi);

      const lerpColor = primaryColor.clone().lerp(secondaryColor, Math.random());
      colors[i * 3] = lerpColor.r;
      colors[i * 3 + 1] = lerpColor.g;
      colors[i * 3 + 2] = lerpColor.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    // 4. Material
    const material = new THREE.PointsMaterial({
      size: 2.2,
      vertexColors: true,
      transparent: true,
      opacity: 0.85,
      blending: THREE.AdditiveBlending,
    });

    const particles = new THREE.Points(geometry, material);
    scene.add(particles);
    particlesRef.current = particles;

    // 5. Animation loop
    let clock = new THREE.Clock();

    const animate = () => {
      frameIdRef.current = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      if (particles) {
        // Base rotation
        particles.rotation.y = elapsedTime * 0.25;
        particles.rotation.x = elapsedTime * 0.12;

        // Interaction with hand tracking position
        if (handX !== 0 || handY !== 0) {
          particles.position.x = THREE.MathUtils.lerp(particles.position.x, handX * 35, 0.1);
          particles.position.y = THREE.MathUtils.lerp(particles.position.y, -handY * 35, 0.1);
        }

        // Pinch contraction / expansion
        const targetScale = isPinching ? 0.75 : 1.0;
        particles.scale.setScalar(
          THREE.MathUtils.lerp(particles.scale.x, targetScale, 0.15)
        );

        // State-based pulsation
        if (state === 'listening') {
          const pulse = 1.0 + Math.sin(elapsedTime * 6) * 0.08;
          particles.scale.multiplyScalar(pulse);
        } else if (state === 'thinking') {
          particles.rotation.y += 0.02;
        }
      }

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(frameIdRef.current);
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
      geometry.dispose();
      material.dispose();
    };
  }, [state, particleCount]);

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full flex items-center justify-center overflow-hidden"
      style={{ minHeight: '280px' }}
    />
  );
}
