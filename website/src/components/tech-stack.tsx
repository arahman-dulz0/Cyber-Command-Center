import { TECH } from "@/lib/data";
import { Section } from "./section";
import { Reveal } from "./reveal";

export function TechStack() {
  return (
    <Section
      id="stack"
      eyebrow="Built with"
      title="A pragmatic, self-hostable stack."
      intro="No proprietary services and no vendor lock-in — everything runs in Docker on hardware you control, with local models doing the AI work."
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {TECH.map((t, i) => (
          <Reveal key={t.group} delay={(i % 3) * 0.06}>
            <div className="h-full rounded-2xl border border-line bg-panel/40 p-6">
              <div className="mono text-[11px] uppercase tracking-widest text-cyan">
                {t.group}
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {t.items.map((item) => (
                  <span
                    key={item}
                    className="rounded-lg border border-line bg-bg/50 px-3 py-1.5 text-sm text-ink"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}
