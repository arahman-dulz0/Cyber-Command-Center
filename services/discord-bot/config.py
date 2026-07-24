"""
Central configuration loader for the Cyber Command Center Discord bot.

All values are read from environment variables (loaded from a local ``.env``
file during development, or injected by Docker Compose in production).
Nothing is ever hard-coded here — every secret must come from the environment.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load a .env file if one exists. In development the file lives at the project
# root (services/discord-bot/config.py -> ../../.env); in Docker the source is
# copied flat into /app and the variables are supplied via Compose `env_file`,
# so reading a .env file is optional there. We probe a few likely locations and
# fall back to load_dotenv()'s default search (CWD / already-exported vars).
_here = Path(__file__).resolve()
_candidates = [p / ".env" for p in _here.parents[:3]]
for _candidate in _candidates:
    if _candidate.exists():
        load_dotenv(_candidate)
        break
else:
    load_dotenv()  # fall back to CWD / already-exported vars


def _get(key: str, default: str | None = None, *, required: bool = False) -> str:
    value = os.getenv(key, default)
    if required and (value is None or value == ""):
        raise RuntimeError(
            f"Required environment variable '{key}' is missing. "
            f"Add it to your .env file (see .env.example)."
        )
    return value if value is not None else ""


def _get_int(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _get_float(key: str, default: float) -> float:
    raw = os.getenv(key)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _get_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


# Built-in RSS sources (Phase 2 adds Krebs on Security + Schneier on Security).
_DEFAULT_FEEDS: dict[str, str] = {
    "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
    "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
    "CISA Alerts": "https://www.cisa.gov/uscert/ncas/alerts.xml",
    "Krebs on Security": "https://krebsonsecurity.com/feed/",
    "Schneier on Security": "https://www.schneier.com/feed/atom/",
}


def _get_feeds() -> dict[str, str]:
    """Return the RSS feed map, allowing a JSON override via the RSS_FEEDS env var."""
    raw = os.getenv("RSS_FEEDS")
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict) and parsed:
                return {str(k): str(v) for k, v in parsed.items()}
        except json.JSONDecodeError:
            pass
    return dict(_DEFAULT_FEEDS)


@dataclass(frozen=True)
class Config:
    """Immutable, fully-typed view of the bot's runtime configuration."""

    # --- Discord ---------------------------------------------------------
    discord_token: str = field(default_factory=lambda: _get("DISCORD_TOKEN", required=True))
    guild_id: int = field(default_factory=lambda: _get_int("DISCORD_GUILD_ID", 0))

    # --- External APIs ---------------------------------------------------
    nvd_api_key: str = field(default_factory=lambda: _get("NVD_API_KEY", ""))
    youtube_api_key: str = field(default_factory=lambda: _get("YOUTUBE_API_KEY", ""))

    # --- PostgreSQL ------------------------------------------------------
    pg_host: str = field(default_factory=lambda: _get("POSTGRES_HOST", "192.168.8.185"))
    pg_port: int = field(default_factory=lambda: _get_int("POSTGRES_PORT", 5432))
    pg_user: str = field(default_factory=lambda: _get("POSTGRES_USER", "cyber"))
    pg_password: str = field(default_factory=lambda: _get("POSTGRES_PASSWORD", required=True))
    pg_db: str = field(default_factory=lambda: _get("POSTGRES_DB", "cyberdb"))

    # --- Redis -----------------------------------------------------------
    redis_host: str = field(default_factory=lambda: _get("REDIS_HOST", "192.168.8.185"))
    redis_port: int = field(default_factory=lambda: _get_int("REDIS_PORT", 6379))

    # --- Ollama ----------------------------------------------------------
    ollama_host: str = field(default_factory=lambda: _get("OLLAMA_HOST", "http://192.168.8.185:11434"))
    ollama_model: str = field(default_factory=lambda: _get("OLLAMA_MODEL", "qwen2.5:3b"))
    ollama_timeout: int = field(default_factory=lambda: _get_int("OLLAMA_TIMEOUT", 45))
    ollama_retries: int = field(default_factory=lambda: _get_int("OLLAMA_RETRIES", 3))
    ollama_max_concurrency: int = field(default_factory=lambda: _get_int("OLLAMA_MAX_CONCURRENCY", 2))

    # --- Bot behaviour ---------------------------------------------------
    bot_logs_channel: str = field(default_factory=lambda: _get("BOT_LOGS_CHANNEL", "bot-logs"))
    timezone: str = field(default_factory=lambda: _get("TIMEZONE", "Asia/Colombo"))
    cve_min_score: float = field(default_factory=lambda: _get_float("CVE_MIN_SCORE", 7.0))
    news_fetch_interval: int = field(default_factory=lambda: _get_int("NEWS_FETCH_INTERVAL", 7200))
    cve_fetch_interval: int = field(default_factory=lambda: _get_int("CVE_FETCH_INTERVAL", 3600))
    daily_brief_time: str = field(default_factory=lambda: _get("DAILY_BRIEF_TIME", "07:30"))

    # --- Phase 2: autonomous monitoring ----------------------------------
    monitors_enabled: bool = field(default_factory=lambda: _get_bool("MONITORS_ENABLED", True))
    cve_lookback_hours: int = field(default_factory=lambda: _get_int("CVE_LOOKBACK_HOURS", 24))
    cve_max_posts_per_run: int = field(default_factory=lambda: _get_int("CVE_MAX_POSTS_PER_RUN", 10))
    cve_post_delay: int = field(default_factory=lambda: _get_int("CVE_POST_DELAY", 3))
    news_max_per_feed: int = field(default_factory=lambda: _get_int("NEWS_MAX_PER_FEED", 3))
    news_post_delay: int = field(default_factory=lambda: _get_int("NEWS_POST_DELAY", 30))
    rss_feeds: dict = field(default_factory=_get_feeds)

    # --- Phase 3: threat-intelligence fusion -----------------------------
    enrichment_enabled: bool = field(default_factory=lambda: _get_bool("ENRICHMENT_ENABLED", True))
    epss_url: str = field(default_factory=lambda: _get("EPSS_URL", "https://api.first.org/data/v1/epss"))
    kev_url: str = field(default_factory=lambda: _get(
        "KEV_URL",
        "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
    ))
    exploitdb_csv_url: str = field(default_factory=lambda: _get(
        "EXPLOITDB_CSV_URL",
        "https://gitlab.com/exploit-database/exploitdb/-/raw/main/files_exploits.csv",
    ))
    github_poc_base: str = field(default_factory=lambda: _get(
        "GITHUB_POC_BASE",
        "https://raw.githubusercontent.com/nomi-sec/PoC-in-GitHub/master",
    ))
    kev_refresh_hours: int = field(default_factory=lambda: _get_int("KEV_REFRESH_HOURS", 6))
    exploitdb_refresh_hours: int = field(default_factory=lambda: _get_int("EXPLOITDB_REFRESH_HOURS", 24))

    # --- Channel names (configurable; the server already has these) -------
    channel_cve_alerts: str = field(default_factory=lambda: _get("CVE_ALERTS_CHANNEL", "cve-alerts"))
    channel_cyber_news: str = field(default_factory=lambda: _get("CYBER_NEWS_CHANNEL", "cyber-news"))
    channel_daily_brief: str = field(default_factory=lambda: _get("DAILY_BRIEF_CHANNEL", "daily-brief"))
    channel_announcements: str = "announcements"
    channel_htb_ctf: str = "htb-ctf"
    channel_ai_summaries: str = "ai-summaries"

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://{self.pg_user}:{self.pg_password}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_db}"
        )

    @property
    def masked_host(self) -> str:
        """Return the PostgreSQL host with the last octet masked, e.g. 192.168.8.xxx."""
        parts = self.pg_host.split(".")
        if len(parts) == 4:
            return ".".join(parts[:3] + ["xxx"])
        return self.pg_host


# A single shared instance imported everywhere.
config = Config()
