"""
Cyber news intelligence monitor.

Every cycle it pulls up to N newest articles per feed, skips ones already stored,
generates a cached AI summary, persists them, and posts new ones to #cyber-news
with a delay between posts to avoid spamming.
"""

from __future__ import annotations

import asyncio

from discord.ext import commands

from config import config
from database import db
from tasks.base import BaseMonitor
from utils import embeds
from utils.logger import news_log as log
from utils.rss_client import Article, fetch_per_feed
from utils.summarizer import summarizer


class NewsMonitor(BaseMonitor):
    name = "news"
    channel_name = config.channel_cyber_news
    interval = config.news_fetch_interval
    # Start well after the CVE monitor so first-run backfills don't contend for
    # the single Ollama slot.
    initial_delay = 180

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)

    async def fetch(self) -> list[Article]:
        return await fetch_per_feed(limit_per_feed=config.news_max_per_feed)

    async def process(self, raw: list[Article]) -> list[Article]:
        """Skip already-seen URLs, summarise + persist the new ones."""
        fresh: list[Article] = []
        for art in raw:
            if await db.news.is_posted(art.url):
                continue
            summary = await summarizer.summarize_article(art.title, art.description or art.title)
            await db.news.upsert(
                title=art.title,
                url=art.url,
                source=art.source,
                description=(art.description or "")[:1000] or None,
                ai_summary=summary,
                published_date=art.published,
            )
            art.ai_summary = summary  # stash for post()
            fresh.append(art)
        return fresh

    async def post(self, items: list[Article]) -> int:
        channel = self.channel()
        if channel is None:
            log.warning("[news] channel #%s not found — nothing posted", self.channel_name)
            return 0

        posted = 0
        for art in items:
            embed = embeds.build_news_embed(
                title=art.title,
                url=art.url,
                source=art.source,
                ai_summary=getattr(art, "ai_summary", None),
                description=art.description,
                published=art.published,
            )
            await channel.send(embed=embed)
            await db.news.mark_posted(art.url)
            posted += 1
            if config.news_post_delay and posted < len(items):
                await asyncio.sleep(config.news_post_delay)
        return posted
