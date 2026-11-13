"""Feedback loop: human corrections are stored, counted, and change what the classifier sees next time."""
import pytest
from fastapi.testclient import TestClient
from src import classify, feedback_loop, ingest, logging_store
from src.api import app

ODD = {"ticket_id": "FB-T1", "channel": "email", "subject": "Quibblezot flange misalignment",
       "body": "our quibblezot flange keeps misaligning with the wobbulator manifold after the zorp upgrade"}


@pytest.fixture
def cleanup():
    yield
    try:
        feedback_loop.remove_from_index("FB-FB-T1")
    except Exception:
        pass


def test_correction_changes_the_next_classification(cleanup):
    t = ingest.normalize_ticket(ODD)
    before = classify.classify_knn(t)
    corrected = "webhook_issue" if before["intent"] != "webhook_issue" else "data_export"
    out = feedback_loop.record_feedback({"ticket_id": "FB-T1", "subject": ODD["subject"], "body": ODD["body"],
                                         "corrected_intent": corrected, "corrected_route": "auto_respond"})
    assert out["applied_to_index"] is True
    after = classify.classify_knn(t)
    assert after["intent"] == corrected, "the human's label should win for the same wording"
    assert after["share"] > before["share"] or after["intent"] != before["intent"]


def test_feedback_is_stored_and_summarised(cleanup):
    base = logging_store.feedback_summary()
    feedback_loop.record_feedback({"ticket_id": "FB-T1", "corrected_route": "escalate", "note": "customer needed a person"})
    now = logging_store.feedback_summary()
    assert now["total"] == base["total"] + 1 and now["route_corrections"] == base["route_corrections"] + 1


@pytest.mark.parametrize("bad", [{"ticket_id": "x"}, {"ticket_id": "x", "corrected_intent": "not_an_intent"},
                                 {"ticket_id": "x", "corrected_route": "maybe"}, {"ticket_id": ""}])
def test_invalid_feedback_is_rejected(bad):
    with pytest.raises(ValueError):
        feedback_loop.record_feedback(bad)


def test_api_feedback_endpoint_and_metric(cleanup):
    with TestClient(app) as c:
        assert c.post("/feedback", json={"ticket_id": "FB-T1", "corrected_route": "escalate"}).status_code == 200
        assert c.post("/feedback", json={"ticket_id": "FB-T1"}).status_code == 422
        assert c.get("/feedback/summary").json()["total"] >= 1
        assert "feedback_total" in c.get("/metrics").text
