"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Check, Plus, ArrowUpRight } from "lucide-react";
import { PHASES, NEXT } from "@/lib/data";
import { cn } from "@/lib/utils";
import { Section } from "./section";
import { Reveal } from "./reveal";

export function Roadmap() {
  const [open, setOpen] = useState(0);

  return (
    <Section
      id="roadmap"
      eyebrow="Roadmap"
      title="Nine milestones, all shipped."
      intro="The platform was built in sequence — each milestone a working stage that the next one builds on. Every stage below is complete and running."
    >
      <div className="relative">
        <div className="absolute bottom-6 left-[27px] top-6 w-px bg-line md:left-[31px]" aria-hidden />
        <div className="space-y-2">
          {PHASES.map((p, i) => {
            const isOpen = i === open;
            return (
              <div key={p.n} className="relative">
                <button
                  onClick={() => setOpen(isOpen ? -1 : i)}
                  className={cn(
                    "group flex w-full items-center gap-4 rounded-2xl border px-4 py-4 text-left transition-all md:px-5",
                    isOpen
                      ? "border-blue/40 bg-panel"
                      : "border-line bg-panel/30 hover:bg-panel/60"
                  )}
                  aria-expanded={isOpen}
                >
                  <span className="relative z-10 flex h-14 w-14 shrink-0 items-center justify-center rounded-xl border border-line bg-bg ring-4 ring-bg">
                    <span className="mono text-sm font-semibold text-cyan">
                      {String(p.n).padStart(2, "0")}
                    </span>
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="truncate font-display text-lg font-semibold tracking-tight text-ink">
                        {p.title}
                      </h3>
                      <span className="mono hidden items-center gap-1 rounded-md border border-green/30 px-1.5 py-0.5 text-[10px] text-green sm:inline-flex">
                        <Check className="h-3 w-3" /> shipped
                      </span>
                    </div>
                  </div>
                  <Plus
                    className={cn(
                      "h-5 w-5 shrink-0 text-faint transition-transform duration-300",
                      isOpen && "rotate-45 text-cyan"
                    )}
                  />
                </button>
                <AnimatePresence initial={false}>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.32, ease: [0.22, 1, 0.36, 1] }}
                      className="overflow-hidden"
                    >
                      <p className="max-w-2xl px-5 py-4 pl-[76px] text-[15px] leading-relaxed text-muted md:pl-[80px]">
                        {p.body}
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            );
          })}
        </div>
      </div>

      {/* What's next */}
      <Reveal className="mt-14">
        <div className="mb-5 flex items-center gap-2">
          <ArrowUpRight className="h-4 w-4 text-cyan" strokeWidth={1.8} />
          <h3 className="font-display text-lg font-semibold tracking-tight text-ink">
            What&apos;s next
          </h3>
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          {NEXT.map((n) => (
            <div
              key={n.title}
              className="rounded-xl border border-dashed border-line bg-panel/20 p-5"
            >
              <div className="font-display text-base font-semibold text-ink">
                {n.title}
              </div>
              <p className="mt-1.5 text-sm leading-relaxed text-muted">{n.body}</p>
            </div>
          ))}
        </div>
      </Reveal>
    </Section>
  );
}
