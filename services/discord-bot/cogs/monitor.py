"""/monitor — run a background monitor on demand (admin only)."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from database import db
from utils import embeds
from utils.logger import scheduler_log as log


class Monitor(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="monitor", description="Run a threat monitor immediately (admin only).")
    @app_commands.describe(target="Which monitor to run now")
    @app_commands.choices(
        target=[
            app_commands.Choice(name="CVE monitor", value="cve"),
            app_commands.Choice(name="News monitor", value="news"),
            app_commands.Choice(name="HTB catalog import", value="htb"),
        ]
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def monitor(self, interaction: discord.Interaction, target: app_commands.Choice[str]) -> None:
        await interaction.response.defer(thinking=True)
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command=f"/monitor {target.value}", guild_id=interaction.guild_id,
        )

        scheduler = getattr(self.bot, "scheduler", None)
        if scheduler is None:
            await interaction.followup.send(
                embed=embeds.error_embed("Scheduler is not running.")
            )
            return

        log.info("Manual monitor run '%s' by %s", target.value, interaction.user)
        await db.audit.record(
            actor=str(interaction.user), action="monitor.run",
            target=target.value, source="discord",
        )
        result = await scheduler.run_now(target.value)
        if result is None:
            await interaction.followup.send(
                embed=embeds.error_embed(f"Unknown monitor `{target.value}`.")
            )
            return

        color = embeds.SUCCESS if result.status == "success" else embeds.ERROR
        embed = embeds.base_embed(title=f"🛰️ Monitor run — {result.task}", color=color)
        embed.add_field(name="Status", value=result.status, inline=True)
        embed.add_field(name="Time taken", value=f"{result.elapsed_seconds:.1f}s", inline=True)
        embed.add_field(name="Items found", value=str(result.items_found), inline=True)
        embed.add_field(name="Items posted", value=str(result.items_posted), inline=True)
        embed.add_field(
            name="Errors",
            value=f"```{result.errors[:1000]}```" if result.errors else "none",
            inline=False,
        )
        await interaction.followup.send(embed=embed)

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            msg = embeds.error_embed("You need administrator permissions for that.")
            if interaction.response.is_done():
                await interaction.followup.send(embed=msg, ephemeral=True)
            else:
                await interaction.response.send_message(embed=msg, ephemeral=True)
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Monitor(bot))
