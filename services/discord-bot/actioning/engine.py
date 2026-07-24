"""
Action engine (Phase 8).

When a high-priority CVE matches the user's lab inventory, it takes action:
raise a ticket, generate an AI remediation checklist, escalate to #announcements,
and (optionally) send an email. This is what makes the platform *act*, not just
notify. Called by the CVE monitor for each posted CVE.
"""

from __future__ import annotations

import re

import discord

from config import config
from database import db
from utils import embeds, notify
from utils.logger import get_logger
from utils.ollama_client import OllamaError, ollama

log = get_logger("actioning")


def _matches(names: list[str], haystack: str) -> list[str]:
    """Lab asset keywords that appear as whole words in the CVE text."""
    hits = []
    for n in names:
        if re.search(rf"\b{re.escape(n)}\b", haystack, re.IGNORECASE):
            hits.append(n)
    return hits


class ActionEngine:
    async def evaluate(
        self,
        bot: discord.Client,
        *,
        cve_id: str,
        description: str,
        products: list[str],
        priority: int,
    ) -> int | None:
        """Raise+escalate a ticket if this CVE is high-priority and hits the lab. Returns ticket id or None."""
        if not config.action_enabled or priority < config.action_min_priority:
            return None
        names = await db.lab.names()
        if not names:
            return None

        haystack = f"{description} {' '.join(products or [])}"
        matched = _matches(names, haystack)
        if not matched:
            return None

        checklist = await self._checklist(cve_id, description, matched)
        ticket_id = await db.tickets.create(
            cve_id=cve_id, assets=matched, priority=priority, checklist=checklist
        )
        if ticket_id is None:  # an open ticket already exists for this CVE
            return None

        log.info("ACTION: ticket #%d raised for %s (assets: %s)", ticket_id, cve_id, matched)
        await self._escalate(bot, cve_id, matched, priority, checklist, ticket_id)
        return ticket_id

    async def _checklist(self, cve_id: str, description: str, assets: list[str]) -> str:
        system = (
            "You are a SOC responder. Given the vulnerability, output a short "
            "numbered remediation checklist (4-6 concrete steps) an operator can "
            "act on now. No preamble, no markdown headers."
        )
        prompt = f"{cve_id} affects: {', '.join(assets)}.\n\n{description[:1000]}"
        try:
            text, _ = await ollama.generate(prompt, system=system, num_predict=300)
            return text
        except OllamaError:
            return (
                "1. Identify affected hosts running the impacted software.\n"
                "2. Check the vendor advisory for a patched version.\n"
                "3. Apply the patch or vendor mitigation.\n"
                "4. Restrict network exposure until patched.\n"
                "5. Verify and monitor for exploitation attempts."
            )

    async def _escalate(
        self, bot: discord.Client, cve_id: str, assets: list[str],
        priority: int, checklist: str, ticket_id: int,
    ) -> None:
        embed = embeds.base_embed(
            title=f"🚨 ACTION REQUIRED — {cve_id} affects your lab",
            description=(
                f"A **priority {priority}/100** CVE matches your lab inventory: "
                f"**{', '.join(assets)}**.\nTicket **#{ticket_id}** opened."
            ),
            color=embeds.CRITICAL,
            url=embeds.nvd_url(cve_id),
        )
        embed.add_field(name="🛠️ Remediation checklist", value=checklist[:1024], inline=False)
        embed.set_footer(text=f"Cyber Command Center • Action Engine • ticket #{ticket_id}")

        channel = bot.find_channel(config.channel_announcements)  # type: ignore[attr-defined]
        if channel is not None:
            try:
                await channel.send(embed=embed, view=embeds.nvd_view(cve_id))
            except discord.HTTPException as exc:
                log.warning("Escalation post failed: %s", exc)

        if config.email_enabled:
            await notify.send_email(
                subject=f"[Cyber Command Center] ACTION: {cve_id} affects your lab ({', '.join(assets)})",
                body=(
                    f"CVE: {cve_id} (priority {priority}/100)\n"
                    f"Affected lab assets: {', '.join(assets)}\n"
                    f"Ticket: #{ticket_id}\n\nRemediation checklist:\n{checklist}\n\n"
                    f"Details: {embeds.nvd_url(cve_id)}"
                ),
            )


# Shared instance.
action_engine = ActionEngine()
