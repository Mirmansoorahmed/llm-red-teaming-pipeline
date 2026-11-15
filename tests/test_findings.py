"""Phase 1.4 — finding record provenance + redaction (R2.5, R6)."""

import json

from lrtp.findings import (
    DataAccess,
    Finding,
    ToolCall,
    args_hash,
    make_provenance,
    redact,
    write_findings,
)


def test_args_hash_is_stable_and_order_independent():
    a = args_hash("send_email", {"to": "x", "body": "y"})
    b = args_hash("send_email", {"body": "y", "to": "x"})
    assert a == b
    assert a != args_hash("send_email", {"to": "z", "body": "y"})


def test_redaction_removes_seeded_markers():
    text = "api_key: sk-ABCD1234efgh and mail bob@example.com phone +49 151 23456789"
    out = redact(text)
    assert "sk-ABCD1234efgh" not in out
    assert "bob@example.com" not in out
    assert "[REDACTED]" in out


def test_provenance_carries_git_sha_and_timestamp():
    prov = make_provenance(repo=".")
    assert prov.git_sha  # 'unknown' or a real sha, never empty
    assert prov.timestamp.endswith("Z")
    assert "lrtp" in prov.runner_versions


def test_finding_round_trips_and_validates(tmp_path):
    f = Finding(
        scenario_id="RT-PI-DIRECT-001",
        suite="prompt_injection_direct",
        language="en",
        target="demo",
        profile="vulnerable",
        runner="lrtp",
        verdict="success",
        tool_calls=[ToolCall("send_email", args_hash("send_email", {"to": "a"}),
                             authorised=False, approved=False, binding_ok=False)],
        data_access=[DataAccess("crm:customer:42", authorised=False)],
        judges={"tool_call": "success"},
        mappings={"owasp_llm_2026": ["LLM01"]},
        provenance=make_provenance(repo="."),
        text_excerpt="contact bob@example.com with api_key: sk-SECRET123",
    )
    out = write_findings([f], tmp_path / "results.json")
    records = json.loads(out.read_text())
    assert records[0]["provenance"]["git_sha"]
    assert records[0]["provenance"]["timestamp"].endswith("Z")
    # text excerpt is redacted on persist
    assert "sk-SECRET123" not in records[0]["text_excerpt"]
    assert "bob@example.com" not in records[0]["text_excerpt"]
