"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react";

type Alert = {
  cve: string;
  score: number;
  epss: number;
  poc: number;
  risk: string;
};

const ALERTS: Alert[] = [
  { cve: "CVE-2021-44228", score: 100, epss: 97, poc: 413, risk: "Public exploit and active exploitation — patch immediately." },
  { cve: "CVE-2024-3400", score: 96, epss: 92, poc: 27, risk: "Command injection exploited in the wild against edge devices." },
  { cve: "CVE-2023-34362", score: 94, epss: 88, poc: 61, risk: "SQL injection in managed file transfer — mass-exploited." },
];

export function ConsoleCard() {
  const [i, setI] = useState(0);

  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) return;
    const id = setInterval(() => setI((v) => (v + 1) % ALERTS.length), 4200);
    return () => clearInterval(id);
  }, []);

  const a = ALERTS[i];

  return (
    <div className="glass w-full max-w-md rounded-2xl p-1.5">
      <div className="flex items-center justify-between px-3.5 pb-2.5 pt-2">
        <div className="mono flex items-center gap-2 text-[11px] text-faint">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green opacity-60" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-green" />
          </span>
          cve-alerts
        </div>
        <span className="mono text-[11px] text-faint">fusion engine</span>
      </div>

      <div className="rounded-xl border border-line bg-bg/60 p-4">
        <AnimatePresence mode="wait">
          <motion.div
            key={a.cve}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.35 }}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="mono text-xs text-cyan">{a.cve}</div>
                <div className="mt-1 flex items-center gap-1.5 text-red">
                  <span className="text-[11px] font-medium uppercase tracking-wider">
                    Critical
                  </span>
                </div>
              </div>
              <div className="text-right">
                <div className="mono text-2xl font-semibold text-ink">{a.score}</div>
                <div className="mono text-[10px] text-faint">priority / 100</div>
              </div>
            </div>

            <div className="mono mt-4 flex flex-wrap gap-1.5 text-[10px]">
              <Badge tone="red">KEV ✓</Badge>
              <Badge tone="amber">EPSS {a.epss}%</Badge>
              <Badge tone="blue">PoC {a.poc}</Badge>
              <Badge tone="blue">ExploitDB ✓</Badge>
            </div>

            <p className="mt-4 border-t border-line pt-3 text-[13px] leading-relaxed text-muted">
              <span className="mono text-cyan">ai_risk › </span>
              {a.risk}
            </p>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

function Badge({
  children,
  tone,
}: {
  children: React.ReactNode;
  tone: "red" | "amber" | "blue";
}) {
  const map = {
    red: "border-red/30 text-red",
    amber: "border-amber/30 text-amber",
    blue: "border-blue/30 text-blue",
  } as const;
  return (
    <span className={`rounded-md border px-2 py-1 ${map[tone]}`}>{children}</span>
  );
}
