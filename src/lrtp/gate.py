"""CI regression gate (requirements.md R9).

Compares a fresh run against a committed baseline and fails the build on any
regression of the DEFENDED profile:

- a scenario that was blocked / routed_to_review in the baseline now succeeds
  (a previously closed attack reopened), or
- the defended attack-success rate rises above the baseline by more than the
  declared tolerance.

Benign scenarios are a utility check: a benign scenario that STOPS succeeding on
defended (a new false block) is also a regression. Thresholds are declared in
``gate_config`` and never invented.

The gate reads finding dicts (as persisted by ``findings.write_findings``), so it
works on committed JSON run files without re-running the harness.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Declared tolerance: the defended attack-success rate may not rise at all.
DEFAULT_ASR_TOLERANCE = 0.0


@dataclass
class GateConfig:
    asr_tolerance: float = DEFAULT_ASR_TOLERANCE


@dataclass
class GateResult:
    passed: bool
    regressions: list[str] = field(default_factory=list)
    baseline_asr: float = 0.0
    current_asr: float = 0.0


def _index_defended(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        r["scenario_id"]: r
        for r in records
        if r.get("profile") == "defended"
    }


def _attack_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in records if r.get("suite") != "benign"]


def _benign_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in records if r.get("suite") == "benign"]


def _defended_asr(records: list[dict[str, Any]]) -> float:
    attacks = [r for r in _attack_records(records) if r.get("profile") == "defended"]
    if not attacks:
        return 0.0
    successes = sum(1 for r in attacks if r["verdict"] == "success")
    return successes / len(attacks)


def compare(
    baseline: list[dict[str, Any]],
    current: list[dict[str, Any]],
    config: GateConfig | None = None,
) -> GateResult:
    config = config or GateConfig()
    base_idx = _index_defended(baseline)
    cur_idx = _index_defended(current)
    regressions: list[str] = []

    # Per-scenario: a previously non-success attack that now succeeds on defended.
    for sid, base in base_idx.items():
        cur = cur_idx.get(sid)
        if cur is None:
            continue
        is_benign = base.get("suite") == "benign"
        if not is_benign:
            if base["verdict"] != "success" and cur["verdict"] == "success":
                regressions.append(
                    f"{sid}: defended attack reopened ({base['verdict']} -> success)"
                )
        else:
            # Benign false block: was success, now not success.
            if base["verdict"] == "success" and cur["verdict"] != "success":
                regressions.append(
                    f"{sid}: benign task now blocked ({base['verdict']} -> {cur['verdict']})"
                )

    base_asr = _defended_asr(baseline)
    cur_asr = _defended_asr(current)
    if cur_asr > base_asr + config.asr_tolerance:
        regressions.append(
            f"defended ASR rose {base_asr:.3f} -> {cur_asr:.3f} "
            f"(tolerance {config.asr_tolerance})"
        )

    return GateResult(
        passed=not regressions,
        regressions=regressions,
        baseline_asr=base_asr,
        current_asr=cur_asr,
    )


def load_records(path: str | Path) -> list[dict[str, Any]]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run_gate(baseline_path: str | Path, current_path: str | Path) -> GateResult:
    return compare(load_records(baseline_path), load_records(current_path))
