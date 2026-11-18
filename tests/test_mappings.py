"""Phase 1.2 — framework mapping tables load and expose the v1 allowed set."""

from lrtp.mappings import allowed_ids, check_mapping_ids, load_frameworks


def test_frameworks_file_loads():
    fw = load_frameworks()
    assert fw["owasp_llm_2026"]["LLM01"] == "Prompt Injection"
    assert "AML.T0085.003" in fw["atlas_v2026_10"]
    # retired id name is not present as a key
    assert "AML.T0085.000" not in fw["atlas_v2026_10"]


def test_allowed_ids_cover_known_ids():
    ids = allowed_ids()
    assert "LLM08" in ids["owasp_llm_2026"]
    assert "ASI09" in ids["owasp_agentic_2026"]
    assert "AML.T0051.001" in ids["atlas_v2026_10"]


def test_check_mapping_ids_accepts_known_and_rejects_unknown():
    assert check_mapping_ids({"owasp_llm_2026": ["LLM01"]}) == []
    errs = check_mapping_ids({"atlas_v2026_10": ["AML.T9999"]})
    assert errs and "unknown id" in errs[0]
