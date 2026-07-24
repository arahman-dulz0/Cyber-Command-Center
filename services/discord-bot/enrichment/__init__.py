"""Threat-Intelligence Fusion layer (Phase 3).

Correlates EPSS, CISA KEV, ExploitDB, and GitHub PoCs into a single prioritised
Enrichment per CVE. Add a new source by writing a client and referencing it in
``fusion.FusionEngine`` — no other wiring required.
"""

from enrichment.base import Enrichment
from enrichment.fusion import FusionEngine, fusion

__all__ = ["Enrichment", "FusionEngine", "fusion"]
