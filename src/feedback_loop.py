"""
Feedback loop (third cross-cutting concern in the brief's high-level design: 'human corrections return').

A person who handles a ticket can say what the right intent / route was. The correction is
  1. stored in the audit database (table feedback), so it can be reviewed and counted;
  2. if it carries a corrected intent and the ticket text, added to the classifier's neighbour index, so the very next
     similar ticket is classified with the human's label (this is the learning path);
  3. counted in the feedback_total metric, so the dashboard shows how often humans overrule the system.

Corrections are never applied silently to routing rules; they change what the nearest-neighbour vote sees.
"""
from typing import Optional

from src import classify, logging_store, retrieve, telemetry
from src.classify import INTENT_CLASSES, URGENCY_LEVELS

ROUTES = ("auto_respond", "escalate")


def record_feedback(fb: dict) -> dict:
    ticket_id = (fb.get("ticket_id") or "").strip()
    if not ticket_id:
        raise ValueError("ticket_id is required")
    ci, cu, cr = fb.get("corrected_intent"), fb.get("corrected_urgency"), fb.get("corrected_route")
    if ci is not None and ci not in INTENT_CLASSES:
        raise ValueError(f"corrected_intent must be one of the {len(INTENT_CLASSES)} known intents")
    if cu is not None and cu not in URGENCY_LEVELS:
        raise ValueError("corrected_urgency must be high, medium or low")
    if cr is not None and cr not in ROUTES:
        raise ValueError("corrected_route must be auto_respond or escalate")
    if ci is None and cu is None and cr is None and fb.get("resolved") is None:
        raise ValueError("nothing to record: give a corrected intent, urgency, route or a resolved flag")

    # Link to what the system decided, when we can find it.
    prior: Optional[dict] = None
    rows = logging_store.get_decisions_for_ticket(ticket_id)
    if rows:
        prior = rows[-1] if not fb.get("decision_id") else next((r for r in rows if r["decision_id"] == fb["decision_id"]), rows[-1])
    fb = dict(fb, decision_id=(prior or {}).get("decision_id"), original_decision=(prior or {}).get("action_taken"),
              original_intent=((prior or {}).get("prediction") or {}).get("value"))

    applied = False
    text = ((fb.get("subject") or "") + "\n" + (fb.get("body") or "")).strip()
    if ci and text:
        applied = add_to_index(f"FB-{ticket_id}", text, ci, cu or "medium", cr)
    fb["applied_to_index"] = applied
    fid = logging_store.log_feedback(fb)

    if ci and ci != fb.get("original_intent"):
        telemetry.FEEDBACK.labels("intent_correction").inc()
    if cr and cr != fb.get("original_decision"):
        telemetry.FEEDBACK.labels("route_correction").inc()
    if (ci is None or ci == fb.get("original_intent")) and (cr is None or cr == fb.get("original_decision")):
        telemetry.FEEDBACK.labels("confirmed").inc()
    return {"feedback_id": fid, "applied_to_index": applied, "original_decision": fb["original_decision"],
            "original_intent": fb["original_intent"]}


def add_to_index(doc_id: str, text: str, intent: str, urgency: str, route: Optional[str]) -> bool:
    """Add (or replace) one human-labelled ticket in the neighbour index used by the classifier."""
    classify.ensure_ticket_index()
    col = retrieve.get_client().get_collection(classify.TICKET_COLLECTION, embedding_function=retrieve._ef())
    try:
        col.delete(ids=[doc_id])
    except Exception:
        pass
    col.add(ids=[doc_id], documents=[text], metadatas=[{"intent": intent, "urgency": urgency,
                                                          "answerable": 0 if route == "escalate" else 1, "esc": 1 if route == "escalate" else 0}])
    return True


def remove_from_index(doc_id: str) -> None:
    col = retrieve.get_client().get_collection(classify.TICKET_COLLECTION, embedding_function=retrieve._ef())
    col.delete(ids=[doc_id])
