"""
Async wrapper around the local Ollama HTTP API.

- Always async (aiohttp).
- Times out after OLLAMA_TIMEOUT seconds.
- Retries 3 times with exponential backoff.
- Strips qwen3 ``<think>...</think>`` reasoning blocks from the output so users
  only see the final answer.
"""

from __future__ import annotations

import asyncio
import re
import time

import aiohttp

from config import config
from utils.logger import ai_log as log

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
_CLOSE_THINK_RE = re.compile(r"</think>", re.IGNORECASE)

# Global semaphore so at most OLLAMA_MAX_CONCURRENCY requests hit the CPU-only
# host at once. Created lazily on first use to bind to the running event loop.
_semaphore: asyncio.Semaphore | None = None


def _get_semaphore() -> asyncio.Semaphore:
    global _semaphore
    if _semaphore is None:
        _semaphore = asyncio.Semaphore(max(1, config.ollama_max_concurrency))
    return _semaphore


class OllamaError(Exception):
    """Raised when Ollama cannot be reached or fails after all retries."""


class OllamaTimeout(OllamaError):
    """Raised specifically when Ollama exceeds the configured timeout."""


def _clean(text: str) -> str:
    """
    Strip qwen3 chain-of-thought from the output.

    qwen3 (via Ollama /api/chat) emits its reasoning followed by a closing
    ``</think>`` marker and then the real answer — often *without* an opening
    ``<think>`` tag. We therefore:
      1. remove any complete ``<think>…</think>`` blocks, then
      2. if a lone ``</think>`` remains, keep only what follows the last one.
    """
    text = _THINK_RE.sub("", text)
    if _CLOSE_THINK_RE.search(text):
        text = _CLOSE_THINK_RE.split(text)[-1]
    return text.strip()


class OllamaClient:
    def __init__(
        self,
        host: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
        retries: int | None = None,
    ) -> None:
        self.host = (host or config.ollama_host).rstrip("/")
        self.model = model or config.ollama_model
        self.timeout = timeout or config.ollama_timeout
        self.retries = retries or config.ollama_retries

    async def generate(
        self,
        prompt: str,
        *,
        system: str | None = None,
        think: bool = False,
        num_predict: int = 400,
    ) -> tuple[str, float]:
        """
        Generate a completion.

        Returns ``(response_text, elapsed_seconds)``.
        Raises :class:`OllamaTimeout` / :class:`OllamaError` on failure.
        """
        # We use /api/chat (not /api/generate): it applies qwen3's chat template
        # and reliably terminates the reasoning block with a </think> marker
        # that _clean() strips, leaving just the answer.
        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            # Bound generation length: on a CPU-only host ~9 tok/s, so a large
            # num_predict alone can exceed the timeout. Callers pass a small value
            # for short summaries.
            "options": {"temperature": 0.4, "num_predict": num_predict},
            "think": think,
        }

        url = f"{self.host}/api/chat"
        last_err: Exception | None = None
        semaphore = _get_semaphore()

        for attempt in range(1, self.retries + 1):
            start = time.monotonic()
            try:
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                # Bound concurrency: never more than OLLAMA_MAX_CONCURRENCY in flight.
                async with semaphore:
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.post(url, json=payload) as resp:
                            resp.raise_for_status()
                            data = await resp.json()
                elapsed = time.monotonic() - start
                message = data.get("message", {}) or {}
                text = _clean(str(message.get("content", "")))
                if not text:
                    text = "_(the model returned an empty response)_"
                return text, elapsed
            except asyncio.TimeoutError:
                last_err = OllamaTimeout("Ollama request timed out.")
                log.warning(
                    "Ollama timeout (attempt %d/%d) after %.1fs",
                    attempt, self.retries, self.timeout,
                )
            except aiohttp.ClientError as exc:
                last_err = OllamaError(f"Ollama request failed: {exc}")
                log.warning(
                    "Ollama client error (attempt %d/%d): %s",
                    attempt, self.retries, exc,
                )

            if attempt < self.retries:
                await asyncio.sleep(2 ** attempt)  # 2s, 4s exponential backoff

        assert last_err is not None
        raise last_err

    async def ping(self) -> None:
        """Fast reachability check for /status (lists models, no generation)."""
        url = f"{self.host}/api/tags"
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                await resp.json()


# Shared instance.
ollama = OllamaClient()
