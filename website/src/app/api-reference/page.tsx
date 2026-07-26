import Link from "next/link";
import type { Metadata } from "next";
import { Lock, Terminal } from "lucide-react";
import { PageShell } from "@/components/page-shell";

export const metadata: Metadata = {
  title: "API Reference — Cyber Command Center",
  description:
    "The Cyber Command Center dashboard HTTP API: authenticated, read-only JSON endpoints for threat posture, fused CVE alerts, news, reports and lab exposure.",
  alternates: { canonical: "/api-reference" },
};

type Endpoint = {
  method: "GET";
  path: string;
  title: string;
  desc: string;
  response: string;
};

const ENDPOINTS: Endpoint[] = [
  {
    method: "GET",
    path: "/api/summary",
    title: "Threat posture summary",
    desc: "Headline counts and the current threat level — the data behind the dashboard's top tiles.",
    response: `{
  "threat_level": "ELEVATED",
  "threat_color": "#FF9500",
  "cves_24h": 12, "critical_24h": 4, "kev_24h": 3,
  "exploited_24h": 6, "top_priority": 100,
  "open_tickets": 3, "lab_assets": 8
}`,
  },
  {
    method: "GET",
    path: "/api/security-score",
    title: "Security score",
    desc: "Inverse-risk posture score (0–100) computed from your lab exposure, with the factors that moved it.",
    response: `{
  "score": 81, "grade": "B", "color": "#9be34e",
  "factors": [
    { "label": "Open remediation tickets", "delta": -9 },
    { "label": "Actively exploited (KEV) in lab", "delta": -4 },
    { "label": "Assets awaiting patch", "delta": -6 }
  ]
}`,
  },
  {
    method: "GET",
    path: "/api/latest-alerts",
    title: "Fused CVE alerts",
    desc: "The most recent CVEs with fused enrichment: CVSS, EPSS, KEV status, exploit availability and CCC priority.",
    response: `[
  {
    "cve_id": "CVE-2021-44228",
    "cvss_score": 10.0, "severity": "CRITICAL",
    "priority_score": 100, "priority_label": "CRITICAL",
    "kev": true, "epss": 0.975,
    "github_poc_count": 90, "exploitdb_count": 12
  }
]`,
  },
  {
    method: "GET",
    path: "/api/assets-summary",
    title: "Lab exposure",
    desc: "Your asset inventory posture — total, healthy, and how many need patching (in an open ticket).",
    response: `{ "total": 8, "needs_patch": 3, "healthy": 5 }`,
  },
  {
    method: "GET",
    path: "/api/priority-distribution",
    title: "Severity mix",
    desc: "Count of tracked CVEs by priority label — the data behind the severity doughnut.",
    response: `{ "CRITICAL": 29, "HIGH": 7, "MEDIUM": 0, "LOW": 0 }`,
  },
  {
    method: "GET",
    path: "/api/activity-trend",
    title: "Activity trend",
    desc: "New CVEs and KEV additions per day over the last week — the data behind the trend chart.",
    response: `[
  { "day": "Jul 24", "cves": 25, "kev": 4 },
  { "day": "Jul 25", "cves": 31, "kev": 6 }
]`,
  },
  {
    method: "GET",
    path: "/api/latest-news",
    title: "Security news",
    desc: "The latest collected and summarized cybersecurity news articles.",
    response: `[
  {
    "title": "CISA adds edge-device flaws to KEV",
    "url": "https://www.cisa.gov/...",
    "source": "CISA", "ts": "2026-07-26T02:05:55Z"
  }
]`,
  },
  {
    method: "GET",
    path: "/api/latest-reports",
    title: "Intelligence reports",
    desc: "The most recent multi-agent intelligence reports (title, executive summary, timestamp).",
    response: `[
  {
    "title": "Executive Intelligence Report",
    "summary": "This week saw sustained mass-exploitation ...",
    "created_at": "2026-07-26T00:00:00Z"
  }
]`,
  },
];

