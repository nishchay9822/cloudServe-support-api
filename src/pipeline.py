"""
End-to-end pipeline: ingest -> classify -> retrieve -> route -> generate -> validate -> log.

Principles
- A ticket never crashes the run (A11): every stage failure becomes an escalation with a reason.
- Every ticket is logged, including errors and escalations (A8).
- Kill switch: if env KILL_SWITCH=1 or the file storage/KILL_SWITCH exists, nothing is auto-answered.
- Ground-truth fields (labels/history) are never read here. The harness scores results separately.
"""
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from src import classify, guardrails, ingest, llm, logging_store, retrieve, route, telemetry
from src.generate import PROMPT_VERSION as GEN_VERSION
from src.generate import generate_response

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIREMENTS = ["FR-01", "FR-02", "FR-03", "FR-04", "FR-06", "FR-07", "FR-08", "FR-09", "FR-11", "FR-12"]


def kill_switch_on() -> bool:
    return os.getenv("KILL_SWITCH", "0") == "1" or os.path.exists(os.path.join(ROOT, "storage", "KILL_SWITCH"))


def new_run_id() -> str:
    return datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%S-") + uuid.uuid4().hex[:6]


def process_ticket(raw: dict, run_id: Optional[str] = None, outcome_fcr: Optional[bool] = None,
                   exclude_id: Optional[str] = None, log: bool = True) -> dict:
    """
    Process one raw ticket. Always returns a result dict and (if log=True) always writes a decision row.
    `outcome_fcr` simulates the feedback signal for the resolution graph (FR-13); it is only used to
    decide whether to store a resolution record, never to make the decision.
    """
    t0 = time.time()
    run_id = run_id or "adhoc"
    r = {"ticket_id": (raw or {}).get("ticket_id", "UNKNOWN") if isinstance(raw, dict) else "UNKNOWN",
         "channel": (raw or {}).get("channel") if isinstance(raw, dict) else None,
         "status": "ok", "decision": "escalate", "reason": "", "reason_code": "", "intent": None, "urgency": None,
         "confidence": None, "classify_method": None, "passages": [], "response_text": None, "citations": [],
         "escalation_context": None, "guardrails": None, "tokens": 0, "error": None, "stage_ms": {}}
    ticket, cls, passages, route_dec = None, {}, [], {}
    try:
        # 0 kill switch
        if kill_switch_on():
            r.update(reason="Kill switch is on: all tickets go to humans.", reason_code="kill_switch")
            ticket = ingest.normalize_ticket(raw) if isinstance(raw, dict) else None
            raise _Done()

        # 1 ingest
        s = time.time()
        ticket = ingest.normalize_ticket(raw)
        r["ticket_id"], r["channel"] = ticket["ticket_id"], ticket["channel"]
        r["stage_ms"]["ingest"] = _ms(s)

        # 2 injection screen BEFORE any model sees the text
        inj = guardrails.check_injection(ticket["body"] + "\n" + ticket["subject"])
        if inj["status"] == "block":
            r.update(reason="Ticket text looks like an attempt to instruct the system; handled by a human.",
                     reason_code="injection_screen", guardrails={"injection": inj, "blocked_by": ["injection"]})
            raise _Done()

        # 3 classify
        s = time.time()
        cls = classify.classify_ticket(ticket, exclude_id=exclude_id)
        r.update(intent=cls["intent"], urgency=cls["urgency"], confidence=cls["confidence"],
                 classify_method=cls["method"])
        r["tokens"] += cls.get("tokens", 0)
        r["stage_ms"]["classify"] = _ms(s)
        r["knn_share"] = (cls.get("raw") or {}).get("knn_share")

        # 4 retrieve
        s = time.time()
        try:
            passages = retrieve.retrieve_passages(ticket["text"])
        except Exception as e:  # vector store problem: degrade to escalation
            passages = []
            r["error"] = f"retrieval failed: {type(e).__name__}"
        r["passages"] = [{"doc_id": p["doc_id"], "score": p["score"]} for p in passages]
        r["stage_ms"]["retrieve"] = _ms(s)

        # 5 route (deterministic)
        route_dec = route.route_ticket(ticket, cls, passages)
        r.update(decision=route_dec["decision"], reason=route_dec["reason"], reason_code=route_dec["reason_code"])

        # 6 generate + 7 validate
        if route_dec["decision"] == "auto_respond":
            s = time.time()
            try:
                gen = generate_response(ticket, passages, cls)
                r["tokens"] += gen["token_count"]
                r["stage_ms"]["generate"] = _ms(s)
                if gen["declined"]:
                    r.update(decision="escalate", reason="The model could not answer from the documentation.",
                             reason_code="model_declined")
                else:
                    shown = [p for p in passages if p["doc_id"] in gen["shown_doc_ids"]]  # exactly what the model saw
                    g = guardrails.run_guardrails(gen, ticket, shown, route_dec)
                    r["guardrails"] = g
                    if g["overall_status"] == "pass":
                        r.update(response_text=gen["final_text"], citations=gen["citations"])
                    else:
                        r.update(decision="escalate", reason_code="guardrail_block",
                                 reason=f"Draft blocked by guardrail(s): {', '.join(g['blocked_by'])}.")
            except llm.LLMUnavailable as e:
                r.update(decision="escalate", reason_code="provider_unavailable",
                         reason="The model provider was unavailable, so the ticket goes to a human.", error=str(e))

        # 8 escalation context packet
        if r["decision"] == "escalate":
            raise _Done()
    except _Done:
        pass
    except Exception as e:  # last line of defence: nothing may crash the run
        r.update(status="error", decision="escalate", reason_code="pipeline_error",
                 reason="Unexpected error; ticket escalated to a human.", error=f"{type(e).__name__}: {e}")

    if r["decision"] == "escalate" and ticket is not None:
        try:
            ctx_route = {"threshold_applied": route_dec.get("threshold_applied", route.get_threshold())}
            r["escalation_context"] = route.build_escalation_context(
                ticket, cls or {"intent": None, "urgency": None, "confidence": None}, passages, r["reason"],
                ctx_route["threshold_applied"])
            r["tokens"] += r["escalation_context"].get("tokens", 0)
        except Exception as e:
            r["escalation_context"] = {"summary": (ticket.get("text") or "")[:240], "retrieved_sources": [],
                                       "uncertainty_reason": r["reason"], "error": type(e).__name__}

    r["latency_ms"] = _ms(t0)
    r["threshold_applied"] = route_dec.get("threshold_applied", route.get_threshold())
    telemetry.record(r)

    if log:
        try:
            r["decision_id"] = logging_store.log_decision(_to_decision(r, ticket, run_id))
            if outcome_fcr and r["decision"] == "auto_respond" and r["intent"]:
                logging_store.log_resolution({"run_id": run_id, "ticket_id": r["ticket_id"], "intent": r["intent"],
                                              "doc_ids": [p["doc_id"] for p in r["passages"][:3]],
                                              "confidence": r["confidence"],
                                              "customer_tier": (ticket or {}).get("customer_tier"),
                                              "language_fluency": (ticket or {}).get("language_fluency")})
        except Exception as e:
            r["status"] = "log_error"
            r["error"] = f"decision log failed: {type(e).__name__}: {e}"
    return r


