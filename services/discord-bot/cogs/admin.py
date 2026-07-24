"""/reload and /sync — administrative commands, restricted to server admins."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from config import config
from database import db
from utils import embeds
from utils.logger import get_logger

log = get_logger()

_COGS = ("ai", "cve", "news", "general", "admin")


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="reload", description="Reload a bot cog (admin only).")
    @app_commands.describe(cog="Which cog to reload")
    @app_commands.choices(
        cog=[app_commands.Choice(name=c, value=c) for c in _COGS]
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def reload(self, interaction: discord.Interaction, cog: app_commands.Choice[str]) -> None:
        await db.log_command(
            user_id=interaction.user.id,
            username=str(interaction.user),
            command=f"/reload {cog.value}",
            guild_id=interaction.guild_id,
        )
        try:
            await self.bot.reload_extension(f"cogs.{cog.value}")
            log.info("Cog reloaded by %s: %s", interaction.user, cog.value)
            await interaction.response.send_message(
                embed=embeds.success_embed(f"Reloaded `cogs.{cog.value}`."),
                ephemeral=True,
            )
        except Exception as exc:  # noqa: BLE001
            log.error("Failed to reload %s: %s", cog.value, exc)
            await interaction.response.send_message(
                embed=embeds.error_embed(f"Reload failed: `{exc}`"),
                ephemeral=True,
            )

    @app_commands.command(name="sync", description="Re-sync slash commands to this guild (admin only).")
    @app_commands.checks.has_permissions(administrator=True)
    async def sync(self, interaction: discord.Interaction) -> None:
        await db.log_command(
            user_id=interaction.user.id,
            username=str(interaction.user),
            command="/sync",
            guild_id=interaction.guild_id,
        )
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            if config.guild_id:
                guild = discord.Object(id=config.guild_id)
                self.bot.tree.copy_global_to(guild=guild)
                synced = await self.bot.tree.sync(guild=guild)
            else:
                synced = await self.bot.tree.sync()
            log.info("Commands synced by %s (%d commands)", interaction.user, len(synced))
            await interaction.followup.send(
                embed=embeds.success_embed(f"Synced **{len(synced)}** commands."),
            )
        except Exception as exc:  # noqa: BLE001
            log.error("Sync failed: %s", exc)
            await interaction.followup.send(
                embed=embeds.error_embed(f"Sync failed: `{exc}`"),
            )

    # Friendly message when a non-admin tries an admin command.
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
    await bot.add_cog(Admin(bot))
