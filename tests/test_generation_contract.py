"""Generation output contract: one JSON object {status, answer, cited_docs, reason}; anything else falls back to plain text."""
import pytest
from src import generate
from src.generate import parse_generation

OK = '{"status": "answer", "answer": "Open the revisions page. [DOC-DEPLOY-002]", "cited_docs": ["DOC-DEPLOY-002"], "reason": ""}'


def test_valid_json_is_parsed_as_structured():
    p = parse_generation(OK)
    assert p == {"declined": False, "answer": "Open the revisions page. [DOC-DEPLOY-002]", "reason": "", "declared": ["DOC-DEPLOY-002"], "format": "json"}


def test_json_in_a_code_fence_or_with_prose_around_it_is_still_parsed():
    assert parse_generation("```json\n" + OK + "\n```")["format"] == "json"
    assert parse_generation("Here you go: " + OK + " hope that helps")["format"] == "json"


def test_raw_newlines_inside_the_answer_do_not_break_parsing():
    p = parse_generation('{"status": "answer", "answer": "Step one. [DOC-A-001]\nStep two. [DOC-A-001]", "cited_docs": [], "reason": ""}')
    assert p["format"] == "json" and "Step two" in p["answer"]


def test_no_answer_status_declines_and_keeps_the_reason():
    p = parse_generation('{"status": "no_answer", "answer": "", "cited_docs": [], "reason": "needs someone to inspect the account"}')
    assert p["declined"] and p["answer"] == "" and p["reason"].startswith("needs someone")


@pytest.mark.parametrize("bad", ['{"status": "answer", "answer": "", "cited_docs": [], "reason": ""}', '{"status": "maybe", "answer": "x"}'])
def test_answer_status_with_no_text_or_unknown_status_is_a_decline(bad):
    assert parse_generation(bad)["declined"] is True


def test_plain_text_falls_back_to_the_old_handling():
    p = parse_generation("Open the revisions page. [DOC-DEPLOY-002]")
    assert p["format"] == "legacy" and not p["declined"] and p["answer"].startswith("Open")
    assert parse_generation("NO_ANSWER")["declined"] is True
    assert parse_generation("")["declined"] is True
    assert parse_generation("Do this. [DOC-A-001] NO_ANSWER")["answer"] == "Do this. [DOC-A-001]"


def test_end_to_end_generate_response_uses_the_json_contract(monkeypatch):
    monkeypatch.setattr(generate.llm, "chat", lambda *a, **k: {"text": OK, "tokens": 9})
    P = [{"doc_id": "DOC-DEPLOY-002", "title": "Rolling back", "score": 0.8, "passage": "x", "full_text": "Rolling back steps"}]
    g = generate.generate_response({"channel": "chat", "subject": "", "body": "roll back"}, P)
    assert g["format"] == "json" and not g["declined"]
    assert [c["doc_id"] for c in g["citations"]] == ["DOC-DEPLOY-002"] and g["citations"][0]["resolves"]
