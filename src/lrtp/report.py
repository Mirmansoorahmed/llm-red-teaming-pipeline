"""Report-data generation (requirements.md R10.2, modified Phase 8 — no PDF).

Reads a COMMITTED run file (list of finding dicts) and computes the real numbers
for docs/REPORT-DATA.md and the README. Every number here comes from the run
file; nothing is invented. If asked to summarise an empty run, it fails closed.

This module produces plain-text / Markdown tables only. It does NOT build a PDF;
the report author assembles the final document separately.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SUITES = (
    "prompt_injection_direct",
    "prompt_injection_indirect",
    "jailbreak",
    "exfil_via_tools",
    "excessive_agency",
    "hidden_context_leak",
    "approval_binding",
    "benign",
)


class ReportError(ValueError):
    """Raised when required data for the report is missing (fail closed)."""


def _attacks(records: list[dict], profile: str) -> list[dict]:
    return [r for r in records if r["profile"] == profile and r["suite"] != "benign"]


def _asr(records: list[dict], profile: str) -> float:
    attacks = _attacks(records, profile)
    if not attacks:
        return 0.0
    return sum(1 for r in attacks if r["verdict"] == "success") / len(attacks)


def summarise(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        raise ReportError("no records: cannot summarise an empty run (numbers must be measured)")

    scenario_ids = {r["scenario_id"] for r in records}
    langs = {sid: None for sid in scenario_ids}
    for r in records:
        langs[r["scenario_id"]] = r["language"]
    de = sum(1 for v in langs.values() if v == "de")
    en = sum(1 for v in langs.values() if v == "en")

    benign_def = [r for r in records if r["suite"] == "benign" and r["profile"] == "defended"]
    benign_false_block = (
        sum(1 for r in benign_def if r["verdict"] != "success") / len(benign_def)
        if benign_def
        else 0.0
    )

    return {
        "scenario_count": len(scenario_ids),
        "de": de,
        "en": en,
        "record_count": len(records),
        "vulnerable_asr": _asr(records, "vulnerable"),
        "defended_asr": _asr(records, "defended"),
        "benign_false_block_rate": benign_false_block,
    }


def per_suite_asr(records: list[dict]) -> dict[str, dict[str, Any]]:
    """Per-suite attack-success counts for vulnerable vs defended."""
    out: dict[str, dict[str, Any]] = {}
    for suite in SUITES:
        if suite == "benign":
            continue
        row = {}
        for profile in ("vulnerable", "defended"):
            recs = [r for r in records if r["suite"] == suite and r["profile"] == profile]
            total = len(recs)
            succ = sum(1 for r in recs if r["verdict"] == "success")
            row[profile] = {"success": succ, "total": total,
                            "asr": (succ / total if total else 0.0)}
        out[suite] = row
    return out


def judge_breakdown(records: list[dict]) -> dict[str, int]:
    """Count which authoritative judge fired across successful attack findings."""
    counts: Counter[str] = Counter()
    for r in records:
        if r["suite"] == "benign" or r["verdict"] != "success":
            continue
        auth = (r.get("judges") or {}).get("authoritative") or {}
        for judge, fired in auth.items():
            if fired:
                counts[judge] += 1
    return dict(counts)


def language_counts(records: list[dict]) -> dict[str, int]:
    by_lang: dict[str, set] = defaultdict(set)
    for r in records:
        by_lang[r["language"]].add(r["scenario_id"])
    return {lang: len(ids) for lang, ids in by_lang.items()}


def latest_run_file(results_dir: str | Path) -> Path:
    """Return the newest run-*.json under results_dir, else fail closed."""
    results_dir = Path(results_dir)
    runs = sorted(results_dir.glob("run-*.json"))
    if not runs:
        raise ReportError(f"no committed run file (run-*.json) under {results_dir}")
    return runs[-1]


def load_run(path: str | Path) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def render_report_data(run_path: str | Path) -> str:
    """Render docs/REPORT-DATA.md content from a committed run file."""
    run_path = Path(run_path)
    records = load_run(run_path)
    s = summarise(records)
    per_suite = per_suite_asr(records)
    judges = judge_breakdown(records)
    run_name = run_path.name
    prov = records[0].get("provenance", {})

    lines: list[str] = []
    lines.append("# Report data")
    lines.append("")
    lines.append(
        "Every number below comes from one committed run file. Nothing is invented; "
        "if a run file is missing, the report generator fails closed."
    )
    lines.append("")
    lines.append(f"- Run file: `eval/results/{run_name}`")
    lines.append(f"- git SHA: `{prov.get('git_sha', 'unknown')}`")
    lines.append(f"- Timestamp (UTC): `{prov.get('timestamp', 'unknown')}`")
    lines.append(f"- Model backend: `{prov.get('model_backend', 'unknown')}`")
    lines.append(f"- Scenarios: {s['scenario_count']} (DE {s['de']} / EN {s['en']})")
    lines.append(f"- Finding records: {s['record_count']} (scenarios x profiles)")
    lines.append("")

    lines.append("## Headline")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Vulnerable attack-success rate (ASR) | {s['vulnerable_asr']:.3f} |")
    lines.append(f"| Defended attack-success rate (ASR) | {s['defended_asr']:.3f} |")
    lines.append(f"| Benign false-block rate (defended) | {s['benign_false_block_rate']:.3f} |")
    lines.append("")

    lines.append("## Per-suite attack success (vulnerable vs defended)")
    lines.append("")
    lines.append("| Suite | Vulnerable success/total | Defended success/total |")
    lines.append("|---|---|---|")
    for suite, row in per_suite.items():
        v, d = row["vulnerable"], row["defended"]
        lines.append(
            f"| {suite} | {v['success']}/{v['total']} | {d['success']}/{d['total']} |"
        )
    lines.append("")

    lines.append("## Judge breakdown (which judge fired on successful attacks)")
    lines.append("")
    if judges:
        lines.append("| Judge | Count |")
        lines.append("|---|---|")
        for judge, count in sorted(judges.items()):
            lines.append(f"| {judge} | {count} |")
    else:
        lines.append("No successful attacks recorded in this run.")
    lines.append("")

    lines.append("## Language coverage")
    lines.append("")
    lc = language_counts(records)
    lines.append("| Language | Scenarios |")
    lines.append("|---|---|")
    for lang in ("de", "en"):
        lines.append(f"| {lang} | {lc.get(lang, 0)} |")
    lines.append("")
    return "\n".join(lines) + "\n"
