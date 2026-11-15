"""AgentDojo adapter (optional extra, pinned 0.1.35).

AgentDojo reports per-task results including whether an injection task succeeded.
We map a successful injection (``injection_successful``) to an attack ``success``.
The upstream API may change between releases, so the package is pinned and only
probed via ``available()``; it is never imported at module load.
"""

from __future__ import annotations

from typing import Any

from .base import Adapter, AdapterResult


class AgentDojoAdapter(Adapter):
    name = "agentdojo"
    pinned_version = "0.1.35"
    module_name = "agentdojo"

    def normalise(self, raw: list[dict[str, Any]]) -> list[AdapterResult]:
        results: list[AdapterResult] = []
        for row in raw or []:
            injected = bool(row.get("injection_successful", row.get("attack_success", False)))
            results.append(
                AdapterResult(
                    scenario_id=str(row.get("task_id", "agentdojo-unknown")),
                    suite=str(row.get("suite", "prompt_injection_indirect")),
                    language=str(row.get("language", "en")),
                    verdict="success" if injected else "blocked",
                    tool_calls=[
                        {
                            "name": str(tc.get("function", tc.get("name", "unknown"))),
                            "args_hash": str(tc.get("args_hash", "")),
                            "authorised": bool(tc.get("authorised", False)),
                            "approved": bool(tc.get("approved", False)),
                            "binding_ok": bool(tc.get("binding_ok", True)),
                        }
                        for tc in row.get("tool_calls", [])
                    ],
                    judges={"agentdojo": "injected" if injected else "clean"},
                )
            )
        return results
