"""Adapter interface and discovery (requirements.md R7.1, R7.3).

An adapter wraps an optional third-party runner. The contract is deliberately
small so the harness never depends on a runner being present:

- ``name`` / ``pinned_version``: identity recorded in provenance.
- ``available()``: True only when the backing package is importable. Import is
  guarded so a missing package never raises at import time.
- ``normalise(raw)``: map the runner's native output into finding-shaped dicts
  (partial records; the runner wiring fills provenance).

``discover_adapters()`` returns every registered adapter; callers filter by
``available()``. With all extras uninstalled, every adapter is simply skipped.
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AdapterResult:
    """A normalised finding fragment produced by an adapter."""

    scenario_id: str
    suite: str
    language: str
    verdict: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    data_access: list[dict[str, Any]] = field(default_factory=list)
    judges: dict[str, Any] = field(default_factory=dict)
    text_excerpt: str | None = None


class Adapter:
    """Base class for optional runner adapters."""

    name: str = "base"
    pinned_version: str = ""
    #: The import name of the backing package, guarded by ``available()``.
    module_name: str | None = None

    def available(self) -> bool:
        """True when the backing package can be imported (no import side effects)."""
        if self.module_name is None:
            return False
        try:
            return importlib.util.find_spec(self.module_name) is not None
        except (ImportError, ValueError, ModuleNotFoundError):
            return False

    def normalise(self, raw: Any) -> list[AdapterResult]:  # pragma: no cover - overridden
        raise NotImplementedError

    def version(self) -> str:
        """Return the installed version when available, else the pinned string."""
        if not self.available() or self.module_name is None:
            return self.pinned_version
        try:
            mod = __import__(self.module_name)
            return str(getattr(mod, "__version__", self.pinned_version))
        except Exception:  # noqa: BLE001 - optional third-party import may raise anything  # pragma: no cover
            return self.pinned_version


def discover_adapters() -> list[Adapter]:
    """Return one instance of every registered adapter (available or not)."""
    # Imported lazily so a broken optional import can never affect discovery.
    from .agentdojo_adapter import AgentDojoAdapter
    from .garak_adapter import GarakAdapter
    from .promptfoo_adapter import PromptfooAdapter
    from .pyrit_adapter import PyritAdapter

    return [GarakAdapter(), AgentDojoAdapter(), PyritAdapter(), PromptfooAdapter()]
