"""Shared fixtures. Tests never call the real model: llm.chat is replaced by a deterministic fake."""
import json
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")


def val_tickets():
    return json.load(open(os.path.join(ROOT, "data", "validation_tickets.json")))


def find_ticket(intent: str, route: str = "auto_respond"):
    return next(t for t in val_tickets() if t["labels"]["intent"] == intent and t["labels"]["expected_route"] == route)


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Every test gets its own decision log and no kill switch."""
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/decisions.db")
    monkeypatch.delenv("KILL_SWITCH", raising=False)
    kill = os.path.join(ROOT, "storage", "KILL_SWITCH")
    if os.path.exists(kill):
        os.remove(kill)
    from src import llm
    llm.reset_breaker()


@pytest.fixture
def fake_llm(monkeypatch):
    """A deterministic stand-in for the model. Cites the first [DOC-...] passage it is shown."""
    from src import llm
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    def chat(messages, max_tokens=400, temperature=0.0, model=None):
        system = messages[0]["content"]
        user = messages[-1]["content"]
        if "classify support tickets" in system:
            return {"text": '{"intent": "rollback_request", "urgency": "high", "confidence": 0.9, "second_choice": "deployment_failure"}', "tokens": 10}
        if "draft replies" in system:
            m = re.search(r"\[(DOC-[A-Z]+-\d+)\]", user)
            doc = m.group(1) if m else "DOC-X-000"
            return {"text": f"Open the revisions page for the service and select roll back on the last healthy revision. [{doc}]", "tokens": 20}
        return {"text": "SUMMARY: Customer needs help. REASON: test. RELEVANT DOCS: none", "tokens": 5}

    monkeypatch.setattr(llm, "chat", chat)
    return chat


@pytest.fixture
def provider_down(monkeypatch):
    from src import llm

    def chat(*a, **k):
        raise llm.LLMUnavailable("simulated outage")

    monkeypatch.setattr(llm, "chat", chat)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
