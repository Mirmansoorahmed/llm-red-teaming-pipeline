"""Phase 4 — v1 attack suites in DE+EN plus benign hard negatives (R5)."""

from collections import defaultdict
from pathlib import Path

import pytest

from lrtp.loader import load_scenario_file
from lrtp.runner import run_demo_scenario

SCENARIOS_DIR = Path(__file__).resolve().parents[1] / "scenarios"
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


def _all_scenario_files():
    return sorted(SCENARIOS_DIR.rglob("*.yaml"))


def test_every_scenario_file_is_valid():
    files = _all_scenario_files()
    assert files, "no scenario files found"
    for path in files:
        load_scenario_file(path)  # raises on invalid


def test_each_suite_has_at_least_one_de_and_one_en():
    langs = defaultdict(set)
    for path in _all_scenario_files():
        s = load_scenario_file(path)
        langs[s["suite"]].add(s["language"])
    for suite in SUITES:
        assert "de" in langs[suite], f"{suite} missing a DE scenario"
        assert "en" in langs[suite], f"{suite} missing an EN scenario"


@pytest.mark.parametrize("path", _all_scenario_files(), ids=lambda p: p.stem)
def test_scenario_meets_expected_outcome_per_profile(path):
    scenario = load_scenario_file(path)
    for profile, expected in scenario["expected"].items():
        finding = run_demo_scenario(scenario, profile)
        # routed_to_review is acceptable wherever 'blocked' is expected and vice
        # versa for a defended non-success; v1 demo agent uses blocked/success.
        if expected == "success":
            assert finding.verdict == "success", (
                f"{scenario['id']} [{profile}] expected success, got {finding.verdict}"
            )
        else:
            assert finding.verdict in ("blocked", "routed_to_review"), (
                f"{scenario['id']} [{profile}] expected {expected}, got {finding.verdict}"
            )


def test_benign_tasks_succeed_on_defended():
    benign = [load_scenario_file(p) for p in (SCENARIOS_DIR / "benign").glob("*.yaml")]
    assert benign
    for s in benign:
        finding = run_demo_scenario(s, "defended")
        assert finding.verdict == "success", f"benign {s['id']} must complete on defended"


def test_not_block_everything_on_defended():
    """A defended profile that blocks EVERY scenario is a failed design (R5.2)."""
    successes = 0
    for path in _all_scenario_files():
        s = load_scenario_file(path)
        if "defended" in s["profiles"] and run_demo_scenario(s, "defended").verdict == "success":
            successes += 1
    assert successes > 0, "defended profile blocked everything (benign must pass)"
