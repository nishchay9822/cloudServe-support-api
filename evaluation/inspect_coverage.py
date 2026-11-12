"""List replies that miss required points. Run: venv/bin/python3 evaluation/inspect_coverage.py <results.json> [N]"""
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(sys.argv[1]))
n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
gt = {g["ticket_id"]: g for g in json.load(open(os.path.join(ROOT, "data", "ground_truth_responses.json")))}
res = {r["ticket_id"]: r for r in d["results"]}
miss = [(tid, v) for tid, v in d["metrics"]["judge"]["verdicts"].items() if v.get("missing_points")]
print(f"{len(miss)} replies with missing points; intents:", Counter(res[t]["intent"] for t, _ in miss).most_common(6))
for tid, v in miss[:n]:
    print("-" * 80)
    print(tid, res[tid]["intent"], "cited", [c["doc_id"] for c in res[tid]["citations"]], "expected", gt[tid]["expected_doc_ids"])
    print("MUST MENTION:", gt[tid]["must_mention"])
    print("MISSING     :", v["missing_points"])
    print("REPLY       :", (res[tid]["response_text"] or "").split("\n\nThis reply")[0][:420].replace("\n", " "))
