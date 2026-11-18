"""promptfoo adapter (optional extra, pinned 0.125.1).

promptfoo is a Node package, not a Python import, so availability is detected by
looking for the ``promptfoo`` CLI on PATH (never by executing it). We map a
failed assertion (promptfoo ``success is False``) to an attack ``success`` in
our schema.

Licence note: promptfoo is documented as MIT OSS as of 0.125.1 (OpenAI announced
an acquisition on 9 Mar 2026). Re-check the licence and install path before
shipping any run that uses it.
"""

from __future__ import annotations

import shutil
from typing import Any

from .base import Adapter, AdapterResult


class PromptfooAdapter(Adapter):
    name = "promptfoo"
    pinned_version = "0.125.1"
    module_name = None  # Node package, not importable from Python

    def available(self) -> bool:
        """True only when the promptfoo CLI is on PATH (no execution)."""
        return shutil.which("promptfoo") is not None

    def normalise(self, raw: dict[str, Any] | list[dict[str, Any]]) -> list[AdapterResult]:
        rows = raw.get("results", raw) if isinstance(raw, dict) else raw
        results: list[AdapterResult] = []
        for row in rows or []:
            passed = bool(row.get("success", True))
            results.append(
                AdapterResult(
                    scenario_id=str(row.get("id", row.get("testId", "promptfoo-unknown"))),
                    suite=str(row.get("suite", "prompt_injection_direct")),
                    language=str(row.get("language", "en")),
                    verdict="blocked" if passed else "success",
                    judges={"promptfoo": "pass" if passed else "fail"},
                    text_excerpt=row.get("response"),
                )
            )
        return results
