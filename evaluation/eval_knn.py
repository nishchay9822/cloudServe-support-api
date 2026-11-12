"""
How good is the deterministic kNN alone? Leave-one-out on dev (500) and clean hold-out on validation (80).
Also: urgency accuracy vs a 'majority urgency per intent' baseline, and accuracy by neighbour-vote share.
Run: venv/bin/python3 evaluation/eval_knn.py
"""
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import classify, ingest, retrieve  # noqa: E402

R = retrieve.ROOT
dev = json.load(open(os.path.join(R, "data", "development_tickets.json")))
val = json.load(open(os.path.join(R, "data", "validation_tickets.json")))
classify.ensure_ticket_index()

# majority urgency per intent (baseline)
by_int = defaultdict(Counter)
for t in dev:
    by_int[t["labels"]["intent"]][t["labels"]["urgency"]] += 1
maj = {k: v.most_common(1)[0][0] for k, v in by_int.items()}


def run(tickets, loo, name):
    rows = []
    for t in tickets:
        nt = ingest.normalize_ticket(t)
        k = classify.classify_knn(nt, exclude_id=t["ticket_id"] if loo else None)
        rows.append((t, k))
    n = len(rows)
    ia = sum(k["intent"] == t["labels"]["intent"] for t, k in rows) / n
    ua = sum(k["urgency"] == t["labels"]["urgency"] for t, k in rows) / n
    base = sum(maj[t["labels"]["intent"]] == t["labels"]["urgency"] for t, k in rows) / n
    print(f"{name}: n={n} kNN intent_acc={ia:.3f} kNN urgency_acc={ua:.3f} (majority-urgency-given-true-intent baseline={base:.3f})")
    for lo, hi in ((0, .6), (.6, .75), (.75, .85), (.85, .95), (.95, 1.01)):
        b = [(t, k) for t, k in rows if lo <= k["share"] < hi]
        if b:
            print(f"   share [{lo},{min(hi,1):.2f}) n={len(b):3d} intent_acc={sum(k['intent']==t['labels']['intent'] for t,k in b)/len(b):.3f}")
    wrong = [(t["ticket_id"], t["labels"]["intent"], k["intent"], t["body"][:70]) for t, k in rows if k["intent"] != t["labels"]["intent"]]
    for w in wrong[:6]:
        print("   miss:", w)


run(dev, True, "DEV (leave-one-out)")
run(val, False, "VAL (hold-out)")
print("urgency label distribution by true intent (dev):", {k: dict(v) for k, v in list(by_int.items())[:4]})
