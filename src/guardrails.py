"""
Five guardrails. Satisfies A7: every one of them runs on every response and can block it.

 1. PII          customer identifiers, emails, phone numbers, keys in the outbound text
 2. Grounding    citations must resolve to retrieved passages and claims must be supported by them
 3. Injection    the customer's ticket tries to give the system instructions
 4. Tone/scope   the reply commits to refunds, credits, guarantees or timelines
 5. Confidence   auto-response without the routing threshold having been applied

There is no flag that disables them.
"""
import re
from typing import Optional

CITE = re.compile(r"\[(DOC-[A-Z]+-\d+)\]")
_WORD = re.compile(r"[a-z0-9_./-]+")
_STOP = set("a an the and or but if then of to in on at for with by from is are was were be been being it its this that "
            "these those as you your we our can will would should could may might do does did not no yes so than also "
            "have has had into out up down over under again once only just more most some any each other such "
            "please thanks thank hello hi dear regards use using used see check make sure".split())

# ------------------------------------------------------------------ 1. PII
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE = re.compile(r"(?<!\w)\+?\d[\d\s().-]{8,}\d(?!\w)")
_CUSTID = re.compile(r"\bCUST-\d+\b", re.I)
_KEY = re.compile(r"\b(?:sk|pk|api|key|tok|secret)[-_][A-Za-z0-9_-]{12,}\b", re.I)
_CARD = re.compile(r"\b(?:\d[ -]?){13,16}\b")


def check_pii(response_text: str, ticket: Optional[dict] = None, passages: Optional[list] = None) -> dict:
    allowed = " ".join((p.get("full_text") or p.get("passage", "")) for p in (passages or []))
    found = []
    for name, rx in (("email", _EMAIL), ("customer_id", _CUSTID), ("api_key", _KEY)):
        for m in rx.finditer(response_text):
            if m.group(0) not in allowed:  # strings quoted from documentation are not customer data
                found.append(name)
    for m in _PHONE.finditer(response_text):
        if sum(c.isdigit() for c in m.group(0)) >= 10 and m.group(0) not in allowed:
            found.append("phone")
    for m in _CARD.finditer(CITE.sub("", response_text)):
        if sum(c.isdigit() for c in m.group(0)) >= 13 and m.group(0) not in allowed:
            found.append("card_number")
    t = ticket or {}
    for field in ("customer_name", "customer_id"):
        val = (t.get(field) or "").strip()
        if len(val) >= 4 and val.lower() in response_text.lower() and val not in allowed:
            found.append(field)
    found = sorted(set(found))
    return {"status": "block" if found else "pass",
            "reason": f"PII detected: {', '.join(found)}" if found else "no PII detected",
            "detected_patterns": found}


# ------------------------------------------------------------------ 2. Grounding
def _tokens(text: str) -> set:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOP and len(w) > 2}


def _numbers(text: str) -> set:
    return set(re.findall(r"\b\d+(?:\.\d+)?\b", text))


def check_grounding(response_text: str, passages: list, ticket_text: str = "") -> dict:
    body = re.sub(r"\n\s*This reply was drafted automatically.*$", "", response_text, flags=re.S)
    cited = CITE.findall(body)
    ids = {p["doc_id"] for p in passages}
    if not passages:
        return {"status": "block", "reason": "no retrieved passages to ground the answer", "ungrounded_claims": ["<all>"]}
    if not cited:
        return {"status": "block", "reason": "answer contains no citation", "ungrounded_claims": ["<no citation>"]}
    unresolved = sorted({c for c in cited if c not in ids})
    if unresolved:
        return {"status": "block", "reason": f"citation(s) do not resolve to retrieved passages: {unresolved}",
                "ungrounded_claims": unresolved}

    source = " ".join((p.get("full_text") or p["passage"]) for p in passages)
    # Numbers the customer wrote themselves (a time, a size) may be echoed back; they are not claims about the product.
    source_tokens, source_numbers = _tokens(source), _numbers(source) | _numbers(ticket_text)
    clean = CITE.sub("", body)
    all_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", clean) if s.strip()]
    sentences = [s for s in all_sentences if len(s.split()) >= 6]   # support check needs enough words to be meaningful
    weak, bad_numbers = [], []
    for s in sentences:
        toks = _tokens(s)
        if toks and len(toks & source_tokens) / len(toks) < 0.45:
            weak.append(s[:120])
    for s in all_sentences:                                          # figures are checked in EVERY sentence, however short
        extra = _numbers(s) - source_numbers
        if extra:
            bad_numbers.append(f"{sorted(extra)} in: {s[:80]}")
    if bad_numbers:
        return {"status": "block", "reason": "figures not present in the cited documentation", "ungrounded_claims": bad_numbers}
    if sentences and len(weak) / len(sentences) > 0.4:
        return {"status": "block", "reason": "too much of the answer is not supported by the passages", "ungrounded_claims": weak}
    return {"status": "pass", "reason": "citations resolve and claims are supported", "ungrounded_claims": []}


