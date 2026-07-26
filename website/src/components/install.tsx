"use client";

import { useState } from "react";
import { Check, Copy, Terminal } from "lucide-react";
import { INSTALL } from "@/lib/data";
import { Section } from "./section";
import { Reveal } from "./reveal";

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      type="button"
      aria-label="Copy command"
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(text);
          setCopied(true);
          setTimeout(() => setCopied(false), 1400);
        } catch {
          /* clipboard unavailable */
        }
      }}
      className="shrink-0 rounded-md border border-line p-1.5 text-faint transition-colors hover:border-blue/40 hover:text-cyan"
    >
      {copied ? (
        <Check className="h-3.5 w-3.5 text-green" />
      ) : (
        <Copy className="h-3.5 w-3.5" />
      )}
    </button>
  );
}

export function Install() {
  return (
    <Section
      id="install"
      eyebrow="Quickstart"
      title="Running in one command."
      intro="No Kubernetes, no cloud account, no glue scripts. Clone it and it comes up — pre-seeded with a real-CVE dataset so the dashboard is alive on first boot."
    >
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {INSTALL.map((mode, i) => (
          <Reveal key={mode.key} delay={i * 0.06}>
            <div className="glass flex h-full flex-col rounded-2xl border border-line p-6">
              <div className="mb-4 flex items-center gap-2">
                <Terminal className="h-4 w-4 text-cyan" strokeWidth={1.6} />
                <h3 className="font-display text-lg font-semibold text-ink">
                  {mode.label}
                </h3>
              </div>
              <p className="mb-5 text-sm leading-relaxed text-muted">{mode.blurb}</p>

              <div className="space-y-2">
                {mode.commands.map((cmd) => (
                  <div
                    key={cmd}
                    className="flex items-center gap-3 rounded-lg border border-line bg-bg/60 px-3 py-2"
                  >
                    <span className="select-none text-faint">$</span>
                    <code className="mono flex-1 overflow-x-auto whitespace-pre text-[13px] text-ink">
                      {cmd}
                    </code>
                    <CopyButton text={cmd} />
                  </div>
                ))}
              </div>

              {mode.note && (
                <p className="mt-4 text-xs leading-relaxed text-faint">{mode.note}</p>
              )}
            </div>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}
