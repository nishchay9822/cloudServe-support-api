"""Show every stage for one validation ticket: timing, passages, raw answer, guardrail verdicts.
Run: venv/bin/python3 evaluation/debug_ticket.py VAL-0005"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import classify, generate, guardrails, ingest, llm, retrieve, route  # noqa: E402

tid = sys.argv[1]
t = next(x for x in json.load(open("data/validation_tickets.json")) if x["ticket_id"] == tid)
nt = ingest.normalize_ticket(t)
print("TICKET:", nt["text"][:300])
print("EXPECTED DOCS:", t["labels"]["expected_doc_ids"], "route:", t["labels"]["expected_route"])
s = time.time(); c = classify.classify_ticket(nt); print(f"classify {time.time()-s:.1f}s ->", c["intent"], c["confidence"], c["raw"])
s = time.time(); ps = retrieve.retrieve_passages(nt["text"]); print(f"retrieve {time.time()-s:.2f}s ->", [(p["doc_id"], p["score"]) for p in ps])
rd = route.route_ticket(nt, c, ps)
print("route:", rd["decision"], rd["reason_code"])
s = time.time(); g = generate.generate_response(nt, ps, c); print(f"generate {time.time()-s:.1f}s tokens={g['token_count']}")
print("ANSWER:\n", g["answer"])
print("CITATIONS:", g["citations"])
res = guardrails.run_guardrails(g, nt, ps, rd)
print("LLM stats:", llm.stats)
print("PASSAGE USED:\n", ps[0]["passage"] if ps else None)
print("GUARDRAILS:", res["overall_status"], res["blocked_by"])
for k in ("pii", "grounding", "injection", "tone_scope", "confidence_floor"):
    print("  ", k, res[k])
