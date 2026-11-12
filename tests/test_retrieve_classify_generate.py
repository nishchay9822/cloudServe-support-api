"""A3, A4, A6: classification, retrieval and generation behave as specified."""
import json
import os

import pytest

from tests.conftest import ROOT, find_ticket
from src import classify, generate, ingest, llm, retrieve

DOC_IDS = {d["doc_id"] for d in json.load(open(os.path.join(ROOT, "data", "documentation.json")))}


# ---- retrieval (A4)
def test_customer_vocabulary_finds_the_right_article():
    ps = retrieve.retrieve_passages("how do I revert to an earlier revision, the release is causing errors")
    assert ps and ps[0]["doc_id"] == "DOC-DEPLOY-002"


def test_every_returned_source_resolves_to_a_real_document():
    ps = retrieve.retrieve_passages("webhook signature verification fails")
    assert ps and all(p["doc_id"] in DOC_IDS and p["passage"] for p in ps)
    assert len({p["doc_id"] for p in ps}) == len(ps)  # one passage per document


def test_gibberish_or_empty_query_returns_nothing():
    assert retrieve.retrieve_passages("") == []
    assert retrieve.retrieve_passages("   ") == []
    assert retrieve.retrieve_passages("zxqv plorp wibble", min_score=0.5) == []


def test_corpus_embedding_is_idempotent():
    a = retrieve.embed_corpus()
    b = retrieve.embed_corpus()
    assert a == b and a >= len(DOC_IDS)


# ---- classification (A3)
def norm(t):
    return ingest.normalize_ticket(t)


def test_confident_neighbours_classify_without_calling_the_model(provider_down):
    t = find_ticket("rollback_request")
    out = classify.classify_ticket(norm(t))
    assert out["intent"] == "rollback_request" and out["method"] == "knn"
    assert 0.0 <= out["confidence"] <= 1.0 and out["urgency"] in classify.URGENCY_LEVELS


def test_empty_ticket_is_unclear():
    out = classify.classify_ticket(norm({"ticket_id": "E", "channel": "chat", "body": ""}))
    assert out["intent"] == "unclear_request"


def test_ambiguous_ticket_with_provider_down_still_returns_a_valid_classification(provider_down):
    out = classify.classify_ticket(norm({"ticket_id": "A", "channel": "chat", "body": "something odd happened with our setup after the change"}))
    assert out["intent"] in classify.INTENT_CLASSES and 0.0 <= out["confidence"] <= 1.0


def test_unparseable_llm_output_is_handled(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setattr(llm, "chat", lambda *a, **k: {"text": "I think it is probably a billing thing", "tokens": 1})
    with pytest.raises(llm.LLMUnavailable):
        classify.classify_llm(norm({"ticket_id": "A", "channel": "chat", "body": "x"}))


def test_llm_label_outside_the_22_classes_becomes_unclear(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setattr(llm, "chat", lambda *a, **k: {"text": '{"intent": "made_up", "urgency": "high", "confidence": 0.99}', "tokens": 1})
    out = classify.classify_llm(norm({"ticket_id": "A", "channel": "chat", "body": "x"}))
    assert out["intent"] == "unclear_request" and out["confidence"] <= 0.3


def test_safety_intents_match_the_discovery_evidence():
    assert classify.SAFETY_INTENTS == {"security_incident", "compliance_request", "feature_request", "unclear_request"}


# ---- generation (A6)
PASSAGE = [{"doc_id": "DOC-DEPLOY-002", "title": "Rolling back", "score": 0.8, "passage": "Rolling back", "full_text": "Open the revisions page."}]


def test_generation_refuses_without_passages():
    with pytest.raises(ValueError):
        generate.generate_response({"body": "x"}, [])


def test_citations_resolve_to_shown_passages(fake_llm):
    out = generate.generate_response({"channel": "chat", "subject": "", "body": "roll back", "customer_tier": "standard"}, PASSAGE)
    assert out["citations"] and all(c["resolves"] for c in out["citations"])
    assert "drafted automatically" in out["final_text"] and not out["declined"]


def test_invented_citation_is_reported_as_unresolved():
    cites = generate.extract_citations("Do this. [DOC-NOPE-001]", PASSAGE)
    assert cites[0]["resolves"] is False


def test_no_answer_sentinel_means_declined(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setattr(llm, "chat", lambda *a, **k: {"text": "NO_ANSWER", "tokens": 1})
    assert generate.generate_response({"body": "x"}, PASSAGE)["declined"] is True


def test_stray_sentinel_after_a_real_answer_is_removed(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setattr(llm, "chat", lambda *a, **k: {"text": "Open the revisions page. [DOC-DEPLOY-002] NO_ANSWER", "tokens": 1})
    out = generate.generate_response({"body": "x"}, PASSAGE)
    assert not out["declined"] and "NO_ANSWER" not in out["answer"]


def test_stale_article_is_never_returned(monkeypatch):
    """R-05: an article past DOC_MAX_AGE_DAYS must be excluded, so the ticket escalates rather than quote it."""
    from src import retrieve
    q = "how do I roll back a failed deployment"
    top = retrieve.retrieve_passages(q, top_k=3)[0]["doc_id"]
    real = retrieve.get_client().get_collection(retrieve.DOC_COLLECTION, embedding_function=retrieve._ef())

    class Aged:
        """The real collection, except the top article reports it was last reviewed 400 days ago."""
        def query(self, **kw):
            out = real.query(**kw)
            out["metadatas"] = [[dict(m, last_reviewed_days_ago=400) if m["doc_id"] == top else m for m in out["metadatas"][0]]]
            return out
        def count(self):
            return real.count()

    class Client:
        def get_collection(self, *a, **k):
            return Aged()

    monkeypatch.setattr(retrieve, "get_client", lambda: Client())
    monkeypatch.setattr(retrieve, "DOC_MAX_AGE_DAYS", 30)
    assert top not in [p["doc_id"] for p in retrieve.retrieve_passages(q, top_k=3)]
    monkeypatch.setattr(retrieve, "DOC_MAX_AGE_DAYS", 0)  # guard off: the article comes back
    assert top in [p["doc_id"] for p in retrieve.retrieve_passages(q, top_k=3)]
