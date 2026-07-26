// Content model for the Cyber Command Center OSS site.
// Icon fields hold Lucide component names, resolved in the UI via an icon map.

export type Module = {
  name: string;
  icon: string;
  category: "Intelligence" | "AI" | "Operations" | "Platform";
  blurb: string;
};

export const FEATURE_CATEGORIES = [
  "Intelligence",
  "AI",
  "Operations",
  "Platform",
] as const;

export const MODULES: Module[] = [
  // --- Intelligence ---
  {
    name: "Threat Intelligence Fusion",
    icon: "GitMerge",
    category: "Intelligence",
    blurb:
      "Correlates every CVE across EPSS probability, CISA KEV, ExploitDB and GitHub PoCs into a single 0–100 exploitability-weighted priority score.",
  },
  {
    name: "Autonomous CVE Monitoring",
    icon: "ShieldAlert",
    category: "Intelligence",
    blurb:
      "Hourly NVD sweeps by published date and CVSS severity, de-duplicated and enriched — the moment a threat lands, it's scored and triaged.",
  },
  {
    name: "Cyber News Intelligence",
    icon: "Newspaper",
    category: "Intelligence",
    blurb:
      "Multi-source news collection from leading security outlets and CISA advisories, summarized by a local model and delivered to your team.",
  },
  {
    name: "Asset Inventory",
    icon: "Boxes",
    category: "Intelligence",
    blurb:
      "Declare your stack once; every alert, ticket and answer is automatically correlated to the technologies you actually run.",
  },
  // --- AI ---
  {
    name: "AI Security Analyst",
    icon: "Sparkles",
    category: "AI",
    blurb:
      "Ask anything in plain English. It searches your own data first — assets, CVEs, KEV, tickets, knowledge base — and reaches for the LLM only as the last step, so it never guesses.",
  },
  {
    name: "Multi-Agent AI Crew",
    icon: "Users",
    category: "AI",
    blurb:
      "A Planner, Researcher, CVE Analyst, Coach and Writer hand off in sequence to synthesize board-ready intelligence reports on demand.",
  },
  {
    name: "Knowledge Base (RAG)",
    icon: "BookOpen",
    category: "AI",
    blurb:
      "Embeds your notes, write-ups and PDFs locally so answers cite your own material — grounded retrieval, private by default, powered by Ollama.",
  },
  {
    name: "Executive Reports",
    icon: "FileText",
    category: "AI",
    blurb:
      "Scheduled and on-demand reports: executive summary, threat level, risk score, affected assets and prioritized remediation — archived for review.",
  },
  // --- Operations ---
  {
    name: "SOC Dashboard",
    icon: "LayoutDashboard",
    category: "Operations",
    blurb:
      "A live operations view: security score, threat level, severity mix, activity trends, fused alerts and open tickets — read-only over your database.",
  },
  {
    name: "Discord Operations",
    icon: "MessageSquare",
    category: "Operations",
    blurb:
      "Twenty-two slash commands turn a Discord workspace into the control surface for the entire platform — chat is the SOC.",
  },
  {
    name: "Ticketing",
    icon: "Ticket",
    category: "Operations",
    blurb:
      "Remediation tickets auto-raised when a high-priority CVE hits your stack, deduplicated per CVE, with an AI-drafted checklist — triage and close from chat.",
  },
  {
    name: "Automation Engine",
    icon: "Workflow",
    category: "Operations",
    blurb:
      "Closed-loop actioning: match → ticket → escalate. Background monitors run inside the process — no cron, no scheduler, no extra services.",
  },
  // --- Platform ---
  {
    name: "Health Monitoring",
    icon: "Activity",
    category: "Platform",
    blurb:
      "Heartbeat healthchecks, auto-heal and uptime monitoring keep every service running — the platform recovers from failure on its own.",
  },
  {
    name: "Backups",
    icon: "Database",
    category: "Platform",
    blurb:
      "Automated, retained database and knowledge-base backups with one-command restore — your intelligence is never a single disk away from gone.",
  },
  {
    name: "Security Hardening",
    icon: "ShieldCheck",
    category: "Platform",
    blurb:
      "Authentication, API keys, rate limiting, strict security headers, audit logging and locked-down containers — built for exposure, not just a lab.",
  },
  {
    name: "Open Source",
    icon: "Code2",
    category: "Platform",
    blurb:
      "MIT-licensed, Docker-ready and fully self-hosted. Read every line, run it on your own hardware, and extend it with a single-file plugin.",
  },
];

