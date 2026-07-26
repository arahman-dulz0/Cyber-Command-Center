import { ArrowRight, BookText } from "lucide-react";
import { Section } from "./section";
import { Reveal } from "./reveal";
import { GithubIcon } from "./github-icon";
import { SITE, DOC_LINKS } from "@/lib/data";

const REPO = SITE.repo;

export function Docs() {
  return (
    <>
      <Section
        id="docs"
        eyebrow="Documentation"
        title="Everything you need to run it yourself."
        intro="A complete manual — from first boot to contributing back. Written for operators, not just developers."
      >
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {DOC_LINKS.map(({ title, body, path }, i) => (
            <Reveal key={title} delay={(i % 3) * 0.05}>
              <a
                href={`${SITE.docsBase}/${path}`}
                target="_blank"
                rel="noreferrer"
                className="group flex h-full items-start gap-4 rounded-xl border border-line bg-panel/30 p-5 transition-colors hover:border-blue/40 hover:bg-panel"
              >
                <BookText className="mt-0.5 h-5 w-5 shrink-0 text-cyan" strokeWidth={1.6} />
                <div className="flex-1">
                  <div className="flex items-center gap-1.5">
                    <h3 className="font-display text-base font-semibold text-ink">
                      {title}
                    </h3>
                    <ArrowRight className="h-3.5 w-3.5 -translate-x-1 text-faint opacity-0 transition-all group-hover:translate-x-0 group-hover:text-cyan group-hover:opacity-100" />
                  </div>
                  <p className="mt-1 text-sm leading-relaxed text-muted">{body}</p>
                </div>
              </a>
            </Reveal>
          ))}
        </div>
      </Section>

      {/* closing CTA band */}
      <section className="mx-auto w-full max-w-7xl px-6 pb-28">
        <Reveal>
          <div className="glass glow-blue relative overflow-hidden rounded-3xl px-8 py-14 text-center md:py-20">
            <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_50%_60%_at_50%_0%,rgba(76,130,251,0.16),transparent_70%)]" />
            <div className="relative mx-auto max-w-2xl">
              <h2 className="font-display text-3xl font-semibold tracking-tight text-balance md:text-5xl">
                Stand up your own{" "}
                <span className="accent-text">command center</span>.
              </h2>
              <p className="mx-auto mt-5 max-w-xl text-lg leading-relaxed text-muted">
                Clone the repository, add your keys, and{" "}
                <span className="mono text-cyan">docker compose up</span>. You&apos;re
                running a full security operations platform.
              </p>
              <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
                <a
                  href={REPO}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-2 rounded-xl bg-ink px-5 py-3 text-sm font-medium text-bg transition-opacity hover:opacity-90"
                >
                  <GithubIcon className="h-4 w-4" />
                  Get it on GitHub
                </a>
                <a
                  href="#docs"
                  className="rounded-xl border border-line bg-panel/60 px-5 py-3 text-sm font-medium transition-colors hover:border-blue/40 hover:bg-panel"
                >
                  Read the docs
                </a>
              </div>
            </div>
          </div>
        </Reveal>
      </section>
    </>
  );
}
