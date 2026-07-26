import Link from "next/link";
import type { Metadata } from "next";
import { ArrowRight, Bell, Play, Terminal } from "lucide-react";
import { PageShell } from "@/components/page-shell";
import { GithubIcon } from "@/components/github-icon";
import { SITE } from "@/lib/data";

export const metadata: Metadata = {
  title: "Launch Demo — Cyber Command Center",
  description:
    "A live, hosted demo of the Cyber Command Center SOC dashboard and AI Security Analyst is coming soon. Run the full platform yourself today with one command.",
  alternates: { canonical: "/demo" },
};

export default function DemoPage() {
  return (
    <PageShell>
      <div className="eyebrow mb-4">Live demo</div>
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="font-display text-4xl font-semibold tracking-tight text-ink md:text-5xl">
          Launch Demo
        </h1>
        <span className="mono rounded-full border border-amber/30 bg-amber/10 px-3 py-1 text-xs uppercase tracking-wider text-amber">
          Coming soon
        </span>
      </div>
      <p className="mt-5 max-w-2xl text-lg leading-relaxed text-muted">
        A public, read-only hosted instance of the SOC dashboard and a full video
        walkthrough of the AI Security Analyst are on the way — so you can explore
        the platform without installing anything.
      </p>

      {/* Preview frame */}
      <div className="glass mt-10 overflow-hidden rounded-2xl border border-line p-2">
        <div className="flex items-center gap-1.5 px-2 py-2">
          <span className="h-2.5 w-2.5 rounded-full bg-red/70" />
          <span className="h-2.5 w-2.5 rounded-full bg-amber/70" />
          <span className="h-2.5 w-2.5 rounded-full bg-green/70" />
          <span className="mono ml-2 text-[10px] text-faint">demo.cybercommandcenter.dev</span>
        </div>
        <div className="relative overflow-hidden rounded-xl border border-line">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/screenshots/dashboard-overview.png"
            alt="Preview of the Cyber Command Center SOC dashboard that the hosted demo will feature."
            width={939}
            height={951}
            loading="lazy"
            className="h-auto w-full opacity-70"
          />
          <div className="absolute inset-0 grid place-items-center bg-bg/50 backdrop-blur-[2px]">
            <div className="flex flex-col items-center gap-3 text-center">
              <span className="flex h-16 w-16 items-center justify-center rounded-full border border-line bg-panel/80">
                <Play className="h-6 w-6 translate-x-0.5 text-cyan" />
              </span>
              <div className="mono text-xs uppercase tracking-widest text-muted">
                Hosted demo + walkthrough — coming soon
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Run it yourself now */}
      <div className="mt-12 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="glass rounded-2xl border border-line p-6">
          <div className="mb-3 flex items-center gap-2">
            <Terminal className="h-4 w-4 text-cyan" strokeWidth={1.6} />
            <h2 className="font-display text-lg font-semibold text-ink">
              Don&apos;t wait — run it now
            </h2>
          </div>
          <p className="mb-4 text-sm leading-relaxed text-muted">
            The demo dashboard is one command away, pre-seeded with a real-CVE
            dataset so it&apos;s populated on first boot.
          </p>
          <div className="rounded-lg border border-line bg-bg/60 px-4 py-3">
            <code className="mono text-[13px] text-ink">
              git clone {SITE.repo.replace("https://github.com/", "")} <br />
              docker compose up -d
            </code>
          </div>
          <Link
            href="/docs/getting-started"
            className="mt-4 inline-flex items-center gap-1.5 text-sm text-cyan hover:underline"
          >
            Full setup guide <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        <div className="glass flex flex-col justify-between rounded-2xl border border-line p-6">
          <div>
            <div className="mb-3 flex items-center gap-2">
              <Bell className="h-4 w-4 text-cyan" strokeWidth={1.6} />
              <h2 className="font-display text-lg font-semibold text-ink">
                Get notified
              </h2>
            </div>
            <p className="text-sm leading-relaxed text-muted">
              Watch or star the repository to be first to know when the hosted demo
              and video walkthrough go live.
            </p>
          </div>
          <div className="mt-5 flex flex-wrap gap-3">
            <a
              href={SITE.repo}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 rounded-xl bg-ink px-4 py-2.5 text-sm font-medium text-bg transition-opacity hover:opacity-90"
            >
              <GithubIcon className="h-4 w-4" /> Star on GitHub
            </a>
            <Link
              href="/docs"
              className="rounded-xl border border-line bg-panel/60 px-4 py-2.5 text-sm font-medium transition-colors hover:border-blue/40 hover:bg-panel"
            >
              Read the docs
            </Link>
          </div>
        </div>
      </div>
    </PageShell>
  );
}
