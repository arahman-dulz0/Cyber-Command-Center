"""/ask — send a question to the local Ollama model and return the answer."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from database import db
from utils import embeds
from utils.logger import ai_log as log
from utils.ollama_client import OllamaError, OllamaTimeout, ollama


class AI(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ask", description="Ask the AI a cybersecurity (or any) question.")
    @app_commands.describe(question="What do you want to ask?")
    async def ask(self, interaction: discord.Interaction, question: str) -> None:
        # Defer so the "thinking" indicator shows while Ollama works.
        await interaction.response.defer(thinking=True)
        log.info("User %s used /ask: %s", interaction.user, question[:120])
        await db.log_command(
            user_id=interaction.user.id,
            username=str(interaction.user),
            command="/ask",
            guild_id=interaction.guild_id,
        )

        try:
            answer, elapsed = await ollama.generate(
                question,
                system="You are a helpful, concise cybersecurity assistant.",
            )
        except OllamaTimeout:
            await interaction.followup.send(
                embed=embeds.error_embed("🧠 AI is thinking too hard, try again."),
            )
            return
        except OllamaError:
            await interaction.followup.send(
                embed=embeds.error_embed("Service temporarily unavailable."),
            )
            return

        # Record the AI call for /stats (best-effort).
        if db.ai is not None:
            await db.ai.record_metric(
                kind="ask", model=ollama.model,
                elapsed_ms=int(elapsed * 1000), cache_hit=False,
            )

        # Discord embed descriptions cap at 4096 chars.
        if len(answer) > 4000:
            answer = answer[:3997] + "..."

        embed = embeds.base_embed(
            title=question if len(question) <= 256 else question[:253] + "...",
            description=answer,
            color=embeds.INFO,
        )
        embed.set_footer(
            text=f"Cyber Command Center • {ollama.model} • {elapsed:.1f}s"
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AI(bot))
