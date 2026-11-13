"""
End-to-end pipeline as a LangGraph state machine (the orchestrator in the brief's low-level design):

  kill_switch -> ingest -> screen -> classify -> retrieve -> route --(auto)--> generate -> validate -> finalize -> END
        \_____________________________ any escalation or error _____________________________/

Each node is a plain function over a shared state. A conditional edge after every node sends the ticket straight to
`finalize` once it has been escalated, so the escalation packet, telemetry and decision log are written exactly once.

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
from typing import Any, Optional, TypedDict

from langgraph.graph import END, StateGraph

from src import classify, guardrails, ingest, llm, logging_store, retrieve, route, telemetry
from src.generate import PROMPT_VERSION as GEN_VERSION
from src.generate import generate_response

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIREMENTS = ["FR-01", "FR-02", "FR-03", "FR-04", "FR-06", "FR-07", "FR-08", "FR-09", "FR-11", "FR-12"]


def kill_switch_on() -> bool:
    return os.getenv("KILL_SWITCH", "0") == "1" or os.path.exists(os.path.join(ROOT, "storage", "KILL_SWITCH"))


def new_run_id() -> str:
    return datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%S-") + uuid.uuid4().hex[:6]



class State(TypedDict, total=False):
    raw: Any
    run_id: str
    outcome_fcr: Optional[bool]
    exclude_id: Optional[str]
    ban_ids: Optional[set]
    sim_cap: Optional[float]
    log: bool
    t0: float
    r: dict            # the result being built (also the return value)
    ticket: Optional[dict]
    cls: dict
    passages: list
    route_dec: dict
    gen: dict
    done: bool         # True once the ticket must go straight to finalize
    sec_hit: Optional[dict]   # security wording found: still classified and retrieved (so the packet carries sources), then forced to escalate


def _node(fn):
    """Wrap a node so no exception can escape: it becomes a logged escalation (A11)."""
    def wrapped(state: State) -> dict:
        try:
            return fn(state) or {}
        except Exception as e:  # last line of defence: nothing may crash the run
            state["r"].update(status="error", decision="escalate", reason_code="pipeline_error",
                              reason="Unexpected error; ticket escalated to a human.", error=f"{type(e).__name__}: {e}")
            return {"done": True}
    wrapped.__name__ = fn.__name__
    return wrapped


@_node
def n_kill_switch(s: State) -> dict:
    if kill_switch_on():
        s["r"].update(reason="Kill switch is on: all tickets go to humans.", reason_code="kill_switch")
        raw = s["raw"]
        return {"ticket": ingest.normalize_ticket(raw) if isinstance(raw, dict) else None, "done": True}
    return {}


@_node
def n_ingest(s: State) -> dict:
    t = time.time()
    ticket = ingest.normalize_ticket(s["raw"])
    s["r"]["ticket_id"], s["r"]["channel"] = ticket["ticket_id"], ticket["channel"]
    s["r"]["stage_ms"]["ingest"] = _ms(t)
    return {"ticket": ticket}


@_node
def n_screen(s: State) -> dict:
    """Injection screen BEFORE any model sees the text."""
    t = s["ticket"]
    inj = guardrails.check_injection(t["body"] + "\n" + t["subject"])
    if inj["status"] == "block":
        s["r"].update(reason="Ticket text looks like an attempt to instruct the system; handled by a human.",
                      reason_code="injection_screen", guardrails={"injection": inj, "blocked_by": ["injection"]})
        return {"done": True}
    sec = guardrails.check_security_language(t["subject"] + "\n" + t["body"])
    if sec["status"] == "block":
        # Do NOT stop here: classify and retrieve still run so the human receives the relevant articles with the ticket.
        s["r"]["guardrails"] = {"security_language": sec, "blocked_by": ["security_language"]}
        return {"sec_hit": sec}
    return {}


@_node
def n_classify(s: State) -> dict:
    t = time.time()
    cls = classify.classify_ticket(s["ticket"], exclude_id=s.get("exclude_id"), ban_ids=s.get("ban_ids"), sim_cap=s.get("sim_cap"))
    r = s["r"]
    r.update(intent=cls["intent"], urgency=cls["urgency"], confidence=cls["confidence"], classify_method=cls["method"],
             alternatives=cls.get("alternatives") or [])
    r["tokens"] += cls.get("tokens", 0)
    r["stage_ms"]["classify"] = _ms(t)
    r["knn_share"] = (cls.get("raw") or {}).get("knn_share")
    return {"cls": cls}


@_node
def n_retrieve(s: State) -> dict:
    t = time.time()
    r = s["r"]
    try:
        passages = retrieve.retrieve_passages(s["ticket"]["text"])
    except Exception as e:  # vector store problem: degrade to escalation
        passages = []
        r["error"] = f"retrieval failed: {type(e).__name__}"
    r["passages"] = [{"doc_id": p["doc_id"], "score": p["score"]} for p in passages]
    r["stage_ms"]["retrieve"] = _ms(t)
    return {"passages": passages}


@_node
def n_route(s: State) -> dict:
    d = route.route_ticket(s["ticket"], s["cls"], s["passages"])
    sec = s.get("sec_hit")
    if sec:   # security wording overrides every other outcome
        d = dict(d, decision="escalate", reason_code="safety_keyword",
                 reason=f"Security-related wording ('{sec['matched']}'): handled by a human regardless of classification.")
    s["r"].update(decision=d["decision"], reason=d["reason"], reason_code=d["reason_code"])
    return {"route_dec": d, "done": d["decision"] != "auto_respond"}


@_node
def n_generate(s: State) -> dict:
    t = time.time()
    r = s["r"]
    try:
        gen = generate_response(s["ticket"], s["passages"], s["cls"])
    except llm.LLMUnavailable as e:
        r.update(decision="escalate", reason_code="provider_unavailable",
                 reason="The model provider was unavailable, so the ticket goes to a human.", error=str(e))
        return {"done": True}
    r["tokens"] += gen["token_count"]
    r["stage_ms"]["generate"] = _ms(t)
    if gen["declined"]:
        r.update(decision="escalate", reason="The model could not answer from the documentation.", reason_code="model_declined")
        return {"gen": gen, "done": True}
    return {"gen": gen}


@_node
def n_validate(s: State) -> dict:
    """Guardrails run on every generated reply before release and can block it."""
    r, gen = s["r"], s["gen"]
    shown = [p for p in s["passages"] if p["doc_id"] in gen["shown_doc_ids"]]  # exactly what the model saw
    g = guardrails.run_guardrails(gen, s["ticket"], shown, s["route_dec"])
    r["guardrails"] = g
    if g["overall_status"] == "pass":
        r.update(response_text=gen["final_text"], citations=gen["citations"])
    else:
        r.update(decision="escalate", reason_code="guardrail_block", reason=f"Draft blocked by guardrail(s): {', '.join(g['blocked_by'])}.")
    return {}


@_node
def n_finalize(s: State) -> dict:
    r, ticket, cls, passages, route_dec = s["r"], s.get("ticket"), s.get("cls") or {}, s.get("passages") or [], s.get("route_dec") or {}
    if r["decision"] == "escalate" and ticket is not None:
        try:
            thr = route_dec.get("threshold_applied", route.get_threshold())
            r["escalation_context"] = route.build_escalation_context(
                ticket, cls or {"intent": None, "urgency": None, "confidence": None}, passages, r["reason"], thr)
            r["tokens"] += r["escalation_context"].get("tokens", 0)
        except Exception as e:
            r["escalation_context"] = {"summary": (ticket.get("text") or "")[:240], "retrieved_sources": [],
                                       "uncertainty_reason": r["reason"], "error": type(e).__name__}
    r["latency_ms"] = _ms(s["t0"])
    r["threshold_applied"] = route_dec.get("threshold_applied", route.get_threshold())
    telemetry.record(r)
    if s.get("log", True):
        try:
            r["decision_id"] = logging_store.log_decision(_to_decision(r, ticket, s["run_id"]))
            if s.get("outcome_fcr") and r["decision"] == "auto_respond" and r["intent"]:
                logging_store.log_resolution({"run_id": s["run_id"], "ticket_id": r["ticket_id"], "intent": r["intent"],
                                              "doc_ids": [p["doc_id"] for p in r["passages"][:3]], "confidence": r["confidence"],
                                              "customer_tier": (ticket or {}).get("customer_tier"),
                                              "language_fluency": (ticket or {}).get("language_fluency")})
        except Exception as e:
            r["status"] = "log_error"
            r["error"] = f"decision log failed: {type(e).__name__}: {e}"
    return {}


def _after(next_node: str):
    return lambda s: "finalize" if s.get("done") else next_node


def build_graph():
    g = StateGraph(State)
    for name, fn in (("kill_switch", n_kill_switch), ("ingest", n_ingest), ("screen", n_screen), ("classify", n_classify),
                     ("retrieve", n_retrieve), ("route", n_route), ("generate", n_generate), ("validate", n_validate),
                     ("finalize", n_finalize)):
        g.add_node(name, fn)
    g.set_entry_point("kill_switch")
    for a, b in (("kill_switch", "ingest"), ("ingest", "screen"), ("screen", "classify"), ("classify", "retrieve"),
                 ("retrieve", "route"), ("route", "generate"), ("generate", "validate")):
        g.add_conditional_edges(a, _after(b), {b: b, "finalize": "finalize"})
    g.add_edge("validate", "finalize")
    g.add_edge("finalize", END)
    return g.compile()


_GRAPH = build_graph()


def process_ticket(raw: dict, run_id: Optional[str] = None, outcome_fcr: Optional[bool] = None,
                   exclude_id: Optional[str] = None, log: bool = True, ban_ids: Optional[set] = None,
                   sim_cap: Optional[float] = None) -> dict:
    """
    Process one raw ticket through the graph. Always returns a result dict and (if log=True) always writes a decision row.
    `outcome_fcr` simulates the feedback signal for the resolution graph (FR-13); it only decides whether to store a
    resolution record, never the decision. `ban_ids` / `sim_cap` are evaluation-only (simulate unseen wording).
    """
    r = {"ticket_id": (raw or {}).get("ticket_id", "UNKNOWN") if isinstance(raw, dict) else "UNKNOWN",
         "channel": (raw or {}).get("channel") if isinstance(raw, dict) else None,
         "status": "ok", "decision": "escalate", "reason": "", "reason_code": "", "intent": None, "urgency": None,
         "confidence": None, "classify_method": None, "alternatives": [], "passages": [], "response_text": None,
         "citations": [], "escalation_context": None, "guardrails": None, "tokens": 0, "error": None, "stage_ms": {}}
    state: State = {"raw": raw, "run_id": run_id or "adhoc", "outcome_fcr": outcome_fcr, "exclude_id": exclude_id, "ban_ids": ban_ids,
                    "sim_cap": sim_cap, "log": log, "t0": time.time(), "r": r, "ticket": None, "cls": {}, "passages": [],
                    "route_dec": {}, "done": False}
    try:
        _GRAPH.invoke(state)
    except Exception as e:  # the graph itself must never take a run down
        r.update(status="error", decision="escalate", reason_code="pipeline_error", reason="Unexpected error; ticket escalated to a human.",
                 error=f"{type(e).__name__}: {e}")
        r.setdefault("latency_ms", _ms(state["t0"]))
    return r


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
        "alternatives": r.get("alternatives") or [],
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
