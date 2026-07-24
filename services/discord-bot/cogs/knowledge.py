"""
Knowledge-base commands (Phase 5).

/kb-add    — attach a PDF/Markdown/text file to ingest into your knowledge base.
/kb-list   — list indexed documents.
/kb-search — semantic search over your knowledge base (no AI, just retrieval).
"""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from database import db
from knowledge.ingest import ingest_file_bytes, is_supported
from knowledge.retriever import retriever
from utils import embeds
from utils.logger import discord_log as log

_MAX_FILE_BYTES = 15 * 1024 * 1024  # 15 MB safety cap


class Knowledge(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="kb-add", description="Add a PDF/Markdown/text file to your knowledge base.")
    @app_commands.describe(file="A .pdf, .md, or .txt file to index")
    async def kb_add(self, interaction: discord.Interaction, file: discord.Attachment) -> None:
        await interaction.response.defer(thinking=True)
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command="/kb-add", guild_id=interaction.guild_id,
        )
        if not is_supported(file.filename):
            await interaction.followup.send(
                embed=embeds.error_embed("Unsupported file type. Use PDF, Markdown, or text.")
            )
            return
        if file.size and file.size > _MAX_FILE_BYTES:
            await interaction.followup.send(
                embed=embeds.error_embed("File too large (max 15 MB).")
            )
            return

        try:
            data = await file.read()
        except Exception as exc:  # noqa: BLE001
            await interaction.followup.send(embed=embeds.error_embed(f"Couldn't read the file: {exc}"))
            return

        log.info("%s ingesting KB file %s (%d bytes)", interaction.user, file.filename, file.size or 0)
        result = await ingest_file_bytes(file.filename, data, added_by=str(interaction.user))

        if result.ok:
            embed = embeds.success_embed(
                f"Indexed **{file.filename}** — {result.chunks} chunks embedded and searchable.",
                title="📚 Added to knowledge base",
            )
        else:
            embed = embeds.error_embed(f"Not indexed: {result.reason}", title="📚 Knowledge base")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="kb-list", description="List documents in your knowledge base.")
    async def kb_list(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command="/kb-list", guild_id=interaction.guild_id,
        )
        docs = await db.kb.list_documents(limit=25)
        total_docs = await db.kb.total_documents()
        total_chunks = await db.kb.total_chunks()

        embed = embeds.base_embed(
            title="📚 Knowledge Base",
            description=f"**{total_docs}** documents · **{total_chunks}** chunks indexed",
            color=embeds.INFO,
        )
        if docs:
            lines = [f"• **{d['title']}** ({d['source_type']}, {d['chunk_count']} chunks)" for d in docs]
            embed.add_field(name="Documents", value="\n".join(lines)[:1024], inline=False)
        else:
            embed.add_field(name="Documents", value="Empty — add one with `/kb-add`.", inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="kb-search", description="Semantic search over your knowledge base.")
    @app_commands.describe(query="What to search for")
    async def kb_search(self, interaction: discord.Interaction, query: str) -> None:
        await interaction.response.defer(thinking=True)
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command="/kb-search", guild_id=interaction.guild_id,
        )
        results = await retriever.search(query)
        embed = embeds.base_embed(title=f"🔍 KB search: {query[:200]}", color=embeds.INFO)
        if not results:
            embed.description = "No matches — is anything indexed? Try `/kb-add`."
            await interaction.followup.send(embed=embed)
            return
        for c in results[:5]:
            snippet = c.content[:280].replace("\n", " ")
            embed.add_field(
                name=f"{c.title} · {c.similarity:.0%}",
                value=snippet + ("…" if len(c.content) > 280 else ""),
                inline=False,
            )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Knowledge(bot))
