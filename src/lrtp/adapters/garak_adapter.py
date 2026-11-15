"""garak adapter (optional extra, pinned 0.17.1).

garak emits JSONL report rows. We map each row into an :class:`AdapterResult`,
treating a failed probe (garak ``passed is False``) as an attack ``success`` in
our schema. The garak package itself is never imported at module load; it is
only probed via ``available()``.
"""

from __future__ import annotations

from typing import Any

from .base import Adapter, AdapterResult


class GarakAdapter(Adapter):
    name = "garak"
    pinned_version = "0.17.1"
    module_name = "garak"

    def normalise(self, raw: list[dict[str, Any]]) -> list[AdapterResult]:
        results: list[AdapterResult] = []
        for row in raw or []:
            if row.get("entry_type") not in (None, "eval", "attempt"):
                continue
            passed = row.get("passed", row.get("status") == "pass")
            results.append(
                AdapterResult(
                    scenario_id=str(row.get("probe", row.get("uuid", "garak-unknown"))),
                    suite=str(row.get("suite", "jailbreak")),
                    language=str(row.get("language", "en")),
                    verdict="blocked" if passed else "success",
                    judges={"garak": "pass" if passed else "fail"},
                    text_excerpt=row.get("output"),
                )
            )
        return results