# ------------------------------------------------------------------ 3. Injection
_INJECTION = [r"ignore (all |any |the )?(previous|prior|above|earlier) (instructions|prompts?|rules)",
              r"disregard (all |any |the )?(previous|prior|above|earlier|your) ", r"forget (everything|your instructions|all previous)",
              r"you are now\b", r"\bact as (a|an|the)\b", r"pretend (to be|you are)", r"system prompt", r"reveal (your|the) (prompt|instructions)",
              r"developer mode", r"jailbreak", r"new instructions?:", r"override (your|the|all) ", r"<\|.*?\|>", r"\[/?(system|inst)\]"]
_INJ_RX = [re.compile(p, re.I) for p in _INJECTION]


def check_injection(ticket_body: str, system_prompt: str = "") -> dict:
    hits = [rx.pattern for rx in _INJ_RX if rx.search(ticket_body or "")]
    return {"status": "block" if hits else "pass",
            "reason": "ticket text attempts to instruct the system" if hits else "no instruction-like text in ticket",
            "suspicious_patterns": hits}


# ------------------------------------------------------------------ 4. Tone / scope
_COMMIT = [r"\bwe (will|'ll|can) (refund|credit|waive|reimburse|compensate)", r"\byou (will|'ll) (be )?(refunded|credited|reimbursed)",
           r"\bguarantee[sd]?\b", r"\bi promise\b", r"\bwe promise\b", r"\bfull refund\b",
           r"\bwithin \d+ (business )?(minutes|hours|days)\b.{0,40}\b(we|our team|support)\b",
           r"\b(we|our team) will (fix|resolve|have)\b.{0,40}\b(today|tomorrow|by|within)\b", r"\bsla (credit|breach|exception)\b",
           r"\bno charge\b", r"\bfree of charge\b", r"\bon the house\b"]
_COM_RX = [re.compile(p, re.I) for p in _COMMIT]


def check_tone_scope(response_text: str) -> dict:
    hits = [m.group(0) for rx in _COM_RX for m in rx.finditer(response_text)]
    return {"status": "block" if hits else "pass",
            "reason": "reply makes a commitment about money or timelines" if hits else "no commitments found",
            "flagged_phrases": hits}


# ------------------------------------------------------------------ 5. Confidence floor
def check_confidence_floor(routing_decision: dict, threshold: Optional[float] = None) -> dict:
    thr = routing_decision.get("threshold_applied")
    if thr is None:
        return {"status": "escalate", "reason": "routing decision records no threshold"}
    if routing_decision.get("decision") == "auto_respond" and float(routing_decision.get("confidence", 0)) < float(thr):
        return {"status": "escalate", "reason": "auto-response issued below the confidence threshold"}
    return {"status": "pass", "reason": f"threshold {thr} was applied"}


# ------------------------------------------------------------------ combined
def run_guardrails(response: dict, ticket: dict, passages: list, routing_decision: dict) -> dict:
    text = response.get("final_text") or response.get("answer") or ""
    results = {
        "pii": check_pii(text, ticket, passages),
        "grounding": check_grounding(text, passages, (ticket.get("subject", "") + " " + ticket.get("body", ""))),
        "injection": check_injection(ticket.get("body", "") + "\n" + ticket.get("subject", "")),
        "tone_scope": check_tone_scope(text),
        "confidence_floor": check_confidence_floor(routing_decision),
    }
    blocked = [name for name, r in results.items() if r["status"] in ("block", "escalate")]
    if not blocked:
        status, action = "pass", "send_response"
    else:
        status, action = "block", "block_and_escalate"
    return {"overall_status": status, "action": action, "blocked_by": blocked, **results}


# Second line of defence for the most costly mistake: a security incident answered as if it were an ordinary ticket.
# The nearest-neighbour classifier can be confidently wrong on unfamiliar wording ("a former employee still has access" looks
# like an account-access ticket), so clearly security-related language escalates regardless of the predicted intent.
# Chosen on the development tickets: catches 25 of 30 security incidents and none of 479 ordinary tickets. Generic compliance
# words (compliance, GDPR) were tried and left out: they only fired on data-residency questions, which the system can answer.
_SECURITY_TERMS = [r"still has? access", r"unauthori[sz]ed", r"\bbreach", r"compromis", r"\bleak(ed|ing)?\b", r"\bstolen\b",
                   r"suspicious", r"\bformer employee", r"ex-employee", r"\bintrusion", r"\bphishing", r"\bexfiltrat",
                   r"vulnerabilit", r"\bcve-\d", r"\bpen ?test"]
_SECURITY_RX = re.compile("|".join(_SECURITY_TERMS), re.I)


def check_security_language(ticket_text: str) -> dict:
    m = _SECURITY_RX.search(ticket_text or "")
    if m:
        return {"status": "block", "matched": m.group(0).lower(), "reason": "security-related wording: always handled by a human"}
    return {"status": "pass", "matched": None}

