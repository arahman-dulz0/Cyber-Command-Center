"use client";

import { motion } from "motion/react";
import { ArrowRight, Play } from "lucide-react";
import { SOURCES, SITE } from "@/lib/data";
import { NetworkCanvas } from "./network-canvas";
import { ConsoleCard } from "./console-card";
import { GithubIcon } from "./github-icon";

const REPO = SITE.repo;

const ease = [0.22, 1, 0.36, 1] as const;

export function Hero() {
  return (
    <section id="top" className="relative overflow-hidden pt-16">
      {/* ambient background */}
      <div className="pointer-events-none absolute inset-0">
        <NetworkCanvas />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_50%_at_30%_30%,rgba(76,130,251,0.12),transparent_70%)]" />
        <div className="absolute inset-0 bg-gradient-to-r from-bg via-bg/70 to-transparent" />
        <div className="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-bg to-transparent" />
      </div>

      <div className="relative mx-auto grid max-w-7xl grid-cols-1 items-center gap-12 px-6 pb-24 pt-20 md:pb-32 md:pt-28 lg:grid-cols-[1.1fr_0.9fr]">
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
            className="font-display text-5xl font-semibold leading-[1.02] tracking-tight text-balance md:text-7xl"
          >
            The security operations
            <br />
            platform that{" "}
            <span className="gradient-text">runs itself</span>.
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease, delay: 0.12 }}
            className="mt-6 max-w-xl text-lg leading-relaxed text-muted"
          >
            One platform to monitor threats, correlate intelligence, learn, and
            respond. Cyber Command Center OSS collects CVEs, fuses them with EPSS,
            CISA KEV, ExploitDB and GitHub PoCs, and acts — continuously, on your
            own infrastructure.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease, delay: 0.19 }}
            className="mt-8 flex flex-wrap items-center gap-3"
          >
            <a
              href="#demo"
              className="group flex items-center gap-2 rounded-xl bg-ink px-5 py-3 text-sm font-medium text-bg transition-opacity hover:opacity-90"
            >
              <Play className="h-4 w-4 fill-bg" />
              Watch the demo
            </a>
            <a
              href={REPO}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 rounded-xl border border-line bg-panel/60 px-5 py-3 text-sm font-medium transition-colors hover:border-blue/40 hover:bg-panel"
            >
              <GithubIcon className="h-4 w-4" />
              View on GitHub
            </a>
            <a
              href="#architecture"
              className="group flex items-center gap-1.5 px-2 py-3 text-sm text-muted transition-colors hover:text-ink"
            >
              See the architecture
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

        <motion.div
          initial={{ opacity: 0, y: 24, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.8, ease, delay: 0.2 }}
          className="flex justify-center lg:justify-end"
        >
          <div className="animate-floaty">
            <ConsoleCard />
          </div>
        </motion.div>
      </div>
    </section>
  );
}
