"""Phase 7 — CI regression gate (R9)."""

import copy
import subprocess
import sys
from pathlib import Path

from lrtp.gate import compare, load_records, run_gate

REPO = Path(__file__).resolve().parents[1]
BASELINE = REPO / "eval" / "results" / "baseline.json"
REGRESSION = REPO / "fixtures" / "regression" / "reopened_defended.json"


def test_gate_passes_baseline_against_itself():
    result = run_gate(BASELINE, BASELINE)
    assert result.passed is True
    assert result.regressions == []


def test_gate_fails_on_regression_fixture():
    result = run_gate(BASELINE, REGRESSION)
    assert result.passed is False
    assert any("reopened" in r for r in result.regressions)


def test_gate_detects_benign_false_block():
    baseline = load_records(BASELINE)
    current = copy.deepcopy(baseline)
    for r in current:
        if r["suite"] == "benign" and r["profile"] == "defended":
            r["verdict"] = "blocked"
            break
    result = compare(baseline, current)
    assert result.passed is False
    assert any("benign" in reg for reg in result.regressions)


def test_gate_detects_asr_rise():
    baseline = load_records(BASELINE)
    current = copy.deepcopy(baseline)
    # Flip one defended attack to success -> ASR rises above tolerance 0.0.
    for r in current:
        if r["profile"] == "defended" and r["suite"] != "benign" and r["verdict"] != "success":
            r["verdict"] = "success"
            break
    result = compare(baseline, current)
    assert result.passed is False


def test_cli_gate_fails_closed_on_regression():
    import os

    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO / "src")
    proc = subprocess.run(
        [sys.executable, "-m", "lrtp.cli", "gate",
         "--baseline", str(BASELINE), "--current", str(REGRESSION)],
        capture_output=True, text=True, env=env, cwd=str(REPO), check=False,
    )
    assert proc.returncode == 1
    assert "GATE FAIL" in proc.stderr


def test_cli_gate_passes_on_fresh_run_matching_baseline():
    """A fresh suite run must still pass against the committed baseline."""
    import os

    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO / "src")
    proc = subprocess.run(
        [sys.executable, "-m", "lrtp.cli", "gate", "--baseline", str(BASELINE)],
        capture_output=True, text=True, env=env, cwd=str(REPO), check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "GATE PASS" in proc.stdout
