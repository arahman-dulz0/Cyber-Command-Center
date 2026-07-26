import Link from "next/link";
import type { Metadata } from "next";
import { ArrowRight } from "lucide-react";
import { PageShell } from "@/components/page-shell";
import { POSTS, UPCOMING } from "@/lib/blog";

export const metadata: Metadata = {
  title: "Blog — Cyber Command Center",
  description: "Notes on building a self-hosted, AI-powered security operations platform.",
};

function fmtDate(iso: string): string {
  return new Date(iso + "T00:00:00Z").toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  });
}

export default function BlogIndex() {
  return (
    <PageShell>
      <div className="eyebrow mb-4">Blog</div>
      <h1 className="font-display text-4xl font-semibold tracking-tight text-ink md:text-5xl">
        Field notes.
      </h1>
      <p className="mt-5 max-w-2xl text-lg leading-relaxed text-muted">
        Building a self-hosted security operations platform, in the open.
      </p>

      <div className="mt-12 space-y-4">
        {POSTS.map((p) => (
          <Link
            key={p.slug}
            href={`/blog/${p.slug}`}
            className="group block rounded-2xl border border-line bg-panel/30 p-6 transition-colors hover:border-blue/40 hover:bg-panel"
          >
            <div className="eyebrow mb-2">{fmtDate(p.date)}</div>
            <h2 className="flex items-center gap-2 font-display text-xl font-semibold text-ink">
              {p.title}
              <ArrowRight className="h-4 w-4 -translate-x-1 text-faint opacity-0 transition-all group-hover:translate-x-0 group-hover:text-cyan group-hover:opacity-100" />
            </h2>
            <p className="mt-2 max-w-2xl text-[15px] leading-relaxed text-muted">
              {p.excerpt}
            </p>
          </Link>
        ))}
      </div>

      {/* Upcoming */}
      <h2 className="mt-16 mb-4 font-display text-sm font-semibold uppercase tracking-widest text-faint">
        Coming soon
      </h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {UPCOMING.map((p) => (
          <div
            key={p.title}
            className="rounded-2xl border border-dashed border-line bg-panel/20 p-6"
          >
            <div className="mono mb-2 inline-block rounded-md border border-line px-2 py-0.5 text-[10px] uppercase tracking-wider text-faint">
              Draft
            </div>
            <h3 className="font-display text-lg font-semibold text-ink">{p.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted">{p.excerpt}</p>
          </div>
        ))}
      </div>
    </PageShell>
  );
}
