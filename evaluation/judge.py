"""
Model-assessed answer quality (prompt PR-EV-01): hallucination, citation resolution, coverage of
required points, prohibited claims. This is ONE assessor (the same small model that writes the
replies) so it is a screening tool, not proof: the harness also writes a CSV for a human second
assessor, and the report states the single-assessor limitation.
"""
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import llm, retrieve  # noqa: E402
from src.prompts import load_prompt, render  # noqa: E402

PROMPT_FILE = "prompts/evaluation/eval_v1.txt"
# A different, stronger model family than the generator, so the assessor is independent of the thing it assesses.
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "openai/gpt-4o-mini")
_JSON = re.compile(r"\{.*\}", re.S)


def judge_one(result: dict, ground_truth: dict = None) -> dict:
    system, user = load_prompt(PROMPT_FILE)
    docs = retrieve._articles()
    shown = [p["doc_id"] for p in result.get("passages", [])[:2]] or [c["doc_id"] for c in result.get("citations", [])]
    passages = "\n\n".join(f"[{d}]\n{docs.get(d, '')}" for d in shown)
    gt = ground_truth or {}
    prompt = render(user, generated_response=result.get("response_text", ""),
                    required_points="\n".join(f"- {x}" for x in gt.get("must_mention", [])) or "(none provided)",
                    must_not_contain="\n".join(f"- {x}" for x in gt.get("must_not_claim", [])) or "(none provided)",
                    passages=passages)
    try:
        out = llm.chat([{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                       max_tokens=350, model=JUDGE_MODEL)
    except llm.LLMUnavailable as e:
        return {"error": str(e)}
    m = _JSON.search(out["text"])
    if not m:
        return {"error": "unparseable judge output"}
    try:
        return json.loads(m.group(0))
    except ValueError:
        return {"error": "unparseable judge output"}


def judge_many(results: list, ground_truth: dict, n: int) -> dict:
    """Judge up to n auto-responded results (evenly spread). Returns per-ticket verdicts and rates."""
    auto = [r for r in results if r["decision"] == "auto_respond" and r.get("response_text")]
    if n <= 0 or not auto:
        return {"n_judged": 0}
    with_gt = [r for r in auto if r["ticket_id"] in ground_truth]  # reference answers make the check stricter
    others = [r for r in auto if r["ticket_id"] not in ground_truth]
    step = max(1, len(others) // max(n - len(with_gt[:n]), 1)) if others else 1
    sample = (with_gt + others[::step])[:n] if len(with_gt) < n else with_gt[:: max(1, len(with_gt) // n)][:n]
    verdicts, errors, causes = {}, 0, {}
    llm.reset_breaker()  # a burst of pipeline calls must not leave the judge locked out
    for r in sample:
        v = {"error": "not attempted"}
        for attempt in range(4):          # pace the calls and retry transient provider errors
            time.sleep(0.4 if attempt == 0 else 3.0 * attempt)
            llm.reset_breaker()
            v = judge_one(r, ground_truth.get(r["ticket_id"]))
            if "error" not in v:
                break
        if "error" in v:
            errors += 1
            causes[v["error"]] = causes.get(v["error"], 0) + 1
            continue
        verdicts[r["ticket_id"]] = v
    vals = list(verdicts.values())
    k = len(vals)

    def rate(field, want=True):
        return round(sum(1 for v in vals if bool(v.get(field)) == want) / k, 4) if k else None
    return {"n_judged": k, "judge_errors": errors, "judge_error_causes": causes, "n_with_reference_answer": sum(1 for tid in verdicts if tid in ground_truth),
            "assessor": f"{JUDGE_MODEL} (independent model; a human second assessor is still required)",
            "hallucination_rate": rate("hallucinations_detected", True),
            "all_citations_resolve_rate": rate("all_citations_resolve", True),
            "prohibited_claims_rate": rate("makes_prohibited_claims", True),
            "coverage_of_required_points_rate": rate("covers_required_points", True),
            "pass_rate": round(sum(1 for v in vals if str(v.get("overall_verdict", "")).lower() == "pass") / k, 4) if k else None,
            "verdicts": verdicts}