export type Source = { name: string; note: string };
export const SOURCES: Source[] = [
  { name: "NVD", note: "CVE feed" },
  { name: "CISA KEV", note: "known exploited" },
  { name: "EPSS", note: "exploit probability" },
  { name: "ExploitDB", note: "public exploits" },
  { name: "GitHub", note: "PoC repositories" },
  { name: "RSS", note: "security news" },
  { name: "YouTube", note: "learning feeds" },
];

export type Phase = { n: number; title: string; body: string; status: "shipped" | "planned" };
export const PHASES: Phase[] = [
  { n: 1, title: "Foundation", status: "shipped", body: "Async Discord bot, PostgreSQL and Redis, structured logging, on-demand CVE and news lookups." },
  { n: 2, title: "Threat Intelligence", status: "shipped", body: "Autonomous hourly CVE monitoring and multi-source news collection with de-duplication." },
  { n: 3, title: "Intelligence Fusion", status: "shipped", body: "EPSS + KEV + ExploitDB + GitHub PoC correlation into a single prioritized alert." },
  { n: 4, title: "Learning Intelligence", status: "shipped", body: "HackTheBox import, a practice journal, and AI recommendations that fill skill gaps." },
  { n: 5, title: "RAG Knowledge Base", status: "shipped", body: "Local embeddings over your own documents so the assistant answers from your material." },
  { n: 6, title: "SOC Dashboard", status: "shipped", body: "A self-hosted operations dashboard reading live from the same database." },
  { n: 7, title: "Multi-Agent Crew", status: "shipped", body: "Specialised agents that hand off to synthesize intelligence reports." },
  { n: 8, title: "Automation & Actioning", status: "shipped", body: "Lab-aware matching that raises tickets and escalates the CVEs that affect you." },
  { n: 9, title: "AI Security Analyst", status: "shipped", body: "A single natural-language interface over the whole platform: classify intent, plan multi-step tool calls, search your own data first, and answer with rich embeds — the LLM is the last resort, never the first." },
  { n: 10, title: "Hosted Demo & Integrations", status: "planned", body: "A public, read-only hosted demo, plus Slack and Microsoft Teams delivery alongside Discord — so anyone can explore the platform, and any team can adopt it." },
];

export type TechGroup = { group: string; items: string[] };
export const TECH: TechGroup[] = [
  { group: "Infrastructure", items: ["Proxmox", "Ubuntu Server", "Docker", "Docker Compose"] },
  { group: "Backend", items: ["Python", "FastAPI", "discord.py", "asyncpg"] },
  { group: "AI", items: ["Ollama", "Qwen2.5", "nomic-embed-text", "RAG"] },
  { group: "Data", items: ["PostgreSQL", "Redis"] },
  { group: "Frontend", items: ["Next.js", "React", "TailwindCSS", "Recharts"] },
  { group: "Delivery", items: ["Docker", "Cloudflare", "GitHub"] },
];

export type Stat = { value: string; label: string };
export const STATS: Stat[] = [
  { value: "22", label: "Discord commands" },
  { value: "8", label: "Development phases" },
  { value: "5", label: "AI agents" },
  { value: "4", label: "Background monitors" },
  { value: "24/7", label: "Autonomous operation" },
  { value: "100%", label: "Self-hosted" },
];

