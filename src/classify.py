"""
Classification: intent (22 classes), urgency, and a calibrated confidence. Satisfies A3.

Two signals are combined:
  1. LLM classifier (prompt PR-CL-01 v2.0) - reads the ticket, self-reports confidence.
  2. kNN classifier over the labelled development tickets (local embeddings, deterministic).

The kNN is (a) the fallback when the provider is down, and (b) an independent check:
when both signals agree the answer is far more likely to be right. Raw LLM confidence is
not trusted on its own; final confidence is calibrated against labelled data
(see evaluation/calibrate.py and data/calibration.json).
"""
import json
import math
import os
import re
from collections import defaultdict
from typing import Optional

from src import llm
from src.prompts import load_prompt, render
from src import retrieve

INTENT_CLASSES = [
    "account_access", "api_key_issue", "api_usage_question", "authentication_failure", "billing_query",
    "compliance_request", "configuration_help", "data_export", "data_residency", "database_issue",
    "deployment_failure", "feature_request", "integration_help", "onboarding", "performance_degradation",
    "quota_or_overage", "rate_limit", "rollback_request", "security_incident", "sso_configuration",
    "unclear_request", "webhook_issue",
]
URGENCY_LEVELS = ["high", "medium", "low"]

# Intents that must always go to a human (security, legal/contractual, nothing to retrieve, or too vague).
# Derived from the discovery evidence: these four intents are exactly the tickets flagged must_not_auto_respond.
SAFETY_INTENTS = {"security_incident", "compliance_request", "feature_request", "unclear_request"}

PROMPT_VERSION = "PR-CL-01 v2.0"
PROMPT_FILE = "prompts/build/classify_v2.txt"
TICKET_COLLECTION = "dev_tickets_v3"  # v3 stores each neighbour's answerable and expected-route labels
KNN_K = int(os.getenv("KNN_K", "7"))
KNN_TRUST = float(os.getenv("KNN_TRUST", "0.85"))  # at/above this neighbour-vote share the LLM is not consulted

# Confidence for a kNN-only decision, by neighbour-vote share. Measured with evaluation/eval_knn.py
# (dev leave-one-out, n=500) and smoothed with a Laplace (k+1)/(n+2) correction so small bins are not
# over-trusted: share>=0.85: 473/473 correct; 0.75-0.85: 17/17; 0.60-0.75: 9/9; <0.60: 0/1.
KNN_CONFIDENCE_BINS = [(0.85, 0.99), (0.75, 0.947), (0.60, 0.909), (0.0, 0.333)]


def knn_confidence(share: float) -> float:
    for floor, conf in KNN_CONFIDENCE_BINS:
        if share >= floor:
            return conf
    return 0.333
CALIBRATION_PATH = os.path.join(retrieve.ROOT, "data", "calibration.json")
DEV_PATH = os.path.join(retrieve.ROOT, "data", "development_tickets.json")


# --------------------------------------------------------------------------- kNN
def ensure_ticket_index() -> None:
    client = retrieve.get_client()
    try:
        col = client.get_collection(TICKET_COLLECTION, embedding_function=retrieve._ef())
        if col.count() > 0:
            return
    except Exception:
        pass
    try:
        client.delete_collection(TICKET_COLLECTION)
    except Exception:
        pass
    col = client.create_collection(TICKET_COLLECTION, embedding_function=retrieve._ef(), metadata={"hnsw:space": "cosine"})
    tickets = json.load(open(DEV_PATH, encoding="utf-8"))
    col.add(
        ids=[t["ticket_id"] for t in tickets],
        documents=[(t.get("subject", "") + "\n" + t.get("body", "")).strip() or "(empty)" for t in tickets],
        metadatas=[{"intent": t["labels"]["intent"], "urgency": t["labels"]["urgency"],
                    "answerable": 1 if t["labels"].get("answerable_from_docs") else 0,
                    "esc": 1 if t["labels"].get("expected_route") == "escalate" else 0} for t in tickets],
    )


