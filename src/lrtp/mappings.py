"""Load and expose the framework mapping tables (mappings/frameworks.yaml).

Provides the allowed id sets so the loader can reject invented or padded
technique ids (requirements.md R1.3, C3). System-instruction collection uses
AML.T0085.003 only; the retired "Extract LLM System Prompt" name is not accepted.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from lrtp import yamlmini

_MAPPINGS_PATH = Path(__file__).resolve().parents[2] / "mappings" / "frameworks.yaml"

# Retired ATLAS name that must never appear in a scenario mapping.
RETIRED_ATLAS_IDS: frozenset[str] = frozenset(
    {"Extract LLM System Prompt", "AML.T0085.000"}
)


@lru_cache(maxsize=1)
def load_frameworks(path: str | None = None) -> dict[str, Any]:
    p = Path(path) if path else _MAPPINGS_PATH
    return yamlmini.load(p.read_text(encoding="utf-8"))


def allowed_ids() -> dict[str, frozenset[str]]:
    fw = load_frameworks()
    return {
        "owasp_llm_2026": frozenset(fw.get("owasp_llm_2026", {}).keys()),
        "owasp_llm_2025_crosswalk": frozenset(fw.get("owasp_llm_2025_crosswalk", {}).keys()),
        "owasp_agentic_2026": frozenset(fw.get("owasp_agentic_2026", {}).keys()),
        "atlas_v2026_10": frozenset(fw.get("atlas_v2026_10", {}).keys()),
    }


def check_mapping_ids(mappings: dict[str, Any]) -> list[str]:
    """Return a list of errors for any mapping id outside the allowed set."""
    allowed = allowed_ids()
    errors: list[str] = []
    for key, ids in mappings.items():
        if key not in allowed:
            # Unknown mapping category; the JSON Schema already rejects these,
            # but guard here too in case the loader is used directly.
            errors.append(f"unknown mapping category '{key}'")
            continue
        for mid in ids or []:
            if mid in RETIRED_ATLAS_IDS:
                errors.append(
                    f"mapping '{key}' uses retired id '{mid}'; use AML.T0085.003"
                )
            elif mid not in allowed[key]:
                errors.append(f"mapping '{key}' has unknown id '{mid}' (not in v1 set)")
    return errors
