"""Scenario loader with fail-closed validation (requirements.md R1).

Loads a scenario from YAML (restricted subset), validates it against the
committed JSON Schema, and rejects any mapping id outside the v1 allowed set.
Validation failures raise :class:`ScenarioError` and the scenario is not run.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from lrtp import yamlmini
from lrtp.mappings import check_mapping_ids
from lrtp.schema import SchemaError, validate

_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas" / "scenario.schema.json"


class ScenarioError(ValueError):
    """Raised when a scenario is invalid; the scenario must not run."""


@lru_cache(maxsize=1)
def _scenario_schema() -> dict[str, Any]:
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def load_scenario_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Validate an already-parsed scenario dict; return it on success."""
    try:
        validate(data, _scenario_schema())
    except SchemaError as exc:
        raise ScenarioError(f"schema validation failed: {exc}") from exc

    mapping_errors = check_mapping_ids(data.get("mappings", {}))
    if mapping_errors:
        raise ScenarioError("; ".join(mapping_errors))

    # Cross-field sanity: every profile named in `expected` must be declared.
    declared = set(data.get("profiles", []))
    for profile in data.get("expected", {}):
        if profile not in declared:
            raise ScenarioError(
                f"expected outcome for profile '{profile}' not in declared profiles {sorted(declared)}"
            )
    return data


def load_scenario_text(text: str) -> dict[str, Any]:
    """Parse YAML text then validate."""
    try:
        parsed = yamlmini.load(text)
    except yamlmini.YamlError as exc:
        raise ScenarioError(f"YAML parse failed: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ScenarioError("scenario must be a mapping at the top level")
    return load_scenario_dict(parsed)


def load_scenario_file(path: str | Path) -> dict[str, Any]:
    """Load and validate a scenario YAML file."""
    p = Path(path)
    return load_scenario_text(p.read_text(encoding="utf-8"))


def load_suite_dir(root: str | Path) -> list[dict[str, Any]]:
    """Load and validate every ``*.yaml`` scenario under ``root`` (recursive)."""
    root = Path(root)
    scenarios: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.yaml")):
        scenarios.append(load_scenario_file(path))
    return scenarios
