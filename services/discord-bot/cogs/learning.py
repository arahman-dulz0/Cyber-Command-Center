"""
Learning-intelligence commands (Phase 4).

/practiced  — log a machine/box you worked on (+ skills, difficulty, notes).
/progress   — show your recent practice and skill coverage.
/recommend  — AI recommendation for what to practice next.
"""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from config import config
from database import db
from learning.recommender import recommender
from utils import embeds
from utils.logger import discord_log as log

_PLATFORMS = ["HTB", "TryHackMe", "CTF", "Other"]
_DIFFICULTIES = ["Easy", "Medium", "Hard", "Insane"]


class Learning(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="practiced", description="Log a machine/box you practiced.")
    @app_commands.describe(
        machine="Name of the machine/box/room (e.g. Forest)",
        skills="Comma-separated skills, e.g. windows, active-directory, kerberoasting",
        platform="Where you practiced",
        difficulty="How hard it was",
        notes="Optional notes / takeaways",
    )
    @app_commands.choices(
        platform=[app_commands.Choice(name=p, value=p) for p in _PLATFORMS],
        difficulty=[app_commands.Choice(name=d, value=d) for d in _DIFFICULTIES],
    )
    async def practiced(
        self,
        interaction: discord.Interaction,
        machine: str,
        skills: str,
        platform: app_commands.Choice[str] | None = None,
        difficulty: app_commands.Choice[str] | None = None,
        notes: str | None = None,
    ) -> None:
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command="/practiced", guild_id=interaction.guild_id,
        )
        skill_list = [s.strip() for s in skills.split(",") if s.strip()]
        await db.practice.add(
            user_id=interaction.user.id,
            username=str(interaction.user),
            machine=machine.strip(),
            platform=platform.value if platform else "HTB",
            skills=skill_list,
            difficulty=difficulty.value if difficulty else None,
            notes=notes,
        )
        log.info("%s logged practice: %s (%s)", interaction.user, machine, skill_list)

        embed = embeds.success_embed(
            f"Logged **{machine}** — {', '.join(skill_list) or 'no skills tagged'}",
            title="🎓 Practice logged",
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="progress", description="Your recent practice and skill coverage.")
    async def progress(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command="/progress", guild_id=interaction.guild_id,
        )

        recent = await db.practice.recent(limit=5)
        skills = await db.practice.skill_counts(days=90)
        total = await db.practice.total()

        embed = embeds.base_embed(title="📈 Your Learning Progress", color=embeds.INFO)
        embed.add_field(name="Sessions logged", value=str(total), inline=True)
        if db.machines is not None and config.htb_enabled:
            embed.add_field(name="HTB machines owned", value=str(await db.machines.owned_count()), inline=True)

        if skills:
            top = "\n".join(f"• {s} × {n}" for s, n in skills[:8])
            embed.add_field(name="🧠 Skills practiced (90d)", value=top, inline=False)
        else:
            embed.add_field(name="🧠 Skills practiced (90d)", value="Nothing logged yet — try `/practiced`.", inline=False)

        if recent:
            lines = []
            for r in recent:
                sk = ", ".join(r.get("skills") or []) or "—"
                lines.append(f"**{r['machine']}** ({r.get('platform','?')}) — {sk}")
            embed.add_field(name="🕒 Recent sessions", value="\n".join(lines), inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="recommend", description="What should I practice next? (AI recommendation)")
    async def recommend(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        await db.log_command(
            user_id=interaction.user.id, username=str(interaction.user),
            command="/recommend", guild_id=interaction.guild_id,
        )
        embed = await recommender.build_recommendation_embed()
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Learning(bot))
