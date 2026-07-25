"""
Tool registry — the catalogue of internal tools the analyst can call.

Each tool is a thin async wrapper over an existing platform service. The
``source`` label ties a tool to the platform's data-source priority ladder
(Asset Inventory → PostgreSQL → RAG → Threat Intel → CVE/KEV/EPSS → News →
Learning → LLM), so the executor can record *which* platform knowledge answered
a question — the LLM is always the last resort, never the first.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from analyst.tool_handlers import (
    assets,
    cves,
    dashboard,
    learning,
    news,
    rag,
    reports,
    tickets,
)

# Source labels (mirror the data-source priority ladder).
SRC_ASSETS = "Asset Inventory"
SRC_DB = "PostgreSQL"
SRC_RAG = "RAG Knowledge Base"
SRC_CVE = "CVE Database"
SRC_KEV = "CISA KEV"
SRC_NEWS = "RSS News"
SRC_LEARNING = "Learning Database"
SRC_REPORTS = "Reports"
SRC_LLM = "LLM"


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    source: str
    func: Callable[..., Awaitable[Any]]

    async def __call__(self, **kwargs: Any) -> Any:
        return await self.func(**kwargs)


# The registry. Keys are stable tool ids used by the planner/executor.
REGISTRY: dict[str, Tool] = {
    # --- Asset inventory (source #1, the key differentiator) ---
    "assets.affected": Tool(
        "assets.affected", "Correlate every lab asset with the CVEs affecting it",
        SRC_ASSETS, assets.affected),
    "assets.by_cve": Tool(
        "assets.by_cve", "Which lab assets a specific CVE affects", SRC_ASSETS, assets.by_cve),
    "assets.by_product": Tool(
        "assets.by_product", "CVEs affecting a named product + lab presence",
        SRC_ASSETS, assets.by_product),
    "assets.list": Tool(
        "assets.list", "List the lab asset inventory", SRC_ASSETS, assets.list_assets),
    # --- CVEs / threat fusion (sources #5–9) ---
    "cves.counts": Tool(
        "cves.counts", "CVE counts in the last 24h", SRC_CVE, cves.counts_24h),
    "cves.top": Tool(
        "cves.top", "Highest CCC-priority CVEs", SRC_CVE, cves.top_priority),
    "cves.critical": Tool(
        "cves.critical", "Recent critical-severity CVEs", SRC_CVE, cves.critical),
    "cves.kev": Tool(
        "cves.kev", "Known-exploited (CISA KEV) CVEs", SRC_KEV, cves.kev),
    "cves.pocs": Tool(
        "cves.pocs", "CVEs with public exploit PoCs", SRC_CVE, cves.pocs),
    "cves.get": Tool(
        "cves.get", "Fetch + enrich a single CVE", SRC_CVE, cves.get),
    # --- Tickets (source #2) ---
    "tickets.open": Tool(
        "tickets.open", "Open remediation tickets", SRC_DB, tickets.open_tickets),
    # --- RAG knowledge base (source #3) ---
    "rag.search": Tool(
        "rag.search", "Retrieve grounding context from the knowledge base",
        SRC_RAG, rag.search),
    # --- News (source #10) ---
    "news.recent": Tool(
        "news.recent", "Recent cybersecurity news", SRC_NEWS, news.recent),
    "news.ransomware": Tool(
        "news.ransomware", "Recent ransomware news", SRC_NEWS, news.ransomware),
    # --- Learning (source #11) ---
    "learning.plan": Tool(
        "learning.plan", "Build today's learning plan", SRC_LEARNING, learning.plan),
    # --- Reports ---
    "reports.executive": Tool(
        "reports.executive", "Generate an executive intelligence report",
        SRC_REPORTS, reports.executive),
    "reports.technical": Tool(
        "reports.technical", "Generate a technical intelligence report",
        SRC_REPORTS, reports.technical),
    # --- System status ---
    "system.status": Tool(
        "system.status", "Live platform health + threat posture", SRC_DB, dashboard.status),
}


def get(name: str) -> Tool:
    return REGISTRY[name]


def catalogue() -> list[dict[str, str]]:
    """Human-readable list of tools (for /help or introspection)."""
    return [{"name": t.name, "description": t.description, "source": t.source}
            for t in REGISTRY.values()]
