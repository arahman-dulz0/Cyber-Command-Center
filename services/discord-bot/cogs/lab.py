"""
Lab inventory + tickets (Phase 8).

/lab add|remove|list  — manage the stack the platform watches for you.
/tickets              — open action tickets (auto-raised when a CVE hits your lab).
/ticket-close [id]    — close a ticket.
"""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from config import config
from database import db
from utils import embeds
from utils.logger import discord_log as log


class Lab(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    lab = app_commands.Group(name="lab", description="Manage your lab/stack inventory.")

    @lab.command(name="add", description="Add a technology to your lab inventory (e.g. vmware, apache).")
    @app_commands.describe(tech="Technology/product keyword", note="Optional note")
    async def lab_add(self, interaction: discord.Interaction, tech: str, note: str | None = None) -> None:
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command=f"/lab add {tech}", guild_id=interaction.guild_id,
        )
        added = await db.lab.add(name=tech, note=note, added_by=str(interaction.user))
        msg = f"Added **{tech.lower()}** to your lab inventory." if added else f"**{tech.lower()}** is already in your inventory."
        await interaction.response.send_message(
            embed=embeds.success_embed(msg, title="🧪 Lab inventory") if added
            else embeds.base_embed(title="🧪 Lab inventory", description=msg, color=embeds.INFO)
        )

    @lab.command(name="remove", description="Remove a technology from your lab inventory.")
    @app_commands.describe(tech="Technology/product keyword to remove")
    async def lab_remove(self, interaction: discord.Interaction, tech: str) -> None:
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command=f"/lab remove {tech}", guild_id=interaction.guild_id,
        )
        removed = await db.lab.remove(tech)
        msg = f"Removed **{tech.lower()}**." if removed else f"**{tech.lower()}** was not in your inventory."
        await interaction.response.send_message(
            embed=embeds.base_embed(title="🧪 Lab inventory", description=msg, color=embeds.INFO)
        )

    @lab.command(name="list", description="Show your lab inventory.")
    async def lab_list(self, interaction: discord.Interaction) -> None:
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command="/lab list", guild_id=interaction.guild_id,
        )
        assets = await db.lab.all()
        embed = embeds.base_embed(
            title="🧪 Lab Inventory",
            description=(
                f"CVEs matching these are auto-triaged into tickets when priority "
                f"≥ {config.action_min_priority}."
            ),
            color=embeds.INFO,
        )
        if assets:
            embed.add_field(
                name=f"{len(assets)} assets",
                value="\n".join(f"• **{a['name']}**" + (f" — {a['note']}" if a.get('note') else "") for a in assets)[:1024],
                inline=False,
            )
        else:
            embed.add_field(name="Empty", value="Add one with `/lab add <tech>` (e.g. `/lab add vmware`).", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tickets", description="Open action tickets (CVEs that hit your lab).")
    async def tickets(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command="/tickets", guild_id=interaction.guild_id,
        )
        open_tickets = await db.tickets.open_tickets(limit=15)
        embed = embeds.base_embed(title="🎫 Open Action Tickets", color=embeds.HIGH)
        if not open_tickets:
            embed.description = "No open tickets — nothing in your lab is under active threat. ✅"
        else:
            for t in open_tickets:
                embed.add_field(
                    name=f"#{t['id']} · {t['cve_id']} · priority {t['priority']}",
                    value=f"Assets: {', '.join(t['assets'])}\nClose with `/ticket-close {t['id']}`",
                    inline=False,
                )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="ticket-close", description="Close an action ticket by id.")
    @app_commands.describe(ticket_id="The ticket number")
    async def ticket_close(self, interaction: discord.Interaction, ticket_id: int) -> None:
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command=f"/ticket-close {ticket_id}", guild_id=interaction.guild_id,
        )
        closed = await db.tickets.close(ticket_id)
        if closed:
            embed = embeds.success_embed(f"Ticket **#{ticket_id}** closed.", title="🎫 Tickets")
        else:
            embed = embeds.error_embed(f"Ticket #{ticket_id} not found or already closed.")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Lab(bot))
