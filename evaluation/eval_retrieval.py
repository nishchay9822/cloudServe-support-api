"""
Retrieval quality check on the labelled development tickets.
Reports hit@k against labels.expected_doc_ids and how often non-answerable
tickets correctly get an empty result, for several relevance floors.

Run:  venv/bin/python3 evaluation/eval_retrieval.py
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import retrieve  # noqa: E402


def query_of(t):
    return (t.get("subject", "") + "\n" + t.get("body", "")).strip()


def main():
    t0 = time.time()
    n = retrieve.embed_corpus()
    print(f"chunks={n} build_s={time.time() - t0:.1f}")
    path = os.path.join(retrieve.ROOT, "data", "development_tickets.json")
    tickets = json.load(open(path))
    ans = [t for t in tickets if t["labels"]["answerable_from_docs"]]
    non = [t for t in tickets if not t["labels"]["answerable_from_docs"]]
    for floor in (0.0, 0.2, 0.3, 0.35, 0.4, 0.45):
        h1 = h3 = h5 = 0
        lat = []
        for t in ans:
            s = time.time()
            r = retrieve.retrieve_passages(query_of(t), 5, min_score=floor)
            lat.append(time.time() - s)
            ids = [p["doc_id"] for p in r]
            exp = set(t["labels"]["expected_doc_ids"])
            h1 += bool(ids[:1] and ids[0] in exp)
            h3 += bool(exp & set(ids[:3]))
            h5 += bool(exp & set(ids))
        empty = sum(1 for t in non if not retrieve.retrieve_passages(query_of(t), 5, min_score=floor))
        p95 = sorted(lat)[int(0.95 * len(lat))] * 1000
        print(f"floor={floor:.2f} hit@1={h1/len(ans):.3f} hit@3={h3/len(ans):.3f} hit@5={h5/len(ans):.3f} "
              f"empty_on_nonanswerable={empty}/{len(non)} p95_ms={p95:.0f}")


if __name__ == "__main__":
    main()
