"""PyRIT adapter (optional extra, pinned 1.2.0).

PyRIT drives adaptive / multi-turn attacks and scores each conversation. We map
a scorer verdict of "attack achieved its objective" to an attack ``success``.
PyRIT is heavy and optional; it is never imported at module load and is only
probed via ``available()``.
"""

from __future__ import annotations

from typing import Any

from .base import Adapter, AdapterResult


class PyritAdapter(Adapter):
    name = "pyrit"
    pinned_version = "1.2.0"
    module_name = "pyrit"

    def normalise(self, raw: list[dict[str, Any]]) -> list[AdapterResult]:
        results: list[AdapterResult] = []
        for row in raw or []:
            achieved = bool(row.get("objective_achieved", row.get("score", 0) >= 1))
            results.append(
                AdapterResult(
                    scenario_id=str(row.get("conversation_id", "pyrit-unknown")),
                    suite=str(row.get("suite", "jailbreak")),
                    language=str(row.get("language", "en")),
                    verdict="success" if achieved else "blocked",
                    judges={"pyrit": "achieved" if achieved else "not_achieved"},
                    text_excerpt=row.get("last_response"),
                )
            )
        return results
