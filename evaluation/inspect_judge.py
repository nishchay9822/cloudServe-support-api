"""Show what the judge flagged, next to the reply and the source article. Run: venv/bin/python3 evaluation/inspect_judge.py <results.json>"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import retrieve  # noqa: E402

d = json.load(open(sys.argv[1]))
res = {r["ticket_id"]: r for r in d["results"]}
docs = retrieve._articles()
for tid, v in (d["metrics"].get("judge") or {}).get("verdicts", {}).items():
    if v.get("hallucinations_detected") or v.get("makes_prohibited_claims") or not v.get("all_citations_resolve", True):
        r = res[tid]
        print("=" * 90)
        print(tid, "| intent:", r["intent"], "| cited:", [c["doc_id"] for c in r["citations"]])
        print("REPLY:", (r["response_text"] or "").split("\n\nThis reply")[0])
        print("JUDGE: hallucinated_facts =", v.get("hallucinated_facts"), "| missing =", v.get("missing_points"))
        for c in r["citations"][:1]:
            print("SOURCE", c["doc_id"], ":", docs.get(c["doc_id"], "")[:700].replace("\n", " "))
