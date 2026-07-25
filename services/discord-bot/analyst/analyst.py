"""
AI Security Analyst — the orchestrator.

One natural-language entry point that classifies intent, plans a multi-step tool
sequence, executes it against the platform's own knowledge (assets → DB → RAG →
threat intel → CVE/KEV/EPSS → news → learning), and only then — if the question
is explanatory — synthesises a grounded answer with the LLM. Every interaction is
logged (intent, tools, sources, whether the LLM was used, latency).
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import discord

from database import db
from utils.logger import get_logger

from analyst.executor import executor
from analyst.intent_router import router
from analyst.memory import memory
from analyst.planner import build_plan
from analyst.response_formatter import Response, formatter

log = get_logger("analyst")


@dataclass
class AnalystResult:
    response: Response
    intent: str
    tools: list[str]
    sources: list[str]
    used_llm: bool
    elapsed_ms: int


class Analyst:
    async def ask(self, *, user_id: int, username: str, query: str) -> AnalystResult:
        start = time.monotonic()

        mem = memory.get(user_id)
        intent = await router.classify(query, mem)

        # Persist entities for follow-up pronoun resolution.
        ent = intent.entities
        memory.remember(user_id, cve=ent.get("cve_id"), product=ent.get("product"),
                        topic=ent.get("topic"))

        plan = build_plan(intent)
        log.info("intent=%s tools=%s (%s)", intent.name,
                 [s.tool for s in plan.steps], plan.rationale)

        ctx = await executor.run(plan)
        response = await formatter.format(ctx)

        used_llm = response.used_llm or intent.llm_classified or ("LLM" in ctx.sources_used)
        sources = list(ctx.sources_used)
        if used_llm and "LLM" not in sources:
            sources.append("LLM")

        elapsed_ms = int((time.monotonic() - start) * 1000)
        memory.add_turn(user_id, query, intent.name)

        # Log every AI interaction (best-effort — never break the reply).
        try:
            if db.analyst is not None:
                await db.analyst.log(
                    user_id=user_id, username=username, query=query,
                    intent=intent.name, tools=ctx.tools_used, sources=sources,
                    used_llm=used_llm, elapsed_ms=elapsed_ms)
        except Exception as exc:  # noqa: BLE001
            log.warning("analyst_log write failed: %s", exc)

        return AnalystResult(
            response=response, intent=intent.name, tools=ctx.tools_used,
            sources=sources, used_llm=used_llm, elapsed_ms=elapsed_ms)


# Shared instance.
analyst = Analyst()
