// Build-time markdown loader for the /docs pages.
// Reads the real docs/*.md files from the repo (single source of truth) and
// renders them to HTML. Runs only on the server at build time.

import fs from "node:fs";
import path from "node:path";
import { marked } from "marked";
import { SITE } from "./data";

const DOCS_DIR = path.join(process.cwd(), "..", "docs");

// Curated order + friendly titles for the docs index.
export const DOC_ORDER: { slug: string; title: string; group: string }[] = [
  { slug: "developer-guide", title: "Developer Guide", group: "Guides" },
  { slug: "api", title: "API & Commands", group: "Guides" },
  { slug: "plugins", title: "Plugins", group: "Guides" },
  { slug: "operations", title: "Operations", group: "Guides" },
  { slug: "security", title: "Security", group: "Guides" },
  { slug: "troubleshooting", title: "Troubleshooting", group: "Guides" },
  { slug: "faq", title: "FAQ", group: "Guides" },
  { slug: "phase1", title: "1 · Foundation", group: "Phase deep-dives" },
  { slug: "phase2", title: "2 · Threat Intelligence", group: "Phase deep-dives" },
  { slug: "phase3", title: "3 · Intelligence Fusion", group: "Phase deep-dives" },
  { slug: "phase4", title: "4 · Learning Intelligence", group: "Phase deep-dives" },
  { slug: "phase5", title: "5 · RAG Knowledge Base", group: "Phase deep-dives" },
  { slug: "phase6", title: "6 · SOC Dashboard", group: "Phase deep-dives" },
  { slug: "phase7", title: "7 · Multi-Agent Crew", group: "Phase deep-dives" },
  { slug: "phase8", title: "8 · Automation & Actioning", group: "Phase deep-dives" },
];

export function docSlugs(): string[] {
  return DOC_ORDER.map((d) => d.slug);
}

export function docTitle(slug: string): string {
  return DOC_ORDER.find((d) => d.slug === slug)?.title ?? slug;
}

/** Read + render one doc to HTML, rewriting inter-doc links to site routes. */
export function renderDoc(slug: string): string | null {
  const file = path.join(DOCS_DIR, `${slug}.md`);
  if (!fs.existsSync(file)) return null;
  const md = fs.readFileSync(file, "utf8");
  let html = marked.parse(md, { async: false }) as string;

  // Rewrite links between docs so they stay inside the site.
  html = html
    .replace(/href="\.\.\/README\.md"/g, `href="/"`)
    .replace(/href="([\w-]+)\.md"/g, (_m, s) => `href="/docs/${s}"`)
    .replace(/href="([\w-]+)\.md#/g, (_m, s) => `href="/docs/${s}#`);

  // Point any remaining repo-relative references at GitHub.
  html = html.replace(/href="(docs\/[^"]+)"/g, `href="${SITE.repo}/blob/main/$1"`);
  return html;
}
