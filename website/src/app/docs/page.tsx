import Link from "next/link";
import type { Metadata } from "next";
import { ArrowRight, BookText } from "lucide-react";
import { PageShell } from "@/components/page-shell";
import { DOC_ORDER } from "@/lib/content";

export const metadata: Metadata = {
  title: "Documentation — Cyber Command Center",
  description:
    "Guides and phase deep-dives for the self-hosted, AI-powered cybersecurity operations platform.",
};

export default function DocsIndex() {
  const groups = Array.from(new Set(DOC_ORDER.map((d) => d.group)));
  return (
    <PageShell>
      <div className="eyebrow mb-4">Documentation</div>
      <h1 className="font-display text-4xl font-semibold tracking-tight text-ink md:text-5xl">
        Everything you need to run it yourself.
      </h1>
      <p className="mt-5 max-w-2xl text-lg leading-relaxed text-muted">
        Written for operators, not just developers — from first boot to extending
        the platform.
      </p>

      {groups.map((group) => (
        <div key={group} className="mt-12">
          <h2 className="mb-4 font-display text-sm font-semibold uppercase tracking-widest text-faint">
            {group}
          </h2>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {DOC_ORDER.filter((d) => d.group === group).map((d) => (
              <Link
                key={d.slug}
                href={`/docs/${d.slug}`}
                className="group flex items-start gap-4 rounded-xl border border-line bg-panel/30 p-5 transition-colors hover:border-blue/40 hover:bg-panel"
              >
                <BookText className="mt-0.5 h-5 w-5 shrink-0 text-cyan" strokeWidth={1.6} />
                <div className="flex items-center gap-1.5">
                  <h3 className="font-display text-base font-semibold text-ink">
                    {d.title}
                  </h3>
                  <ArrowRight className="h-3.5 w-3.5 -translate-x-1 text-faint opacity-0 transition-all group-hover:translate-x-0 group-hover:text-cyan group-hover:opacity-100" />
                </div>
              </Link>
            ))}
          </div>
        </div>
      ))}
    </PageShell>
  );
}
