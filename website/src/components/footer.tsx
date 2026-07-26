import Link from "next/link";
import { Logo } from "./logo";
import { GithubIcon } from "./github-icon";
import { SITE } from "@/lib/data";

const REPO = SITE.repo;

const COLUMNS = [
  {
    title: "Platform",
    links: [
      ["Features", "/#platform"],
      ["Architecture", "/#architecture"],
      ["Roadmap", "/#roadmap"],
      ["Stack", "/#stack"],
    ],
  },
  {
    title: "Resources",
    links: [
      ["Documentation", "/docs"],
      ["API Reference", "/api-reference"],
      ["Blog", "/blog"],
      ["Launch Demo", "/demo"],
    ],
  },
  {
    title: "Project",
    links: [
      ["Getting Started", "/docs/getting-started"],
      ["Contributing", `${REPO}/blob/main/CONTRIBUTING.md`],
      ["License (MIT)", `${REPO}/blob/main/LICENSE`],
      ["GitHub", REPO],
    ],
  },
];

export function Footer() {
  return (
    <footer className="border-t border-line">
      <div className="mx-auto max-w-7xl px-6 py-16">
        <div className="grid grid-cols-2 gap-10 md:grid-cols-[1.5fr_repeat(3,1fr)]">
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center gap-2.5">
              <Logo className="h-7 w-7" />
              <span className="font-display text-sm font-semibold tracking-tight">
                Cyber Command Center
              </span>
              <span className="mono rounded-md border border-line bg-panel px-1.5 py-0.5 text-[10px] text-cyan">
                OSS
              </span>
            </Link>
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-muted">
              An open-source, self-hosted AI security operations platform. Monitor,
              learn, automate and respond — from one place.
            </p>
            <a
              href={REPO}
              target="_blank"
              rel="noreferrer"
              className="mt-5 inline-flex items-center gap-2 rounded-lg border border-line bg-panel/60 px-3 py-2 text-sm transition-colors hover:border-blue/40"
            >
              <GithubIcon className="h-4 w-4" /> Star on GitHub
            </a>
          </div>

          {COLUMNS.map((col) => (
            <div key={col.title}>
              <div className="mono text-[11px] uppercase tracking-widest text-faint">
                {col.title}
              </div>
              <ul className="mt-4 space-y-2.5">
                {col.links.map(([label, href]) => (
                  <li key={label}>
                    <a
                      href={href}
                      className="text-sm text-muted transition-colors hover:text-ink"
                      {...(href.startsWith("http")
                        ? { target: "_blank", rel: "noreferrer" }
                        : {})}
                    >
                      {label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-14 flex flex-col items-center justify-between gap-3 border-t border-line pt-8 md:flex-row">
          <p className="mono text-xs text-faint">
            © {new Date().getFullYear()} Cyber Command Center OSS · MIT License
          </p>
          <p className="mono text-xs text-faint">
            Runs on local hardware · No telemetry · No vendor lock-in
          </p>
        </div>
      </div>
    </footer>
  );
}
