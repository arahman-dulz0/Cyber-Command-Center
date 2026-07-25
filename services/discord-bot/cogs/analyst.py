"""
/analyst and /chat — the AI Security Analyst.

One natural-language command that becomes the primary interface to the whole
platform. It classifies intent, searches the platform's own knowledge first
(assets, DB, RAG, threat intel, CVEs/KEV/EPSS, news, learning) and only falls
back to the LLM for explanatory questions — then replies with rich embeds.
"""

from __future__ import annotations

import traceback

import discord
from discord import app_commands
from discord.ext import commands

from database import db
from utils import embeds
from utils.logger import discord_log as log

from analyst import analyst


class AnalystCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _handle(self, interaction: discord.Interaction, query: str, command: str) -> None:
        query = (query or "").strip()
        if not query:
            await interaction.response.send_message(
                embed=embeds.error_embed("Ask me something, e.g. `what should I patch today?`"),
                ephemeral=True)
            return

        await interaction.response.defer(thinking=True)
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command=command, guild_id=interaction.guild_id)

        try:
            result = await analyst.ask(
                user_id=interaction.user.id, username=str(interaction.user), query=query)
        except Exception:  # noqa: BLE001
            log.error("Analyst failed for %r\n%s", query, traceback.format_exc())
            await interaction.followup.send(
                embed=embeds.error_embed("The analyst hit an error — see #bot-logs."))
            return

        resp = result.response
        payload = resp.embeds[:10] or [embeds.base_embed(
            title="🤖 AI Analyst", description="No answer produced.")]

        log.info("Analyst: intent=%s tools=%s sources=%s llm=%s %dms",
                 result.intent, result.tools, result.sources, result.used_llm, result.elapsed_ms)

        # Fast path: reply on the interaction. Slow (crew) path already took a
        # while; fall back to a channel message if the token has expired.
        try:
            await interaction.followup.send(embeds=payload, view=resp.view or discord.utils.MISSING)
        except discord.HTTPException:
            channel = interaction.channel
            if channel is not None:
                await channel.send(embeds=payload, view=resp.view or discord.utils.MISSING)

    @app_commands.command(name="analyst",
                          description="Ask the AI Security Analyst anything about your threat landscape.")
    @app_commands.describe(query="Your question, in plain English")
    async def analyst_cmd(self, interaction: discord.Interaction, query: str) -> None:
        await self._handle(interaction, query, "/analyst")

    @app_commands.command(name="chat",
                          description="Chat with the AI Security Analyst (natural language).")
    @app_commands.describe(message="What you want to ask or discuss")
    async def chat_cmd(self, interaction: discord.Interaction, message: str) -> None:
        await self._handle(interaction, message, "/chat")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AnalystCog(bot))
