"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { ArrowRight, BookText, Play } from "lucide-react";
import { SOURCES, SITE } from "@/lib/data";
import { NetworkCanvas } from "./network-canvas";
import { GithubIcon } from "./github-icon";

const REPO = SITE.repo;
const ease = [0.22, 1, 0.36, 1] as const;

export function Hero() {
  return (
    <section id="top" className="relative overflow-hidden pt-16">
      {/* ambient background */}
      <div className="pointer-events-none absolute inset-0">
        <NetworkCanvas />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_50%_at_25%_20%,rgba(76,130,251,0.14),transparent_70%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_50%_60%_at_90%_10%,rgba(155,108,255,0.10),transparent_70%)]" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-bg/40 to-bg" />
      </div>

      <div className="relative mx-auto grid max-w-7xl grid-cols-1 items-center gap-12 px-6 pb-24 pt-20 md:pb-32 md:pt-28 lg:grid-cols-[1.05fr_0.95fr]">
        <div>
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease }}
            className="mb-6 inline-flex items-center gap-2 rounded-full border border-line bg-panel/60 px-3 py-1.5"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-cyan" />
            <span className="mono text-[11px] tracking-wider text-muted">
              open source · self-hosted · local AI
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease, delay: 0.05 }}
            className="font-display text-[2.75rem] font-semibold leading-[1.03] tracking-tight text-balance sm:text-6xl md:text-7xl"
          >
            Autonomous threat intelligence.
            <br />
            Self-hosted <span className="gradient-text">cyber operations</span>.
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease, delay: 0.12 }}
            className="mt-6 max-w-xl text-lg leading-relaxed text-muted"
          >
            Cyber Command Center fuses global threat intelligence, correlates it to
            your stack, and acts on it — an AI Security Analyst, a multi-agent report
            crew, and closed-loop remediation, running continuously on your own
            infrastructure. No cloud, no vendor lock-in.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease, delay: 0.19 }}
            className="mt-8 flex flex-wrap items-center gap-3"
          >
            <Link
              href="/demo"
              className="group flex items-center gap-2 rounded-xl bg-ink px-5 py-3 text-sm font-medium text-bg transition-opacity hover:opacity-90"
            >
              <Play className="h-4 w-4 fill-bg" />
              Launch Demo
              <span className="mono rounded-md bg-bg/15 px-1.5 py-0.5 text-[9px] uppercase tracking-wider">
                soon
              </span>
            </Link>
            <a
              href={REPO}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 rounded-xl border border-line bg-panel/60 px-5 py-3 text-sm font-medium transition-colors hover:border-blue/40 hover:bg-panel"
            >
              <GithubIcon className="h-4 w-4" />
              View GitHub
            </a>
            <Link
              href="/docs"
              className="flex items-center gap-1.5 px-2 py-3 text-sm text-muted transition-colors hover:text-ink"
            >
              <BookText className="h-4 w-4" />
              Documentation
            </Link>
            <a
              href="#architecture"
              className="group flex items-center gap-1.5 px-2 py-3 text-sm text-muted transition-colors hover:text-ink"
            >
              Architecture
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </a>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="mt-12"
          >
            <div className="mono mb-3 text-[11px] tracking-wider text-faint">
              CORRELATES INTELLIGENCE FROM
            </div>
            <div className="flex flex-wrap gap-2">
              {SOURCES.map((s) => (
                <span
                  key={s.name}
                  className="mono rounded-lg border border-line bg-panel/40 px-2.5 py-1.5 text-xs text-muted"
                  title={s.note}
                >
                  {s.name}
                </span>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Real product screenshot */}
        <motion.div
          initial={{ opacity: 0, y: 24, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.8, ease, delay: 0.2 }}
          className="relative"
        >
          <div className="absolute -inset-4 rounded-3xl bg-[radial-gradient(ellipse_at_center,rgba(76,130,251,0.18),transparent_70%)] blur-xl" />
          <figure className="glass relative overflow-hidden rounded-2xl border border-line p-2 shadow-2xl">
            <div className="flex items-center gap-1.5 px-2 py-2">
              <span className="h-2.5 w-2.5 rounded-full bg-red/70" />
              <span className="h-2.5 w-2.5 rounded-full bg-amber/70" />
              <span className="h-2.5 w-2.5 rounded-full bg-green/70" />
              <span className="mono ml-2 text-[10px] text-faint">localhost:8080</span>
            </div>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/screenshots/dashboard-overview.png"
              alt="Cyber Command Center SOC dashboard — security score, live threat posture, activity trends, severity mix and fused CVE alerts."
              width={939}
              height={951}
              loading="eager"
              className="h-auto w-full rounded-xl border border-line"
            />
          </figure>
        </motion.div>
      </div>
    </section>
  );
}
