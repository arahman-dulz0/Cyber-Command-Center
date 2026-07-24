"""
Recommendation engine (Phase 4).

Fuses the user's practice history (explicit skills), their HTB own-status (OS
balance), and the machine catalogue, then asks the local AI to recommend the
single best next machine/topic — targeting under-practiced areas.
"""

from __future__ import annotations

import discord

from config import config
from database import db
from utils import embeds
from utils.logger import get_logger
from utils.ollama_client import OllamaError, ollama

log = get_logger("learning.recommender")

_REC_SYSTEM = (
    "You are a cybersecurity learning coach. Recommend exactly ONE next thing to "
    "practice that targets the learner's weakest/least-recent area. Be specific and "
    "motivating in 2-3 sentences. Plain text, no markdown, no preamble."
)
_SKILL_SYSTEM = (
    "You label HackTheBox machines with technique tags. Reply with ONLY a comma-"
    "separated list of 2-5 lowercase tags (e.g. 'active-directory, kerberoasting, "
    "windows'). No prose."
)


class Recommender:
    async def infer_skill_areas(self, name: str, os: str | None, difficulty: str | None) -> list[str]:
        prompt = f"HTB machine '{name}' (OS: {os or 'unknown'}, difficulty: {difficulty or 'unknown'})."
        try:
            text, _ = await ollama.generate(prompt, system=_SKILL_SYSTEM, num_predict=60)
        except OllamaError:
            return []
        tags = [t.strip().lower() for t in text.replace("\n", ",").split(",") if t.strip()]
        # Keep it clean: short, no sentences.
        return [t for t in tags if 1 <= len(t) <= 30][:5]

    async def build_recommendation_embed(self) -> discord.Embed:
        skills = await db.practice.skill_counts(days=90)
        recent = await db.practice.recent(limit=5)
        htb_on = config.htb_enabled
        balance = await db.machines.os_balance() if htb_on else {}
        candidates = await db.machines.candidates(exclude_owned=True, limit=40) if htb_on else []

        embed = embeds.base_embed(title="🎯 What To Practice Next", color=embeds.INFO)

        if not skills and not candidates:
            embed.description = (
                "No data yet. Log a few sessions with `/practiced` "
                "(and add your `HTB_APP_TOKEN` to import your HTB machines)."
            )
            return embed

        # Context summary shown to the user.
        if skills:
            embed.add_field(
                name="🧠 Recently practiced",
                value=", ".join(f"{s}×{n}" for s, n in skills[:6]),
                inline=False,
            )
        if htb_on and balance:
            embed.add_field(
                name="🖥️ Owned by OS",
                value=" · ".join(f"{k}: {v}" for k, v in balance.items()) or "none yet",
                inline=False,
            )

        recommendation = await self._ask_ai(skills, recent, balance, candidates)
        embed.add_field(name="🤖 Recommendation", value=recommendation[:1024], inline=False)
        return embed

    async def _ask_ai(self, skills, recent, balance, candidates) -> str:
        recent_txt = ", ".join(r["machine"] for r in recent) or "none"
        skills_txt = ", ".join(f"{s}({n})" for s, n in skills[:10]) or "none logged"
        balance_txt = ", ".join(f"{k}:{v}" for k, v in balance.items()) or "unknown"

        if candidates:
            shortlist = "\n".join(
                f"- {c['name']} ({c.get('os') or '?'}, {c.get('difficulty') or '?'})"
                + (f": {', '.join(c.get('skill_areas') or [])}" if c.get("skill_areas") else "")
                for c in candidates[:30]
            )
            prompt = (
                f"Learner's recently practiced skills: {skills_txt}.\n"
                f"Recent machines: {recent_txt}.\n"
                f"Machines owned per OS: {balance_txt}.\n\n"
                f"Pick ONE machine from this candidate list that best targets an "
                f"under-practiced area, and say why:\n{shortlist}"
            )
        else:
            prompt = (
                f"Learner's recently practiced skills: {skills_txt}.\n"
                f"Recent machines: {recent_txt}.\n\n"
                f"Recommend ONE specific technique or topic to practice next that "
                f"fills their biggest gap, with a concrete example machine or lab if you can."
            )

        try:
            text, _ = await ollama.generate(prompt, system=_REC_SYSTEM, num_predict=300)
            if db.ai is not None:
                await db.ai.record_metric(kind="recommend", model=ollama.model, elapsed_ms=0, cache_hit=False)
            return text
        except OllamaError:
            # Deterministic fallback: least-practiced OS among candidates.
            if candidates:
                return (
                    f"Try **{candidates[0]['name']}** "
                    f"({candidates[0].get('os')}, {candidates[0].get('difficulty')}). "
                    "(AI offline — showing a fresh unowned machine.)"
                )
            return "Log more practice with /practiced so I can tailor a recommendation."


# Shared instance.
recommender = Recommender()
