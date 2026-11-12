"""A8: decisions are persisted and can be reconciled against tickets processed."""
import pytest

from src import logging_store as ls


def decision(tid, run="r1", action="auto_respond"):
    return {"run_id": run, "ticket_id": tid, "stage": "final", "input_summary": "x", "model": {"name": "m", "version": "v"},
            "prediction": {"value": "rollback_request", "confidence": 0.99}, "sources_used": [{"doc_id": "DOC-1", "score": 0.7}],
            "threshold_applied": 0.8, "action_taken": action, "reason": "because", "guardrail_results": {"pii": {"status": "pass"}},
            "prompt_version": "PR-CL-01 v2.0", "requirement_ids": ["FR-03"]}


def test_round_trip_keeps_structured_fields():
    did = ls.log_decision(decision("T-1"))
    got = ls.get_decision(did)
    assert got["ticket_id"] == "T-1" and got["reason"] == "because" and got["threshold_applied"] == 0.8
    assert got["sources_used"] == [{"doc_id": "DOC-1", "score": 0.7}] and got["requirement_ids"] == ["FR-03"]


def test_counts_reconcile_by_run_and_ticket():
    for i in range(5):
        ls.log_decision(decision(f"T-{i}", run="a"))
    ls.log_decision(decision("T-0", run="b"))
    assert ls.count_decisions(run_id="a") == 5 and ls.count_decisions(run_id="b") == 1
    assert ls.count_decisions(ticket_id="T-0") == 2 and ls.count_decisions() == 6


def test_missing_ticket_id_is_rejected():
    with pytest.raises(ValueError):
        ls.log_decision({"action_taken": "x"})


def test_unknown_decision_returns_none():
    assert ls.get_decision("nope") is None


def test_resolution_records_hold_no_customer_identity():
    ls.log_resolution({"run_id": "r", "ticket_id": "T-1", "intent": "rollback_request", "doc_ids": ["DOC-DEPLOY-002"],
                       "confidence": 0.99, "customer_tier": "standard", "language_fluency": "fluent"})
    assert ls.count_resolutions("r") == 1
