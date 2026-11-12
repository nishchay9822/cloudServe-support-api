"""Quick look at the full pipeline on a handful of tickets. Run: venv/bin/python3 evaluation/smoke.py [N]"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///./storage/smoke.db"
from src import pipeline  # noqa: E402

n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
tickets = json.load(open("data/validation_tickets.json"))[:n]
rid = pipeline.new_run_id()
for t in tickets:
    r = pipeline.process_ticket(t, run_id=rid)
    exp = t["labels"]
    print(f"{r['ticket_id']} [{r['channel']:12}] pred={r['intent']:24} true={exp['intent']:24} conf={r['confidence']} "
          f"-> {r['decision']:12} (expected {exp['expected_route']}) {r['reason_code']} {r['latency_ms']}ms {r['stage_ms']}")
    if r["response_text"]:
        print("    REPLY:", r["response_text"][:300].replace("\n", " "))
    if r["guardrails"] and r["guardrails"].get("blocked_by"):
        print("    BLOCKED BY:", r["guardrails"]["blocked_by"], {k: v.get("reason") for k, v in r["guardrails"].items() if isinstance(v, dict) and v.get("status") in ("block", "escalate")})
