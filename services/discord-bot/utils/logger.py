"""
Logging setup for the bot.

Logs to both the console and a daily-rotated file (``logs/bot.log``), keeping
7 days of history. Format:

    [2026-07-22 07:30:00] [INFO] [cve] User abdul used /cve CVE-2021-44228

Phase 2 introduces named component loggers (AI, Discord, CVE, News, Scheduler,
Database, Errors) that all share the same handlers. Use ``get_logger(name)`` or
one of the pre-built module-level loggers.
"""

from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# %(name)s carries the component (e.g. "cybercommand.cve").
_LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_ROOT_NAME = "cybercommand"

# Component logger suffixes required by the spec.
COMPONENTS = ("ai", "discord", "cve", "news", "scheduler", "database", "errors")

_configured = False


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure the root 'cybercommand' logger exactly once and return it."""
    global _configured

    root = logging.getLogger(_ROOT_NAME)
    if _configured:
        return root

    root.setLevel(level)
    root.propagate = False

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    log_dir = Path(__file__).resolve().parents[1] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = TimedRotatingFileHandler(
        log_dir / "bot.log",
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    logging.getLogger("discord").setLevel(logging.WARNING)

    _configured = True
    return root


def get_logger(component: str | None = None) -> logging.Logger:
    """
    Return a component logger.

    Child loggers propagate to the configured 'cybercommand' root, so they all
    share the console + rotating-file handlers. ``get_logger()`` returns the
    root logger (backward compatible with Phase 1).
    """
    setup_logging()
    if component is None:
        return logging.getLogger(_ROOT_NAME)
    return logging.getLogger(f"{_ROOT_NAME}.{component}")


# Pre-built component loggers for convenient imports.
ai_log = get_logger("ai")
discord_log = get_logger("discord.bot")
cve_log = get_logger("cve")
news_log = get_logger("news")
scheduler_log = get_logger("scheduler")
db_log = get_logger("database")
error_log = get_logger("errors")
