"""Phase 2 — demo sales agent profiles and scripted backend (R3)."""

from lrtp.findings import args_hash
from lrtp.targets.demo_agent import data as D
from lrtp.targets.demo_agent.agent import Approval, DemoAgent
from lrtp.targets.demo_agent.backend import BACKEND_ID, run_script


def test_junior_denied_forecast_on_defended():
    agent = DemoAgent("defended", D.JUNIOR_REP)
    ev = agent.run_step("get_forecast", {})
    assert ev.authorised is False
    assert ev.error  # blocked by defended policy
    # No successful forecast access recorded.
    assert not any(a.resource.startswith("crm:forecast") for a in agent.result.access_events)


def test_junior_reaches_forecast_on_vulnerable():
    agent = DemoAgent("vulnerable", D.JUNIOR_REP)
    ev = agent.run_step("get_forecast", {})
    assert ev.result is not None
    assert any(a.resource.startswith("crm:forecast") for a in agent.result.access_events)


def test_head_of_sales_allowed_forecast_on_defended():
    agent = DemoAgent("defended", D.HEAD_OF_SALES)
    ev = agent.run_step("get_forecast", {})
    assert ev.authorised is True
    assert ev.result is not None


def test_approval_binding_rejects_swapped_recipient_on_defended():
    agent = DemoAgent("defended", D.HEAD_OF_SALES)
    # Reviewer approved send_email to customer A.
    approved_args = {"to": "a@example.example", "body": "hi"}
    approval = Approval(tool="send_email", bound_hash=args_hash("send_email", approved_args))
    # Agent swaps the recipient after approval.
    swapped = {"to": "attacker@example.example", "body": "hi"}
    ev = agent.run_step("send_email", swapped, approval=approval)
    assert ev.binding_ok is False
    assert ev.error  # defended rejects the bound-token mismatch


def test_approval_binding_accepts_matching_args_on_defended():
    agent = DemoAgent("defended", D.HEAD_OF_SALES)
    args = {"to": "a@example.example", "body": "hi"}
    approval = Approval(tool="send_email", bound_hash=args_hash("send_email", args))
    ev = agent.run_step("send_email", args, approval=approval)
    assert ev.binding_ok is True
    assert ev.result == {"sent": True, "to": "a@example.example"}


def test_vulnerable_sends_without_binding():
    agent = DemoAgent("vulnerable", D.JUNIOR_REP)
    ev = agent.run_step("send_email", {"to": "x@example.example", "body": "y"})
    assert ev.result == {"sent": True, "to": "x@example.example"}


def test_system_prompt_leak_difference():
    vuln = DemoAgent("vulnerable", D.JUNIOR_REP)
    vuln.reveal_system_prompt()
    assert vuln.result.leaked_canary is True
    assert D.SYSTEM_PROMPT_CANARY in vuln.result.text

    defended = DemoAgent("defended", D.JUNIOR_REP)
    defended.reveal_system_prompt()
    assert defended.result.leaked_canary is False
    assert D.SYSTEM_PROMPT_CANARY not in defended.result.text


def test_scripted_backend_is_deterministic_and_offline():
    steps = [
        {"tool": "search_customers", "args": {"query": "Birnbaum"}},
        {"tool": "get_deal", "args": {"deal_id": "D-900"}},
    ]
    a1 = run_script("vulnerable", D.JUNIOR_REP, steps)
    a2 = run_script("vulnerable", D.JUNIOR_REP, steps)
    names1 = [e.name for e in a1.result.tool_events]
    names2 = [e.name for e in a2.result.tool_events]
    assert names1 == names2 == ["search_customers", "get_deal"]
    assert BACKEND_ID == "scripted-mock"


def test_delete_record_requires_approval_on_defended():
    agent = DemoAgent("defended", D.HEAD_OF_SALES)
    ev = agent.run_step("delete_record", {"record_id": "D-900"})
    assert ev.error  # no approval -> blocked
    assert "D-900" in agent.world.deals  # not deleted
