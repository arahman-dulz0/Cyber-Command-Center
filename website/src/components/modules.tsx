import { MODULES, FEATURE_CATEGORIES } from "@/lib/data";
import { ICONS } from "@/lib/icons";
import { Section } from "./section";
import { Reveal } from "./reveal";

const CATEGORY_BLURB: Record<string, string> = {
  Intelligence: "Collect and correlate threats automatically.",
  AI: "Reason over your data, locally.",
  Operations: "Run the SOC where your team already works.",
  Platform: "Production-grade foundations underneath.",
};

export function Modules() {
  return (
    <Section
      id="platform"
      eyebrow="The platform"
      title="Sixteen capabilities. One operating picture."
      intro="Every module is a real, running part of the system — from autonomous collection to closed-loop remediation. They share one database, one local AI layer and one control surface."
    >
      <div className="space-y-14">
        {FEATURE_CATEGORIES.map((cat) => {
          const items = MODULES.filter((m) => m.category === cat);
          return (
            <div key={cat}>
              <Reveal>
                <div className="mb-5 flex items-baseline gap-3 border-b border-line pb-3">
                  <h3 className="font-display text-sm font-semibold uppercase tracking-widest text-cyan">
                    {cat}
                  </h3>
                  <span className="text-sm text-faint">{CATEGORY_BLURB[cat]}</span>
                </div>
              </Reveal>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {items.map((m, idx) => {
                  const Icon = ICONS[m.icon] ?? ICONS.Radar;
                  return (
                    <Reveal key={m.name} delay={(idx % 4) * 0.05}>
                      <article className="group relative flex h-full flex-col overflow-hidden rounded-2xl border border-line bg-panel/40 p-5 transition-all duration-300 hover:-translate-y-1 hover:border-blue/40 hover:bg-panel">
                        <div
                          className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
                          style={{
                            background:
                              "radial-gradient(360px circle at 30% 0%, rgba(76,130,251,0.12), transparent 60%)",
                          }}
                        />
                        <div className="relative flex h-11 w-11 items-center justify-center rounded-xl border border-line bg-bg/60 text-cyan transition-colors group-hover:border-blue/40 group-hover:text-blue">
                          <Icon className="h-5 w-5" strokeWidth={1.6} aria-hidden />
                        </div>
                        <h4 className="relative mt-4 font-display text-base font-semibold tracking-tight text-ink">
                          {m.name}
                        </h4>
                        <p className="relative mt-2 text-[13px] leading-relaxed text-muted">
                          {m.blurb}
                        </p>
                      </article>
                    </Reveal>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </Section>
  );
}
