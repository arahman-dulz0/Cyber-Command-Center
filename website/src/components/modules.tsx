import { ArrowUpRight } from "lucide-react";
import { MODULES } from "@/lib/data";
import { ICONS } from "@/lib/icons";
import { Section } from "./section";
import { Reveal } from "./reveal";

export function Modules() {
  return (
    <Section
      id="platform"
      eyebrow="The platform"
      title="Fifteen modules, one operating picture."
      intro="Each capability is a real, running part of the system — from autonomous collection to closed-loop remediation. They share one database, one AI layer and one control surface."
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {MODULES.map((m, idx) => {
          const Icon = ICONS[m.icon] ?? ICONS.Radar;
          return (
            <Reveal key={m.name} delay={(idx % 3) * 0.06}>
              <article className="group relative h-full overflow-hidden rounded-2xl border border-line bg-panel/40 p-6 transition-all duration-300 hover:-translate-y-1 hover:border-blue/40 hover:bg-panel">
                <div
                  className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
                  style={{
                    background:
                      "radial-gradient(400px circle at 30% 0%, rgba(76,130,251,0.10), transparent 60%)",
                  }}
                />
                <div className="relative flex items-start justify-between">
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-line bg-bg/60 text-cyan">
                    <Icon className="h-5 w-5" strokeWidth={1.6} />
                  </div>
                  <ArrowUpRight className="h-4 w-4 text-faint transition-colors group-hover:text-cyan" />
                </div>
                <div className="mono relative mt-5 text-[10px] uppercase tracking-widest text-faint">
                  {m.tag}
                </div>
                <h3 className="relative mt-1.5 font-display text-lg font-semibold tracking-tight text-ink">
                  {m.name}
                </h3>
                <p className="relative mt-2.5 text-sm leading-relaxed text-muted">
                  {m.blurb}
                </p>
              </article>
            </Reveal>
          );
        })}
      </div>
    </Section>
  );
}
