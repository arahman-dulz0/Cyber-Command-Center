"""
Async RSS feed fetcher.

feedparser is synchronous, so we download each feed with aiohttp and parse the
raw bytes in a thread executor to avoid blocking the event loop.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from time import mktime

import aiohttp
import feedparser

from config import config
from utils.logger import news_log as log


def _feeds() -> dict[str, str]:
    """Current feed map (configurable via RSS_FEEDS; Phase 2 default has 5)."""
    return config.rss_feeds


@dataclass
class Article:
    title: str
    url: str
    source: str
    description: str
    published: datetime | None


def _to_datetime(entry) -> datetime | None:
    struct = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if struct:
        try:
            return datetime.fromtimestamp(mktime(struct), tz=timezone.utc)
        except (ValueError, OverflowError):
            return None
    return None


async def _fetch_one(session: aiohttp.ClientSession, source: str, url: str) -> list[Article]:
    try:
        async with session.get(url) as resp:
            resp.raise_for_status()
            raw = await resp.read()
    except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
        log.warning("RSS fetch failed for %s: %s", source, exc)
        return []

    # Parse off the event loop.
    loop = asyncio.get_running_loop()
    parsed = await loop.run_in_executor(None, feedparser.parse, raw)

    articles: list[Article] = []
    for entry in parsed.entries:
        title = getattr(entry, "title", "").strip()
        link = getattr(entry, "link", "").strip()
        if not title or not link:
            continue
        summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
        articles.append(
            Article(
                title=title,
                url=link,
                source=source,
                description=summary,
                published=_to_datetime(entry),
            )
        )
    return articles


async def _fetch_all() -> list[tuple[str, list[Article]]]:
    """Fetch every configured feed concurrently; return (source, articles) pairs."""
    feeds = _feeds()
    timeout = aiohttp.ClientTimeout(total=20)
    headers = {"User-Agent": "CyberCommandCenter/1.0 (+https://github.com)"}
    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        results = await asyncio.gather(
            *[_fetch_one(session, name, url) for name, url in feeds.items()]
        )
    return list(zip(feeds.keys(), results))


def _newest(articles: list[Article], limit: int) -> list[Article]:
    articles.sort(
        key=lambda a: a.published or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return articles[:limit]


async def fetch_latest(limit: int = 5) -> list[Article]:
    """Newest ``limit`` articles across all sources (most recent first)."""
    grouped = await _fetch_all()
    all_articles = [a for _, group in grouped for a in group]
    return _newest(all_articles, limit)


async def fetch_per_feed(limit_per_feed: int = 3) -> list[Article]:
    """
    Up to ``limit_per_feed`` newest articles from EACH source.

    Used by the news monitor so every feed is represented and no single feed can
    dominate. Returned newest-first per feed, feeds in configured order.
    """
    grouped = await _fetch_all()
    out: list[Article] = []
    for _, group in grouped:
        out.extend(_newest(group, limit_per_feed))
    return out
