"""Phase 8 — demo run file + report-data generation, fail-closed (R10)."""

import json
import re
from pathlib import Path

import pytest

from lrtp.demo import main as demo_main
from lrtp.eval_run import run_all
from lrtp.report import (
    ReportError,
    judge_breakdown,
    latest_run_file,
    per_suite_asr,
    render_report_data,
    summarise,
)

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "eval" / "results"


def test_demo_writes_timestamped_run_file(tmp_path):
    rc = demo_main([str(tmp_path)])
    assert rc == 0
    runs = list(tmp_path.glob("run-*.json"))
    assert len(runs) == 1
    records = json.loads(runs[0].read_text())
    assert len(records) == 32  # 16 scenarios x 2 profiles
    # provenance present on every record
    assert all(r["provenance"]["git_sha"] for r in records)


def test_summarise_matches_expected_shape():
    findings = run_all()
    s = summarise([f.to_dict() for f in findings])
    assert s["scenario_count"] == 16
    assert s["de"] == 8 and s["en"] == 8
    assert 0.0 <= s["vulnerable_asr"] <= 1.0
    assert s["benign_false_block_rate"] == 0.0  # benign must complete on defended


def test_report_fails_closed_on_empty_run():
    with pytest.raises(ReportError):
        summarise([])


def test_report_fails_closed_when_no_run_file(tmp_path):
    with pytest.raises(ReportError):
        latest_run_file(tmp_path)


def test_per_suite_and_judge_breakdown():
    findings = [f.to_dict() for f in run_all()]
    per_suite = per_suite_asr(findings)
    assert "benign" not in per_suite
    assert per_suite["approval_binding"]["vulnerable"]["total"] == 2
    judges = judge_breakdown(findings)
    # successful attacks are detected by tool-call or canary judges
    assert sum(judges.values()) >= 1


def _committed_run_files():
    return sorted(RESULTS.glob("run-*.json"))


def test_committed_run_file_exists_and_report_matches():
    """At least one committed run file is real and renders a report (C2)."""
    runs = _committed_run_files()
    assert runs, "no committed run-*.json file under eval/results/"
    for run_path in runs:
        content = render_report_data(run_path)
        assert "# Report data" in content
        assert run_path.name in content
        records = json.loads(run_path.read_text())
        sha = records[0]["provenance"]["git_sha"]
        assert re.fullmatch(r"[0-9a-f]{7,40}|unknown", sha)


def test_readme_references_a_committed_run_file():
    """README must cite a committed run file that actually exists (no free numbers)."""
    readme = (REPO / "README.md").read_text()
    runs = {p.name for p in _committed_run_files()}
    assert runs, "no committed run file"
    assert any(name in readme for name in runs), "README cites no committed run file"
