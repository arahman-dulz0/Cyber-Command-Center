"""/news — pull the latest cybersecurity headlines from the configured RSS feeds."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from database import db
from utils import embeds
from utils.logger import get_logger
from utils.rss_client import fetch_latest

log = get_logger()


class News(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="news", description="Latest 5 cybersecurity news headlines.")
    async def news(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        log.info("User %s used /news", interaction.user)
        await db.log_command(
            user_id=interaction.user.id,
            username=str(interaction.user),
            command="/news",
            guild_id=interaction.guild_id,
        )

        try:
            articles = await fetch_latest(limit=5)
        except Exception as exc:  # noqa: BLE001 - surfaced as a friendly message
            log.error("News fetch failed: %s", exc)
            await interaction.followup.send(
                embed=embeds.error_embed("Service temporarily unavailable.")
            )
            return

        if not articles:
            await interaction.followup.send(
                embed=embeds.error_embed("No news could be fetched right now, try again.")
            )
            return

        lines = []
        for i, art in enumerate(articles, start=1):
            title = art.title if len(art.title) <= 200 else art.title[:197] + "..."
            lines.append(f"**{i}.** [{title}]({art.url})\n_{art.source}_")
            # Persist for later re-use / de-duplication.
            await db.upsert_news(
                title=art.title,
                url=art.url,
                source=art.source,
                description=art.description[:1000] if art.description else None,
                ai_summary=None,
                published_date=art.published,
            )

        embed = embeds.base_embed(
            title="📰 Latest Cybersecurity News",
            description="\n\n".join(lines),
            color=embeds.INFO,
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(News(bot))
