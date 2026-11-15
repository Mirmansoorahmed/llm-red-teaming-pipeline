"""Deterministic judges (requirements.md R2.2-R2.4).

Tool-call, data-access, approval-binding, and canary judges are authoritative.
The text judge is secondary and must never override a successful disallowed
tool call (C4). :func:`judge_scenario` combines them into a single verdict.
"""

from .verdict import judge_scenario, judge_trace

__all__ = ["judge_scenario", "judge_trace"]
