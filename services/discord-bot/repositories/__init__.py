"""Repository-pattern data access layer for the Cyber Command Center bot."""

from repositories.ai_repository import AIRepository, content_hash
from repositories.base import BaseRepository
from repositories.command_repository import CommandRepository
from repositories.cve_repository import CVERepository
from repositories.enrichment_repository import EnrichmentRepository
from repositories.learning_repository import MachineRepository, PracticeRepository
from repositories.monitor_repository import MonitorRepository
from repositories.news_repository import NewsRepository

__all__ = [
    "BaseRepository",
    "CVERepository",
    "NewsRepository",
    "MonitorRepository",
    "CommandRepository",
    "AIRepository",
    "EnrichmentRepository",
    "PracticeRepository",
    "MachineRepository",
    "content_hash",
]
