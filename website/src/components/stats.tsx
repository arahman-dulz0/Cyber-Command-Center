"use client";

import { useEffect, useRef, useState } from "react";
import { useInView } from "motion/react";
import { STATS } from "@/lib/data";

function CountUp({ value }: { value: string }) {
  const match = value.match(/^(\d+)(.*)$/);
  const target = match ? parseInt(match[1], 10) : 0;
  const suffix = match ? match[2] : value;
  const isNumeric = !!match && !value.includes("/");
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });
  const [n, setN] = useState(0);

  useEffect(() => {
    if (!inView || !isNumeric) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      const id = requestAnimationFrame(() => setN(target));
      return () => cancelAnimationFrame(id);
    }
    let raf = 0;
    const start = performance.now();
    const dur = 1100;
    const tick = (t: number) => {
      const p = Math.min((t - start) / dur, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setN(Math.round(target * eased));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [inView, isNumeric, target]);

  return (
    <span ref={ref} className="mono">
      {isNumeric ? n + suffix : value}
    </span>
  );
}

export function Stats() {
  return (
    <div className="mx-auto w-full max-w-7xl px-6">
      <div className="glass grid grid-cols-2 gap-px overflow-hidden rounded-2xl md:grid-cols-3 lg:grid-cols-6">
        {STATS.map((s) => (
          <div key={s.label} className="bg-panel/40 px-6 py-8">
            <div className="font-display text-3xl font-semibold text-ink md:text-4xl">
              <CountUp value={s.value} />
            </div>
            <div className="mt-2 text-xs leading-snug text-muted">{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
