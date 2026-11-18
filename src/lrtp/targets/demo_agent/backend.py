"""Scripted/mock backend for the demo agent (requirements.md R3.5).

Deterministic: given a scenario's declared steps, it produces the same tool
calls every time, with no GPU, no paid API, and no network. A real local model
(e.g. Ollama) is optional and only used when explicitly present; this module is
the default and the one CI uses.

A scenario may declare an optional ``steps`` list in its ``success_criteria``
is not used for this; instead the runner passes an explicit step script derived
from the suite. To keep Phase 2 self-contained and testable, the backend accepts
an explicit list of steps.
"""

from __future__ import annotations

from typing import Any

from .agent import Approval, DemoAgent

# Provenance string recorded on every finding produced via this backend.
BACKEND_ID = "scripted-mock"


def run_script(
    profile: str,
    user: str,
    steps: list[dict[str, Any]],
) -> DemoAgent:
    """Execute a deterministic step script against a fresh agent.

    Each step is a dict:
      {"tool": <name>, "args": {...}, "approval": {"tool":..., "bound_hash":...}?}
    A special step {"action": "reveal_system_prompt"} probes hidden context.
    """
    agent = DemoAgent(profile=profile, user=user)
    for step in steps:
        if step.get("action") == "reveal_system_prompt":
            agent.reveal_system_prompt()
            continue
        approval = None
        if step.get("approval"):
            ap = step["approval"]
            approval = Approval(tool=ap.get("tool"), bound_hash=ap.get("bound_hash"))
        agent.run_step(step["tool"], step.get("args", {}), approval=approval)
    return agent
