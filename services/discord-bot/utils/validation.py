"""
Input validation & sanitisation helpers.

User-supplied text (lab keywords, skill tags, machine names) is normalised to a
safe character set and length-bounded before it touches the database or is echoed
back into embeds. Discord slash-command types already constrain ints/choices;
this covers the free-text fields.
"""

from __future__ import annotations

import re

# Allow letters, digits, space and a few technical separators only.
_KEYWORD_RE = re.compile(r"[^a-z0-9 .+_/#-]")
_WS_RE = re.compile(r"\s+")


def clean_keyword(value: str, *, maxlen: int = 40) -> str:
    """Lowercase, strip disallowed characters, collapse whitespace, bound length."""
    value = _WS_RE.sub(" ", value.strip().lower())
    value = _KEYWORD_RE.sub("", value)
    return value.strip()[:maxlen].strip()


def clean_text(value: str | None, *, maxlen: int = 500) -> str | None:
    """Trim and length-bound a free-text field (notes), preserving readable chars."""
    if value is None:
        return None
    value = value.strip()
    return value[:maxlen] if value else None


def clean_skills(raw: str, *, maxitems: int = 15) -> list[str]:
    """Parse a comma-separated skills string into a clean, de-duplicated list."""
    out: list[str] = []
    for part in raw.split(","):
        k = clean_keyword(part, maxlen=30)
        if k and k not in out:
            out.append(k)
    return out[:maxitems]
