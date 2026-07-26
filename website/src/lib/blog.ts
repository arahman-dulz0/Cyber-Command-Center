// Blog content. Posts are authored as markdown here and rendered at build time.
import { marked } from "marked";

export type Post = {
  slug: string;
  title: string;
  date: string; // ISO
  excerpt: string;
  body: string; // markdown
};

export const POSTS: Post[] = [
  {
    slug: "why-i-built-a-self-hosted-soc",
    title: "Why I built a self-hosted, AI-powered SOC",
    date: "2026-07-26",
    excerpt:
      "Threat intelligence is scattered across a dozen tabs. I wanted one system that collects it, fuses it, correlates it against my own stack, and just tells me what to do — running entirely on my own hardware.",
    body: `
Security operations, for most people learning the craft, means keeping a dozen
browser tabs open: NVD for CVEs, CISA KEV for what's exploited, EPSS for
probability, ExploitDB and GitHub for proof-of-concepts, a few RSS feeds for
news. Every morning you re-derive the same question by hand — *does any of this
actually affect me, and what should I do first?*

**Cyber Command Center** is my answer: one self-hosted platform that collects all
of that automatically, fuses it into a single priority score, correlates it
against my own lab inventory, and delivers the result where I already work.

## The pipeline

\`\`\`
CVE → EPSS → CISA KEV → ExploitDB → GitHub PoC → vendor patch
    → AI risk → CCC Priority (0–100) → your stack → action
\`\`\`

A new CVE isn't just posted — it's enriched across every free intelligence
source, scored, checked against my lab keywords, and if it matters, it raises a
remediation ticket with an AI-written checklist. No cloud service sees any of it;
the AI runs locally via Ollama.

## The part I'm most proud of

The **AI Security Analyst**. Instead of memorising twenty slash commands, you ask
in plain English — *"what should I patch today?"* — and it searches the platform's
own knowledge first (your assets, the CVE database, KEV, tickets, the knowledge
base) and only falls back to the language model as the last step. It never answers
from general knowledge first, so it doesn't hallucinate your environment.

## Try it

The whole thing comes up with one command, pre-loaded with a real-CVE demo
dataset so the dashboard is alive on first boot:

\`\`\`bash
git clone https://github.com/arahman-dulz0/Cyber-Command-Center.git
cd Cyber-Command-Center && docker compose up -d   # → http://localhost:8080
\`\`\`

No API keys, no model download, no configuration. That was the whole point.
`,
  },
];

export function postSlugs(): string[] {
  return POSTS.map((p) => p.slug);
}

export function getPost(slug: string): Post | undefined {
  return POSTS.find((p) => p.slug === slug);
}

export function renderPost(body: string): string {
  return marked.parse(body, { async: false }) as string;
}