def classify_knn(ticket: dict, exclude_id: Optional[str] = None, k: int = KNN_K) -> dict:
    """Distance-weighted vote of the k nearest labelled dev tickets."""
    ensure_ticket_index()
    col = retrieve.get_client().get_collection(TICKET_COLLECTION, embedding_function=retrieve._ef())
    res = col.query(query_texts=[ticket.get("text") or "(empty)"], n_results=k + 1)
    votes, uvotes, ans_w, esc_w = defaultdict(float), defaultdict(float), 0.0, 0.0
    used = 0
    for tid, meta, dist in zip(res["ids"][0], res["metadatas"][0], res["distances"][0]):
        if exclude_id and tid == exclude_id:
            continue
        if used >= k:
            break
        w = max(1.0 - float(dist), 0.01)
        votes[meta["intent"]] += w
        uvotes[meta["urgency"]] += w
        ans_w += w * meta.get("answerable", 0)
        esc_w += w * meta.get("esc", 0)
        used += 1
    total = sum(votes.values()) or 1.0
    ranked = sorted(votes.items(), key=lambda kv: -kv[1])
    intent, score = ranked[0]
    return {
        "intent": intent,
        "share": round(score / total, 4),
        "answerable_share": round(ans_w / total, 4),  # weighted share of similar past tickets the docs could answer
        "escalate_share": round(esc_w / total, 4),    # weighted share of similar past tickets that were escalated
        "urgency": max(uvotes.items(), key=lambda kv: kv[1])[0] if uvotes else "medium",
        "alternatives": [{"intent": i, "confidence": round(s / total, 4)} for i, s in ranked[1:3]],
    }


# --------------------------------------------------------------------------- LLM
_JSON = re.compile(r"\{.*?\}", re.S)


def _parse_llm(text: str) -> Optional[dict]:
    for m in _JSON.finditer(text or ""):
        try:
            obj = json.loads(m.group(0))
        except ValueError:
            continue
        if isinstance(obj, dict) and "intent" in obj:
            return obj
    return None


def classify_llm(ticket: dict) -> dict:
    """Raises llm.LLMUnavailable if the provider cannot be used."""
    system, user = load_prompt(PROMPT_FILE)
    body = render(user, channel=ticket.get("channel", ""), subject=ticket.get("subject", ""),
                  ticket_body=(ticket.get("body", "") or "")[:2500])
    out = llm.chat([{"role": "system", "content": system}, {"role": "user", "content": body}], max_tokens=120)
    obj = _parse_llm(out["text"])
    if obj is None:
        raise llm.LLMUnavailable("model returned unparseable classification")
    intent = str(obj.get("intent", "")).strip()
    if intent not in INTENT_CLASSES:
        intent = "unclear_request"
        obj["confidence"] = min(float(obj.get("confidence", 0.3) or 0.3), 0.3)
    urgency = str(obj.get("urgency", "medium")).strip().lower()
    if urgency not in URGENCY_LEVELS:
        urgency = "medium"
    try:
        conf = float(obj.get("confidence", 0.5))
    except (TypeError, ValueError):
        conf = 0.5
    second = str(obj.get("second_choice", "")).strip()
    return {"intent": intent, "urgency": urgency, "confidence": max(0.0, min(1.0, conf)),
            "second_choice": second if second in INTENT_CLASSES else None, "tokens": out["tokens"]}


# --------------------------------------------------------------------------- calibration
_calib = {"loaded": False, "coef": None}


def _load_calibration():
    if not _calib["loaded"]:
        _calib["loaded"] = True
        if os.path.exists(CALIBRATION_PATH):
            try:
                _calib["coef"] = json.load(open(CALIBRATION_PATH))
            except ValueError:
                _calib["coef"] = None
    return _calib["coef"]


