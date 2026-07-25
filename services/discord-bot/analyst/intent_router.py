"""
Intent router — classifies a natural-language query into an intent + entities.

Deterministic keyword/regex rules cover the common analyst questions reliably;
an LLM classifier is the fallback for anything ambiguous. Follow-up pronouns
("it", "that", "my lab") are resolved from conversational memory.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from analyst.memory import UserMemory
from utils.logger import get_logger
from utils.ollama_client import OllamaError, ollama

log = get_logger("analyst.router")

CVE_RE = re.compile(r"CVE-\d{4}-\d{4,}", re.IGNORECASE)

# Small tech vocabulary for product extraction (the asset handler also cross-
# checks the real inventory). Lowercase.
TECH_VOCAB = [
    "apache", "nginx", "wordpress", "vmware", "windows", "linux", "ubuntu",
    "log4j", "log4shell", "openssl", "exchange", "fortinet", "cisco", "citrix",
    "docker", "kubernetes", "jenkins", "gitlab", "confluence", "jira", "spring",
    "struts", "tomcat", "postgres", "mysql", "redis", "mongodb", "php", "python",
    "active directory", "kerberos", "smb", "rdp", "sharepoint", "outlook",
]

# Intent labels used across the analyst.
INTENTS = [
    "OVERNIGHT", "CRITICAL_CVES", "KEV", "PATCH_PRIORITIES", "AFFECTED_ASSETS",
    "EXPLAIN_CVE", "EXPLAIN_TOPIC", "NEWS", "RANSOMWARE", "POCS", "LEARNING",
    "EXEC_REPORT", "TECH_REPORT", "TICKETS", "POSTURE", "STATUS", "GENERAL",
]


@dataclass
class Intent:
    name: str
    entities: dict = field(default_factory=dict)
    confidence: float = 1.0
    llm_classified: bool = False  # True when the LLM fallback resolved the intent


def _has(text: str, *terms: str) -> bool:
    return any(t in text for t in terms)


def _extract_product(text: str) -> str | None:
    for tech in TECH_VOCAB:
        if re.search(rf"\b{re.escape(tech)}\b", text):
            return tech
    return None


class IntentRouter:
    async def classify(self, query: str, mem: UserMemory) -> Intent:
        q = query.lower().strip()
        cve = CVE_RE.search(query)
        cve_id = cve.group(0).upper() if cve else None
        product = _extract_product(q)

        # Resolve follow-up pronouns from memory.
        refers_back = _has(q, "it", "this", "that", "them", "those") or q.startswith(("does", "is"))
        if not cve_id and refers_back and mem.last_cve:
            cve_id = mem.last_cve
        if not product and refers_back and mem.last_product:
            product = mem.last_product

        # --- Asset correlation (highest-value, checked early) ---
        _possessive = _has(q, "my", "our", "lab", "system", "asset", "stack", "server",
                           "environment", "infra", "inventory", "network")
        _exposure = _has(q, "affect", "affected", "impact", "vulnerable", "at risk",
                         "exposure", "exposed", "expose", "susceptible")
        if _exposure and (_possessive or cve_id):
            return Intent("AFFECTED_ASSETS", {"cve_id": cve_id, "product": product})
        if _possessive and _has(q, "risk", "cve", "vulnerabilit", "threat", "danger"):
            return Intent("AFFECTED_ASSETS", {"cve_id": cve_id, "product": product})
        if product and _has(q, "vulnerabilit", "cve", "affecting", "issues with", "problems with"):
            return Intent("AFFECTED_ASSETS", {"product": product})
        if _has(q, "most vulnerable", "weakest asset", "riskiest"):
            return Intent("AFFECTED_ASSETS", {"product": product})

        # --- Explain ---
        if cve_id and _has(q, "explain", "what is", "tell me about", "details", "describe"):
            return Intent("EXPLAIN_CVE", {"cve_id": cve_id})
        if cve_id and not _has(q, "patch", "affect"):
            return Intent("EXPLAIN_CVE", {"cve_id": cve_id})
        if _has(q, "explain", "what is", "how does", "tell me about"):
            topic = query.strip()
            return Intent("EXPLAIN_TOPIC", {"topic": topic, "product": product})

        # --- Summaries / briefings ---
        if _has(q, "overnight", "last night", "since yesterday", "happened") or (
            _has(q, "summar") and _has(q, "today", "threat")
        ):
            return Intent("OVERNIGHT", {})
        if _has(q, "soc brief", "morning brief", "daily brief", "today's brief", "briefing"):
            return Intent("OVERNIGHT", {})

        # --- Prioritisation ---
        if _has(q, "patch first", "patch today", "should i patch", "prioriti", "remediat", "fix first"):
            return Intent("PATCH_PRIORITIES", {})

        # --- Specific intel views ---
        if _has(q, "kev", "known exploited", "actively exploited"):
            return Intent("KEV", {})
        if _has(q, "critical cve", "any critical", "critical vuln"):
            return Intent("CRITICAL_CVES", {})
        if _has(q, "ransomware"):
            return Intent("RANSOMWARE", {})
        if _has(q, "poc", "proof of concept", "exploit", "github"):
            return Intent("POCS", {})
        if _has(q, "news", "cisa alert", "advisor", "headline"):
            return Intent("NEWS", {})

        # --- Learning ---
        if _has(q, "learn", "study", "practice", "htb", "hackthebox", "recommend a", "recommend an", "recommend machine"):
            return Intent("LEARNING", {})

        # --- Reports ---
        if _has(q, "report"):
            kind = "technical" if _has(q, "technical", "ioc", "mitre", "att&ck") else "executive"
            return Intent("EXEC_REPORT" if kind == "executive" else "TECH_REPORT", {})

        # --- Tickets / posture / status ---
        if _has(q, "ticket"):
            return Intent("TICKETS", {})
        if _has(q, "posture", "how is my lab", "how's my lab", "how are we doing", "overall risk", "risk score"):
            return Intent("POSTURE", {})
        if _has(q, "status", "health", "services up", "system status"):
            return Intent("STATUS", {})

        # --- LLM fallback classification ---
        label = await self._llm_classify(query)
        if label == "AFFECTED_ASSETS":
            return Intent(label, {"cve_id": cve_id, "product": product}, llm_classified=True)
        if label == "EXPLAIN_CVE" and cve_id:
            return Intent(label, {"cve_id": cve_id}, llm_classified=True)
        if label in ("EXPLAIN_TOPIC", "GENERAL"):
            return Intent(label, {"topic": query.strip(), "product": product}, llm_classified=True)
        if label in INTENTS:
            return Intent(label, {"cve_id": cve_id, "product": product}, llm_classified=True)
        return Intent("GENERAL", {"topic": query.strip(), "product": product}, llm_classified=True)

    async def _llm_classify(self, query: str) -> str:
        system = (
            "Classify the security analyst question into exactly ONE label from this "
            "list and reply with only the label, nothing else:\n"
            + ", ".join(INTENTS)
        )
        try:
            text, _ = await ollama.generate(query, system=system, num_predict=12)
        except OllamaError:
            return "GENERAL"
        text = text.strip().upper()
        for label in INTENTS:
            if label in text:
                return label
        return "GENERAL"


# Shared instance.
router = IntentRouter()
