"""Repository for the RAG knowledge base (``kb_documents`` + ``kb_chunks``)."""

from __future__ import annotations

from typing import Any

from repositories.base import BaseRepository


class KBRepository(BaseRepository):
    # --- Documents -------------------------------------------------------
    async def document_exists(self, content_hash: str) -> bool:
        val = await self.pool.fetchval(
            "SELECT 1 FROM kb_documents WHERE content_hash = $1;", content_hash
        )
        return val is not None

    async def add_document(
        self, *, title: str, source_type: str, source_ref: str | None,
        content_hash: str, added_by: str | None,
    ) -> int | None:
        """Insert a document; return its id, or None if it already exists (dup hash)."""
        return await self.pool.fetchval(
            """
            INSERT INTO kb_documents (title, source_type, source_ref, content_hash, added_by)
            VALUES ($1,$2,$3,$4,$5)
            ON CONFLICT (content_hash) DO NOTHING
            RETURNING id;
            """,
            title, source_type, source_ref, content_hash, added_by,
        )

    async def set_chunk_count(self, document_id: int, n: int) -> None:
        await self.pool.execute(
            "UPDATE kb_documents SET chunk_count = $2 WHERE id = $1;", document_id, n
        )

    async def list_documents(self, limit: int = 25) -> list[dict[str, Any]]:
        rows = await self.pool.fetch(
            "SELECT * FROM kb_documents ORDER BY created_at DESC LIMIT $1;", limit
        )
        return [dict(r) for r in rows]

    async def total_documents(self) -> int:
        return await self.pool.fetchval("SELECT COUNT(*) FROM kb_documents;")

    async def total_chunks(self) -> int:
        return await self.pool.fetchval("SELECT COUNT(*) FROM kb_chunks;")

    # --- Chunks ----------------------------------------------------------
    async def add_chunk(
        self, *, document_id: int, chunk_index: int, content: str, embedding: list[float]
    ) -> None:
        await self.pool.execute(
            """
            INSERT INTO kb_chunks (document_id, chunk_index, content, embedding)
            VALUES ($1,$2,$3,$4);
            """,
            document_id, chunk_index, content, embedding,
        )

    async def all_chunk_vectors(self) -> list[dict[str, Any]]:
        """(id, embedding) for every chunk — used to rank by cosine similarity."""
        rows = await self.pool.fetch("SELECT id, embedding FROM kb_chunks;")
        return [{"id": r["id"], "embedding": r["embedding"]} for r in rows]

    async def fetch_chunks(self, ids: list[int]) -> list[dict[str, Any]]:
        """Full chunk content + document title for the given chunk ids."""
        if not ids:
            return []
        rows = await self.pool.fetch(
            """
            SELECT c.id, c.content, c.chunk_index, d.title, d.source_type, d.source_ref
            FROM kb_chunks c JOIN kb_documents d ON d.id = c.document_id
            WHERE c.id = ANY($1::int[]);
            """,
            ids,
        )
        return [dict(r) for r in rows]
