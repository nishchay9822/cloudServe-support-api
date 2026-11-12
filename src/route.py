"""
Routing: auto_respond or escalate. Satisfies A5 (deterministic, threshold applied).

The decision is plain code - no model call, no randomness - so the same input always
gives the same decision. Order of checks (first match wins):
  1. Safety intent (security / compliance / feature request / unclear) -> escalate
  2. No relevant passages retrieved                                     -> escalate
  3. Classification confidence below the threshold                      -> escalate
  4. Otherwise                                                          -> auto_respond
Every decision carries a human-readable reason and the threshold that was applied.
Escalations carry a context packet (summary + sources + reason), see build_escalation_context().
"""
import os
import re
from typing import Optional

from src import llm
from src.classify import SAFETY_INTENTS
from src.prompts import load_prompt, render

DEFAULT_THRESHOLD = 0.80
CONTEXT_PROMPT_FILE = "prompts/build/route_v1.txt"
CONTEXT_PROMPT_VERSION = "PR-RO-01 v1.0"


def get_threshold() -> float:
    try:
        return float(os.getenv("CONFIDENCE_THRESHOLD", str(DEFAULT_THRESHOLD)))
    except ValueError:
        return DEFAULT_THRESHOLD


def route_ticket(ticket: dict, classification: dict, passages: list, threshold: Optional[float] = None,
                 build_context: bool = False) -> dict:
    """Decide the route. Pure and deterministic unless build_context=True (which only adds the packet)."""
    thr = get_threshold() if threshold is None else float(threshold)
    intent = classification.get("intent")
    conf = float(classification.get("confidence", 0.0) or 0.0)

    if intent in SAFETY_INTENTS:
        decision, code = "escalate", "safety_intent"
        reason = f"Intent '{intent}' is always handled by a human (security, legal/contractual, no documented answer, or too vague)."
    elif not passages:
        decision, code = "escalate", "no_passages"
        reason = "No documentation passage was relevant enough to ground an answer."
    elif conf < thr:
        decision, code = "escalate", "low_confidence"
        reason = f"Classification confidence {conf:.2f} is below the threshold {thr:.2f}."
    else:
        decision, code = "auto_respond", "confident_and_grounded"
        reason = f"Confidence {conf:.2f} meets threshold {thr:.2f}, intent '{intent}' is not safety-restricted, and {len(passages)} relevant passage(s) were found."

    out = {"decision": decision, "reason": reason, "reason_code": code, "threshold_applied": thr,
           "confidence": conf, "escalation_context": None}
    if decision == "escalate" and build_context:
        out["escalation_context"] = build_escalation_context(ticket, classification, passages, reason, thr)
    return out


def _fallback_summary(ticket: dict) -> str:
    text = (ticket.get("subject") or "") + ". " + (ticket.get("body") or "")
    text = re.sub(r"\s+", " ", text).strip()
    return (text[:240] + "...") if len(text) > 240 else text


def build_escalation_context(ticket: dict, classification: dict, passages: list, reason: str, threshold: float) -> dict:
    """Summary + sources + reason, so tier 2 does not start from a raw forwarded ticket (FR-08)."""
    summary, tokens = None, 0
    try:
        system, user = load_prompt(CONTEXT_PROMPT_FILE)
        plist = "\n".join(f"- {p['doc_id']}: {p['title']}" for p in passages[:3]) or "(none)"
        prompt = render(user, channel=ticket.get("channel", ""), subject=ticket.get("subject", ""),
                        ticket_body=(ticket.get("body", "") or "")[:2000], customer_tier=ticket.get("customer_tier", ""),
                        intent=classification.get("intent"), urgency=classification.get("urgency"),
                        confidence=classification.get("confidence"), threshold=threshold, passages=plist)
        out = llm.chat([{"role": "system", "content": system}, {"role": "user", "content": prompt}], max_tokens=200)
        tokens = out["tokens"]
        m = re.search(r"SUMMARY:\s*(.+?)(?:\n\s*REASON|\n\s*RELEVANT|$)", out["text"], flags=re.S | re.I)
        summary = re.sub(r"\s+", " ", m.group(1)).strip() if m else None
    except (llm.LLMUnavailable, ValueError, FileNotFoundError):
        summary = None
    return {
        "summary": summary or _fallback_summary(ticket),
        "summary_source": "llm" if summary else "extract",
        "predicted_intent": classification.get("intent"),
        "predicted_urgency": classification.get("urgency"),
        "confidence": classification.get("confidence"),
        "retrieved_sources": [{"doc_id": p["doc_id"], "title": p["title"], "score": p["score"]} for p in passages[:3]],
        "uncertainty_reason": reason,
        "tokens": tokens,
    }
