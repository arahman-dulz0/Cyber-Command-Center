"""Shared types for the threat-intelligence enrichment layer."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Enrichment:
    """Fused threat-intelligence for a single CVE."""

    cve_id: str
    epss: float | None = None            # 0..1 probability of exploitation
    epss_percentile: float | None = None  # 0..1
    kev: bool = False                    # CISA Known Exploited Vulnerability
    kev_ransomware: bool = False
    exploitdb_ids: list[str] = field(default_factory=list)
    github_poc_urls: list[str] = field(default_factory=list)
    patch_available: bool = False
    priority_score: int = 0              # 0..100 (CCC Priority)
    priority_label: str = "LOW"          # CRITICAL | HIGH | MEDIUM | LOW
    ai_risk: str | None = None

    @property
    def exploit_available(self) -> bool:
        return bool(self.exploitdb_ids) or bool(self.github_poc_urls)

    @property
    def exploitdb_count(self) -> int:
        return len(self.exploitdb_ids)

    @property
    def github_poc_count(self) -> int:
        return len(self.github_poc_urls)
