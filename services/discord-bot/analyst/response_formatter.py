"""
Response formatter — turns gathered evidence into rich Discord embeds.

Structured intents (briefings, patch plans, asset correlation, posture, tickets)
are rendered *deterministically* from the data the executor gathered — no LLM, so
no hallucination. Explanatory intents (explain a CVE / topic / general question)
run a grounded LLM synthesis as the final step, constrained to the platform data
already retrieved. Either way the LLM is the last resort, never the first source.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import discord

from utils import embeds
from utils.embeds import nvd_view, nvd_url
from utils.logger import get_logger
from utils.ollama_client import OllamaError, ollama

from analyst.executor import Context

log = get_logger("analyst.formatter")

_MAX_FIELD = 1024


@dataclass
class Response:
    embeds: list[discord.Embed] = field(default_factory=list)
    view: discord.ui.View | None = None
    used_llm: bool = False
    extra_files: list = field(default_factory=list)


def _bar(n: int, total: int, width: int = 10) -> str:
    if total <= 0:
        return "▱" * width
    filled = round(width * min(n, total) / total)
    return "▰" * filled + "▱" * (width - filled)


def _risk_emoji(label: str | None) -> str:
    return {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(
        (label or "").upper(), "🔵")


def _cve_line(c: dict) -> str:
    label = c.get("priority_label") or c.get("severity") or "?"
    score = c.get("priority_score")
    flags = []
    if c.get("kev"):
        flags.append("KEV")
    if (c.get("github_poc_count") or 0) or (c.get("exploitdb_count") or 0):
        flags.append("PoC")
    tag = f" · {' '.join(flags)}" if flags else ""
    score_txt = f" `{score}/100`" if score is not None else ""
    return f"{_risk_emoji(label)} **[{c['cve_id']}]({nvd_url(c['cve_id'])})**{score_txt}{tag}"


class ResponseFormatter:
    async def format(self, ctx: Context) -> Response:
        name = ctx.intent.name
        handler = getattr(self, f"_fmt_{name.lower()}", None)
        try:
            if handler is not None:
                return await handler(ctx)
        except Exception as exc:  # noqa: BLE001 - never crash the reply on a format bug
            log.exception("formatter %s failed: %s", name, exc)
        # Fallback: synthesise or a plain notice.
        if ctx.mode == "synthesis":
            return await self._synthesise(ctx)
        return Response([embeds.base_embed(
            title="🤖 AI Analyst",
            description="I couldn't find platform data for that. Try `/help` for what I can do.",
        )])

    # ---------------------------------------------------------------- briefings

    async def _fmt_overnight(self, ctx: Context) -> Response:
        counts = ctx.get("cves.counts") or {}
        top = ctx.get("cves.top") or []
        kev = ctx.get("cves.kev") or []
        affected = (ctx.get("assets.affected") or {}).get("assets") or {}
        news = ctx.get("news.recent") or []
        tickets = ctx.get("tickets.open") or []

        e = embeds.base_embed(title="🌅 SOC Morning Brief", color=embeds.DARK_BLUE,
                              description="Everything that moved on the threat landscape recently.")
        e.add_field(
            name="📊 Last 24h",
            value=(f"**{counts.get('cves', 0)}** new CVEs · **{counts.get('critical', 0)}** critical · "
                   f"**{counts.get('kev', 0)}** KEV · **{counts.get('news', 0)}** news"),
            inline=False)
        if top:
            e.add_field(name="🎯 Top Priorities",
                        value="\n".join(_cve_line(c) for c in top[:5])[:_MAX_FIELD], inline=False)
        if kev:
            e.add_field(name="🚨 Actively Exploited (KEV)",
                        value="\n".join(_cve_line(c) for c in kev[:5])[:_MAX_FIELD], inline=False)
        if affected:
            lines = [f"⚠️ **{a}** — {len(v)} CVE(s)" for a, v in list(affected.items())[:6]]
            e.add_field(name="🖥️ Your Exposed Assets", value="\n".join(lines)[:_MAX_FIELD], inline=False)
        if news:
            e.add_field(name="📰 Headlines",
                        value="\n".join(f"• [{n['title'][:80]}]({n['url']})" for n in news[:4])[:_MAX_FIELD],
                        inline=False)
        if tickets:
            e.add_field(name="🎫 Open Tickets", value=f"**{len(tickets)}** awaiting action", inline=False)
        return Response([e])

    async def _fmt_patch_priorities(self, ctx: Context) -> Response:
        top = ctx.get("cves.top") or []
        kev_ids = {c["cve_id"] for c in (ctx.get("cves.kev") or [])}
        affected = (ctx.get("assets.affected") or {}).get("assets") or {}
        # Which CVEs touch a lab asset?
        asset_by_cve: dict[str, list[str]] = {}
        for asset, cve_list in affected.items():
            for c in cve_list:
                asset_by_cve.setdefault(c["cve_id"], []).append(asset)

        # Rank: lab-exposed + KEV first, then by priority score.
        def rank(c: dict) -> tuple:
            return (c["cve_id"] in asset_by_cve, c["cve_id"] in kev_ids, c.get("priority_score") or 0)

        ranked = sorted(top, key=rank, reverse=True)
        e = embeds.base_embed(title="🩹 Patch Priorities — What To Fix First",
                              color=embeds.HIGH,
                              description="Ranked by lab exposure, active exploitation, then CCC priority.")
        if not ranked:
            e.description = "No high-priority CVEs in the recent window. ✅"
            return Response([e])
        for i, c in enumerate(ranked[:8], 1):
            bits = [_cve_line(c)]
            if c["cve_id"] in kev_ids:
                bits.append("🔥 actively exploited")
            hit = asset_by_cve.get(c["cve_id"])
            if hit:
                bits.append(f"💥 affects **{', '.join(hit[:3])}**")
            desc = (c.get("description") or "").strip()
            body = "  ".join(bits)
            if desc:
                body += f"\n{desc[:160]}"
            e.add_field(name=f"#{i}", value=body[:_MAX_FIELD], inline=False)
        return Response([e])

    # ------------------------------------------------------------ asset correl.

    async def _fmt_affected_assets(self, ctx: Context) -> Response:
        # Case A: whole-lab correlation.
        whole = ctx.get("assets.affected")
        if whole is not None:
            assets_map = whole.get("assets") or {}
            e = embeds.base_embed(title="🖥️ Lab Exposure — Assets vs. Threats",
                                  color=embeds.HIGH if assets_map else embeds.LOW)
            if not assets_map:
                note = whole.get("note") or "No CVEs currently correlate to your lab inventory. ✅"
                e.description = note
                return Response([e])
            e.description = f"**{len(assets_map)}** of {whole.get('total_assets', 0)} assets have known exposure."
            for asset, cve_list in list(assets_map.items())[:10]:
                top = cve_list[:5]
                val = "\n".join(_cve_line(c) for c in top)
                if len(cve_list) > 5:
                    val += f"\n…and {len(cve_list) - 5} more"
                e.add_field(name=f"⚠️ {asset} ({len(cve_list)})", value=val[:_MAX_FIELD], inline=False)
            return Response([e])

        # Case B: a specific CVE.
        by_cve = ctx.get("assets.by_cve")
        if by_cve is not None:
            cve = by_cve.get("cve") or {}
            matched = by_cve.get("matched") or []
            cid = cve.get("cve_id", "CVE")
            if not by_cve.get("has_inventory"):
                e = embeds.base_embed(title=f"🖥️ {cid} vs. your lab", color=embeds.INFO,
                                      description="No lab inventory yet — add assets with `/lab add` to enable correlation.")
                return Response([e], view=nvd_view(cid) if cve else None)
            color = embeds.CRITICAL if matched else embeds.LOW
            e = embeds.base_embed(title=f"🖥️ {cid} vs. your lab", color=color)
            if matched:
                e.description = f"🔴 **Affects {len(matched)} asset(s):** {', '.join(matched)}"
            else:
                e.description = "🟢 None of your lab assets appear to be affected."
            if cve.get("description"):
                e.add_field(name="Description", value=cve["description"][:700], inline=False)
            return Response([e], view=nvd_view(cid) if cve else None)

        # Case C: a product.
        by_prod = ctx.get("assets.by_product")
        if by_prod is not None:
            prod = by_prod.get("product", "product")
            hits = by_prod.get("cves") or []
            in_lab = by_prod.get("in_lab")
            e = embeds.base_embed(title=f"🔎 {prod.title()} — exposure", color=embeds.HIGH if hits else embeds.LOW)
            e.description = (f"{'🔴 In your lab inventory. ' if in_lab else '⚪ Not in your lab inventory. '}"
                            f"Found **{len(hits)}** recent related CVE(s).")
            if hits:
                e.add_field(name="Related CVEs",
                            value="\n".join(_cve_line(c) for c in hits[:8])[:_MAX_FIELD], inline=False)
            return Response([e])

        return Response([embeds.base_embed(title="🖥️ Lab Exposure",
                                           description="No correlation data available.")])

    # ------------------------------------------------------------- intel lists

    async def _cve_list_embed(self, title: str, color: int, cves: list[dict],
                              empty: str, affected: dict | None = None) -> Response:
        e = embeds.base_embed(title=title, color=color)
        if not cves:
            e.description = empty
            return Response([e])
        exposed = set()
        if affected:
            for cl in affected.values():
                exposed |= {c["cve_id"] for c in cl}
        lines = []
        for c in cves[:12]:
            line = _cve_line(c)
            if c["cve_id"] in exposed:
                line += " · 💥 **in your lab**"
            lines.append(line)
        e.description = "\n".join(lines)[:4000]
        return Response([e])

    async def _fmt_critical_cves(self, ctx: Context) -> Response:
        affected = (ctx.get("assets.affected") or {}).get("assets")
        return await self._cve_list_embed(
            "🔴 Recent Critical CVEs", embeds.CRITICAL, ctx.get("cves.critical") or [],
            "No critical CVEs in the recent window. ✅", affected)

    async def _fmt_kev(self, ctx: Context) -> Response:
        affected = (ctx.get("assets.affected") or {}).get("assets")
        return await self._cve_list_embed(
            "🚨 Known Exploited Vulnerabilities (CISA KEV)", embeds.CRITICAL,
            ctx.get("cves.kev") or [], "No KEV entries in the recent window.", affected)

    async def _fmt_pocs(self, ctx: Context) -> Response:
        return await self._cve_list_embed(
            "💣 CVEs With Public Exploits", embeds.HIGH, ctx.get("cves.pocs") or [],
            "No CVEs with public PoCs in the recent window.")

    # ---------------------------------------------------------------- news

    async def _fmt_news(self, ctx: Context) -> Response:
        return self._news_embed("📰 Latest Security News", ctx.get("news.recent") or [])

    async def _fmt_ransomware(self, ctx: Context) -> Response:
        return self._news_embed("🦠 Ransomware Watch", ctx.get("news.ransomware") or [],
                                empty="No ransomware-tagged news in the recent feed.")

    def _news_embed(self, title: str, news: list[dict], empty: str = "No recent news.") -> Response:
        e = embeds.base_embed(title=title, color=embeds.INFO)
        if not news:
            e.description = empty
            return Response([e])
        e.description = "\n\n".join(
            f"**[{n['title'][:120]}]({n['url']})**\n{n.get('source', '')}" for n in news[:6])[:4000]
        return Response([e])

    # ---------------------------------------------------------------- tickets

    async def _fmt_tickets(self, ctx: Context) -> Response:
        tickets = ctx.get("tickets.open") or []
        e = embeds.base_embed(title="🎫 Open Remediation Tickets",
                              color=embeds.HIGH if tickets else embeds.LOW)
        if not tickets:
            e.description = "No open tickets. ✅"
            return Response([e])
        e.description = f"**{len(tickets)}** open ticket(s)."
        for t in tickets[:10]:
            assets = ", ".join(t.get("assets") or []) or "—"
            e.add_field(
                name=f"#{t['id']} · {t['cve_id']} (P{t.get('priority', 0)})",
                value=f"Assets: {assets}", inline=False)
        return Response([e])

    # ---------------------------------------------------------------- posture

    async def _fmt_posture(self, ctx: Context) -> Response:
        return self._status_embed(ctx, title="🛡️ Security Posture")

    async def _fmt_status(self, ctx: Context) -> Response:
        return self._status_embed(ctx, title="📟 Platform Status")

    def _status_embed(self, ctx: Context, *, title: str) -> Response:
        s = ctx.get("system.status") or {}
        color = {"critical": embeds.CRITICAL, "high": embeds.HIGH,
                 "low": embeds.LOW}.get(s.get("color_key"), embeds.INFO)
        e = embeds.base_embed(title=title, color=color)
        level = s.get("threat_level", "UNKNOWN")
        e.add_field(name="Threat Level", value=f"**{level}**", inline=True)
        e.add_field(name="Max Priority (24h)", value=f"{s.get('max_priority_24h', 0)}/100", inline=True)
        e.add_field(name="Open Tickets", value=str(s.get("open_tickets", 0)), inline=True)
        e.add_field(name="CVEs (24h)", value=str(s.get("cves_24h", 0)), inline=True)
        e.add_field(name="Critical (24h)", value=str(s.get("critical_24h", 0)), inline=True)
        e.add_field(name="KEV (24h)", value=str(s.get("kev_24h", 0)), inline=True)
        e.add_field(name="Lab Assets", value=str(s.get("lab_assets", 0)), inline=True)
        e.add_field(name="KB Documents", value=str(s.get("kb_documents", 0)), inline=True)
        e.add_field(name="Total CVEs Tracked", value=str(s.get("total_cves", 0)), inline=True)
        return Response([e])

    # ---------------------------------------------------------------- learning

    async def _fmt_learning(self, ctx: Context) -> Response:
        plan = ctx.get("learning.plan") or {}
        embed = plan.get("embed")
        if embed is None:
            embed = embeds.base_embed(title="🎯 Learning Plan",
                                      description="No learning data yet. Log sessions with `/practiced`.")
        focus = plan.get("focus")
        if focus:
            embed.insert_field_at(
                0, name="🔥 Today's Threat-Driven Focus",
                value=f"**{focus.title()}** — trending in {plan.get('focus_hits', 0)} recent critical CVE(s).",
                inline=False)
        return Response([embed], used_llm=True)  # recommender uses the LLM internally

    # ---------------------------------------------------------------- reports

    async def _fmt_exec_report(self, ctx: Context) -> Response:
        from cogs.reports import build_report_embed

        data = ctx.get("reports.executive") or {}
        report = data.get("report")
        if report is None:
            return Response([embeds.error_embed("The report crew did not return a result.")])
        return Response([build_report_embed(report)], used_llm=True)

    async def _fmt_tech_report(self, ctx: Context) -> Response:
        data = ctx.get("reports.technical") or {}
        top = data.get("top") or []
        counts = data.get("counts") or {}
        affected = (data.get("affected") or {}).get("assets") or {}
        e = embeds.base_embed(title="🧪 Technical Intelligence Report", color=embeds.DARK_BLUE)
        e.add_field(name="Window (24h)",
                    value=(f"Critical: **{counts.get('critical', 0)}** · "
                           f"KEV: **{counts.get('kev', 0)}** · Exploited: **{counts.get('exploited', 0)}**"),
                    inline=False)
        if top:
            for c in top[:6]:
                head = f"{_risk_emoji(c.get('priority_label'))} {c['cve_id']}"
                meta = (f"CVSS {c.get('cvss_score', '?')} · EPSS "
                        f"{(c.get('epss') or 0) * 100:.0f}% · Priority {c.get('priority_score', '?')}/100"
                        f"{' · KEV' if c.get('kev') else ''}")
                desc = (c.get("description") or "")[:300]
                e.add_field(name=head, value=f"{meta}\n{desc}"[:_MAX_FIELD], inline=False)
        if affected:
            e.add_field(name="💥 Affected Lab Assets",
                        value=", ".join(f"{a} ({len(v)})" for a, v in list(affected.items())[:8]),
                        inline=False)
        return Response([e])

    # ---------------------------------------------------------- explain / LLM

    async def _fmt_explain_cve(self, ctx: Context) -> Response:
        cve = ctx.get("cves.get")
        if not cve:
            cid = ctx.intent.entities.get("cve_id", "that CVE")
            return Response([embeds.error_embed(
                f"I couldn't find **{cid}** in the platform or via NVD.")])

        cid = cve["cve_id"]
        e = embeds.base_embed(
            title=f"{_risk_emoji(cve.get('priority_label'))} {cid}",
            color=embeds.priority_color(cve.get("priority_label")) if cve.get("priority_label")
            else embeds.severity_color(cve.get("severity")),
            url=nvd_url(cid))
        # Fusion scorecard.
        e.add_field(name="🎯 CCC Priority",
                    value=f"**{cve.get('priority_score', '—')}/100**", inline=True)
        e.add_field(name="CVSS",
                    value=f"**{cve.get('cvss_score', 'N/A')}** ({cve.get('severity', '?')})", inline=True)
        epss = cve.get("epss")
        e.add_field(name="EPSS", value=f"{epss * 100:.0f}%" if epss is not None else "n/a", inline=True)
        e.add_field(name="Known Exploited",
                    value=("✅ YES" + (" 🦠" if cve.get("kev_ransomware") else "")) if cve.get("kev") else "❌ No",
                    inline=True)
        pocs = (cve.get("github_poc_count") or 0) + (cve.get("exploitdb_count") or 0)
        e.add_field(name="Public Exploits", value=f"{pocs}" if pocs else "none", inline=True)
        e.add_field(name="Vendor Patch",
                    value="Available" if cve.get("patch_available") else "Unknown", inline=True)
        if cve.get("description"):
            e.add_field(name="Description", value=cve["description"][:900], inline=False)

        # Lab impact (asset correlation).
        by_cve = ctx.get("assets.by_cve") or {}
        matched = by_cve.get("matched") or []
        if by_cve.get("has_inventory"):
            e.add_field(
                name="🖥️ Impact on Your Lab",
                value=(f"🔴 Affects: **{', '.join(matched)}**" if matched
                       else "🟢 No lab assets appear affected."),
                inline=False)

        # Grounded AI explanation (LLM last, constrained to gathered data).
        rag = ctx.get("rag.search") or {}
        explanation, used = await self._llm_explain_cve(cve, matched, rag)
        if explanation:
            e.add_field(name="🤖 AI Analyst", value=explanation[:_MAX_FIELD], inline=False)
        return Response([e], view=nvd_view(cid), used_llm=used)

    async def _fmt_explain_topic(self, ctx: Context) -> Response:
        return await self._synthesise(ctx)

    async def _fmt_general(self, ctx: Context) -> Response:
        return await self._synthesise(ctx)

    async def _llm_explain_cve(self, cve: dict, matched: list[str], rag: dict):
        if cve.get("ai_risk"):
            # Fusion already produced a risk analysis — prefer it, no extra LLM call.
            return cve["ai_risk"][:1000], False
        context = (
            f"CVE: {cve['cve_id']}\n"
            f"CVSS: {cve.get('cvss_score')} ({cve.get('severity')})\n"
            f"EPSS: {cve.get('epss')}\nKEV: {cve.get('kev')}\n"
            f"Description: {(cve.get('description') or '')[:800]}\n"
        )
        if rag.get("grounded") and rag.get("text"):
            context += f"\nKnowledge base:\n{rag['text'][:800]}\n"
        if matched:
            context += f"\nAffected lab assets: {', '.join(matched)}\n"
        system = (
            "You are a senior security analyst. Using ONLY the context provided, "
            "explain this CVE to an operator in 3-4 sentences: what it is, why it "
            "matters, and what to do. Do not invent facts not in the context."
        )
        try:
            text, _ = await ollama.generate(context, system=system, num_predict=220)
            return text.strip(), True
        except OllamaError:
            return None, False

    async def _synthesise(self, ctx: Context) -> Response:
        """Grounded LLM answer for explanatory / general questions (LLM = last step)."""
        q = ctx.intent.entities.get("topic") or ""
        rag = ctx.get("rag.search") or {}
        by_prod = ctx.get("assets.by_product") or {}

        context_parts = []
        sources = []
        if rag.get("text"):
            context_parts.append(f"Knowledge base:\n{rag['text'][:1200]}")
            sources = rag.get("sources") or []
        if by_prod.get("cves"):
            context_parts.append(
                "Related CVEs: " + ", ".join(c["cve_id"] for c in by_prod["cves"][:6]))

        context = "\n\n".join(context_parts)
        grounded = bool(rag.get("grounded"))
        if grounded:
            system = (
                "You are the Cyber Command Center security analyst. Answer the "
                "operator's question using PRIMARILY the provided platform context. "
                "Be concise (4-6 sentences), practical, and accurate."
            )
            prompt = f"Question: {q}\n\nContext:\n{context}"
        else:
            # No platform grounding found — answer from expertise but flag it.
            system = (
                "You are the Cyber Command Center security analyst. The platform "
                "knowledge base had no strong match, so answer this cybersecurity "
                "question from general expertise, concisely (4-6 sentences). If it is "
                "not a security question, say so briefly."
            )
            prompt = q

        e = embeds.base_embed(title="🤖 AI Security Analyst", color=embeds.INFO)
        try:
            text, _ = await ollama.generate(prompt, system=system, num_predict=320)
            used = True
        except OllamaError:
            text = ("I couldn't reach the local model just now, and I don't have "
                    "platform data cached for that question. Try again shortly.")
            used = False
        e.description = text.strip()[:4000] or "No answer produced."
        if grounded and sources:
            e.add_field(name="📚 Sources", value=", ".join(sources[:5])[:_MAX_FIELD], inline=False)
        elif not grounded:
            e.set_footer(text="Cyber Command Center • general knowledge (no KB match)")
        return Response([e], used_llm=used)


# Shared instance.
formatter = ResponseFormatter()
