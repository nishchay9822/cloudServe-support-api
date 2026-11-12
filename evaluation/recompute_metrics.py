"""
Re-derive the metric blocks of a saved run from its stored per-ticket results, without calling any model.
Used when a metric definition is extended after a run (for example adding the mean response time the spec asks for).
Only pure metric functions run; decisions, replies and judge verdicts are untouched.
  venv/bin/python3 evaluation/recompute_metrics.py --run evaluation/results/dev_run.json --tickets data/development_tickets.json
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from evaluation import metrics as M


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--tickets", required=True)
    a = ap.parse_args()
    run = json.load(open(a.run))
    by_id = {t["ticket_id"]: t for t in json.load(open(a.tickets))}
    rows = [(r, by_id.get(r["ticket_id"], {})) for r in run["results"]]
    run["metrics"]["latency"] = M.latency_metrics(rows)
    run["metrics"]["business"] = M.business_proxies(rows)
    json.dump(run, open(a.run, "w"), indent=2)
    print("updated latency and business blocks in", a.run)


if __name__ == "__main__":
    main()
