"""
AI summarisation service.

Sits between the cogs/monitors and the low-level :class:`OllamaClient`, adding:

  * a persistent summary cache (never summarise the same content twice),
  * AI metric recording (count + latency for /stats),
  * graceful failure — returns ``None`` so callers can post without a summary.

Concurrency is bounded inside the Ollama client (global semaphore), so this
service is safe to call from multiple monitors at once.
"""

from __future__ import annotations

from database import db
from repositories import content_hash
from utils.logger import ai_log as log
from utils.ollama_client import OllamaClient, OllamaError, ollama

_CVE_SYSTEM = (
    "You are a cybersecurity analyst. Summarise the vulnerability in plain, "
    "non-technical English in exactly 2 short sentences. No preamble, no "
    "markdown, no bullet points."
)
_ARTICLE_SYSTEM = (
    "Summarise this security news article in 2-3 concise sentences for a busy "
    "reader. Plain English, no preamble, no markdown."
)
_TIP_SYSTEM = "You are a security awareness coach."
_TIP_PROMPT = (
    "Give one practical, actionable cybersecurity tip in a single sentence. "
    "No preamble."
)
_TIP_FALLBACK = "Keep your systems patched and enable MFA everywhere."


class Summarizer:
    """Cached, metric-recording AI summariser."""

    def __init__(self, client: OllamaClient | None = None) -> None:
        self.client = client or ollama

    # Short summaries need few tokens; capping keeps each call well under the
    # timeout on a CPU-only host.
    _SUMMARY_TOKENS = 200

    async def _cached_generate(self, *, kind: str, prompt: str, system: str) -> str | None:
        """Return a cached summary if present, else generate, cache, and record."""
        key = content_hash(self.client.model, f"{system}\n{prompt}")

        if db.ai is not None:
            cached = await db.ai.get_cached_summary(key)
            if cached is not None:
                await db.ai.record_metric(
                    kind=kind, model=self.client.model, elapsed_ms=0, cache_hit=True
                )
                return cached

        try:
            text, elapsed = await self.client.generate(
                prompt, system=system, num_predict=self._SUMMARY_TOKENS
            )
        except OllamaError:
            log.warning("AI summary failed (kind=%s) — continuing without summary", kind)
            return None

        if db.ai is not None:
            await db.ai.save_summary(key, self.client.model, text)
            await db.ai.record_metric(
                kind=kind, model=self.client.model,
                elapsed_ms=int(elapsed * 1000), cache_hit=False,
            )
        return text

    async def summarize_cve(self, description: str) -> str | None:
        # Cap prompt length: long descriptions inflate CPU prompt-processing time
        # and can exceed the timeout. 1500 chars is ample for a 2-sentence summary.
        return await self._cached_generate(
            kind="cve", prompt=description[:1500], system=_CVE_SYSTEM
        )

    async def summarize_article(self, title: str, body: str) -> str | None:
        prompt = f"Title: {title}\n\n{body}"[:4000]
        return await self._cached_generate(kind="news", prompt=prompt, system=_ARTICLE_SYSTEM)

    async def risk_assessment(self, facts: str) -> str | None:
        """
        Cached AI risk narrative for a fused CVE (Phase 3).

        ``facts`` is a compact, deterministic summary of the enrichment signals
        so identical inputs hit the cache.
        """
        system = (
            "You are a senior threat-intelligence analyst. Given the facts, write "
            "a 2-3 sentence risk assessment and a clear remediation recommendation. "
            "Plain English, no preamble, no markdown."
        )
        return await self._cached_generate(kind="risk", prompt=facts, system=system)

    async def tip(self) -> str:
        """A fresh security tip (not cached — variety is desirable). Never raises."""
        try:
            text, elapsed = await self.client.generate(
                _TIP_PROMPT, system=_TIP_SYSTEM, num_predict=120
            )
        except OllamaError:
            return _TIP_FALLBACK
        if db.ai is not None:
            await db.ai.record_metric(
                kind="tip", model=self.client.model,
                elapsed_ms=int(elapsed * 1000), cache_hit=False,
            )
        return text or _TIP_FALLBACK


# Shared instance.
summarizer = Summarizer()
