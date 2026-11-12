"""The HTTP interface."""
import pytest
from fastapi.testclient import TestClient

from tests.conftest import find_ticket
from src.api import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def payload(t):
    return {k: t[k] for k in ("ticket_id", "channel", "subject", "body", "customer_id", "customer_name", "customer_tier", "customer_region", "language_fluency")}


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "healthy"


def test_process_returns_a_decision_and_it_is_auditable(client, fake_llm):
    t = find_ticket("rollback_request")
    r = client.post("/process", json=payload(t))
    assert r.status_code == 200
    body = r.json()
    assert body["decision"] == "auto_respond" and body["citations"] and body["decision_id"]
    audit = client.get(f"/decisions/{t['ticket_id']}")
    assert audit.status_code == 200 and audit.json()[0]["reason"]


def test_process_during_a_provider_outage_is_an_escalation_not_a_500(client, provider_down):
    r = client.post("/process", json=payload(find_ticket("rollback_request")))
    assert r.status_code == 200 and r.json()["decision"] == "escalate"


def test_missing_required_field_is_a_422(client):
    assert client.post("/process", json={"channel": "email"}).status_code == 422


def test_unknown_ticket_has_no_audit_trail(client):
    assert client.get("/decisions/DOES-NOT-EXIST").status_code == 404


def test_metrics_endpoint_exposes_prometheus_counters(client, fake_llm):
    client.post("/process", json=payload(find_ticket("rollback_request")))
    text = client.get("/metrics").text
    assert "tickets_processed_total" in text and "ticket_latency_seconds" in text


def test_kill_switch_requires_the_admin_token(client):
    assert client.post("/admin/kill-switch", json={"on": True, "token": "wrong"}).status_code == 403
