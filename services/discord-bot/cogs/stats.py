"""/stats — platform statistics pulled from PostgreSQL."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from database import db
from utils import embeds
from utils.logger import discord_log as log


class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="stats", description="Cyber Command Center usage & intelligence statistics.")
    async def stats(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command="/stats", guild_id=interaction.guild_id,
        )

        cves_today = await db.cves.count_since(24)
        news_today = await db.news.count_since(24)
        summaries_today = await db.ai.summaries_generated_since(24)
        commands_today = await db.commands.count_since(24)
        avg_ms = await db.ai.avg_response_ms_since(24)
        top = await db.commands.top_command()
        db_size = await db.database_size_pretty()
        kev_today = await db.enrichment.count_kev_since(24)
        exploited_today = await db.enrichment.count_exploited_since(24)
        max_priority = await db.enrichment.max_priority_since(24)

        embed = embeds.base_embed(title="📊 Platform Statistics (last 24h)", color=embeds.INFO)
        embed.add_field(name="🔎 CVEs", value=str(cves_today), inline=True)
        embed.add_field(name="📰 News", value=str(news_today), inline=True)
        embed.add_field(name="🚨 KEVs", value=str(kev_today), inline=True)
        embed.add_field(name="💥 Exploited", value=str(exploited_today), inline=True)
        embed.add_field(name="🎯 Top priority", value=f"{max_priority}/100", inline=True)
        embed.add_field(name="🤖 AI summaries", value=str(summaries_today), inline=True)
        embed.add_field(name="⌨️ Commands used", value=str(commands_today), inline=True)
        embed.add_field(
            name="⚡ Avg AI response",
            value=f"{avg_ms / 1000:.1f}s" if avg_ms else "n/a",
            inline=True,
        )
        embed.add_field(name="🗄️ Database size", value=db_size or "n/a", inline=True)
        if top:
            embed.add_field(
                name="🏆 Top command (all-time)",
                value=f"`{top['cmd']}` — {top['n']} uses",
                inline=False,
            )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Stats(bot))