def calibrated_confidence(llm_conf: float, agree: bool, knn_share: float) -> float:
    """
    Map raw signals to a probability that the intent is correct.
    Uses logistic coefficients fitted on labelled data when available (data/calibration.json);
    otherwise a conservative heuristic.
    """
    coef = _load_calibration()
    if coef:
        z = (coef["intercept"] + coef["w_llm"] * llm_conf + coef["w_agree"] * (1.0 if agree else 0.0)
             + coef["w_knn"] * knn_share)
        return round(min(0.99, 1.0 / (1.0 + math.exp(-z))), 4)
    base = 0.5 * llm_conf + 0.5 * knn_share
    return round(min(0.95, base if agree else base * 0.6), 4)


# --------------------------------------------------------------------------- public API
def classify_ticket(ticket: dict, exclude_id: Optional[str] = None, use_llm: bool = True) -> dict:
    """
    Classify a normalised ticket. Never raises for provider problems: falls back to kNN, and if
    that fails too returns unclear_request with confidence 0 so the ticket escalates.
    """
    if ticket.get("is_empty"):
        return {"intent": "unclear_request", "urgency": "low", "confidence": 0.99, "alternatives": [],
                "method": "empty_ticket", "prompt_version": PROMPT_VERSION, "tokens": 0,
                "raw": {"llm_confidence": None, "knn_share": None, "agree": None}}
    knn = None
    try:
        knn = classify_knn(ticket, exclude_id=exclude_id)
    except Exception:
        knn = None

    # Fast path: a strong, unanimous neighbour vote needs no model call (about 95% of tickets).
    if knn and knn["share"] >= KNN_TRUST:
        return {"intent": knn["intent"], "urgency": knn["urgency"], "confidence": knn_confidence(knn["share"]),
                "alternatives": knn["alternatives"], "method": "knn", "prompt_version": "knn-v1", "tokens": 0,
                "raw": {"llm_confidence": None, "knn_share": knn["share"], "agree": None}}

    llm_res = None
    if use_llm:
        try:
            llm_res = classify_llm(ticket)
        except llm.LLMUnavailable:
            llm_res = None

    if llm_res and knn:
        agree = llm_res["intent"] == knn["intent"]
        conf = calibrated_confidence(llm_res["confidence"], agree, knn["share"] if agree else 0.0)
        alts = []
        if llm_res.get("second_choice"):
            alts.append({"intent": llm_res["second_choice"], "confidence": None})
        if not agree:
            alts.insert(0, {"intent": knn["intent"], "confidence": knn["share"]})
        return {"intent": llm_res["intent"], "urgency": llm_res["urgency"], "confidence": conf,
                "alternatives": alts[:2], "method": "llm+knn", "prompt_version": PROMPT_VERSION,
                "tokens": llm_res["tokens"],
                "raw": {"llm_confidence": llm_res["confidence"], "knn_share": knn["share"], "agree": agree}}
    if llm_res:  # kNN unavailable
        return {"intent": llm_res["intent"], "urgency": llm_res["urgency"],
                "confidence": round(min(llm_res["confidence"], 0.7), 4), "alternatives": [],
                "method": "llm_only", "prompt_version": PROMPT_VERSION, "tokens": llm_res["tokens"],
                "raw": {"llm_confidence": llm_res["confidence"], "knn_share": None, "agree": None}}
    if knn:  # ambiguous ticket and the provider is down: use the kNN answer with its measured confidence
        return {"intent": knn["intent"], "urgency": knn["urgency"], "confidence": knn_confidence(knn["share"]),
                "alternatives": knn["alternatives"], "method": "knn_fallback", "prompt_version": "knn-fallback",
                "tokens": 0, "raw": {"llm_confidence": None, "knn_share": knn["share"], "agree": None}}
    return {"intent": "unclear_request", "urgency": "medium", "confidence": 0.0, "alternatives": [],
            "method": "unavailable", "prompt_version": "none", "tokens": 0,
            "raw": {"llm_confidence": None, "knn_share": None, "agree": None}}
