"""
Compare the human second assessor with the independent model judge (NFR-03: report inter-assessor agreement).
Reads evaluation/results/human_review_answers.csv (filled in by the human) and the judge verdicts stored in the run file.
Writes evaluation/results/human_review_agreement.json, which the report picks up automatically on its next build.

  venv/bin/python3 evaluation/review_agreement.py [--run evaluation/results/gate_run_validation.json]
"""
import argparse
import csv
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--run", default=os.path.join(ROOT, "evaluation", "results", "gate_run_validation.json"))
ap.add_argument("--answers", default=os.path.join(ROOT, "evaluation", "results", "human_review_answers.csv"))
a = ap.parse_args()
verdicts = (json.load(open(a.run))["metrics"].get("judge") or {}).get("verdicts", {})
human = {}
for r in csv.DictReader(open(a.answers, encoding="utf-8")):
    v = (r.get("human_hallucination (Y/N)") or "").strip().upper()
    if v in ("Y", "N"):
        human[r["ticket_id"]] = v == "Y"
both = [t for t in human if t in verdicts]
if len(both) < 10:
    raise SystemExit(f"only {len(both)} answered replies found; fill in human_review_answers.csv (Y or N) first")
model = {t: bool(verdicts[t].get("hallucinations_detected")) for t in both}
n = len(both)
agree = sum(human[t] == model[t] for t in both)
ph, pm = sum(human[t] for t in both) / n, sum(model[t] for t in both) / n
pe = ph * pm + (1 - ph) * (1 - pm)
kappa = None if pe == 1 else round((agree / n - pe) / (1 - pe), 3)
z = 1.96
upper = (human_k := sum(human[t] for t in both)) / n
wil = lambda k: ((k / n + z * z / (2 * n) + z * math.sqrt(k / n * (1 - k / n) / n + z * z / (4 * n * n))) / (1 + z * z / n))
res = {"n_compared": n, "agreement": round(agree / n, 4), "cohens_kappa": kappa,
       "human_hallucinations": human_k, "model_hallucinations": sum(model.values()),
       "human_rate": round(ph, 4), "human_rate_upper95": round(wil(human_k), 4),
       "disagreements": [t for t in both if human[t] != model[t]],
       "note": "kappa is undefined when both assessors flag nothing (no variation); agreement is then the figure to quote" if kappa is None else ""}
json.dump(res, open(os.path.join(ROOT, "evaluation", "results", "human_review_agreement.json"), "w"), indent=1)
print(json.dumps(res, indent=1))
