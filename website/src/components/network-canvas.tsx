"use client";

import { useEffect, useRef } from "react";

type Node = { x: number; y: number; r: number; core?: boolean };
type Edge = { a: number; b: number; phase: number; speed: number };

// Normalized node layout: index 0 is the core, the rest are threat sources
// arranged around it. Edges connect every source to the core (the pipeline).
const LAYOUT: Array<[number, number]> = [
  [0.66, 0.46], // core
  [0.2, 0.2],
  [0.16, 0.55],
  [0.28, 0.82],
  [0.52, 0.16],
  [0.5, 0.86],
  [0.86, 0.24],
  [0.9, 0.66],
  [0.74, 0.84],
];

export function NetworkCanvas() {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let w = 0;
    let h = 0;
    let raf = 0;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);

    let nodes: Node[] = [];
    let edges: Edge[] = [];

    const build = () => {
      nodes = LAYOUT.map(([nx, ny], i) => ({
        x: nx * w,
        y: ny * h,
        r: i === 0 ? 6 : 3,
        core: i === 0,
      }));
      edges = nodes
        .slice(1)
        .map((_, i) => ({ a: i + 1, b: 0, phase: Math.random(), speed: 0.0016 + Math.random() * 0.0018 }));
    };

    const resize = () => {
      const rect = canvas.parentElement?.getBoundingClientRect();
      w = rect?.width ?? window.innerWidth;
      h = rect?.height ?? 520;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = `${w}px`;
      canvas.style.height = `${h}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      build();
    };

    const draw = (t: number) => {
      ctx.clearRect(0, 0, w, h);

      // edges + traveling pulses
      for (const e of edges) {
        const A = nodes[e.a];
        const B = nodes[e.b];
        ctx.strokeStyle = "rgba(76,130,251,0.14)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(A.x, A.y);
        ctx.lineTo(B.x, B.y);
        ctx.stroke();

        const p = reduce ? 0.5 : (e.phase + t * e.speed) % 1;
        const px = A.x + (B.x - A.x) * p;
        const py = A.y + (B.y - A.y) * p;
        const g = ctx.createRadialGradient(px, py, 0, px, py, 5);
        g.addColorStop(0, "rgba(52,228,234,0.9)");
        g.addColorStop(1, "rgba(52,228,234,0)");
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(px, py, 5, 0, Math.PI * 2);
        ctx.fill();
      }

      // nodes
      for (const n of nodes) {
        if (n.core) {
          const pulse = reduce ? 26 : 24 + Math.sin(t * 0.002) * 6;
          const cg = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, pulse);
          cg.addColorStop(0, "rgba(76,130,251,0.35)");
          cg.addColorStop(1, "rgba(76,130,251,0)");
          ctx.fillStyle = cg;
          ctx.beginPath();
          ctx.arc(n.x, n.y, pulse, 0, Math.PI * 2);
          ctx.fill();
          ctx.fillStyle = "#8ab4ff";
        } else {
          ctx.fillStyle = "rgba(151,164,185,0.85)";
        }
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fill();
      }

      if (!reduce) raf = requestAnimationFrame(draw);
    };

    resize();
    if (reduce) {
      draw(0);
    } else {
      raf = requestAnimationFrame(draw);
    }

    const ro = new ResizeObserver(resize);
    if (canvas.parentElement) ro.observe(canvas.parentElement);

    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
    };
  }, []);

  return <canvas ref={ref} className="absolute inset-0 h-full w-full" aria-hidden="true" />;
}
