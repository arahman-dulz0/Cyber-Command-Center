"""/cve — look up a CVE from NVD, summarise it with Ollama, cache it in Postgres."""

from __future__ import annotations

import re

import discord
from discord import app_commands
from discord.ext import commands

from config import config
from database import db
from enrichment import fusion
from utils import embeds
from utils.logger import cve_log as log
from utils.nvd_client import CVENotFound, NVDError, nvd
from utils.summarizer import summarizer

_CVE_RE = re.compile(r"^CVE-\d{4}-\d{4,}$", re.IGNORECASE)


class CVE(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="cve", description="Look up a CVE by its ID (e.g. CVE-2021-44228).")
    @app_commands.describe(cve_id="The CVE identifier, e.g. CVE-2021-44228")
    async def cve(self, interaction: discord.Interaction, cve_id: str) -> None:
        await interaction.response.defer(thinking=True)
        cve_id = cve_id.strip().upper()
        log.info("User %s used /cve %s", interaction.user, cve_id)
        await db.log_command(
            user_id=interaction.user.id,
            username=str(interaction.user),
            command=f"/cve {cve_id}",
            guild_id=interaction.guild_id,
        )

        if not _CVE_RE.match(cve_id):
            await interaction.followup.send(
                embed=embeds.error_embed(
                    "That doesn't look like a CVE ID. Try `CVE-2021-44228`."
                )
            )
            return

        # Fetch fresh from NVD.
        try:
            data = await nvd.fetch_cve(cve_id)
        except CVENotFound:
            await interaction.followup.send(
                embed=embeds.error_embed("CVE not found in NVD database.")
            )
            return
        except NVDError:
            await interaction.followup.send(
                embed=embeds.error_embed("Service temporarily unavailable.")
            )
            return

        # Fusion path (Phase 3): correlate threat intel + priority + AI risk.
        if config.enrichment_enabled:
            enr = await fusion.enrich_one({
                "cve_id": data.cve_id,
                "cvss_score": data.cvss_score,
                "severity": data.severity,
                "references": data.references,
            })
            await db.cves.upsert(
                cve_id=data.cve_id, title=data.cve_id, description=data.description,
                cvss_score=data.cvss_score, severity=data.severity,
                published_date=data.published, ai_summary=None,
            )
            await db.enrichment.upsert(
                cve_id=enr.cve_id, epss=enr.epss, epss_percentile=enr.epss_percentile,
                kev=enr.kev, kev_ransomware=enr.kev_ransomware,
                exploitdb_ids=enr.exploitdb_ids, github_poc_urls=enr.github_poc_urls,
                patch_available=enr.patch_available, priority_score=enr.priority_score,
                priority_label=enr.priority_label, ai_risk=enr.ai_risk,
            )
            embed = embeds.build_fused_cve_embed(
                cve_id=data.cve_id, description=data.description,
                cvss_score=data.cvss_score, severity=data.severity,
                published=data.published, enr=enr, source_note="NVD • Fusion Engine",
            )
            await interaction.followup.send(embed=embed, view=embeds.nvd_view(cve_id))
            return

        # Fallback: basic embed with a plain AI summary.
        ai_summary = await summarizer.summarize_cve(data.description)
        await db.cves.upsert(
            cve_id=data.cve_id, title=data.cve_id, description=data.description,
            cvss_score=data.cvss_score, severity=data.severity,
            published_date=data.published, ai_summary=ai_summary,
        )
        embed = embeds.build_cve_embed(
            cve_id=data.cve_id, description=data.description, cvss_score=data.cvss_score,
            severity=data.severity, cvss_vector=data.cvss_vector, products=data.products,
            published=data.published, ai_summary=ai_summary,
        )
        await interaction.followup.send(embed=embed, view=embeds.nvd_view(cve_id))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CVE(bot))
