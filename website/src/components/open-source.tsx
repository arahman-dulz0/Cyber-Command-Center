import {
  Scale,
  ServerCog,
  Lock,
  Container,
  HeartHandshake,
  Ban,
  Cpu,
  GitFork,
  Star,
  CircleDot,
  GitPullRequest,
} from "lucide-react";
import { Reveal } from "./reveal";
import { GithubIcon } from "./github-icon";
import { SITE } from "@/lib/data";

const PRINCIPLES = [
  { icon: Scale, title: "MIT licensed", body: "Permissive. Fork it, ship it, sell your services on top." },
  { icon: ServerCog, title: "Self-hosted", body: "Runs on your Proxmox, your Docker, your rules." },
  { icon: Lock, title: "Privacy first", body: "AI runs on local Ollama models — your data never leaves." },
  { icon: Container, title: "Docker ready", body: "Compose up the whole platform in minutes." },
  { icon: Cpu, title: "Runs locally", body: "No cloud dependency for core operations." },
  { icon: Ban, title: "No subscription", body: "No seats, no metering, no per-CVE pricing." },
  { icon: GitFork, title: "No lock-in", body: "Open formats, open database, open source end to end." },
  { icon: HeartHandshake, title: "Community driven", body: "Built in the open and shaped by contributors." },
];

export function OpenSource() {
  return (
    <section id="open-source" className="relative mx-auto w-full max-w-7xl px-6 py-24 md:py-32">
      <div className="glass overflow-hidden rounded-3xl">
        <div className="relative border-b border-line px-8 py-12 md:px-12">
          <div className="grid-field absolute inset-0 opacity-70" aria-hidden />
          <Reveal className="relative max-w-2xl">
            <div className="eyebrow mb-4">Open source</div>
            <h2 className="font-display text-3xl font-semibold tracking-tight text-balance md:text-5xl">
              Yours to run, forever.
            </h2>
            <p className="mt-5 text-lg leading-relaxed text-muted">
              This is a real, complete platform released as open source — not a
              trial, not a freemium tier. Own the whole stack.
            </p>
          </Reveal>
        </div>
        <div className="grid grid-cols-1 gap-px bg-line sm:grid-cols-2 lg:grid-cols-4">
          {PRINCIPLES.map((p) => (
            <div key={p.title} className="bg-panel/40 p-6">
              <p.icon className="h-5 w-5 text-cyan" strokeWidth={1.6} />
              <h3 className="mt-4 font-display text-base font-semibold text-ink">
                {p.title}
              </h3>
              <p className="mt-1.5 text-sm leading-relaxed text-muted">{p.body}</p>
            </div>
          ))}
        </div>

        {/* GitHub band */}
        <div className="flex flex-col items-center justify-between gap-5 border-t border-line px-8 py-8 md:flex-row md:px-12">
          <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-muted">
            <span className="flex items-center gap-2">
              <Star className="h-4 w-4 text-cyan" /> Star the project
            </span>
            <span className="flex items-center gap-2">
              <CircleDot className="h-4 w-4 text-cyan" /> Open an issue
            </span>
            <span className="flex items-center gap-2">
              <GitPullRequest className="h-4 w-4 text-cyan" /> Send a PR
            </span>
          </div>
          <a
            href={SITE.repo}
            target="_blank"
            rel="noreferrer"
            className="flex shrink-0 items-center gap-2 rounded-xl bg-ink px-5 py-3 text-sm font-medium text-bg transition-opacity hover:opacity-90"
          >
            <GithubIcon className="h-4 w-4" /> Contribute on GitHub
          </a>
        </div>
      </div>
    </section>
  );
}
