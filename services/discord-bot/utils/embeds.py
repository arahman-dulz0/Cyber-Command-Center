"""
Discord embed builder + the shared visual design system.

Every command in the bot builds its embeds through the helpers here so the
look and feel stays consistent (colors, footer, author line).
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import discord

from config import config

# --- Color palette (from the design spec) --------------------------------
CRITICAL = 0xFF0000  # red
HIGH = 0xFF6600      # orange
MEDIUM = 0xFFCC00    # yellow
LOW = 0x00CC00       # green
INFO = 0x0099FF      # blue
SUCCESS = 0x00FF00   # bright green
ERROR = 0xFF0000     # red
DARK_BLUE = 0x001F54  # daily brief sidebar

_TZ = ZoneInfo(config.timezone)


def now_local() -> datetime:
    """Current time in the configured timezone (Asia/Colombo by default)."""
    return datetime.now(_TZ)


def severity_color(severity: str | None) -> int:
    """Map an NVD severity string to the palette color."""
    mapping = {
        "CRITICAL": CRITICAL,
        "HIGH": HIGH,
        "MEDIUM": MEDIUM,
        "LOW": LOW,
    }
    return mapping.get((severity or "").upper(), INFO)


def _stamp(embed: discord.Embed) -> discord.Embed:
    """Apply the standard footer + timestamp used across the whole bot."""
    ts = now_local().strftime("%Y-%m-%d %H:%M:%S")
    embed.set_footer(text=f"Cyber Command Center • {ts}")
    return embed


def base_embed(
    *,
    title: str,
    description: str | None = None,
    color: int = INFO,
    url: str | None = None,
) -> discord.Embed:
    """Create an embed pre-styled with the house footer."""
    embed = discord.Embed(title=title, description=description, color=color, url=url)
    return _stamp(embed)


def error_embed(message: str, *, title: str = "⚠️ Something went wrong") -> discord.Embed:
    """A friendly, user-facing error embed (never contains a raw traceback)."""
    return base_embed(title=title, description=message, color=ERROR)


def success_embed(message: str, *, title: str = "✅ Success") -> discord.Embed:
    return base_embed(title=title, description=message, color=SUCCESS)


def nvd_url(cve_id: str) -> str:
    return f"https://nvd.nist.gov/vuln/detail/{cve_id}"


def nvd_view(cve_id: str) -> discord.ui.View:
    """A View with a single 'View on NVD' link button (no callback needed)."""
    view = discord.ui.View()
    view.add_item(
        discord.ui.Button(
            label="View on NVD",
            style=discord.ButtonStyle.link,
            url=nvd_url(cve_id),
            emoji="🔗",
        )
    )
    return view


def build_cve_embed(
    *,
    cve_id: str,
    description: str,
    cvss_score: float | None,
    severity: str | None,
    cvss_vector: str | None = None,
    products: list[str] | None = None,
    published: datetime | None = None,
    ai_summary: str | None = None,
    from_cache: bool = False,
    source_note: str = "NVD",
) -> discord.Embed:
    """Shared CVE embed used by both the /cve command and the CVE monitor."""
    embed = base_embed(title=cve_id, color=severity_color(severity), url=nvd_url(cve_id))

    score_txt = f"{cvss_score}" if cvss_score is not None else "N/A"
    embed.add_field(name="CVSS Score", value=f"**{score_txt}** ({severity or 'UNKNOWN'})", inline=True)
    if cvss_vector:
        embed.add_field(name="Vector", value=f"`{cvss_vector}`", inline=True)
    if published:
        embed.add_field(name="Published", value=published.strftime("%Y-%m-%d"), inline=True)

    if products:
        embed.add_field(
            name="Affected Products (max 5)",
            value="\n".join(f"• {p}" for p in products[:5]),
            inline=False,
        )

    desc = description if len(description) <= 1000 else description[:997] + "..."
    embed.add_field(name="Description", value=desc, inline=False)

    if ai_summary:
        embed.add_field(name="🤖 AI Summary", value=ai_summary[:1024], inline=False)

    suffix = " (cached)" if from_cache else ""
    embed.set_footer(text=f"Cyber Command Center • {source_note}{suffix}")
    return embed


def priority_color(label: str | None) -> int:
    return {
        "CRITICAL": CRITICAL,
        "HIGH": HIGH,
        "MEDIUM": MEDIUM,
        "LOW": LOW,
    }.get((label or "").upper(), INFO)


def build_fused_cve_embed(
    *,
    cve_id: str,
    description: str,
    cvss_score: float | None,
    severity: str | None,
    published: datetime | None,
    enr,  # enrichment.base.Enrichment
    source_note: str = "NVD • Fusion Engine",
) -> discord.Embed:
    """Phase 3 alert: CVE fused with EPSS/KEV/ExploitDB/PoCs + priority + AI risk."""
    embed = base_embed(
        title=f"🚨 {enr.priority_label} — {cve_id}",
        color=priority_color(enr.priority_label),
        url=nvd_url(cve_id),
    )
    embed.add_field(name="🎯 CCC Priority", value=f"**{enr.priority_score}/100**", inline=True)
    embed.add_field(
        name="CVSS",
        value=f"**{cvss_score if cvss_score is not None else 'N/A'}** ({severity or '?'})",
        inline=True,
    )
    embed.add_field(
        name="EPSS",
        value=f"**{enr.epss * 100:.0f}%**" if enr.epss is not None else "n/a",
        inline=True,
    )
    kev = ("✅ YES" + (" 🦠 ransomware" if enr.kev_ransomware else "")) if enr.kev else "❌ No"
    embed.add_field(name="Known Exploited", value=kev, inline=True)
    embed.add_field(
        name="Exploit Available",
        value="✅ YES" if enr.exploit_available else "❌ No",
        inline=True,
    )
    embed.add_field(
        name="GitHub PoC",
        value=f"{enr.github_poc_count} repos" if enr.github_poc_count else "none",
        inline=True,
    )
    embed.add_field(
        name="ExploitDB",
        value=f"{enr.exploitdb_count} entries" if enr.exploitdb_count else "none",
        inline=True,
    )
    embed.add_field(
        name="Vendor Patch",
        value="Available" if enr.patch_available else "Unknown",
        inline=True,
    )
    if published:
        embed.add_field(name="Published", value=published.strftime("%Y-%m-%d"), inline=True)

    desc = description if len(description) <= 700 else description[:697] + "..."
    embed.add_field(name="Description", value=desc, inline=False)
    if enr.ai_risk:
        embed.add_field(name="🤖 AI Risk Analysis", value=enr.ai_risk[:1024], inline=False)

    embed.set_footer(text=f"Cyber Command Center • {source_note}")
    return embed


def build_news_embed(
    *,
    title: str,
    url: str,
    source: str,
    ai_summary: str | None = None,
    description: str | None = None,
    published: datetime | None = None,
) -> discord.Embed:
    """Shared single-article embed used by the news monitor."""
    embed = base_embed(title=title[:256], url=url, color=INFO)
    embed.add_field(name="Source", value=source, inline=True)
    if published:
        embed.add_field(name="Published", value=published.strftime("%Y-%m-%d %H:%M"), inline=True)

    body = ai_summary or (description or "")
    if body:
        label = "🤖 AI Summary" if ai_summary else "Summary"
        embed.add_field(name=label, value=body[:1024], inline=False)
    return embed
