"""
Measure classification on labelled tickets and (optionally) fit the confidence calibration.

  venv/bin/python3 evaluation/eval_classify.py --split dev --n 150            # accuracy + raw signals
  venv/bin/python3 evaluation/eval_classify.py --split dev --n 200 --fit      # also write data/calibration.json
  venv/bin/python3 evaluation/eval_classify.py --split val                    # held-out check

Few-shot ticket ids in classify_v2.txt are excluded from dev measurement.
For dev tickets, the kNN excludes the ticket itself (leave-one-out).
Results are cached in evaluation/results/classify_<split>.json so re-runs are cheap.
"""
import argparse
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import classify, ingest, retrieve  # noqa: E402


def shots_to_exclude():
    text = open(os.path.join(retrieve.ROOT, classify.PROMPT_FILE), encoding="utf-8").read()
    m = re.search(r"Few-shot ticket ids.*?: (.*)", text)
    return set(x.strip() for x in m.group(1).split(",")) if m else set()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["dev", "val"], default="dev")
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--fit", action="store_true")
    ap.add_argument("--fresh", action="store_true")
    args = ap.parse_args()

    fname = "development_tickets.json" if args.split == "dev" else "validation_tickets.json"
    tickets = json.load(open(os.path.join(retrieve.ROOT, "data", fname)))
    if args.split == "dev":
        ex = shots_to_exclude()
        tickets = [t for t in tickets if t["ticket_id"] not in ex]
        random.Random(7).shuffle(tickets)
        tickets = tickets[: args.n]

    cache_path = os.path.join(retrieve.ROOT, "evaluation", "results", f"classify_{args.split}.json")
    cache = {}
    if os.path.exists(cache_path) and not args.fresh:
        cache = {r["ticket_id"]: r for r in json.load(open(cache_path))}

    rows = []
    for i, t in enumerate(tickets):
        if t["ticket_id"] in cache:
            rows.append(cache[t["ticket_id"]])
            continue
        nt = ingest.normalize_ticket(t)
        res = classify.classify_ticket(nt, exclude_id=t["ticket_id"] if args.split == "dev" else None)
        rows.append({"ticket_id": t["ticket_id"], "true": t["labels"]["intent"], "true_urgency": t["labels"]["urgency"],
                     "pred": res["intent"], "pred_urgency": res["urgency"], "conf": res["confidence"],
                     "method": res["method"], **res["raw"]})
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{len(tickets)}")
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    json.dump(rows, open(cache_path, "w"), indent=1)

    n = len(rows)
    acc = sum(r["pred"] == r["true"] for r in rows) / n
    uacc = sum(r["pred_urgency"] == r["true_urgency"] for r in rows) / n
    llm_rows = [r for r in rows if r.get("llm_confidence") is not None]
    print(f"\nn={n} intent_acc={acc:.3f} urgency_acc={uacc:.3f} methods={sorted(set(r['method'] for r in rows))}")
    if llm_rows:
        la = sum(r["pred"] == r["true"] for r in llm_rows) / len(llm_rows)
        ka = sum(1 for r in llm_rows if r["agree"]) / len(llm_rows)
        ag = [r for r in llm_rows if r["agree"]]
        dg = [r for r in llm_rows if not r["agree"]]
        print(f"LLM acc={la:.3f}; LLM/kNN agree on {ka:.2%}; acc when agree={sum(r['pred']==r['true'] for r in ag)/max(len(ag),1):.3f} "
              f"(n={len(ag)}), when disagree={sum(r['pred']==r['true'] for r in dg)/max(len(dg),1):.3f} (n={len(dg)})")

    print("\nCalibration of final confidence (stated vs observed):")
    for lo in (0.0, 0.5, 0.6, 0.7, 0.8, 0.9):
        hi = {0.0: 0.5, 0.5: 0.6, 0.6: 0.7, 0.7: 0.8, 0.8: 0.9, 0.9: 1.01}[lo]
        b = [r for r in rows if lo <= r["conf"] < hi]
        if b:
            print(f"  [{lo:.1f},{min(hi,1.0):.1f}) n={len(b):3d} stated={sum(r['conf'] for r in b)/len(b):.3f} observed={sum(r['pred']==r['true'] for r in b)/len(b):.3f}")

    if args.fit and llm_rows:
        import numpy as np
        from sklearn.linear_model import LogisticRegression
        # Features: do the two independent classifiers agree, and how strongly do the neighbours vote.
        # The LLM's own self-reported confidence is deliberately NOT a feature: with ~10 negatives it fits
        # a spurious (negative) weight, and self-reported confidence is the least trustworthy signal.
        X = np.array([[1.0 if r["agree"] else 0.0, r["knn_share"] if r["agree"] else 0.0] for r in llm_rows])
        y = np.array([1 if r["pred"] == r["true"] else 0 for r in llm_rows])
        lr = LogisticRegression(C=5.0, max_iter=1000).fit(X, y)
        out = {"intercept": float(lr.intercept_[0]), "w_llm": 0.0, "w_agree": float(lr.coef_[0][0]),
               "w_knn": float(lr.coef_[0][1]), "n_fit": int(len(y)), "fit_on": "development_tickets (leave-one-out kNN)"}
        json.dump(out, open(classify.CALIBRATION_PATH, "w"), indent=1)
        print("\nwrote", classify.CALIBRATION_PATH, out)


if __name__ == "__main__":
    main()
