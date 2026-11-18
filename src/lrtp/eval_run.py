"""Run the full scenario set against the demo agent (both profiles).

Shared by the regression gate (baseline generation) and ``make demo``. Produces
a list of :class:`Finding` and can write a single timestamped JSON run file with
shared provenance (git SHA + timestamp). Deterministic and offline.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from lrtp.findings import Finding, make_provenance, write_findings
from lrtp.loader import load_scenario_file
from lrtp.runner import RUNNER_ID, run_demo_scenario
from lrtp.targets.demo_agent.backend import BACKEND_ID

REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_DIR = REPO_ROOT / "scenarios"
RESULTS_DIR = REPO_ROOT / "eval" / "results"


def _version() -> str:
    import lrtp

    return lrtp.__version__


def run_all(scenarios_dir: str | Path = SCENARIOS_DIR) -> list[Finding]:
    """Run every scenario against both declared profiles on the demo agent."""
    provenance = make_provenance(
        runner_versions={RUNNER_ID: _version()}, model_backend=BACKEND_ID, repo=REPO_ROOT
    )
    findings: list[Finding] = []
    for path in sorted(Path(scenarios_dir).rglob("*.yaml")):
        scenario = load_scenario_file(path)
        for profile in scenario.get("profiles", []):
            findings.append(run_demo_scenario(scenario, profile, provenance=provenance))
    return findings


def records(findings: list[Finding]) -> list[dict[str, Any]]:
    return [f.to_dict() for f in findings]


def write_run(findings: list[Finding], out_path: str | Path) -> Path:
    return write_findings(findings, out_path)


def timestamped_run_name(findings: list[Finding]) -> str:
    """Build a deterministic-per-run file name from the shared provenance."""
    ts = findings[0].provenance.timestamp if findings and findings[0].provenance else "unknown"
    sha = findings[0].provenance.git_sha[:12] if findings and findings[0].provenance else "unknown"
    safe_ts = ts.replace(":", "").replace("-", "")
    return f"run-{safe_ts}-{sha}.json"
