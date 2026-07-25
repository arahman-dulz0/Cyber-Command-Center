"""
AI Security Analyst package.

A single natural-language interface over the whole platform. Import the shared
``analyst`` orchestrator to answer a query:

    from analyst import analyst
    result = await analyst.ask(user_id=..., username=..., query="...")
"""

from analyst.analyst import Analyst, AnalystResult, analyst

__all__ = ["Analyst", "AnalystResult", "analyst"]
