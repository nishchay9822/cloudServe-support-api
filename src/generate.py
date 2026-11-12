"""
Grounded answer generation with citations. Satisfies A6.

The model only sees the retrieved passages. Citations are parsed out of the answer and
resolved against those same passages; anything that does not resolve is reported so the
grounding guardrail can block it. Generation is refused when there are no passages.
"""
import re

from src import llm
from src.prompts import load_prompt, render

PROMPT_VERSION = "PR-GN-01 v3.0"
PROMPT_FILE = "prompts/build/generate_v3.txt"
MAX_PASSAGES = 2          # the model sees at most this many whole articles
RELATIVE_SCORE = 0.60     # a second article is only shown if it scores at least this fraction of the best one
CITE = re.compile(r"\[(DOC-[A-Z]+-\d+)\]")


def select_for_generation(passages: list) -> list:
    """Top article plus any close runner-up; drops low-scoring distractors that invite wrong citations."""
    if not passages:
        return []
    top = passages[0]["score"]
    chosen = [p for p in passages if p["score"] >= RELATIVE_SCORE * top]
    return chosen[:MAX_PASSAGES]
DISCLOSURE = ("This reply was drafted automatically from our documentation. "
              "If it does not solve the problem, reply and a member of the support team will take over.")


def _passage_block(passages: list) -> str:
    return "\n\n".join(f"[{p['doc_id']}] {p['title']}\n{p.get('full_text') or p['passage']}" for p in passages)


def extract_citations(text: str, passages: list) -> list:
    by_id = {p["doc_id"]: p for p in passages}
    out, seen = [], set()
    for did in CITE.findall(text or ""):
        if did in seen:
            continue
        seen.add(did)
        p = by_id.get(did)
        out.append({"doc_id": did, "resolves": p is not None,
                    "passage_excerpt": (p["passage"][:160].replace("\n", " ") if p else None)})
    return out


def generate_response(ticket: dict, passages: list, classification: dict = None) -> dict:
    """
    Raises ValueError if passages is empty, llm.LLMUnavailable if the provider cannot be used.
    """
    if not passages:
        raise ValueError("Cannot generate a response without retrieved passages; escalate instead.")
    passages = select_for_generation(passages)  # the same list is what citations are resolved against
    system, user = load_prompt(PROMPT_FILE)
    prompt = render(user, channel=ticket.get("channel", ""), subject=ticket.get("subject", ""),
                    ticket_body=(ticket.get("body", "") or "")[:2500], customer_tier=ticket.get("customer_tier", ""),
                    passages=_passage_block(passages))
    out = llm.chat([{"role": "system", "content": system}, {"role": "user", "content": prompt}], max_tokens=380)
    answer = out["text"].strip()
    declined = answer.upper().startswith("NO_ANSWER") or not answer
    if not declined:  # tidy a stray sentinel the model may have appended after a real answer
        answer = re.sub(r"\s*NO_ANSWER\.?\s*$", "", answer).strip()
    return {
        "answer": answer,
        "final_text": f"{answer}\n\n{DISCLOSURE}",
        "citations": extract_citations(answer, passages),
        "shown_doc_ids": [p["doc_id"] for p in passages],
        "model_used": llm.model_name(),
        "prompt_version": PROMPT_VERSION,
        "token_count": out["tokens"],
        "declined": declined,
    }
