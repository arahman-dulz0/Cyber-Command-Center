"""
Planner — turns a classified intent into an ordered plan of tool calls.

This is where multi-step reasoning lives: e.g. "what should I patch today?"
expands to (fetch top-priority CVEs → fetch KEV → correlate with lab assets →
pull open tickets), so the formatter can rank recommendations across *all* that
platform data rather than a single query. The plan is declarative — the executor
runs it — which keeps the reasoning transparent and loggable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from analyst.intent_router import Intent


@dataclass
class ToolCall:
    tool: str
    kwargs: dict[str, Any] = field(default_factory=dict)
    optional: bool = False  # a failure here degrades gracefully, doesn't abort


@dataclass
class Plan:
    intent: Intent
    steps: list[ToolCall]
    # Where the final answer comes from: "deterministic" builds embeds straight
    # from gathered data; "synthesis" runs a grounded LLM pass as the last step.
    mode: str = "deterministic"
    rationale: str = ""


def build_plan(intent: Intent) -> Plan:
    name = intent.name
    ent = intent.entities

    if name == "OVERNIGHT":
        return Plan(intent, [
            ToolCall("cves.counts"),
            ToolCall("cves.top", {"limit": 5}),
            ToolCall("cves.kev", {"limit": 5}, optional=True),
            ToolCall("assets.affected", optional=True),
            ToolCall("news.recent", {"limit": 4}, optional=True),
            ToolCall("tickets.open", {"limit": 5}, optional=True),
        ], rationale="Aggregate overnight threat activity across CVEs, KEV, assets, news, tickets.")

    if name == "PATCH_PRIORITIES":
        return Plan(intent, [
            ToolCall("cves.top", {"limit": 10}),
            ToolCall("cves.kev", {"limit": 10}, optional=True),
            ToolCall("assets.affected", optional=True),
            ToolCall("tickets.open", {"limit": 10}, optional=True),
        ], rationale="Rank what to patch by CCC priority, KEV status, and lab exposure.")

    if name == "AFFECTED_ASSETS":
        if ent.get("cve_id"):
            return Plan(intent, [ToolCall("assets.by_cve", {"cve_id": ent["cve_id"]})],
                        rationale="Correlate a specific CVE against lab inventory.")
        if ent.get("product"):
            return Plan(intent, [ToolCall("assets.by_product", {"product": ent["product"]})],
                        rationale="Correlate a product against lab inventory + recent CVEs.")
        return Plan(intent, [ToolCall("assets.affected")],
                    rationale="Correlate the whole lab inventory against threat intel.")

    if name == "CRITICAL_CVES":
        return Plan(intent, [ToolCall("cves.critical", {"hours": 48}),
                             ToolCall("assets.affected", optional=True)],
                    rationale="List recent critical CVEs and flag lab exposure.")

    if name == "KEV":
        return Plan(intent, [ToolCall("cves.kev", {"limit": 10}),
                             ToolCall("assets.affected", optional=True)],
                    rationale="Show actively-exploited CVEs and lab exposure.")

    if name == "POCS":
        return Plan(intent, [ToolCall("cves.pocs", {"limit": 10})],
                    rationale="List CVEs with public exploit code.")

    if name == "RANSOMWARE":
        return Plan(intent, [ToolCall("news.ransomware", {"limit": 6})],
                    rationale="Surface recent ransomware activity.")

    if name == "NEWS":
        return Plan(intent, [ToolCall("news.recent", {"limit": 6})],
                    rationale="Show recent security headlines.")

    if name == "TICKETS":
        return Plan(intent, [ToolCall("tickets.open", {"limit": 15})],
                    rationale="List open remediation tickets.")

    if name in ("POSTURE", "STATUS"):
        return Plan(intent, [ToolCall("system.status")],
                    rationale="Report live platform health + threat posture.")

    if name == "LEARNING":
        return Plan(intent, [ToolCall("learning.plan")],
                    rationale="Build today's learning plan from threats + practice history.")

    if name == "EXEC_REPORT":
        return Plan(intent, [ToolCall("reports.executive")],
                    rationale="Generate an executive intelligence report.")

    if name == "TECH_REPORT":
        return Plan(intent, [ToolCall("reports.technical")],
                    rationale="Generate a technical intelligence report.")

    if name == "EXPLAIN_CVE":
        return Plan(intent, [
            ToolCall("cves.get", {"cve_id": ent.get("cve_id")}),
            ToolCall("assets.by_cve", {"cve_id": ent.get("cve_id")}, optional=True),
            ToolCall("rag.search", {"query": ent.get("cve_id") or ""}, optional=True),
        ], mode="synthesis",
           rationale="Gather CVE fusion data + lab impact + KB context, then synthesise an explanation.")

    if name == "EXPLAIN_TOPIC":
        q = ent.get("topic") or ""
        steps = [ToolCall("rag.search", {"query": q})]
        if ent.get("product"):
            steps.append(ToolCall("assets.by_product", {"product": ent["product"]}, optional=True))
        return Plan(intent, steps, mode="synthesis",
                    rationale="Retrieve KB grounding for the topic, then synthesise an explanation.")

    # GENERAL — still try the knowledge base first before the LLM.
    q = ent.get("topic") or ""
    return Plan(intent, [ToolCall("rag.search", {"query": q}, optional=True)],
                mode="synthesis",
                rationale="Search platform knowledge first, then synthesise a grounded answer.")
