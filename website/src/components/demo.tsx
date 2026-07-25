"use client";

import { motion } from "motion/react";
import { Play } from "lucide-react";
import { Section } from "./section";

const CHAPTERS = [
  "Architecture",
  "Threat Intelligence",
  "SOC Dashboard",
  "Knowledge Base",
  "Automation",
  "AI Agents",
  "Discord Ops",
  "Reports",
];

const BARS = [42, 58, 35, 71, 49, 63, 88, 54, 67, 40, 77, 59];

export function Demo() {
  return (
    <Section
      id="demo"
      eyebrow="See it run"
      title="Cyber Command Center OSS, in action."
      intro="A walkthrough of the full platform — from a fused CVE alert to an auto-raised remediation ticket, a grounded AI answer, and a multi-agent report."
    >
      <div className="glass overflow-hidden rounded-2xl p-2 md:p-3">
        {/* browser chrome */}
        <div className="flex items-center gap-2 px-3 py-2.5">
          <span className="h-3 w-3 rounded-full bg-red/70" />
          <span className="h-3 w-3 rounded-full bg-amber/70" />
          <span className="h-3 w-3 rounded-full bg-green/70" />
          <div className="mono ml-3 hidden rounded-md border border-line bg-bg/60 px-3 py-1 text-[11px] text-faint sm:block">
            command.local/dashboard
          </div>
        </div>

        {/* mock dashboard preview */}
        <div className="relative overflow-hidden rounded-xl border border-line bg-bg">
          <div className="grid-field absolute inset-0 opacity-40" aria-hidden />
          <div className="relative p-5 md:p-7">
            <div className="flex items-center justify-between">
              <div>
                <div className="mono text-[11px] tracking-wider text-faint">THREAT LEVEL</div>
                <div className="font-display text-2xl font-bold text-red md:text-3xl">HIGH</div>
              </div>
              <div className="mono hidden gap-2 sm:flex">
                {["CVEs 47", "KEV 1", "Exploited 1", "Tickets 3"].map((t) => (
                  <span key={t} className="rounded-lg border border-line bg-panel/60 px-3 py-2 text-xs text-muted">
                    {t}
                  </span>
                ))}
              </div>
            </div>

            <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-[1.4fr_1fr]">
              {/* chart */}
              <div className="rounded-xl border border-line bg-panel/40 p-5">
                <div className="mono mb-4 text-[11px] text-faint">CVEs · LAST 12 DAYS</div>
                <div className="flex h-28 items-end gap-1.5">
                  {BARS.map((b, i) => (
                    <motion.div
                      key={i}
                      initial={{ height: 0 }}
                      whileInView={{ height: `${b}%` }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.6, delay: i * 0.04, ease: [0.22, 1, 0.36, 1] }}
                      className="flex-1 rounded-sm bg-gradient-to-t from-blue/30 to-cyan/80"
                    />
                  ))}
                </div>
              </div>
              {/* alert feed */}
              <div className="rounded-xl border border-line bg-panel/40 p-5">
                <div className="mono mb-4 text-[11px] text-faint">LATEST FUSED ALERTS</div>
                <div className="space-y-2.5">
                  {[
                    ["CVE-2021-44228", 100],
                    ["CVE-2024-3400", 96],
                    ["CVE-2023-34362", 94],
                  ].map(([c, s]) => (
                    <div key={c as string} className="flex items-center justify-between border-b border-line pb-2 last:border-0">
                      <span className="mono text-xs text-cyan">{c}</span>
                      <span className="mono text-sm font-semibold text-red">{s}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* play overlay */}
          <button
            className="group absolute inset-0 grid place-items-center bg-bg/40 backdrop-blur-[1px] transition-colors hover:bg-bg/25"
            aria-label="Play demo walkthrough"
          >
            <span className="flex h-16 w-16 items-center justify-center rounded-full bg-ink text-bg shadow-2xl transition-transform group-hover:scale-105">
              <Play className="h-6 w-6 translate-x-0.5 fill-bg" />
            </span>
          </button>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        {CHAPTERS.map((c) => (
          <span
            key={c}
            className="mono rounded-lg border border-line bg-panel/40 px-3 py-1.5 text-xs text-muted"
          >
            {c}
          </span>
        ))}
      </div>
    </Section>
  );
}
