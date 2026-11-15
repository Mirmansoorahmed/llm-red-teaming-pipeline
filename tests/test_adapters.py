"""Phase 5 — optional OSS adapters skip cleanly when absent (R7)."""

from lrtp.adapters import discover_adapters
from lrtp.adapters.agentdojo_adapter import AgentDojoAdapter
from lrtp.adapters.garak_adapter import GarakAdapter
from lrtp.adapters.promptfoo_adapter import PromptfooAdapter
from lrtp.adapters.pyrit_adapter import PyritAdapter

PINNED = {
    "garak": "0.17.1",
    "agentdojo": "0.1.35",
    "pyrit": "1.2.0",
    "promptfoo": "0.125.1",
}


def test_discover_returns_all_four_adapters():
    names = {a.name for a in discover_adapters()}
    assert names == {"garak", "agentdojo", "pyrit", "promptfoo"}


def test_pinned_versions():
    for a in discover_adapters():
        assert a.pinned_version == PINNED[a.name]


def test_all_adapters_absent_in_default_env():
    """With no extras installed (default CI), every adapter is skipped cleanly."""
    for a in discover_adapters():
        # available() must never raise, even when the package is missing.
        assert a.available() is False


def test_version_falls_back_to_pinned_when_absent():
    for a in discover_adapters():
        assert a.version() == PINNED[a.name]


def test_garak_normalise_maps_failed_probe_to_success():
    out = GarakAdapter().normalise(
        [{"entry_type": "eval", "probe": "dan.Dan_11_0", "passed": False, "output": "..."}]
    )
    assert out[0].verdict == "success"
    assert out[0].judges["garak"] == "fail"


def test_agentdojo_normalise_maps_injection_to_success():
    out = AgentDojoAdapter().normalise(
        [{"task_id": "injection_task_3", "injection_successful": True,
          "tool_calls": [{"function": "send_money"}]}]
    )
    assert out[0].verdict == "success"
    assert out[0].tool_calls[0]["name"] == "send_money"


def test_pyrit_normalise_maps_objective_to_success():
    out = PyritAdapter().normalise([{"conversation_id": "c1", "objective_achieved": True}])
    assert out[0].verdict == "success"


def test_promptfoo_normalise_maps_failed_assert_to_success():
    out = PromptfooAdapter().normalise({"results": [{"id": "t1", "success": False}]})
    assert out[0].verdict == "success"
    # promptfoo availability is CLI-based, not a Python import
    assert PromptfooAdapter().module_name is None
