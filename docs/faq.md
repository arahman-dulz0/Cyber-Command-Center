# FAQ

### What is Cyber Command Center?

A self-hosted, AI-powered cybersecurity operations platform. It autonomously
collects and fuses threat intelligence (CVEs, EPSS, CISA KEV, ExploitDB, GitHub
PoCs, news), correlates it against *your* stack, raises remediation tickets,
answers natural-language questions, and writes intelligence reports — all on your
own hardware.

### Is it just a Discord bot?

Discord is the primary interface, but no. It's an autonomous monitoring engine, a
threat-intel fusion pipeline, a RAG knowledge base, a multi-agent report crew, a
web dashboard, and a closed-loop actioning system. Discord is the chat surface.

### Do I need to send my data to anyone?

No. It's fully self-hosted. The AI runs **locally via Ollama** — prompts never
leave your machine. The only outbound traffic is to public threat-intel sources
(NVD, EPSS, CISA KEV, RSS feeds), and those are configurable.

### Does it cost anything?

No paid services are required. Every intelligence source used is free, and the AI
is a local open model. You supply the hardware.

### What are the hardware requirements?

Modest. It runs on a home server / small VM. The AI model (`qwen2.5:3b`) runs on
CPU — no GPU required. On a CPU-only host, expect fast structured answers
(<1s) and ~6–22s for AI-written explanations/reports.

### Is the demo data real?

Yes. The demo dataset (`docker/demo/initdb/`) is built from **real, publicly
documented CVEs** (Log4Shell, Spring4Shell, MOVEit, Citrix Bleed, …) with
accurate CVSS/KEV/EPSS values. Nothing is fabricated.

### How do I try it without setting anything up?

```bash
git clone <repo> && cd Cyber-Command-Center
docker compose up -d          # → http://localhost:8080
```

Postgres auto-seeds and the dashboard is fully populated. No `.env`, no tokens,
no model download. Add the Discord bot + AI with `--profile full`.

### What AI model does it use, and can I change it?

`qwen2.5:3b` for chat/analysis and `nomic-embed-text` for RAG embeddings, both via
Ollama. Change `OLLAMA_MODEL` in `.env` to any Ollama model. Larger models give
better answers but are slower on CPU.

### Does the AI make things up?

The AI Analyst searches **platform knowledge first** (assets → DB → RAG → threat
intel → CVE/KEV/EPSS → news) and only uses the LLM as the last step. Structured
answers (patch plans, asset exposure, tickets) are built deterministically from
your data — no LLM, no hallucination. Explanatory answers are grounded in
retrieved context and cite sources.

### How does "asset correlation" work?

You add keywords to your lab inventory (`/lab add tech: apache`). The platform
whole-word-matches those against incoming CVE products/descriptions and open
tickets, so every relevant answer ("what should I patch today?", "does CVE-X
affect my lab?") is scoped to *your* stack.

### Is the dashboard safe to expose to the internet?

By default it's LAN-only with Basic Auth + API keys + rate limiting + strict
security headers. To expose it publicly, follow **[security.md](security.md)**
(reverse proxy + TLS + fail2ban). The demo "open mode" is for localhost only.

### Can I extend it?

Yes — see **[plugins.md](plugins.md)**. New monitors, enrichment sources, and
analyst tools are each a small, single-file extension point.

### What's the license?

MIT. Self-hosted, no telemetry.
