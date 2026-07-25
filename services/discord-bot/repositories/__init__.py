"""Repository-pattern data access layer for the Cyber Command Center bot."""

from repositories.action_repository import LabRepository, TicketRepository
from repositories.ai_repository import AIRepository, content_hash
from repositories.analyst_repository import AnalystRepository
from repositories.audit_repository import AuditRepository
from repositories.base import BaseRepository
from repositories.command_repository import CommandRepository
from repositories.cve_repository import CVERepository
from repositories.enrichment_repository import EnrichmentRepository
from repositories.kb_repository import KBRepository
from repositories.learning_repository import MachineRepository, PracticeRepository
from repositories.monitor_repository import MonitorRepository
from repositories.news_repository import NewsRepository
from repositories.report_repository import ReportRepository

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
    "KBRepository",
    "ReportRepository",
    "LabRepository",
    "TicketRepository",
    "AuditRepository",
    "AnalystRepository",
    "content_hash",
]
