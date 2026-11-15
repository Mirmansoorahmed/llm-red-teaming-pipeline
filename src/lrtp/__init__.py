"""LLM Red-Teaming Pipeline (lrtp).

Standard-library-only harness for the default `oss` profile: scenario DSL,
deterministic tool-call / data-access / approval-binding / canary judges, a
shipped demo sales agent (vulnerable + defended test double), and a target
allowlist that refuses anything outside our permitted targets.

Optional OSS runner adapters and Azure hybrid adapters are added in later
phases and are never required for default CI or `make demo`.
"""

__version__ = "0.1.0"
