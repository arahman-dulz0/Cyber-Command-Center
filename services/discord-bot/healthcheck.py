"""
Container healthcheck for the Discord bot.

The bot writes a heartbeat file every ~30s from its event loop (see
bot.py::heartbeat_task). This script passes only if that heartbeat is fresh,
which proves the asyncio loop is actually running — not just that the process
exists. Exit 0 = healthy, 1 = unhealthy.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

HEARTBEAT = Path("/app/logs/heartbeat")
MAX_AGE_SECONDS = 180

try:
    ts = int(HEARTBEAT.read_text().strip())
except Exception:
    sys.exit(1)

sys.exit(0 if (time.time() - ts) < MAX_AGE_SECONDS else 1)
