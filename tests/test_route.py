"""A5: routing applies the threshold and is deterministic."""
import pytest

from src.classify import SAFETY_INTENTS
from src.route import route_ticket

P = [{"doc_id": "DOC-DEPLOY-002", "title": "Rolling back", "score": 0.76, "passage": "x"}]
T = {"ticket_id": "T", "channel": "chat", "subject": "", "body": "roll back please", "customer_tier": "standard"}


def cls(intent="rollback_request", conf=0.99):
    return {"intent": intent, "urgency": "high", "confidence": conf}


def test_confident_grounded_non_safety_ticket_is_auto_responded():
    d = route_ticket(T, cls(), P)
    assert d["decision"] == "auto_respond" and d["threshold_applied"] == 0.8 and d["reason"]


@pytest.mark.parametrize("intent", sorted(SAFETY_INTENTS))
def test_safety_intents_always_escalate_even_at_full_confidence(intent):
    d = route_ticket(T, cls(intent, 0.99), P)
    assert d["decision"] == "escalate" and d["reason_code"] == "safety_intent"


def test_no_passages_escalates():
    assert route_ticket(T, cls(), [])["reason_code"] == "no_passages"


def test_low_confidence_escalates_and_boundary_is_inclusive():
    assert route_ticket(T, cls(conf=0.79), P)["decision"] == "escalate"
    assert route_ticket(T, cls(conf=0.80), P)["decision"] == "auto_respond"


def test_threshold_comes_from_environment(monkeypatch):
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "0.95")
    assert route_ticket(T, cls(conf=0.9), P)["decision"] == "escalate"
    assert route_ticket(T, cls(conf=0.9), P)["threshold_applied"] == 0.95


def test_same_input_always_gives_the_same_decision():
    first = route_ticket(T, cls(conf=0.83), P)
    assert all(route_ticket(T, cls(conf=0.83), P) == first for _ in range(100))


def test_escalation_context_has_summary_sources_and_reason(provider_down):
    d = route_ticket(T, cls(conf=0.4), P, build_context=True)
    ctx = d["escalation_context"]
    assert ctx["summary"] and ctx["uncertainty_reason"] and ctx["retrieved_sources"][0]["doc_id"] == "DOC-DEPLOY-002"
