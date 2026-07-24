"""
Automated CVE monitor.

Every cycle it fetches CVEs modified since the last successful run (defaulting to
a lookback window on first run), keeps only CVSS >= threshold, skips ones already
seen, generates a cached AI summary, stores everything, and posts new ones to
#cve-alerts with a "View on NVD" button.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from discord.ext import commands

from actioning import action_engine
from config import config
from database import db
from enrichment import fusion
from tasks.base import BaseMonitor
from utils import embeds
from utils.logger import cve_log as log
from utils.nvd_client import CVEData, nvd
from utils.summarizer import summarizer


class CVEMonitor(BaseMonitor):
    name = "cve"
    channel_name = config.channel_cve_alerts
    interval = config.cve_fetch_interval
    initial_delay = 20

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)

    async def fetch(self) -> list[CVEData]:
        """Fetch CVSS>=threshold CVEs modified since the last successful run."""
        now = datetime.now(timezone.utc)
        last = await db.monitors.last_success(self.name)
        if last is None:
            start = now - timedelta(hours=config.cve_lookback_hours)
            log.info("[cve] first run — looking back %dh", config.cve_lookback_hours)
        else:
            # NVD windows are capped at 120 days; clamp defensively.
            start = max(last, now - timedelta(days=110))
            log.info("[cve] looking back to last success %s", start.isoformat())

        return await nvd.fetch_recent(
            start, now, min_score=config.cve_min_score, max_results=200
        )

    async def process(self, raw: list[CVEData]) -> list[dict]:
        """
        Persist newly-fetched CVEs, select the unposted backlog, then FUSE each
        with threat intel (EPSS/KEV/ExploitDB/PoCs), compute a priority score, and
        generate an AI risk narrative. Fetching and posting stay decoupled through
        the DB so items stranded by a transient failure still get posted later.
        """
        for cve in raw:
            if not await db.cves.exists(cve.cve_id):
                await db.cves.upsert(
                    cve_id=cve.cve_id, title=cve.cve_id, description=cve.description,
                    cvss_score=cve.cvss_score, severity=cve.severity,
                    published_date=cve.published, ai_summary=None,
                )

        rows = await db.cves.unposted(config.cve_min_score, config.cve_max_posts_per_run)
        if not rows:
            return []

        if not config.enrichment_enabled:
            # Phase-2 behaviour: plain summary + basic embed.
            for row in rows:
                if not row.get("ai_summary"):
                    row["ai_summary"] = await summarizer.summarize_cve(row.get("description") or "")
            return rows

        # --- Phase 3 fusion --------------------------------------------
        # Pull fresh NVD references (for vendor-patch detection) per CVE.
        enrich_input: list[dict] = []
        for row in rows:
            references: list[dict] = []
            try:
                data = await nvd.fetch_cve(row["cve_id"])
                references = data.references
                row["_products"] = data.products  # for lab-matching in the action engine
                if data.description:
                    row["description"] = data.description
            except Exception as exc:  # noqa: BLE001
                log.debug("[cve] reference fetch failed for %s: %s", row["cve_id"], exc)
            enrich_input.append({
                "cve_id": row["cve_id"],
                "cvss_score": row.get("cvss_score"),
                "severity": row.get("severity"),
                "references": references,
            })

        enrichments = await fusion.enrich_many(enrich_input)

        for row in rows:
            enr = enrichments.get(row["cve_id"].upper())
            if enr is None:
                continue
            await db.enrichment.upsert(
                cve_id=enr.cve_id, epss=enr.epss, epss_percentile=enr.epss_percentile,
                kev=enr.kev, kev_ransomware=enr.kev_ransomware,
                exploitdb_ids=enr.exploitdb_ids, github_poc_urls=enr.github_poc_urls,
                patch_available=enr.patch_available, priority_score=enr.priority_score,
                priority_label=enr.priority_label, ai_risk=enr.ai_risk,
            )
            row["_enr"] = enr

        # Highest CCC Priority first.
        rows.sort(key=lambda r: getattr(r.get("_enr"), "priority_score", 0), reverse=True)
        return rows

    async def post(self, items: list[dict]) -> int:
        import asyncio

        channel = self.channel()
        if channel is None:
            log.warning("[cve] channel #%s not found — nothing posted", self.channel_name)
            return 0

        posted = 0
        for row in items:
            enr = row.get("_enr")
            if enr is not None:
                embed = embeds.build_fused_cve_embed(
                    cve_id=row["cve_id"],
                    description=row.get("description") or "No description available.",
                    cvss_score=row.get("cvss_score"),
                    severity=row.get("severity"),
                    published=row.get("published_date"),
                    enr=enr,
                )
            else:
                embed = embeds.build_cve_embed(
                    cve_id=row["cve_id"],
                    description=row.get("description") or "No description available.",
                    cvss_score=row.get("cvss_score"),
                    severity=row.get("severity"),
                    published=row.get("published_date"),
                    ai_summary=row.get("ai_summary"),
                    source_note="NVD • auto",
                )
            await channel.send(embed=embed, view=embeds.nvd_view(row["cve_id"]))
            await db.cves.mark_posted(row["cve_id"])
            posted += 1

            # Phase 8: if this CVE hits the lab, auto-raise a ticket + escalate.
            if enr is not None:
                try:
                    await action_engine.evaluate(
                        self.bot,
                        cve_id=row["cve_id"],
                        description=row.get("description") or "",
                        products=row.get("_products", []) or [],
                        priority=enr.priority_score,
                    )
                except Exception as exc:  # noqa: BLE001 - actioning must not break posting
                    log.error("[cve] action engine failed for %s: %s", row["cve_id"], exc)

            if config.cve_post_delay and posted < len(items):
                await asyncio.sleep(config.cve_post_delay)
        return posted
