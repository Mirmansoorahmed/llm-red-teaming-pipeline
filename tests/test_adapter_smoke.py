"""Phase 5.6 — adapter smoke target skips cleanly with no extras (R7.4)."""

from lrtp.adapters.smoke import run_smoke


def test_smoke_skips_all_adapters_in_default_env():
    status = run_smoke()
    assert set(status) == {"garak", "agentdojo", "pyrit", "promptfoo"}
    # With no extras installed every adapter is skipped (never 'error').
    assert all(v == "skipped" for v in status.values())
