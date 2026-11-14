"""
Can the retrieval relevance floor decide 'return nothing because nothing fits'?  (Build Specification, Retrieve: 'returns nothing rather than
something irrelevant'.) Measures how well the score of the best article separates tickets the documentation can answer from those it cannot,
and what each higher floor would do. Result recorded in the report, section 5: the score barely separates them (AUC 0.56 dev, 0.64 validation),
so a higher floor loses answerable tickets about as fast as it removes unanswerable ones.

  venv/bin/python3 evaluation/eval_floor_answerability.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import ingest, retrieve


def auc(pos, neg):
    return sum(1 if p > n else (0.5 if p == n else 0) for p in pos for n in neg) / (len(pos) * len(neg))


for name, f in (("dev", "data/development_tickets.json"), ("val", "data/validation_tickets.json")):
    tickets = json.load(open(os.path.join(ROOT, f)))
    rows = []
    for t in tickets:
        ps = retrieve.retrieve_passages(ingest.normalize_ticket(t)["text"], min_score=0.0)
        rows.append((ps[0]["score"] if ps else 0.0, bool(t["labels"]["answerable_from_docs"]), bool(t["labels"]["must_not_auto_respond"])))
    pos = [r[0] for r in rows if r[1]]
    neg = [r[0] for r in rows if not r[1]]
    print(f"{name}: AUC of the best article's score for 'answerable from the documentation' = {auc(pos, neg):.3f} (answerable {len(pos)}, not {len(neg)})")
    ordinary = [r for r in rows if not r[2]]
    print("  floor | share still answered | of those, answerable | answerable tickets lost")
    for fl in (0.30, 0.35, 0.40, 0.45, 0.50, 0.55):
        kept = [r for r in ordinary if r[0] >= fl]
        print(f"  {fl:.2f}  | {len(kept) / len(ordinary):.3f} | {sum(r[1] for r in kept) / max(1, len(kept)):.3f} | {sum(1 for r in ordinary if r[1] and r[0] < fl)}")
