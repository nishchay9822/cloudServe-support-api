"""
Response formatter (last box of the application layer in the brief's low-level design).
Turns a pipeline result into the payload the API returns, so the HTTP layer holds no business logic.
An automatic reply carries the text and its citations; an escalation carries the context packet for the human who picks it up.
"""


def format_response(result: dict) -> dict:
    auto = result.get("decision") == "auto_respond"
    return {
        "ticket_id": result.get("ticket_id"),
        "decision": result.get("decision"),
        "reason": result.get("reason"),
        "reason_code": result.get("reason_code"),
        "intent": result.get("intent"),
        "urgency": result.get("urgency"),
        "confidence": result.get("confidence"),
        "alternatives": result.get("alternatives") or [],
        "response": result.get("response_text") if auto else None,
        "citations": result.get("citations") if auto else [],
        "escalation_context": None if auto else result.get("escalation_context"),
        "decision_id": result.get("decision_id"),
        "latency_ms": result.get("latency_ms"),
    }
