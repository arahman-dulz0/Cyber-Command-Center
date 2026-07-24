"""
Knowledge-base retriever.

Embeds a query, ranks all stored chunks by cosine similarity (computed in Python
with numpy — no pgvector), and returns the top-k with their source documents.
Also builds the grounded-context block used by RAG /ask.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from config import config
from database import db
from knowledge.embedder import embedder
from utils.logger import get_logger

log = get_logger("knowledge.retriever")


@dataclass
class RetrievedChunk:
    chunk_id: int
    content: str
    title: str
    source_type: str
    source_ref: str | None
    similarity: float


@dataclass
class RagContext:
    text: str                       # concatenated context block for the prompt
    sources: list[str]              # distinct source document titles, ranked
    best_similarity: float
    chunks: list[RetrievedChunk]

    @property
    def grounded(self) -> bool:
        return self.best_similarity >= config.kb_min_similarity


class Retriever:
    async def search(self, query: str, k: int | None = None) -> list[RetrievedChunk]:
        k = k or config.kb_top_k
        qvec = await embedder.embed(query)
        if qvec is None:
            return []

        vectors = await db.kb.all_chunk_vectors()
        if not vectors:
            return []

        q = np.asarray(qvec, dtype=np.float32)
        q_norm = np.linalg.norm(q) or 1.0

        ids = [v["id"] for v in vectors]
        mat = np.asarray([v["embedding"] for v in vectors], dtype=np.float32)
        norms = np.linalg.norm(mat, axis=1)
        norms[norms == 0] = 1.0
        sims = (mat @ q) / (norms * q_norm)

        top_idx = np.argsort(-sims)[:k]
        top_ids = [ids[i] for i in top_idx]
        sim_by_id = {ids[i]: float(sims[i]) for i in top_idx}

        rows = await db.kb.fetch_chunks(top_ids)
        out = [
            RetrievedChunk(
                chunk_id=r["id"], content=r["content"], title=r["title"],
                source_type=r["source_type"], source_ref=r.get("source_ref"),
                similarity=sim_by_id.get(r["id"], 0.0),
            )
            for r in rows
        ]
        out.sort(key=lambda c: c.similarity, reverse=True)
        return out

    async def build_context(self, query: str) -> RagContext:
        chunks = await self.search(query)
        if not chunks:
            return RagContext(text="", sources=[], best_similarity=0.0, chunks=[])

        blocks, sources = [], []
        for c in chunks:
            blocks.append(f"[Source: {c.title}]\n{c.content}")
            if c.title not in sources:
                sources.append(c.title)
        return RagContext(
            text="\n\n---\n\n".join(blocks),
            sources=sources,
            best_similarity=chunks[0].similarity,
            chunks=chunks,
        )


# Shared instance.
retriever = Retriever()
