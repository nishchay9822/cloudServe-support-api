"""
Fit the classifier's confidence and choose the routing threshold from data, WITHOUT touching the validation set.

Why not plain leave-one-out: ~half of the development tickets have a same-text twin, so the nearest neighbour is usually a copy and
confidence collapses to 0.99 everywhere (a threshold then does nothing). Here every ticket is classified as if its wording were new:
all same-text twins are removed from the index, and neighbours above a similarity cap (0.97, 0.90, 0.85) are removed too.
These pooled 'unseen wording' samples spread the vote share over its range, so confidence can be calibrated against reality.

Outputs
  data/calibration.json                         knn_bins (share -> P(correct)) and logistic coefficients for the LLM+kNN path
  evaluation/results/threshold_selection.json   sweep and the chosen threshold with its reasoning

Run: venv/bin/python3 evaluation/calibrate.py   (makes one model call per low-vote ticket; a few hundred calls at most)
"""
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import classify, ingest, llm, retrieve
from evaluation.eval_novel import norm

CAPS = (0.97, 0.90, 0.85)
SHARE_BINS = [0.85, 0.75, 0.60, 0.45, 0.0]
THRESHOLD_GRID = [0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99]
OUT_CAL = os.path.join(ROOT, "data", "calibration.json")
OUT_SEL = os.path.join(ROOT, "evaluation", "results", "threshold_selection.json")


def fit_logistic(X, y, l2=0.5, iters=200):
    X = np.hstack([np.ones((len(X), 1)), np.asarray(X, float)])
    y = np.asarray(y, float)
    w = np.zeros(X.shape[1])
    for _ in range(iters):  # Newton steps with an L2 penalty (keeps the few-sample fit stable)
        p = 1 / (1 + np.exp(-X @ w))
        g = X.T @ (p - y) + l2 * np.r_[0, w[1:]]
        H = (X.T * (p * (1 - p))) @ X + l2 * np.diag(np.r_[0, np.ones(len(w) - 1)])
        w -= np.linalg.solve(H, g)
    return w


