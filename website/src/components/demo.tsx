import { Section } from "./section";
import { Reveal } from "./reveal";

const CHAPTERS = [
  "Security score",
  "Threat activity",
  "Severity mix",
  "Fused CVE alerts",
  "Lab exposure",
  "Learning",
  "Latest news",
  "Agent reports",
];

const SHOTS = [
  {
    src: "/screenshots/dashboard-overview.png",
    alt: "Cyber Command Center dashboard — security score, live posture, lab assets, threat-activity chart and severity mix.",
    caption: "Overview — score, posture, assets & charts",
  },
  {
    src: "/screenshots/dashboard-detail.png",
    alt: "Cyber Command Center dashboard — fused CVE alerts, learning progress, latest news and multi-agent intelligence reports.",
    caption: "Fused alerts, news & agent reports",
  },
];

export function Demo() {
  return (
    <Section
      id="demo"
      eyebrow="See it run"
      title="The dashboard, populated on first boot."
      intro="Real screenshots — no mockups. This is the self-hosted SOC dashboard reading live from the database: a computed security score, threat-activity trends, fused CVE alerts correlated to your assets, and multi-agent intelligence reports."
    >
      <div className="glass overflow-hidden rounded-2xl p-2 md:p-3">
        {/* browser chrome */}
        <div className="flex items-center gap-2 px-3 py-2.5">
          <span className="h-3 w-3 rounded-full bg-red/70" />
          <span className="h-3 w-3 rounded-full bg-amber/70" />
          <span className="h-3 w-3 rounded-full bg-green/70" />
          <div className="mono ml-3 hidden rounded-md border border-line bg-bg/60 px-3 py-1 text-[11px] text-faint sm:block">
            localhost:8080/dashboard
          </div>
        </div>

        <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
          {SHOTS.map((s, i) => (
            <Reveal key={s.src} delay={i * 0.08}>
              <figure className="overflow-hidden rounded-xl border border-line bg-bg">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={s.src}
                  alt={s.alt}
                  width={939}
                  height={951}
                  loading="lazy"
                  className="h-auto w-full"
                />
                <figcaption className="mono border-t border-line px-4 py-2 text-[11px] text-faint">
                  {s.caption}
                </figcaption>
              </figure>
            </Reveal>
          ))}
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
