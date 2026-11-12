#!/usr/bin/env python3
"""
Re-run only the answer-quality judge on a saved results file (no pipeline re-run) and refresh its report.
    python evaluation/rejudge.py evaluation/results/gate_run_validation.json --n 50
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from evaluation import harness  # noqa: E402
from evaluation.judge import judge_many  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("results")
ap.add_argument("--n", type=int, default=50)
args = ap.parse_args()

d = json.load(open(args.results, encoding="utf-8"))
gt = harness.load_ground_truth(os.path.join(ROOT, "data", "ground_truth_responses.json"))
d["metrics"]["judge"] = judge_many(d["results"], gt, args.n)
json.dump(d, open(args.results, "w", encoding="utf-8"), indent=2, default=str)
stem = os.path.splitext(args.results)[0]
open(stem + ".md", "w", encoding="utf-8").write(harness.render_report(d["metrics"]))
harness.write_review_csv(stem + "_human_review.csv", d["results"], d["metrics"]["judge"]["verdicts"])
j = d["metrics"]["judge"]
print({k: v for k, v in j.items() if k != "verdicts"})