def main():
    classify.ensure_ticket_index()
    tickets = json.load(open(os.path.join(ROOT, "data", "development_tickets.json")))
    groups = defaultdict(set)
    for t in tickets:
        groups[norm(t)].add(t["ticket_id"])
    samples = []   # one per (ticket, cap)
    for cap in CAPS:
        for t in tickets:
            nt = ingest.normalize_ticket(t)
            ban = groups[norm(t)]                       # includes the ticket itself
            k = classify.classify_knn(nt, ban_ids=ban, sim_cap=cap)
            samples.append({"id": t["ticket_id"], "cap": cap, "true": t["labels"]["intent"], "restricted": bool(t["labels"]["must_not_auto_respond"]),
                            "knn_intent": k["intent"], "share": k["share"], "ticket": nt})
    print(f"{len(samples)} simulated samples ({len(tickets)} tickets x {len(CAPS)} similarity caps)")

    # ---- kNN-only confidence by vote share (used when share >= KNN_TRUST and as the provider-outage fallback)
    bins = []
    print("kNN vote share -> observed accuracy (Laplace-smoothed)")
    prev = 1.0
    for lo in SHARE_BINS:
        hi = bins[-1][0] if bins else 1.01
        grp = [s for s in samples if lo <= s["share"] < (hi if bins else 1.01)]
        ok = sum(s["knn_intent"] == s["true"] for s in grp)
        conf = min((ok + 1) / (len(grp) + 2), prev)     # monotone non-increasing as share falls
        prev = conf
        bins.append((lo, round(conf, 3)))
        print(f"  share >= {lo:.2f}: n={len(grp):4d} correct={ok:4d} -> {conf:.3f}")

    # ---- LLM + kNN path for low-vote samples (model asked once per ticket)
    low = [s for s in samples if s["share"] < classify.KNN_TRUST]
    llm_cache = {}
    for s in low:
        if s["id"] not in llm_cache:
            try:
                llm_cache[s["id"]] = classify.classify_llm(s["ticket"])
            except llm.LLMUnavailable as e:
                sys.exit(f"cannot calibrate the LLM path: {e}")
    X, y = [], []
    for s in low:
        r = llm_cache[s["id"]]
        agree = r["intent"] == s["knn_intent"]
        s["llm_intent"], s["llm_conf"], s["agree"] = r["intent"], r["confidence"], agree
        X.append([r["confidence"], 1.0 if agree else 0.0, s["share"] if agree else 0.0])
        y.append(1.0 if r["intent"] == s["true"] else 0.0)
    w = fit_logistic(X, y)
    print(f"LLM+kNN path: {len(low)} samples, LLM correct {int(sum(y))}/{len(y)}; coefficients {np.round(w, 3).tolist()}")
    coef = {"intercept": float(w[0]), "w_llm": float(w[1]), "w_agree": float(w[2]), "w_knn": float(w[3]), "n_fit": len(low),
            "knn_bins": [list(b) for b in bins],
            "fit_on": f"development tickets, same-text twins removed, similarity caps {list(CAPS)} (evaluation/calibrate.py)"}
    json.dump(coef, open(OUT_CAL, "w"), indent=1)
    classify._calib["loaded"] = False                      # use the new coefficients immediately

    # ---- end-to-end confidence for every sample, reliability, and the threshold sweep
    final = []
    for s in samples:
        if s["share"] >= classify.KNN_TRUST:
            pred, conf = s["knn_intent"], classify.knn_confidence(s["share"])
        else:
            pred = s["llm_intent"]
            conf = classify.calibrated_confidence(s["llm_conf"], s["agree"], s["share"] if s["agree"] else 0.0)
        final.append({"pred": pred, "conf": conf, "true": s["true"], "restricted": s["restricted"]})
    arr = lambda k: np.array([f[k] for f in final])
    conf_a, ok_a = arr("conf"), arr("pred") == arr("true")
    print("reliability (final confidence band -> observed accuracy)")
    ece, rel = 0.0, []
    for lo, hi in ((0, .5), (.5, .7), (.7, .8), (.8, .9), (.9, .97), (.97, 1.01)):
        m = (conf_a >= lo) & (conf_a < hi)
        if m.any():
            st, ob = float(conf_a[m].mean()), float(ok_a[m].mean())
            ece += m.mean() * abs(st - ob)
            rel.append({"band": f"{lo}-{min(hi,1.0)}", "n": int(m.sum()), "stated": round(st, 3), "observed": round(ob, 3)})
            print(f"  {lo:.2f}-{min(hi,1.0):.2f}: n={int(m.sum()):4d} stated={st:.3f} observed={ob:.3f}")
    print(f"expected calibration error {ece*100:.1f} pp")

    restricted = [f for f in final if f["restricted"]]
    sweep = []
    print("threshold sweep (pooled unseen-wording samples)")
    print("  thr   auto-rate  intent-acc(auto)  restricted-leaks   escalated-though-fine")
    for thr in THRESHOLD_GRID:
        auto = [f for f in final if f["conf"] >= thr]
        acc = sum(f["pred"] == f["true"] for f in auto) / len(auto) if auto else None
        leaks = sum(1 for f in restricted if f["conf"] >= thr and f["pred"] not in classify.SAFETY_INTENTS)
        sweep.append({"threshold": thr, "auto_rate": round(len(auto) / len(final), 4), "intent_accuracy_of_auto": None if acc is None else round(acc, 4),
                      "restricted_leaks": leaks, "restricted_leak_rate": round(leaks / len(restricted), 4)})
        print(f"  {thr:<5} {len(auto)/len(final):<10.3f} {acc if acc is None else round(acc,4)!s:<17} {leaks:<18} {round(leaks/len(restricted),4)}")

    # Rule: the lowest threshold at which auto-answered tickets are classified correctly at least 99% of the time, i.e. at most
    # one in a hundred automatic replies addresses the wrong problem. Lowest = the most automation that still meets that bar.
    # Confidently-wrong restricted tickets are NOT fixed by any threshold (the leak count above is constant); the safety-proximity
    # rule in src/route.py is the control for those.
    ok = [x for x in sweep if x["intent_accuracy_of_auto"] and x["intent_accuracy_of_auto"] >= 0.99]
    chosen = ok[0]["threshold"] if ok else None
    json.dump({"rule": "lowest threshold with intent accuracy of auto-answered >= 99%",
               "chosen": chosen, "ece_pp": round(ece * 100, 2), "reliability": rel, "sweep": sweep,
               "samples": len(samples), "caps": list(CAPS)}, open(OUT_SEL, "w"), indent=1)
    print("chosen threshold:", chosen)


if __name__ == "__main__":
    main()
