"""Run trace — the record of what the agent actually did (requirements.md R2.1).

A :class:`Trace` captures prompts, tool calls (name + args hash), data-access
events, approvals, and a redacted text excerpt. Judges read the trace; they never
re-run the agent. Building the trace from a demo-agent result keeps the judging
contract identical across backends and (later) runner adapters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from lrtp.findings import args_hash
from lrtp.targets.demo_agent.agent import AgentResult


@dataclass
class TracedToolCall:
    name: str
    args: dict[str, Any]
    args_hash: str
    authorised: bool
    approved: bool
    binding_ok: bool
    executed: bool  # False when the profile blocked the call


@dataclass
class TracedAccess:
    resource: str
    authorised: bool


@dataclass
class Trace:
    tool_calls: list[TracedToolCall] = field(default_factory=list)
    data_access: list[TracedAccess] = field(default_factory=list)
    text: str = ""
    leaked_canary: bool = False
    blocked_steps: int = 0


def from_agent_result(result: AgentResult) -> Trace:
    trace = Trace(text=result.text, leaked_canary=result.leaked_canary,
                  blocked_steps=result.blocked_steps)
    for ev in result.tool_events:
        executed = ev.error is None
        trace.tool_calls.append(
            TracedToolCall(
                name=ev.name,
                args=ev.args,
                args_hash=args_hash(ev.name, ev.args),
                authorised=ev.authorised,
                approved=ev.approved,
                binding_ok=ev.binding_ok,
                executed=executed,
            )
        )
    for a in result.access_events:
        trace.data_access.append(TracedAccess(a.resource, a.authorised))
    return trace
