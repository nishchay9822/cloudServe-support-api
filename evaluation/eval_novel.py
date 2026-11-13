"""
Honest estimate of classifier quality on tickets the index has never seen in any form.

Plain leave-one-out removes only the ticket itself, but ~half the development tickets share their exact text with another
ticket, so the nearest neighbour is often a twin and the label is copied. A hidden set drawn from the same population may or may
not contain twins of our tickets. This script removes EVERY ticket whose normalised text equals the query's (and optionally every
neighbour above a similarity cap) before voting, which is the 'novel wording' case.

Writes per-ticket records used to calibrate confidence (evaluation/calibrate.py):
  id, true intent, predicted intent, vote share, top similarity, whether a twin existed.

  venv/bin/python3 evaluation/eval_novel.py [--cap 0.97] [--out evaluation/results/novel_knn.json]
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import classify, retrieve


def norm(t: dict) -> str:
    return re.sub(r"\s+", " ", ((t.get("subject") or "") + " " + (t.get("body") or "")).lower()).strip()


def knn_vote(col, text: str, ban_ids: set, cap: float, k: int):
    res = col.query(query_texts=[text or "(empty)"], n_results=60)
    votes, used, top_sim = defaultdict(float), 0, 0.0
    for tid, meta, dist in zip(res["ids"][0], res["metadatas"][0], res["distances"][0]):
        sim = 1.0 - float(dist)
        if tid in ban_ids or (cap and sim > cap):
            continue
        if used == 0:
            top_sim = sim
        votes[meta["intent"]] += max(sim, 0.01)
        used += 1
        if used >= k:
            break
    total = sum(votes.values()) or 1.0
    intent, score = max(votes.items(), key=lambda kv: kv[1]) if votes else ("unclear_request", 0.0)
    return intent, round(score / total, 4), round(top_sim, 4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=float, default=0.97, help="ignore neighbours more similar than this (near-duplicates); 0 = off")
    ap.add_argument("--tickets", default=os.path.join(ROOT, "data", "development_tickets.json"))
    ap.add_argument("--out", default=os.path.join(ROOT, "evaluation", "results", "novel_knn.json"))
    a = ap.parse_args()
    classify.ensure_ticket_index()
    col = retrieve.get_client().get_collection(classify.TICKET_COLLECTION, embedding_function=retrieve._ef())
    tickets = json.load(open(a.tickets))
    groups = defaultdict(set)
    for t in tickets:
        groups[norm(t)].add(t["ticket_id"])
    rows = []
    for t in tickets:
        twins = groups[norm(t)] - {t["ticket_id"]}
        pred, share, sim = knn_vote(col, (t.get("subject", "") + "\n" + t.get("body", "")).strip(), twins | {t["ticket_id"]}, a.cap, classify.KNN_K)
        rows.append({"id": t["ticket_id"], "true": t["labels"]["intent"], "pred": pred, "share": share, "top_sim": sim, "had_twin": bool(twins)})
    json.dump(rows, open(a.out, "w"), indent=1)
    acc = lambda rs: round(sum(r["true"] == r["pred"] for r in rs) / len(rs), 4) if rs else None
    tw = [r for r in rows if r["had_twin"]]
    nt = [r for r in rows if not r["had_twin"]]
    print(f"cap={a.cap}  all={acc(rows)} (n={len(rows)})  with twin={acc(tw)} (n={len(tw)})  no twin={acc(nt)} (n={len(nt)})")
    for lo, hi in ((0, .5), (.5, .7), (.7, .85), (.85, 1.01)):
        b = [r for r in rows if lo <= r["share"] < hi]
        print(f"  vote share {lo:.2f}-{min(hi,1):.2f}: n={len(b):3d} acc={acc(b)}")


if __name__ == "__main__":
    main()
