"""/ask — send a question to the local Ollama model and return the answer."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from config import config
from database import db
from knowledge.retriever import retriever
from utils import embeds
from utils.logger import ai_log as log
from utils.ollama_client import OllamaError, OllamaTimeout, ollama

_PLAIN_SYSTEM = "You are a helpful, concise cybersecurity assistant."
_RAG_SYSTEM = (
    "You are a cybersecurity assistant. Answer the question using ONLY the "
    "provided context from the user's personal knowledge base. If the context is "
    "insufficient, say so and answer from general knowledge, but prefer the "
    "context. Be concise. Do not invent sources."
)


class AI(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ask", description="Ask the AI — grounded in your knowledge base when relevant.")
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

        # RAG: retrieve grounding context from the user's knowledge base.
        sources: list[str] = []
        prompt, system = question, _PLAIN_SYSTEM
        if config.kb_enabled:
            try:
                ctx = await retriever.build_context(question)
            except Exception as exc:  # noqa: BLE001 - retrieval must never break /ask
                log.warning("KB retrieval failed: %s", exc)
                ctx = None
            if ctx and ctx.grounded:
                sources = ctx.sources
                system = _RAG_SYSTEM
                prompt = f"Context from the knowledge base:\n\n{ctx.text}\n\nQuestion: {question}"

        try:
            answer, elapsed = await ollama.generate(prompt, system=system, num_predict=500)
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

        if db.ai is not None:
            await db.ai.record_metric(
                kind="ask", model=ollama.model,
                elapsed_ms=int(elapsed * 1000), cache_hit=False,
            )

        if len(answer) > 4000:
            answer = answer[:3997] + "..."

        embed = embeds.base_embed(
            title=question if len(question) <= 256 else question[:253] + "...",
            description=answer,
            color=embeds.INFO,
        )
        if sources:
            embed.add_field(
                name="📚 Sources (your knowledge base)",
                value="\n".join(f"• {s}" for s in sources[:5]),
                inline=False,
            )
        tag = "KB-grounded" if sources else "general"
        embed.set_footer(text=f"Cyber Command Center • {ollama.model} • {tag} • {elapsed:.1f}s")
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AI(bot))
