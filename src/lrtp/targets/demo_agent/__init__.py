"""Demo sales agent for the fictional client Ortenwald Handel GmbH.

Synthetic data only. Two profiles share one code path:

- ``vulnerable``: shared high-privilege toolset, retrieved documents trusted as
  instructions, no approval binding, a retrievable system prompt.
- ``defended``: a TEST DOUBLE (not the Agent Hardening Sandbox) — per-user
  allowlist, narrow wrappers, risk-tiered approval, approval token bound to a
  hash of the exact tool name + arguments, hidden-context canaries, and
  retrieved content treated as data.

The default backend is a deterministic scripted/mock model (no GPU, no paid API,
no network).
"""
