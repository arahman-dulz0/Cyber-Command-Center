"""/status, /brief and /help — the general-purpose command set (Phase 2 upgraded)."""

from __future__ import annotations

import os
import time
from typing import Awaitable, Callable

import discord
import psutil
from discord import app_commands
from discord.ext import commands

from config import config
from database import db
from utils import embeds
from utils.logger import discord_log as log
from utils.ollama_client import ollama
from utils.summarizer import summarizer


class General(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # --- /status (Threat Intelligence Dashboard) -------------------------
    @app_commands.command(name="status", description="Full system + service health dashboard.")
    async def status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command="/status", guild_id=interaction.guild_id,
        )

        embed = embeds.base_embed(title="🩺 Threat Intelligence Dashboard", color=embeds.INFO)

        # --- System resources ---
        cpu = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        embed.add_field(name="🖥️ CPU", value=f"{cpu:.0f}%", inline=True)
        embed.add_field(
            name="🧠 RAM",
            value=f"{mem.percent:.0f}% ({mem.used / 1e9:.1f}/{mem.total / 1e9:.1f} GB)",
            inline=True,
        )
        embed.add_field(
            name="💾 Disk",
            value=f"{disk.percent:.0f}% ({disk.used / 1e9:.0f}/{disk.total / 1e9:.0f} GB)",
            inline=True,
        )

        # --- Services ---
        docker = "🟢 Containerized" if os.path.exists("/.dockerenv") else "⚪ Host process"
        embed.add_field(name="🐳 Docker", value=docker, inline=True)
        embed.add_field(name="🐘 PostgreSQL", value=await self._check(db.ping), inline=True)
        embed.add_field(name="🧱 Redis", value=await self._check(self._ping_redis), inline=True)
        embed.add_field(name="🤖 Ollama", value=await self._check(ollama.ping), inline=True)
        embed.add_field(name="📡 Bot latency", value=f"{self.bot.latency * 1000:.0f} ms", inline=True)
        embed.add_field(name="🧬 AI model", value=f"`{config.ollama_model}`", inline=True)

        # --- Database counts ---
        embed.add_field(
            name="🗄️ Database",
            value=(
                f"CVEs: **{await db.cves.total()}**\n"
                f"News: **{await db.news.total()}**\n"
                f"Commands: **{await db.commands.total()}**"
            ),
            inline=True,
        )

        # --- Monitor state ---
        embed.add_field(name="🔎 Last CVE run", value=self._fmt_run(await db.monitors.last_run("cve")), inline=True)
        embed.add_field(name="📰 Last News run", value=self._fmt_run(await db.monitors.last_run("news")), inline=True)

        # --- Uptime + server ---
        uptime = self._format_uptime(time.monotonic() - getattr(self.bot, "start_time", time.monotonic()))
        embed.add_field(name="⏱️ Uptime", value=uptime, inline=True)
        embed.add_field(name="🌐 Server IP", value=config.masked_host, inline=True)

        await interaction.followup.send(embed=embed)

    @staticmethod
    def _fmt_run(run: dict | None) -> str:
        if not run:
            return "never"
        icon = {"success": "🟢", "error": "🔴", "running": "🟡"}.get(run.get("status", ""), "⚪")
        when = run.get("finished") or run.get("started")
        stamp = when.astimezone(embeds._TZ).strftime("%H:%M") if when else "?"
        return f"{icon} {stamp} · found {run.get('items_found', 0)} / posted {run.get('items_posted', 0)}"

    @staticmethod
    async def _check(coro_fn: Callable[[], Awaitable[None]]) -> str:
        start = time.monotonic()
        try:
            await coro_fn()
            elapsed = (time.monotonic() - start) * 1000
            return f"🟢 Online · `{elapsed:.0f} ms`"
        except Exception as exc:  # noqa: BLE001
            log.warning("Status check failed: %s", exc)
            return "🔴 Offline"

    async def _ping_redis(self) -> None:
        redis = getattr(self.bot, "redis", None)
        if redis is None:
            raise RuntimeError("Redis client not initialised")
        await redis.ping()

    @staticmethod
    def _format_uptime(seconds: float) -> str:
        seconds = int(seconds)
        days, rem = divmod(seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, secs = divmod(rem, 60)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        return " ".join(parts)

    # --- /brief (pulled entirely from PostgreSQL) ------------------------
    @app_commands.command(name="brief", description="On-demand daily security briefing.")
    async def brief(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command="/brief", guild_id=interaction.guild_id,
        )
        embed = await self.build_brief_embed()
        await interaction.followup.send(embed=embed)

    async def build_brief_embed(self) -> discord.Embed:
        """
        Assemble the daily-brief embed from PostgreSQL only (never refetches
        the CVE/news APIs). Reused by the scheduled task in bot.py.
        """
        now = embeds.now_local()
        embed = embeds.base_embed(title="🛡️ Daily Security Briefing", color=embeds.DARK_BLUE)
        embed.add_field(
            name="📅 Date",
            value=f"{now.strftime('%A, %d %B %Y')} — {now.strftime('%H:%M')} ({config.timezone})",
            inline=False,
        )

        # Counts over the last 24h (from the DB).
        crit = await db.cves.count_by_severity_since("CRITICAL", 24)
        high = await db.cves.count_by_severity_since("HIGH", 24)
        news_count = await db.news.count_since(24)
        embed.add_field(name="🚨 Critical CVEs (24h)", value=str(crit), inline=True)
        embed.add_field(name="🟧 High CVEs (24h)", value=str(high), inline=True)
        embed.add_field(name="📰 News (24h)", value=str(news_count), inline=True)

        # Highest-CVSS CVE stored today.
        top = await db.cves.highest_score_since(24)
        if top:
            embed.add_field(
                name="🔺 Highest CVSS today",
                value=f"[{top['cve_id']}]({embeds.nvd_url(top['cve_id'])}) — "
                f"**{top.get('cvss_score', 'N/A')}** ({top.get('severity', '?')})",
                inline=False,
            )
        else:
            embed.add_field(name="🔺 Highest CVSS today", value="No CVEs recorded today.", inline=False)

        # Top headlines from the DB.
        articles = await db.news.recent(limit=3)
        if articles:
            headlines = "\n".join(
                f"**{i}.** [{a['title']}]({a['url']}) — _{a.get('source', '')}_"
                for i, a in enumerate(articles, start=1)
            )
        else:
            headlines = "No headlines stored yet."
        embed.add_field(name="📰 Top headlines", value=headlines, inline=False)

        # One AI security tip (generation, not an API refetch).
        embed.add_field(name="💡 Security tip", value=await summarizer.tip(), inline=False)
        return embed

    # --- /help -----------------------------------------------------------
    @app_commands.command(name="help", description="Show all available commands.")
    async def help_cmd(self, interaction: discord.Interaction) -> None:
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command="/help", guild_id=interaction.guild_id,
        )
        embed = embeds.base_embed(
            title="📖 Cyber Command Center — Commands",
            description="Your personal, autonomous cybersecurity operations center.",
            color=embeds.INFO,
        )
        embed.add_field(
            name="🤖 AI & Knowledge",
            value=(
                "`/ask [question]` — Ask the AI (grounded in your notes when relevant).\n"
                "`/kb-add [file]` — Index a PDF/Markdown/text doc.\n"
                "`/kb-search [query]` — Search your knowledge base.\n"
                "`/kb-list` — List indexed documents."
            ),
            inline=False,
        )
        embed.add_field(
            name="🔎 Threat Intel",
            value=(
                "`/cve [cve-id]` — Look up a CVE with an AI summary.\n"
                "`/news` — Latest 5 cybersecurity headlines."
            ),
            inline=False,
        )
        embed.add_field(
            name="🎓 Learning",
            value=(
                "`/practiced` — Log a machine/box you practiced.\n"
                "`/progress` — Your practice history & skill coverage.\n"
                "`/recommend` — AI: what to practice next."
            ),
            inline=False,
        )
        embed.add_field(
            name="📊 General",
            value=(
                "`/status` — System + service dashboard.\n"
                "`/stats` — Platform statistics.\n"
                "`/brief` — Daily security briefing.\n"
                "`/help` — This message."
            ),
            inline=False,
        )
        embed.add_field(
            name="🛠️ Admin",
            value=(
                "`/monitor [cve|news]` — Run a monitor now (admin only).\n"
                "`/reload [cog]` — Reload a cog (admin only).\n"
                "`/sync` — Re-sync slash commands (admin only)."
            ),
            inline=False,
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))
