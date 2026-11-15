"""Optional OSS runner adapters (requirements.md R7).

Each adapter normalises a third-party runner's output into our finding schema.
All adapters are OPTIONAL: their backing package is import-guarded, and when it
is not installed the adapter reports ``available() is False`` and is skipped
cleanly. Default CI and ``make demo`` must pass with every extra UNINSTALLED.

Pinned extras (see pyproject ``[adapters]``):
  - garak 0.17.1
  - AgentDojo 0.1.35 (isolated; upstream API may change)
  - PyRIT 1.2.0
  - promptfoo 0.125.1 (Node package; re-check MIT licence at implementation)
"""

from .base import Adapter, AdapterResult, discover_adapters

__all__ = ["Adapter", "AdapterResult", "discover_adapters"]
