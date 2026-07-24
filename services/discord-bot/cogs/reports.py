"""/report — run the multi-agent intelligence crew and post the report."""

from __future__ import annotations

import traceback

import discord
from discord import app_commands
from discord.ext import commands

from agents.crew import Report, crew
from database import db
from utils import embeds
from utils.logger import discord_log as log


def build_report_embed(report: Report) -> discord.Embed:
    """Render a crew Report as a Discord embed (summary + per-agent sections)."""
    embed = embeds.base_embed(
        title=f"🧠 {report.title}",
        description=report.summary[:4000] if report.summary else "(no summary)",
        color=embeds.DARK_BLUE,
    )
    for name, text in report.sections.items():
        if text:
            embed.add_field(name=name, value=text[:1024], inline=False)
    embed.set_footer(text="Cyber Command Center • Agent Crew")
    return embed


async def run_and_store(title: str) -> Report:
    """Run the crew, persist the report, return it."""
    report = await crew.generate_report(title)
    if db.reports is not None:
        await db.reports.add(title=report.title, summary=report.summary, content=report.content)
    return report


class Reports(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="report", description="Run the AI agent crew to generate an intelligence report.")
    async def report(self, interaction: discord.Interaction) -> None:
        # The crew runs 5 sequential AI agents and can take several minutes on a
        # CPU-only host. A slash-command interaction token is only valid for 15
        # minutes, so we ACK immediately and then deliver the finished report via
        # a normal channel message (no token expiry) rather than a followup.
        await interaction.response.send_message(
            embed=embeds.base_embed(
                title="🧠 Agent crew engaged",
                description=(
                    "Compiling your intelligence report — five agents run in "
                    "sequence (Planner → Researcher → Analyst → Coach → Writer). "
                    "This can take a couple of minutes; I'll post it here when ready."
                ),
                color=embeds.INFO,
            )
        )
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command="/report", guild_id=interaction.guild_id,
        )
        log.info("Agent crew report requested by %s", interaction.user)

        channel = interaction.channel
        now = embeds.now_local().strftime("%Y-%m-%d %H:%M")
        try:
            report = await run_and_store(f"Intelligence Report — {now}")
            if channel is not None:
                await channel.send(embed=build_report_embed(report))
        except Exception:  # noqa: BLE001
            log.error("Agent crew report failed\n%s", traceback.format_exc())
            if channel is not None:
                await channel.send(
                    embed=embeds.error_embed("Report generation failed — see #bot-logs.")
                )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Reports(bot))
