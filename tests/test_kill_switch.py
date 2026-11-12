"""Kill switch drill (Governance Framework: 'How is it tested?').
Flip the switch over HTTP while a ticket is mid-generation: that ticket finishes normally,
the very next ticket goes to a human, and switching off restores automatic replies."""
import os
import threading
import time
import pytest
from fastapi.testclient import TestClient
from tests.conftest import ROOT, find_ticket
from src import api, llm
from src.api import app
KILL_FILE = os.path.join(ROOT, "storage", "KILL_SWITCH")
def payload(t):
    return {k: t[k] for k in ("ticket_id", "channel", "subject", "body", "customer_id", "customer_name", "customer_tier", "customer_region", "language_fluency")}
@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(api, "ADMIN_TOKEN", "drill-token")
    with TestClient(app) as c:
        yield c
    if os.path.exists(KILL_FILE):
        os.remove(KILL_FILE)
def test_flip_during_a_ticket_in_flight(client, fake_llm, monkeypatch):
    base = fake_llm
    started, release = threading.Event(), threading.Event()
    def slow_chat(messages, max_tokens=400, temperature=0.0, model=None):
        if "draft replies" in messages[0]["content"]:          # the generation step
            started.set()
            assert release.wait(10)
        return base(messages, max_tokens, temperature, model)
    monkeypatch.setattr(llm, "chat", slow_chat)
    t = find_ticket("rollback_request")
    box = {}
    th = threading.Thread(target=lambda: box.update(r=client.post("/process", json=payload(t)).json()))
    th.start()
    assert started.wait(10), "ticket never reached generation"
    # --- switch on while that ticket is in flight
    t0 = time.time()
    assert client.post("/admin/kill-switch", json={"on": True, "token": "drill-token"}).json() == {"kill_switch": True}
    assert client.get("/health").json()["kill_switch"] is True
    nxt = client.post("/process", json=payload(find_ticket("rollback_request"))).json()
    took = time.time() - t0
    assert nxt["decision"] == "escalate" and nxt["reason_code"] == "kill_switch" and nxt["response"] is None
    assert took < 2, f"kill switch took {took:.2f}s to affect the next ticket"
    logged = client.get(f"/decisions/{nxt['ticket_id']}").json()          # the escalation is auditable
    assert any("kill switch" in (d["reason"] or "").lower() for d in logged)
    release.set(); th.join(10)
    assert box["r"]["decision"] == "auto_respond", "an in-flight ticket should finish normally"
    # --- switch off restores service
    assert client.post("/admin/kill-switch", json={"on": False, "token": "drill-token"}).json() == {"kill_switch": False}
    assert client.post("/process", json=payload(find_ticket("rollback_request"))).json()["decision"] == "auto_respond"
def test_wrong_or_missing_token_cannot_switch(client):
    assert client.post("/admin/kill-switch", json={"on": True, "token": ""}).status_code == 403
    assert client.get("/health").json()["kill_switch"] is False
