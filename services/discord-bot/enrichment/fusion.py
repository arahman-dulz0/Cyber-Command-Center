"""
Threat-Intelligence Fusion Engine (Phase 3).

Correlates multiple free intelligence sources for a CVE into a single
:class:`Enrichment`, computes a 0-100 CCC Priority score, and asks the local AI
for a risk narrative. Adding a new source = add a client + one line in ``enrich``.

Priority score (0-100):
    CVSS      -> up to 40   (cvss/10 * 40)
    EPSS      -> up to 30   (epss * 30)
    KEV       -> +20        (actively exploited)
    Exploit   -> +10        (public exploit or PoC available)
"""

from __future__ import annotations

from enrichment.base import Enrichment
from enrichment.epss import EPSSClient
from enrichment.exploitdb import ExploitDBClient
from enrichment.github_poc import GitHubPoCClient
from enrichment.kev import KEVClient
from utils.logger import get_logger
from utils.summarizer import summarizer

log = get_logger("enrichment.fusion")


def _score_and_label(
    cvss: float | None, epss: float | None, kev: bool, exploit: bool
) -> tuple[int, str]:
    score = 0.0
    if cvss:
        score += (cvss / 10.0) * 40.0
    if epss:
        score += epss * 30.0
    if kev:
        score += 20.0
    if exploit:
        score += 10.0
    score = max(0, min(100, round(score)))

    if score >= 80:
        label = "CRITICAL"
    elif score >= 60:
        label = "HIGH"
    elif score >= 40:
        label = "MEDIUM"
    else:
        label = "LOW"
    return score, label


def _facts(
    cve_id: str, cvss: float | None, sev: str | None, enr: Enrichment
) -> str:
    """Deterministic fact sheet fed to the AI (also the cache key input)."""
    epss_pct = f"{enr.epss * 100:.0f}%" if enr.epss is not None else "unknown"
    return (
        f"CVE: {cve_id}\n"
        f"CVSS: {cvss if cvss is not None else 'unknown'} ({sev or 'unknown'})\n"
        f"EPSS: {epss_pct}\n"
        f"Known Exploited (CISA KEV): {'yes' if enr.kev else 'no'}"
        f"{' (ransomware)' if enr.kev_ransomware else ''}\n"
        f"Public exploit (ExploitDB): {'yes, ' + str(enr.exploitdb_count) + ' entries' if enr.exploitdb_ids else 'no'}\n"
        f"GitHub PoCs: {enr.github_poc_count}\n"
        f"Vendor patch available: {'yes' if enr.patch_available else 'unknown'}\n"
        f"CCC Priority: {enr.priority_score}/100 ({enr.priority_label})"
    )


class FusionEngine:
    def __init__(self) -> None:
        self.epss = EPSSClient()
        self.kev = KEVClient()
        self.exploitdb = ExploitDBClient()
        self.github = GitHubPoCClient()

    async def enrich_many(self, cves: list[dict]) -> dict[str, Enrichment]:
        """
        Enrich a batch of CVE rows (each needs cve_id, cvss_score, severity, and
        optionally 'references'). Returns {cve_id: Enrichment}. Never raises —
        any failed source degrades to a neutral value.
        """
        ids = [c["cve_id"].upper() for c in cves]

        # Bulk/prepared sources.
        epss_map = await self.epss.scores(ids)
        await self.kev.ensure()
        await self.exploitdb.ensure()

        out: dict[str, Enrichment] = {}
        for cve in cves:
            cid = cve["cve_id"].upper()
            cvss = cve.get("cvss_score")
            sev = cve.get("severity")
            references = cve.get("references") or []

            epss_val = epss_map.get(cid)
            enr = Enrichment(cve_id=cid)
            if epss_val:
                enr.epss, enr.epss_percentile = epss_val
            enr.kev = self.kev.is_kev(cid)
            enr.kev_ransomware = self.kev.ransomware(cid)
            enr.exploitdb_ids = self.exploitdb.exploits(cid)
            enr.github_poc_urls = await self.github.pocs(cid)
            enr.patch_available = any(
                "Patch" in (r.get("tags") or []) for r in references
            )

            enr.priority_score, enr.priority_label = _score_and_label(
                cvss, enr.epss, enr.kev, enr.exploit_available
            )
            enr.ai_risk = await summarizer.risk_assessment(_facts(cid, cvss, sev, enr))
            out[cid] = enr
            log.info(
                "Fused %s -> priority %d/%d (KEV=%s EPSS=%s exploit=%s)",
                cid, enr.priority_score, 100, enr.kev,
                f"{enr.epss:.2f}" if enr.epss is not None else "?", enr.exploit_available,
            )
        return out

    async def enrich_one(self, cve: dict) -> Enrichment:
        result = await self.enrich_many([cve])
        return result[cve["cve_id"].upper()]


# Shared instance.
fusion = FusionEngine()
