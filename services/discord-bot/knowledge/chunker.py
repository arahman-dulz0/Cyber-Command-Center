"""
Text chunking for the knowledge base.

Splits documents into overlapping chunks on paragraph/sentence boundaries so
each embedded chunk is self-contained and retrievable.
"""

from __future__ import annotations

import re

from config import config

_WS_RE = re.compile(r"[ \t]+")
_PARA_RE = re.compile(r"\n\s*\n")


def _normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _WS_RE.sub(" ", text)
    # Collapse 3+ newlines to a paragraph break.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(
    text: str,
    *,
    size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    """
    Split ``text`` into ~``size``-char chunks with ``overlap`` char overlap,
    preferring paragraph boundaries and never splitting mid-word.
    """
    size = size or config.kb_chunk_size
    overlap = overlap or config.kb_chunk_overlap
    text = _normalize(text)
    if not text:
        return []
    if len(text) <= size:
        return [text]

    # Build chunks paragraph-by-paragraph, packing until the size cap.
    paragraphs = _PARA_RE.split(text)
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(para) > size:
            # Hard-split an oversized paragraph on word boundaries.
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(_hard_split(para, size))
            continue
        if len(current) + len(para) + 2 <= size:
            current = f"{current}\n\n{para}" if current else para
        else:
            if current:
                chunks.append(current)
            current = para
    if current:
        chunks.append(current)

    return _apply_overlap(chunks, overlap)


def _hard_split(text: str, size: int) -> list[str]:
    words = text.split(" ")
    out: list[str] = []
    cur = ""
    for w in words:
        if len(cur) + len(w) + 1 <= size:
            cur = f"{cur} {w}" if cur else w
        else:
            if cur:
                out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def _apply_overlap(chunks: list[str], overlap: int) -> list[str]:
    if overlap <= 0 or len(chunks) <= 1:
        return chunks
    out = [chunks[0]]
    for i in range(1, len(chunks)):
        tail = chunks[i - 1][-overlap:]
        out.append(f"{tail} {chunks[i]}")
    return out
