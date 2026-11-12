"""
Sweep the answerability threshold for routing and report the trade-off.

 false_auto      = system auto-responds where the label says escalate (the costly error: a wrong/unsafe reply)
 over_escalation = system escalates where the label says auto_respond (lost automation, not a harm)

Dev is leave-one-out; validation is a clean hold-out (kNN built from dev only).
Run: venv/bin/python3 evaluation/eval_routing.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import classify, ingest, retrieve  # noqa: E402

R = retrieve.ROOT
dev = json.load(open(os.path.join(R, "data", "development_tickets.json")))
val = json.load(open(os.path.join(R, "data", "validation_tickets.json")))
classify.ensure_ticket_index()


def collect(tickets, loo):
    out = []
    for t in tickets:
        k = classify.classify_knn(ingest.normalize_ticket(t), exclude_id=t["ticket_id"] if loo else None)
        out.append((t, k))
    return out


def decide(k, tau, conf_thr=0.80):
    if k["intent"] in classify.SAFETY_INTENTS:
        return "escalate"
    if classify.knn_confidence(k["share"]) < conf_thr:
        return "escalate"
    return "escalate" if k["escalate_share"] >= tau else "auto_respond"


def report(rows, name):
    n = len(rows)
    exp_auto = sum(1 for t, _ in rows if t["labels"]["expected_route"] == "auto_respond")
    print(f"\n{name}: n={n}, labelled auto_respond={exp_auto} ({exp_auto/n:.0%})")
    print("  tau   route_acc  auto_rate  false_auto  over_escalation  precision_of_auto")
    for tau in (1.01, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1):  # tau = escalate-vote share needed to escalate
        dec = [(decide(k, tau), t["labels"]["expected_route"]) for t, k in rows]
        acc = sum(d == e for d, e in dec) / n
        auto = [e for d, e in dec if d == "auto_respond"]
        fa = sum(1 for d, e in dec if d == "auto_respond" and e == "escalate")
        oe = sum(1 for d, e in dec if d == "escalate" and e == "auto_respond")
        prec = (len(auto) - fa) / len(auto) if auto else float("nan")
        print(f"  {tau:4.2f}   {acc:.3f}     {len(auto)/n:.3f}      {fa:3d}         {oe:3d}              {prec:.3f}")


report(collect(dev, True), "DEV leave-one-out")
report(collect(val, False), "VAL hold-out")
