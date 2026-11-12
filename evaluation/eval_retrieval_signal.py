"""
Does the top retrieval score predict that a (non-safety) ticket should be escalated?
Reports AUC and a sweep of an 'auto-respond only if top score >= s' rule on dev and validation.
Run: venv/bin/python3 evaluation/eval_retrieval_signal.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import classify, retrieve  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402

R = retrieve.ROOT


def load(name):
    ts = json.load(open(os.path.join(R, "data", name)))
    return [t for t in ts if t["labels"]["intent"] not in classify.SAFETY_INTENTS]


def top_score(t):
    ps = retrieve.retrieve_passages((t["subject"] + "\n" + t["body"]).strip(), 5, min_score=0.0)
    return ps[0]["score"] if ps else 0.0


for name in ("development_tickets.json", "validation_tickets.json"):
    ts = load(name)
    sc = [top_score(t) for t in ts]
    y_esc = [1 if t["labels"]["expected_route"] == "escalate" else 0 for t in ts]
    auc = roc_auc_score(y_esc, [-s for s in sc])  # low score -> escalate
    print(f"\n{name}: non-safety n={len(ts)}  AUC(low top-score => escalate)={auc:.3f}")
    print("  floor  auto_rate  false_auto  over_escalation  precision_of_auto")
    for s in (0.0, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7):
        auto = [(1 - y) for sc_i, y in zip(sc, y_esc) if sc_i >= s]
        fa = sum(1 for sc_i, y in zip(sc, y_esc) if sc_i >= s and y == 1)
        oe = sum(1 for sc_i, y in zip(sc, y_esc) if sc_i < s and y == 0)
        print(f"  {s:4.2f}   {len(auto)/len(ts):.3f}      {fa:3d}         {oe:3d}              {(len(auto)-fa)/max(len(auto),1):.3f}")
