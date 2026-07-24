"""
Base agent for the multi-agent intelligence crew (Phase 7).

An Agent is a specialised role over the local model: a fixed system prompt + a
bounded generation. Agents are composed into a pipeline in ``crew.py`` where each
one's output becomes the next one's input (handoff). Recorded to ai_metrics.
"""

from __future__ import annotations

import time

from database import db
from utils.logger import get_logger
from utils.ollama_client import OllamaError, ollama

log = get_logger("agents")


class Agent:
    def __init__(self, name: str, emoji: str, system: str, *, max_tokens: int = 300) -> None:
        self.name = name
        self.emoji = emoji
        self.system = system
        self.max_tokens = max_tokens

    async def run(self, task: str) -> str:
        """Execute this agent's role on the given task/context. Never raises."""
        start = time.monotonic()
        try:
            text, _ = await ollama.generate(task, system=self.system, num_predict=self.max_tokens)
        except OllamaError:
            log.warning("Agent %s failed (Ollama unavailable)", self.name)
            return f"_({self.name} unavailable — AI offline)_"
        elapsed = time.monotonic() - start
        if db.ai is not None:
            await db.ai.record_metric(
                kind=f"agent:{self.name}", model=ollama.model,
                elapsed_ms=int(elapsed * 1000), cache_hit=False,
            )
        log.info("Agent %s produced %d chars in %.1fs", self.name, len(text), elapsed)
        return text.strip()
