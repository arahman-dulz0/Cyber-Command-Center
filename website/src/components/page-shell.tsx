import Link from "next/link";
import type { ReactNode } from "react";
import { ArrowLeft } from "lucide-react";
import { Logo } from "./logo";
import { GithubIcon } from "./github-icon";
import { Footer } from "./footer";
import { SITE } from "@/lib/data";

export function PageShell({ children }: { children: ReactNode }) {
  return (
    <>
      <header className="sticky top-0 z-50 border-b border-line/60 bg-bg/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <Link href="/" className="flex items-center gap-2">
            <Logo className="h-7 w-7" />
            <span className="font-display text-sm font-semibold tracking-tight text-ink">
              Cyber Command Center
            </span>
          </Link>
          <div className="flex items-center gap-4 text-sm">
            <Link href="/docs" className="text-muted transition-colors hover:text-ink">
              Docs
            </Link>
            <Link
              href="/api-reference"
              className="hidden text-muted transition-colors hover:text-ink sm:inline"
            >
              API
            </Link>
            <Link href="/blog" className="text-muted transition-colors hover:text-ink">
              Blog
            </Link>
            <Link
              href="/demo"
              className="hidden text-muted transition-colors hover:text-ink sm:inline"
            >
              Demo
            </Link>
            <a
              href={SITE.repo}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 text-muted transition-colors hover:text-ink"
            >
              <GithubIcon className="h-4 w-4" />
              GitHub
            </a>
          </div>
        </div>
      </header>
      <main className="mx-auto min-h-[70vh] w-full max-w-7xl px-6 py-14">
        <Link
          href="/"
          className="mb-8 inline-flex items-center gap-1.5 text-sm text-faint transition-colors hover:text-cyan"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back to home
        </Link>
        {children}
      </main>
      <Footer />
    </>
  );
}
