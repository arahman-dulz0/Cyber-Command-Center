// Content model for the Cyber Command Center OSS site.
// Icon fields hold Lucide component names, resolved in the UI via an icon map.

export type Module = {
  name: string;
  icon: string;
  tag: string;
  blurb: string;
};

export const MODULES: Module[] = [
  {
    name: "Threat Intelligence",
    icon: "Radar",
    tag: "collect",
    blurb:
      "Pulls CVEs, advisories and alerts from NVD, CISA and vendor feeds on a schedule — no manual checking.",
  },
  {
    name: "Autonomous CVE Monitoring",
    icon: "ShieldAlert",
    tag: "collect",
    blurb:
      "Watches NVD by published date and CVSS severity every hour, de-duplicates, and stores what's new.",
  },
  {
    name: "Threat Intelligence Fusion",
    icon: "GitMerge",
    tag: "correlate",
    blurb:
      "Correlates each CVE with EPSS probability, CISA KEV, ExploitDB and GitHub PoCs into a 0–100 priority score.",
  },
  {
    name: "Learning Intelligence",
    icon: "GraduationCap",
    tag: "learn",
    blurb:
      "Imports your HackTheBox progress and practice log, then recommends the box that targets your weakest area.",
  },
  {
    name: "Knowledge Base (RAG)",
    icon: "BookOpen",
    tag: "knowledge",
    blurb:
      "Embeds your notes, write-ups and PDFs locally so answers cite your own material, not the open internet.",
  },
  {
    name: "AI Assistant",
    icon: "Bot",
    tag: "ai",
    blurb:
      "Grounded question answering over the knowledge base using local Ollama models — private by default.",
  },
  {
    name: "Multi-Agent Crew",
    icon: "Users",
    tag: "ai",
    blurb:
      "A Planner, Researcher, CVE Analyst, Learning Coach and Writer hand off in sequence to produce one report.",
  },
  {
    name: "SOC Dashboard",
    icon: "LayoutDashboard",
    tag: "operate",
    blurb:
      "A read-only operations view: threat level, priority distribution, timelines and open action tickets.",
  },
  {
    name: "Automation Engine",
    icon: "Workflow",
    tag: "automate",
    blurb:
      "Background monitors run continuously inside the bot process — no cron, no external scheduler, no extra services.",
  },
  {
    name: "Closed-loop Actioning",
    icon: "Zap",
    tag: "automate",
    blurb:
      "When a high-priority CVE matches your stack, it raises a ticket, drafts remediation steps and escalates.",
  },
  {
    name: "Ticketing",
    icon: "Ticket",
    tag: "operate",
    blurb:
      "Auto-raised remediation tickets, deduplicated per CVE, that you triage and close from chat.",
  },
  {
    name: "Reporting",
    icon: "FileText",
    tag: "ai",
    blurb:
      "Scheduled and on-demand intelligence reports synthesized by the agent crew and archived for review.",
  },
  {
    name: "Discord Operations",
    icon: "MessageSquare",
    tag: "operate",
    blurb:
      "20+ slash commands turn a Discord server into the control surface for the whole platform.",
  },
  {
    name: "Asset Inventory",
    icon: "Boxes",
    tag: "operate",
    blurb:
      "Declare the technologies in your lab so intelligence is matched to what you actually run.",
  },
  {
    name: "Analytics",
    icon: "BarChart3",
    tag: "operate",
    blurb:
      "Command usage, AI response times, KEV counts and exploitability trends, tracked in PostgreSQL.",
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

export type Phase = { n: number; title: string; body: string };
export const PHASES: Phase[] = [
  { n: 1, title: "Foundation", body: "Async Discord bot, PostgreSQL and Redis, structured logging, on-demand CVE and news lookups." },
  { n: 2, title: "Threat Intelligence", body: "Autonomous hourly CVE monitoring and multi-source news collection with de-duplication." },
  { n: 3, title: "Intelligence Fusion", body: "EPSS + KEV + ExploitDB + GitHub PoC correlation into a single prioritized alert." },
  { n: 4, title: "Learning Intelligence", body: "HackTheBox import, a practice journal, and AI recommendations that fill skill gaps." },
  { n: 5, title: "RAG Knowledge Base", body: "Local embeddings over your own documents so the assistant answers from your material." },
  { n: 6, title: "SOC Dashboard", body: "A self-hosted operations dashboard reading live from the same database." },
  { n: 7, title: "Multi-Agent Crew", body: "Specialised agents that hand off to synthesize intelligence reports." },
  { n: 8, title: "Automation & Actioning", body: "Lab-aware matching that raises tickets and escalates the CVEs that affect you." },
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
  { value: "20+", label: "Discord commands" },
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
  { id: "sources", label: "Threat Sources", kind: "source", desc: "NVD, CISA KEV, EPSS, ExploitDB, GitHub advisories, RSS and YouTube — polled on independent schedules." },
  { id: "collectors", label: "Collectors", kind: "source", desc: "Background monitors fetch, normalize and de-duplicate each source, storing only what's new." },
  { id: "engine", label: "Intelligence Engine", kind: "core", desc: "Fuses signals per CVE and computes a 0–100 priority from CVSS, EPSS, KEV and exploit availability." },
  { id: "ai", label: "AI Layer", kind: "core", desc: "Local Ollama models summarize, assess risk, embed documents and drive the multi-agent report crew." },
  { id: "data", label: "PostgreSQL + Redis", kind: "store", desc: "All intelligence, embeddings, metrics and tickets persist in Postgres; Redis handles fast state." },
  { id: "rag", label: "Knowledge Base", kind: "store", desc: "Vector search over your own notes and write-ups, grounding assistant answers in your material." },
  { id: "automation", label: "Automation Engine", kind: "core", desc: "Matches priority CVEs against your asset inventory and takes action without waiting for you." },
  { id: "outputs", label: "Discord · Dashboard · API", kind: "output", desc: "Delivered where you work: chat commands, a live SOC dashboard, and programmatic access." },
];
