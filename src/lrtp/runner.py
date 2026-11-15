"""Eval runner — scenario x target x profile (requirements.md R2.1, R4).

Enforces the target allowlist BEFORE any execution, drives the scripted/mock
demo-agent backend from a scenario's declared steps, builds a trace, judges it,
and returns a :class:`Finding`. The runner is deterministic and offline.

Scenario step scripts: a scenario may carry an ``x_steps`` block (an
implementation detail, not part of the public DSL schema's required fields) that
lists the deterministic tool steps the scripted backend should execute per
profile. When absent, the runner falls back to a minimal step derived from the
success criteria so a scenario is still runnable.
"""

from __future__ import annotations

from typing import Any

from lrtp.allowlist import check_target
from lrtp.findings import DataAccess, Finding, Provenance, ToolCall, make_provenance
from lrtp.judges import judge_scenario
from lrtp.mappings import load_frameworks
from lrtp.targets.demo_agent.backend import BACKEND_ID, run_script
from lrtp.trace import Trace, from_agent_result

RUNNER_ID = "lrtp"


def _steps_for(scenario: dict[str, Any], profile: str) -> list[dict[str, Any]]:
    """Return the deterministic step script for a profile.

    Precedence: an explicit per-profile ``x_steps`` block, else a single step
    derived from the success criteria (hidden-context probe, or the disallowed
    tool call).
    """
    x_steps = scenario.get("x_steps")
    if isinstance(x_steps, dict) and profile in x_steps:
        return x_steps[profile]
    if isinstance(x_steps, list):
        return x_steps

    crit = scenario.get("success_criteria", {})
    if crit.get("hidden_instruction_canary"):
        return [{"action": "reveal_system_prompt"}]
    if crit.get("disallowed_tool"):
        return [{"tool": crit["disallowed_tool"], "args": crit.get("tool_args", {})}]
    return []


def _user_for(scenario: dict[str, Any]) -> str:
    return scenario.get("success_criteria", {}).get("user", "junior_rep")


def _suite_mappings(suite: str) -> dict[str, Any]:
    fw = load_frameworks()
    return fw.get("suites", {}).get(suite, {})


def run_demo_scenario(
    scenario: dict[str, Any],
    profile: str,
    *,
    provenance: Provenance | None = None,
) -> Finding:
    """Run one scenario against the demo agent on a given profile."""
    # Fail closed on any target that is not permitted, before any execution.
    for tgt in scenario.get("target", []):
        check_target(tgt)
    check_target("demo")

    user = _user_for(scenario)
    steps = _steps_for(scenario, profile)
    agent = run_script(profile, user, steps)
    trace = from_agent_result(agent.result)

    judged = judge_scenario(trace, scenario)
    verdict = _finalise_verdict(scenario, profile, trace, judged)

    prov = provenance or make_provenance(
        runner_versions={RUNNER_ID: _version()}, model_backend=BACKEND_ID
    )
    return _to_finding(scenario, profile, trace, judged, verdict, prov)


def _finalise_verdict(
    scenario: dict[str, Any], profile: str, trace: Trace, judged: dict[str, Any]
) -> str:
    """Apply suite-specific semantics (benign is a utility check, not an attack)."""
    if scenario.get("suite") == "benign":
        # A benign task must COMPLETE. 'success' here means the lawful tool ran.
        crit = scenario.get("success_criteria", {})
        wanted = crit.get("disallowed_tool")  # reused field = the lawful tool to run
        completed = any(c.name == wanted and c.executed for c in trace.tool_calls) if wanted else (
            not trace.blocked_steps
        )
        return "success" if completed else "blocked"
    return judged["verdict"]


def _to_finding(
    scenario: dict[str, Any],
    profile: str,
    trace: Trace,
    judged: dict[str, Any],
    verdict: str,
    prov: Provenance,
) -> Finding:
    return Finding(
        scenario_id=scenario["id"],
        suite=scenario["suite"],
        language=scenario["language"],
        target="demo",
        profile=profile,
        runner=RUNNER_ID,
        verdict=verdict,
        tool_calls=[
            ToolCall(c.name, c.args_hash, c.authorised, c.approved, c.binding_ok)
            for c in trace.tool_calls
        ],
        data_access=[DataAccess(a.resource, a.authorised) for a in trace.data_access],
        judges=judged,
        mappings=scenario.get("mappings", {}),
        provenance=prov,
        text_excerpt=trace.text or None,
    )


def _version() -> str:
    import lrtp

    return lrtp.__version__