class _Done(Exception):
    pass


def warm_up() -> dict:
    """Load models and indexes once so the first ticket is not charged their start-up cost."""
    t = time.time()
    ok = {"retrieval": False, "ticket_index": False}
    try:
        retrieve.retrieve_passages("warm up")
        ok["retrieval"] = True
    except Exception:
        pass
    try:
        classify.classify_knn(ingest.normalize_ticket({"ticket_id": "warm", "channel": "chat", "body": "warm up"}))
        ok["ticket_index"] = True
    except Exception:
        pass
    ok["seconds"] = round(time.time() - t, 1)
    return ok


def _ms(t: float) -> int:
    return int((time.time() - t) * 1000)


def _to_decision(r: dict, ticket: Optional[dict], run_id: str) -> dict:
    return {
        "run_id": run_id,
        "ticket_id": r["ticket_id"],
        "stage": "final",
        "input_summary": f"{r.get('channel')} | {(ticket or {}).get('customer_tier')} | " + ((ticket or {}).get("text") or "")[:160],
        "model": {"name": llm.model_name(), "version": "openrouter"},
        "prediction": {"value": r["intent"], "confidence": r["confidence"]},
        "alternatives": [],
        "sources_used": r["passages"],
        "threshold_applied": r.get("threshold_applied"),
        "action_taken": r["decision"],
        "reason": r["reason"],
        "guardrail_results": r["guardrails"] or {},
        "prompt_version": f"PR-CL-01 v2.0 / {GEN_VERSION} / PR-RO-01 v1.0",
        "requirement_ids": REQUIREMENTS,
        "extra": {"reason_code": r["reason_code"], "status": r["status"], "urgency": r["urgency"],
                  "classify_method": r["classify_method"], "tokens": r["tokens"], "latency_ms": r.get("latency_ms"),
                  "error": r["error"], "has_response": bool(r["response_text"]),
                  "escalation_context": r["escalation_context"]},
    }
