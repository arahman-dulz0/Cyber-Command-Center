"""
Cyber Command Center — Discord bot entry point.

Responsibilities:
  * Load configuration and set up logging.
  * Open the PostgreSQL pool and Redis connection.
  * Load every cog and sync slash commands.
  * Provide a global slash-command error handler that reports full tracebacks
    to the #bot-logs channel while showing users only a friendly message.
  * Run the scheduled daily briefing to #daily-brief.
"""

from __future__ import annotations

import asyncio
import time
import traceback
from datetime import datetime, timedelta

import discord
import redis.asyncio as aioredis
from discord.ext import commands, tasks
from zoneinfo import ZoneInfo

from config import config
from database import db
from tasks.scheduler import build_default_scheduler
from utils import embeds
from utils.logger import discord_log as log

INITIAL_COGS = (
    "cogs.ai",
    "cogs.cve",
    "cogs.news",
    "cogs.general",
    "cogs.admin",
    "cogs.stats",
    "cogs.monitor",
    "cogs.learning",
)


class CyberCommandBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True  # enabled in the Developer Portal
        intents.members = True          # Server Members Intent
        super().__init__(command_prefix="!", intents=intents, help_command=None)

        self.redis: aioredis.Redis | None = None
        self.start_time: float = time.monotonic()
        self.scheduler = None  # set in setup_hook (tasks.scheduler.Scheduler)

    async def setup_hook(self) -> None:
        # --- Backend connections ---------------------------------------
        await db.init()
        self.redis = aioredis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            decode_responses=True,
            socket_connect_timeout=5,
        )
        try:
            await self.redis.ping()
            log.info("Redis connection ready.")
        except Exception as exc:  # noqa: BLE001
            log.warning("Redis not reachable at startup: %s", exc)

        # --- Cogs ------------------------------------------------------
        for ext in INITIAL_COGS:
            try:
                await self.load_extension(ext)
                log.info("Loaded extension %s", ext)
            except Exception:  # noqa: BLE001
                log.error("Failed to load %s\n%s", ext, traceback.format_exc())

        # --- Slash-command sync ---------------------------------------
        if config.guild_id:
            guild = discord.Object(id=config.guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            log.info("Synced %d commands to guild %s", len(synced), config.guild_id)
        else:
            synced = await self.tree.sync()
            log.info("Synced %d global commands", len(synced))

        # --- Global slash error handler -------------------------------
        self.tree.on_error = self.on_app_command_error

        # --- Background monitors (Phase 2) ----------------------------
        self.scheduler = build_default_scheduler(self)
        self.scheduler.start()

        # --- Scheduled tasks ------------------------------------------
        self.daily_brief_task.start()
        self.weekly_recommend_task.start()

    async def on_ready(self) -> None:
        log.info("Logged in as %s (id: %s)", self.user, self.user.id if self.user else "?")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="the internet for threats"
            )
        )

    async def close(self) -> None:
        log.info("Shutting down…")
        if self.scheduler is not None:
            self.scheduler.stop()
        self.daily_brief_task.cancel()
        self.weekly_recommend_task.cancel()
        if self.redis is not None:
            await self.redis.aclose()
        await db.close()
        await super().close()

    # --- Error handling --------------------------------------------------
    async def on_app_command_error(self, interaction: discord.Interaction, error: Exception) -> None:
        # discord.py wraps the real error; unwrap it for a cleaner report.
        original = getattr(error, "original", error)
        tb = "".join(traceback.format_exception(type(original), original, original.__traceback__))

        command_name = interaction.command.qualified_name if interaction.command else "unknown"
        log.error("Error in /%s by %s: %s", command_name, interaction.user, original)

        # 1) Friendly message to the user (never a raw traceback).
        friendly = embeds.error_embed(
            "Something went wrong running that command. The incident has been logged."
        )
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=friendly, ephemeral=True)
            else:
                await interaction.response.send_message(embed=friendly, ephemeral=True)
        except discord.HTTPException:
            pass

        # 2) Detailed report to #bot-logs.
        await self.report_to_bot_logs(
            command=f"/{command_name}",
            user=str(interaction.user),
            error_type=type(original).__name__,
            traceback_text=tb,
        )

    async def report_to_bot_logs(
        self, *, command: str, user: str, error_type: str, traceback_text: str
    ) -> None:
        channel = self.find_channel(config.bot_logs_channel)
        if channel is None:
            return
        ts = embeds.now_local().strftime("%Y-%m-%d %H:%M:%S")
        embed = discord.Embed(
            title="🐞 Command Error",
            color=embeds.ERROR,
            description=f"**Command:** `{command}`\n**User:** {user}\n**Type:** `{error_type}`\n**Time:** {ts}",
        )
        # Discord field values cap at 1024 chars.
        snippet = traceback_text[-1000:]
        embed.add_field(name="Traceback", value=f"```py\n{snippet}\n```", inline=False)
        try:
            await channel.send(embed=embed)
        except discord.HTTPException as exc:
            log.warning("Could not post to #%s: %s", config.bot_logs_channel, exc)

    def find_channel(self, name: str) -> discord.TextChannel | None:
        """Resolve a text channel by name across the bot's guilds (public: used by monitors)."""
        for guild in self.guilds:
            channel = discord.utils.get(guild.text_channels, name=name)
            if channel is not None:
                return channel
        return None

    # --- Daily briefing scheduler ---------------------------------------
    @tasks.loop(hours=24)  # first run aligned by _before_brief below
    async def daily_brief_task(self) -> None:
        channel = self.find_channel(config.channel_daily_brief)
        if channel is None:
            log.warning("Daily brief channel #%s not found", config.channel_daily_brief)
            return
        general = self.get_cog("General")
        if general is None:
            return
        try:
            embed = await general.build_brief_embed()  # type: ignore[attr-defined]
            await channel.send(embed=embed)
            log.info("Posted daily briefing to #%s", config.channel_daily_brief)
        except Exception:  # noqa: BLE001
            log.error("Daily brief failed\n%s", traceback.format_exc())

    @daily_brief_task.before_loop
    async def _before_brief(self) -> None:
        await self.wait_until_ready()
        # Sleep until the next configured brief time (Asia/Colombo).
        tz = ZoneInfo(config.timezone)
        try:
            hour, minute = (int(x) for x in config.daily_brief_time.split(":"))
        except ValueError:
            hour, minute = 7, 30
        now = datetime.now(tz)
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        wait = (target - now).total_seconds()
        log.info("Daily brief scheduled in %.0f minutes (%02d:%02d %s), then every 24h",
                 wait / 60, hour, minute, config.timezone)
        await asyncio.sleep(wait)

    # --- Weekly learning recommendation (Phase 4) -----------------------
    @tasks.loop(hours=24)  # checked daily; posts only on the configured weekday
    async def weekly_recommend_task(self) -> None:
        now = embeds.now_local()
        if now.weekday() != config.recommend_day:
            return
        channel = self.find_channel(config.channel_htb_ctf)
        if channel is None:
            log.warning("Recommendation channel #%s not found", config.channel_htb_ctf)
            return
        try:
            from learning.recommender import recommender
            embed = await recommender.build_recommendation_embed()
            embed.title = "📅 Weekly Practice Recommendation"
            await channel.send(embed=embed)
            log.info("Posted weekly recommendation to #%s", config.channel_htb_ctf)
        except Exception:  # noqa: BLE001
            log.error("Weekly recommendation failed\n%s", traceback.format_exc())

    @weekly_recommend_task.before_loop
    async def _before_recommend(self) -> None:
        await self.wait_until_ready()
        tz = ZoneInfo(config.timezone)
        try:
            hour, minute = (int(x) for x in config.recommend_time.split(":"))
        except ValueError:
            hour, minute = 8, 0
        now = datetime.now(tz)
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())


def main() -> None:
    log.info("Starting Cyber Command Center bot…")
    bot = CyberCommandBot()
    bot.run(config.discord_token, log_handler=None)  # we manage logging ourselves


if __name__ == "__main__":
    main()
