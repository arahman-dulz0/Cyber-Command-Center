# Cyber Command Center OSS — product website

The marketing site for **Cyber Command Center OSS**, an open-source, self-hosted
AI cybersecurity operations platform. Built to read like a commercial security
SaaS, not a project page.

## Design direction — "instrument panel for the modern SOC"

Deliberate choices, not template defaults:

- **Signature 1 — live threat-network canvas.** The hero renders the real data
  pipeline: source nodes (NVD, CISA, EPSS, ExploitDB, GitHub, RSS) feeding a
  glowing core, with data pulses traveling the edges. Paired with a glass
  "console" card that ticks through fused CVE alerts.
- **Signature 2 — a monospace operations layer.** Every eyebrow, CVE id, metric
  and command name is set in mono, like telemetry on an instrument panel — the
  SOC feeling with zero green-terminal / hacker clichés.
- **Structure encodes meaning.** Numbered markers appear only on the roadmap (a
  real 8-phase sequence); modules are a set, so they carry no fake numbering.

### Tokens

| Role | Value |
|------|-------|
| Background | `#05070d` space-black · `#0b1120` navy panel |
| Text | `#e8eef7` ink · `#97a4b9` muted |
| Accents | electric-blue `#4c82fb` → cyan `#34e4ea` → violet `#9b6cff` |
| Type | Space Grotesk (display) · Inter (body) · JetBrains Mono (telemetry) |

## Stack

Next.js 16 (App Router) · React 19 · TypeScript · Tailwind CSS v4 ·
Framer Motion (`motion`) · Lucide icons. Static-generated, dark-mode only.

## Sections

Hero · live stats · why-it-exists · 15 platform modules · interactive
architecture · 8-phase roadmap · product demo mock · tech stack · open-source ·
documentation portal · CTA · footer.

## Develop

```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
npm start        # serve the production build
```

## Deploy

### Vercel (recommended)
Import the repository (root directory = `website/`) into Vercel — zero config.

```bash
npx vercel --cwd website          # preview
npx vercel --cwd website --prod   # production
```

### Docker (self-hosted)
Uses Next.js `output: "standalone"` for a small runtime image.

```bash
docker build -t ccc-website ./website
docker run -p 3000:3000 ccc-website
# http://localhost:3000
```

### Static export / GitHub Pages
The site is fully static. For GitHub Pages, set `output: "export"` in
`next.config.ts`, run `npm run build`, and publish the generated `out/`
directory. (The `robots`/`sitemap` route handlers assume a real domain — set
`metadataBase` first.)

## Accessibility & performance

- WCAG-minded contrast on a dark palette, visible keyboard focus, semantic
  landmarks and ARIA labels on interactive controls.
- `prefers-reduced-motion` is respected — the canvas renders a static frame and
  ticker/counter animations are disabled.
- Statically prerendered, no client data fetching, fonts via `next/font`.

## Accuracy

Copy describes the real platform: correlation of CVEs with EPSS, CISA KEV,
ExploitDB and GitHub PoCs; autonomous collection; local Ollama models; RAG over
personal notes; multi-agent reporting; and closed-loop remediation. The demo
frame is an illustrative mock — swap in a real recording at `#demo`.