export type ArchNode = {
  id: string;
  label: string;
  kind: "source" | "core" | "store" | "output";
  desc: string;
};
export const ARCH: ArchNode[] = [
  { id: "sources", label: "Threat Sources", kind: "source", desc: "NVD, CISA KEV, EPSS, ExploitDB, GitHub advisories and security news — the world's public threat intelligence, polled on independent schedules." },
  { id: "collectors", label: "Collectors", kind: "source", desc: "Autonomous background monitors fetch, normalize and de-duplicate every source in-process — storing only what's genuinely new. No cron, no scheduler." },
  { id: "fusion", label: "Threat Intelligence Fusion", kind: "core", desc: "The core differentiator: each CVE is correlated across EPSS, CISA KEV, ExploitDB and GitHub PoCs into a single exploitability-weighted 0–100 priority score." },
  { id: "data", label: "PostgreSQL + Redis", kind: "store", desc: "All intelligence, enrichment, embeddings, tickets and metrics persist in PostgreSQL; Redis handles fast ephemeral state. Everything on your own infrastructure." },
  { id: "analyst", label: "AI Security Analyst", kind: "core", desc: "Local Ollama models power a natural-language analyst that classifies intent, plans multi-step tool calls, and answers from your own data first — the LLM is the last step, never the first." },
  { id: "surfaces", label: "Discord · Dashboard · Knowledge Base · Automation", kind: "output", desc: "Delivered where you work: a chat control surface, a live SOC dashboard, RAG over your own notes, and closed-loop automation that raises tickets and escalates." },
  { id: "team", label: "Security Team", kind: "output", desc: "Your team receives prioritized, correlated, already-actioned intelligence — not a firehose of raw alerts. Decisions in seconds, not hours." },
];

// --- Single source of truth for outbound links ------------------------------
export const SITE = {
  repo: "https://github.com/arahman-dulz0/Cyber-Command-Center",
  docsBase: "https://github.com/arahman-dulz0/Cyber-Command-Center/blob/main/docs",
};

// --- Install (the one-command story) ----------------------------------------
export type InstallMode = {
  key: string;
  label: string;
  blurb: string;
  commands: string[];
  note?: string;
};
export const INSTALL: InstallMode[] = [
  {
    key: "demo",
    label: "Try the dashboard",
    blurb: "Postgres pre-loaded with a real-CVE demo dataset + the SOC dashboard. No config, no keys, no model download.",
    commands: [
      "git clone https://github.com/arahman-dulz0/Cyber-Command-Center.git",
      "cd Cyber-Command-Center",
      "docker compose up -d",
    ],
    note: "Open http://localhost:8080 — a fully populated dashboard in ~30s.",
  },
  {
    key: "full",
    label: "Full platform",
    blurb: "Adds the Discord bot, Redis and a local Ollama for the complete autonomous experience.",
    commands: [
      "cp .env.example .env        # set DISCORD_TOKEN",
      "docker compose --profile full up -d",
      "docker compose exec ollama ollama pull qwen2.5:3b",
    ],
    note: "The AI runs locally — nothing leaves your machine.",
  },
];

// --- Documentation index (deep-links to the real docs) ----------------------
export type DocLink = { title: string; body: string; path: string };
export const DOC_LINKS: DocLink[] = [
  { title: "Getting Started", body: "Clone → Discord bot → run the full platform, step by step.", path: "getting-started.md" },
  { title: "Developer Guide", body: "Repo layout, the repository pattern, local dev.", path: "developer-guide.md" },
  { title: "API & Commands", body: "All 22 slash commands + the dashboard HTTP API.", path: "api.md" },
  { title: "Architecture", body: "How collection, fusion, AI and delivery fit together.", path: "phase6.md" },
  { title: "Deployment", body: "Ship the bot and dashboard to your server.", path: "operations.md" },
  { title: "Security", body: "Auth, rate limiting, headers, going public.", path: "security.md" },
  { title: "Threat Intelligence", body: "CVE monitoring and multi-source fusion.", path: "phase3.md" },
  { title: "Learning Intelligence", body: "HackTheBox import and recommendations.", path: "phase4.md" },
  { title: "Knowledge Base", body: "Ingest documents and query with RAG.", path: "phase5.md" },
  { title: "Automation", body: "Asset matching, tickets and escalation.", path: "phase8.md" },
  { title: "Plugins", body: "Add a monitor, enrichment source, or analyst tool.", path: "plugins.md" },
  { title: "Troubleshooting & FAQ", body: "Symptom → cause → fix, and common questions.", path: "troubleshooting.md" },
  { title: "Contributing", body: "Open an issue, send a PR, or write a plugin.", path: "contributing.md" },
];

// --- What's next (roadmap forward-look) -------------------------------------
export const NEXT: { title: string; body: string }[] = [
  { title: "Plugin marketplace", body: "Drop-in monitors, enrichment sources and analyst tools contributed by the community." },
  { title: "Managed cloud option", body: "An optional hosted deployment for teams that want the platform without running the infrastructure." },
  { title: "Community detections", body: "Shared detection and correlation rules, versioned and installable in one command." },
];
