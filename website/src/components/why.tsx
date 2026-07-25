import { Section } from "./section";
import { Reveal } from "./reveal";

const BEFORE = [
  "NVD tab",
  "CISA KEV",
  "EPSS lookup",
  "ExploitDB",
  "GitHub advisories",
  "RSS reader",
  "Spreadsheet",
  "Ticketing tool",
  "Notes app",
  "ChatGPT tab",
];

export function Why() {
  return (
    <Section
      id="why"
      eyebrow="Why it exists"
      title="Security work is spread across too many tabs."
      intro="Analysts spend the day switching between feeds, dashboards, documents and AI tools — copying context by hand. Cyber Command Center OSS collapses that sprawl into one platform that watches, correlates and acts, while keeping you in control."
    >
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Reveal>
          <div className="glass h-full rounded-2xl p-7">
            <div className="mono mb-5 text-[11px] tracking-wider text-faint">
              BEFORE — TEN TOOLS, MANUAL CONTEXT
            </div>
            <div className="flex flex-wrap gap-2">
              {BEFORE.map((t) => (
                <span
                  key={t}
                  className="rounded-lg border border-line bg-bg/50 px-3 py-2 text-sm text-muted"
                >
                  {t}
                </span>
              ))}
            </div>
            <p className="mt-6 text-sm leading-relaxed text-faint">
              Every alert means checking a severity here, an exploit status there,
              then deciding by hand whether it matters to you.
            </p>
          </div>
        </Reveal>

        <Reveal delay={0.08}>
          <div className="glass glow-blue relative h-full overflow-hidden rounded-2xl p-7">
            <div className="mono mb-5 text-[11px] tracking-wider text-cyan">
              AFTER — ONE PLATFORM, ANSWERED
            </div>
            <div className="space-y-3">
              <Row k="Collect" v="Autonomous monitors pull every source on a schedule." />
              <Row k="Correlate" v="Each CVE fused into a 0–100 priority with exploit context." />
              <Row k="Decide" v="Matched against your asset inventory — signal, not noise." />
              <Row k="Act" v="Tickets raised, remediation drafted, escalations sent." />
            </div>
            <p className="mt-6 text-sm leading-relaxed text-muted">
              The repetitive work runs on its own. You review, adjust and close —
              from one control surface.
            </p>
          </div>
        </Reveal>
      </div>
    </Section>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-line bg-bg/40 p-3.5">
      <span className="mono mt-0.5 shrink-0 rounded-md bg-blue/10 px-2 py-1 text-[11px] text-blue">
        {k}
      </span>
      <span className="text-sm leading-relaxed text-ink">{v}</span>
    </div>
  );
}
