"""
Intelligence crew (Phase 7) — a multi-agent pipeline.

Gathers the current intel from PostgreSQL, then runs specialised agents in
sequence, each handing its output to the next:

    Planner → Threat Researcher → CVE Analyst → Learning Coach → Report Writer

The Report Writer synthesises every agent's contribution into an executive
summary. The result is a structured Report (sections attributed to each agent).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agents.base import Agent
from database import db
from utils.logger import get_logger

log = get_logger("agents.crew")

# --- The crew --------------------------------------------------------------
PLANNER = Agent(
    "Planner", "🗺️",
    "You are the Planner in a cybersecurity intelligence team. Given today's raw "
    "intel digest, decide the 2-3 things that matter most today and what the "
    "report should focus on. Reply with 3 short bullet points, no preamble.",
    max_tokens=180,
)
RESEARCHER = Agent(
    "Threat Researcher", "🌐",
    "You are the Threat Researcher. From the news headlines and CVE activity in "
    "the context, write a 2-3 sentence summary of the current threat landscape. "
    "Plain prose, no preamble.",
    max_tokens=220,
)
ANALYST = Agent(
    "CVE Analyst", "🎯",
    "You are the CVE Analyst. From the prioritised CVEs in the context (score, "
    "EPSS, KEV, exploit availability), state which ONE matters most and the exact "
    "action to take. 2-3 sentences, no preamble.",
    max_tokens=220,
)
COACH = Agent(
    "Learning Coach", "🎓",
    "You are the Learning Coach. From the user's practised skills and HTB progress "
    "in the context, recommend the single next focus area and why. 2 sentences.",
    max_tokens=160,
)
WRITER = Agent(
    "Report Writer", "📝",
    "You are the Report Writer. Synthesise your teammates' notes (focus, threat "
    "landscape, CVE analysis, learning recommendation) into a crisp executive "
    "summary of 3-4 sentences for a security operator. No headers, no preamble.",
    max_tokens=320,
)


@dataclass
class Report:
    title: str
    summary: str
    sections: dict[str, str] = field(default_factory=dict)

    @property
    def content(self) -> str:
        parts = [self.summary, ""]
        for name, text in self.sections.items():
            parts.append(f"## {name}\n{text}\n")
        return "\n".join(parts).strip()


class IntelligenceCrew:
    async def _gather(self) -> dict:
        """Read the current intel picture from PostgreSQL."""
        pool = db.pool
        cves_24h = await pool.fetchval(
            "SELECT COUNT(*) FROM cves WHERE created_at >= NOW() - INTERVAL '24 hours'") or 0
        kev_24h = await pool.fetchval(
            "SELECT COUNT(*) FROM cve_enrichment WHERE kev AND enriched_at >= NOW() - INTERVAL '24 hours'") or 0
        top = await pool.fetch(
            """
            SELECT c.cve_id, c.cvss_score, e.priority_score, e.priority_label,
                   e.kev, e.epss, e.github_poc_count, e.exploitdb_count
            FROM cve_enrichment e JOIN cves c ON c.cve_id = e.cve_id
            ORDER BY e.priority_score DESC, e.enriched_at DESC LIMIT 5;
            """
        )
        news = await db.news.recent(limit=5)
        skills = await db.practice.skill_counts(days=90)
        owned = await db.machines.owned_count() if db.machines else 0
        balance = await db.machines.os_balance() if db.machines else {}
        return {
            "cves_24h": cves_24h, "kev_24h": kev_24h,
            "top": [dict(r) for r in top], "news": news,
            "skills": skills, "owned": owned, "balance": balance,
        }

    @staticmethod
    def _digest_text(d: dict) -> str:
        top = "\n".join(
            f"- {r['cve_id']} priority {r['priority_score']}/100 ({r['priority_label']}), "
            f"CVSS {r['cvss_score']}, EPSS {round((r['epss'] or 0)*100)}%, "
            f"KEV={'yes' if r['kev'] else 'no'}, PoCs {r['github_poc_count']}, EDB {r['exploitdb_count']}"
            for r in d["top"]
        ) or "- none"
        news = "\n".join(f"- {n['title']} ({n.get('source','')})" for n in d["news"]) or "- none"
        skills = ", ".join(f"{s}({n})" for s, n in d["skills"][:10]) or "none logged"
        balance = ", ".join(f"{k}:{v}" for k, v in d["balance"].items()) or "unknown"
        return (
            f"CVEs stored (24h): {d['cves_24h']} | New KEV (24h): {d['kev_24h']}\n"
            f"Top prioritised CVEs:\n{top}\n\n"
            f"Recent news:\n{news}\n\n"
            f"Practised skills: {skills}\n"
            f"HTB machines owned: {d['owned']} (by OS: {balance})"
        )

    async def generate_report(self, title: str) -> Report:
        d = await self._gather()
        digest = self._digest_text(d)

        # Sequential pipeline with handoff — each agent sees the digest plus the
        # accumulated notes from earlier agents.
        plan = await PLANNER.run(f"Intel digest:\n{digest}")
        landscape = await RESEARCHER.run(f"Focus from planner:\n{plan}\n\nIntel digest:\n{digest}")
        cve_analysis = await ANALYST.run(f"Intel digest:\n{digest}")
        learning = await COACH.run(f"Intel digest:\n{digest}")

        writer_input = (
            f"Planner focus:\n{plan}\n\n"
            f"Threat landscape:\n{landscape}\n\n"
            f"CVE analysis:\n{cve_analysis}\n\n"
            f"Learning recommendation:\n{learning}"
        )
        summary = await WRITER.run(writer_input)

        return Report(
            title=title,
            summary=summary,
            sections={
                f"{PLANNER.emoji} Focus — {PLANNER.name}": plan,
                f"{RESEARCHER.emoji} Threat Landscape — {RESEARCHER.name}": landscape,
                f"{ANALYST.emoji} CVE Analysis — {ANALYST.name}": cve_analysis,
                f"{COACH.emoji} Learning Focus — {COACH.name}": learning,
            },
        )


# Shared instance.
crew = IntelligenceCrew()