function MethodBadge() {
  return (
    <span className="mono rounded-md border border-green/30 bg-green/10 px-2 py-0.5 text-[11px] font-semibold text-green">
      GET
    </span>
  );
}

export default function ApiReference() {
  return (
    <PageShell>
      <div className="eyebrow mb-4">Developers</div>
      <h1 className="font-display text-4xl font-semibold tracking-tight text-ink md:text-5xl">
        API Reference
      </h1>
      <p className="mt-5 max-w-2xl text-lg leading-relaxed text-muted">
        The dashboard exposes a small, read-only JSON API over the same PostgreSQL
        the platform fills. Every endpoint returns the exact data the SOC dashboard
        renders — build your own views, alerts or integrations on top.
      </p>

      {/* Auth */}
      <div className="glass mt-10 rounded-2xl border border-line p-6">
        <div className="mb-3 flex items-center gap-2">
          <Lock className="h-4 w-4 text-cyan" strokeWidth={1.6} />
          <h2 className="font-display text-lg font-semibold text-ink">Authentication</h2>
        </div>
        <p className="text-sm leading-relaxed text-muted">
          All <code className="mono rounded bg-panel2 px-1.5 py-0.5 text-cyan">/api/*</code>{" "}
          endpoints require HTTP Basic auth <em>or</em> an{" "}
          <code className="mono rounded bg-panel2 px-1.5 py-0.5 text-cyan">X-API-Key</code>{" "}
          header. <code className="mono rounded bg-panel2 px-1.5 py-0.5 text-cyan">/healthz</code>{" "}
          is unauthenticated. Requests are rate-limited per IP.
        </p>
        <pre className="mt-4 overflow-x-auto rounded-lg border border-line bg-bg/60 p-4 text-[13px] leading-relaxed">
          <code className="mono text-muted">
            <span className="text-faint"># API key</span>
            {"\n"}curl -H <span className="text-cyan">&quot;X-API-Key: $DASHBOARD_API_KEY&quot;</span> \{"\n"}
            {"  "}https://your-host:8080/api/summary
            {"\n\n"}
            <span className="text-faint"># or basic auth</span>
            {"\n"}curl -u <span className="text-cyan">&quot;$USER:$PASS&quot;</span> https://your-host:8080/api/security-score
          </code>
        </pre>
      </div>

      {/* Endpoints */}
      <div className="mt-10 space-y-4">
        {ENDPOINTS.map((e) => (
          <div key={e.path} className="rounded-2xl border border-line bg-panel/30 p-6">
            <div className="flex flex-wrap items-center gap-3">
              <MethodBadge />
              <code className="mono text-sm text-ink">{e.path}</code>
            </div>
            <h3 className="mt-3 font-display text-base font-semibold text-ink">{e.title}</h3>
            <p className="mt-1.5 text-sm leading-relaxed text-muted">{e.desc}</p>
            <div className="mono mt-4 mb-1.5 flex items-center gap-1.5 text-[11px] uppercase tracking-widest text-faint">
              <Terminal className="h-3.5 w-3.5" /> Response
            </div>
            <pre className="overflow-x-auto rounded-lg border border-line bg-bg/60 p-4 text-[12.5px] leading-relaxed">
              <code className="mono text-muted">{e.response}</code>
            </pre>
          </div>
        ))}
      </div>

      {/* Command interface note */}
      <div className="mt-8 rounded-2xl border border-dashed border-line bg-panel/20 p-6">
        <h3 className="font-display text-base font-semibold text-ink">
          Beyond HTTP: the command interface
        </h3>
        <p className="mt-2 text-sm leading-relaxed text-muted">
          Actions like generating a report or asking the AI analyst run through the
          Discord command surface (<code className="mono text-cyan">/report</code>,{" "}
          <code className="mono text-cyan">/analyst</code>) rather than the read-only
          HTTP API. See the{" "}
          <Link href="/docs/api" className="text-cyan hover:underline">
            full command reference
          </Link>
          .
        </p>
      </div>
    </PageShell>
  );
}
