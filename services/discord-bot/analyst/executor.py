"""
Executor — runs a plan's tool calls and gathers the results.

Every tool hits the platform's own data (assets, DB, RAG, threat intel) before
the LLM is ever consulted. Failures degrade gracefully: an optional step that
errors is logged and skipped, and the analyst answers with whatever platform
data it *did* gather rather than aborting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from analyst import tool_registry
from analyst.intent_router import Intent
from analyst.planner import Plan
from utils.logger import get_logger

log = get_logger("analyst.executor")


def _has_data(result: Any) -> bool:
    """Did a tool actually return usable platform data?"""
    if result is None:
        return False
    if isinstance(result, dict):
        # Treat {"assets": {}, ...} / empty-lists-only payloads as no data.
        meaningful = [v for k, v in result.items()
                      if k not in ("note", "has_inventory", "in_lab", "grounded",
                                   "best_similarity", "total_assets", "product")]
        return any(bool(v) for v in meaningful) if meaningful else bool(result)
    return bool(result)


@dataclass
class Context:
    """The gathered evidence a plan produced, ready for formatting."""
    intent: Intent
    mode: str
    data: dict[str, Any] = field(default_factory=dict)
    tools_used: list[str] = field(default_factory=list)
    sources_used: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def get(self, tool: str, default: Any = None) -> Any:
        return self.data.get(tool, default)

    def add_source(self, src: str) -> None:
        if src not in self.sources_used:
            self.sources_used.append(src)


class Executor:
    async def run(self, plan: Plan) -> Context:
        ctx = Context(intent=plan.intent, mode=plan.mode)

        for step in plan.steps:
            try:
                tool = tool_registry.get(step.tool)
            except KeyError:
                log.warning("unknown tool in plan: %s", step.tool)
                continue

            try:
                result = await tool(**step.kwargs)
            except Exception as exc:  # noqa: BLE001 - graceful degradation is the point
                log.warning("tool %s failed: %s", step.tool, exc)
                ctx.errors.append(f"{step.tool}: {exc}")
                if step.optional:
                    continue
                # A required tool failed — record and move on; formatter copes.
                ctx.data[step.tool] = None
                continue

            ctx.data[step.tool] = result
            if step.tool not in ctx.tools_used:
                ctx.tools_used.append(step.tool)
            if _has_data(result):
                ctx.add_source(tool.source)

        return ctx


# Shared instance.
executor = Executor()
