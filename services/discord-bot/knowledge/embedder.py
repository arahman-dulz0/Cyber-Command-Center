"""
Embedding client (Ollama).

Wraps Ollama's /api/embeddings with the configured embedding model
(nomic-embed-text, 768-dim). Used to embed knowledge-base chunks at ingest time
and questions at query time.
"""

from __future__ import annotations

import asyncio

import aiohttp

from config import config
from utils.logger import get_logger

log = get_logger("knowledge.embed")


class Embedder:
    def __init__(self, host: str | None = None, model: str | None = None) -> None:
        self.host = (host or config.ollama_host).rstrip("/")
        self.model = model or config.embed_model

    async def embed(self, text: str) -> list[float] | None:
        """Embed a single string. Returns None on failure (caller degrades)."""
        url = f"{self.host}/api/embeddings"
        payload = {"model": self.model, "prompt": text}
        for attempt in range(1, 3):
            try:
                timeout = aiohttp.ClientTimeout(total=config.ollama_timeout)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(url, json=payload) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                vec = data.get("embedding")
                if vec:
                    return [float(x) for x in vec]
                return None
            except Exception as exc:  # noqa: BLE001
                log.warning("Embed failed (attempt %d): %s", attempt, exc)
                await asyncio.sleep(1.5 * attempt)
        return None

    async def embed_many(self, texts: list[str]) -> list[list[float] | None]:
        """Embed sequentially (ingest is a background job; keeps host load low)."""
        return [await self.embed(t) for t in texts]


# Shared instance.
embedder = Embedder()
