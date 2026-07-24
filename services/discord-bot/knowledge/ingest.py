"""
Knowledge-base ingestion.

Parse a document (PDF / Markdown / text) into plain text, chunk it, embed each
chunk, and persist to kb_documents/kb_chunks. De-duplicates on a content hash so
the same file is never ingested twice.
"""

from __future__ import annotations

import hashlib
import io

from config import config
from database import db
from knowledge.chunker import chunk_text
from knowledge.embedder import embedder
from utils.logger import get_logger

log = get_logger("knowledge.ingest")

_TEXT_EXTS = {".md", ".markdown", ".txt", ".text", ".log", ".rst"}


class IngestResult:
    def __init__(self, *, ok: bool, reason: str, doc_id: int | None = None, chunks: int = 0) -> None:
        self.ok = ok
        self.reason = reason
        self.doc_id = doc_id
        self.chunks = chunks


def extract_text(filename: str, data: bytes) -> tuple[str, str]:
    """Return (text, source_type) for a file's bytes."""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        from pypdf import PdfReader  # imported lazily so non-PDF paths don't need it

        reader = PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages), "pdf"
    # Everything else: decode as UTF-8 text.
    ext = "." + lower.rsplit(".", 1)[-1] if "." in lower else ""
    source_type = "md" if ext in {".md", ".markdown"} else "txt"
    return data.decode("utf-8", errors="replace"), source_type


async def ingest_document(
    *, title: str, text: str, source_type: str, source_ref: str | None, added_by: str | None
) -> IngestResult:
    """Chunk, embed, and store a document. Skips duplicates by content hash."""
    text = (text or "").strip()
    if not text:
        return IngestResult(ok=False, reason="empty document")

    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if await db.kb.document_exists(content_hash):
        return IngestResult(ok=False, reason="already ingested (duplicate)")

    doc_id = await db.kb.add_document(
        title=title, source_type=source_type, source_ref=source_ref,
        content_hash=content_hash, added_by=added_by,
    )
    if doc_id is None:  # lost a race on the unique hash
        return IngestResult(ok=False, reason="already ingested (duplicate)")

    chunks = chunk_text(text)
    stored = 0
    for i, chunk in enumerate(chunks):
        vec = await embedder.embed(chunk)
        if vec is None:
            log.warning("Skipping chunk %d of '%s' — embedding failed", i, title)
            continue
        await db.kb.add_chunk(document_id=doc_id, chunk_index=i, content=chunk, embedding=vec)
        stored += 1

    await db.kb.set_chunk_count(doc_id, stored)
    log.info("Ingested '%s' (%s): %d/%d chunks", title, source_type, stored, len(chunks))
    return IngestResult(ok=(stored > 0), reason="ok" if stored else "no chunks embedded",
                        doc_id=doc_id, chunks=stored)


async def ingest_file_bytes(filename: str, data: bytes, *, added_by: str | None) -> IngestResult:
    """Convenience wrapper: extract text from raw file bytes, then ingest."""
    try:
        text, source_type = extract_text(filename, data)
    except Exception as exc:  # noqa: BLE001
        return IngestResult(ok=False, reason=f"parse error: {exc}")
    return await ingest_document(
        title=filename, text=text, source_type=source_type,
        source_ref=filename, added_by=added_by,
    )


def is_supported(filename: str) -> bool:
    lower = filename.lower()
    return lower.endswith(".pdf") or any(lower.endswith(e) for e in _TEXT_EXTS)
