"""RAG tool handler — reuse the knowledge-base retriever (source #3 in priority)."""

from __future__ import annotations

from typing import Any

from knowledge.retriever import retriever


async def search(query: str) -> dict[str, Any]:
    """Retrieve grounding context from the ingested knowledge base."""
    ctx = await retriever.build_context(query)
    return {
        "text": ctx.text,
        "sources": ctx.sources,
        "grounded": ctx.grounded,
        "best_similarity": ctx.best_similarity,
    }
