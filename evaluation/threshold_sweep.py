"""
Threshold selection analysis (brief section 5: 'the thresholds are yours to set and yours to defend').
Replays the routing rule from a saved run at different confidence thresholds, using the stored intent, confidence and
retrieved passages. No model calls. Approximation: it ignores later model declines and guardrail blocks, which are rare.

  venv/bin/python3 evaluation/threshold_sweep.py --run evaluation/results/dev_run.json --tickets data/development_tickets.json
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src.route import SAFETY_INTENTS

THRESHOLDS = [0.0, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]


def sweep(results: list, tickets: dict) -> list:
    out = []
    for thr in THRESHOLDS:
        n = auto = false_auto = good_auto = over_esc = correct = 0
        for r in results:
            t = tickets.get(r["ticket_id"])
            if not t:
                continue
            exp = t["labels"]["expected_route"]
            go = (r.get("intent") not in SAFETY_INTENTS) and bool(r.get("passages")) and (r.get("confidence") or 0) >= thr
            n += 1
            auto += go
            correct += (go and exp == "auto_respond") or ((not go) and exp == "escalate")
            false_auto += go and exp == "escalate"
            good_auto += go and exp == "auto_respond"
            over_esc += (not go) and exp == "auto_respond"
        out.append({"threshold": thr, "n": n, "auto_rate": round(auto / n, 4), "auto_precision": round(good_auto / auto, 4) if auto else None,
                    "false_auto": false_auto, "over_escalation": over_esc, "route_accuracy": round(correct / n, 4)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--tickets", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    results = json.load(open(a.run))["results"]
    tickets = {t["ticket_id"]: t for t in json.load(open(a.tickets))}
    table = sweep(results, tickets)
    print("thr   auto_rate  precision  false_auto  over_esc  route_acc")
    for x in table:
        print(f"{x['threshold']:<5} {x['auto_rate']:<10} {x['auto_precision']!s:<10} {x['false_auto']:<11} {x['over_escalation']:<9} {x['route_accuracy']}")
    if a.out:
        json.dump(table, open(a.out, "w"), indent=2)


if __name__ == "__main__":
    main()
