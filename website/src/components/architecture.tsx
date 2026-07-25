"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { ChevronRight } from "lucide-react";
import { ARCH, type ArchNode } from "@/lib/data";
import { cn } from "@/lib/utils";
import { Section } from "./section";

const KIND_LABEL: Record<ArchNode["kind"], string> = {
  source: "ingest",
  core: "process",
  store: "persist",
  output: "deliver",
};
const KIND_COLOR: Record<ArchNode["kind"], string> = {
  source: "text-cyan",
  core: "text-blue",
  store: "text-violet",
  output: "text-green",
};

export function Architecture() {
  const [active, setActive] = useState(2);
  const node = ARCH[active];

  return (
    <Section
      id="architecture"
      eyebrow="Architecture"
      title="From raw sources to acted-on intelligence."
      intro="Data flows one direction: sources are collected, fused into priority, enriched by local AI, persisted, and delivered where you work. Hover a stage to see what it does."
    >
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)]">
        {/* pipeline rail */}
        <div className="relative">
          <div className="absolute bottom-4 left-[19px] top-4 w-px bg-line" aria-hidden />
          <ul className="space-y-1.5">
            {ARCH.map((n, i) => (
              <li key={n.id}>
                <button
                  onMouseEnter={() => setActive(i)}
                  onFocus={() => setActive(i)}
                  onClick={() => setActive(i)}
                  className={cn(
                    "group flex w-full items-center gap-4 rounded-xl border px-4 py-3 text-left transition-all",
                    i === active
                      ? "border-blue/40 bg-panel"
                      : "border-transparent hover:border-line hover:bg-panel/50"
                  )}
                >
                  <span
                    className={cn(
                      "relative z-10 flex h-2.5 w-2.5 shrink-0 rounded-full ring-4 ring-bg transition-colors",
                      i === active ? "bg-cyan" : "bg-faint group-hover:bg-muted"
                    )}
                  />
                  <span
                    className={cn(
                      "flex-1 text-sm font-medium transition-colors",
                      i === active ? "text-ink" : "text-muted"
                    )}
                  >
                    {n.label}
                  </span>
                  <ChevronRight
                    className={cn(
                      "h-4 w-4 transition-all",
                      i === active
                        ? "translate-x-0 text-cyan opacity-100"
                        : "-translate-x-1 text-faint opacity-0 group-hover:opacity-100"
                    )}
                  />
                </button>
              </li>
            ))}
          </ul>
        </div>

        {/* detail panel */}
        <div className="glass relative min-h-[280px] overflow-hidden rounded-2xl p-8">
          <div className="grid-field absolute inset-0 opacity-60" aria-hidden />
          <AnimatePresence mode="wait">
            <motion.div
              key={node.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.3 }}
              className="relative"
            >
              <div
                className={cn(
                  "mono text-[11px] uppercase tracking-widest",
                  KIND_COLOR[node.kind]
                )}
              >
                {KIND_LABEL[node.kind]} — stage {active + 1} / {ARCH.length}
              </div>
              <h3 className="mt-3 font-display text-2xl font-semibold tracking-tight text-ink">
                {node.label}
              </h3>
              <p className="mt-4 max-w-md text-[15px] leading-relaxed text-muted">
                {node.desc}
              </p>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </Section>
  );
}
