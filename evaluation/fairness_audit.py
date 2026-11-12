"""
Fairness audit (Governance Framework section 3).

Segments a finished harness run and compares outcomes across customer groups:
tier, English fluency, ticket length, region and channel.

For each segment it reports
  n                  tickets in the segment
  auto_rate          share answered automatically
  resolution_rate    share where auto-reply was the right route (expected_route == auto_respond and we replied)
  false_auto_rate    share where we replied but should have escalated (the harmful error)
  quality            retrieval hit@1 on tickets answerable from the docs (did the right article rank first)
  route_accuracy     decision == expected_route, with a 95% Wilson interval
  gap_pp             route-accuracy gap to the best segment in the same dimension
  significant        two-proportion z-test p < 0.05 against the best segment

A gap only counts as a finding when it is both above the 5 pp target and statistically distinguishable
from noise. Small segments are flagged low_n (< 30).

Run: venv/bin/python3 evaluation/fairness_audit.py --run evaluation/results/dev_run.json \
       --tickets data/development_tickets.json --out evaluation/results/fairness_dev
"""
import argparse
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

TARGET_GAP_PP = 5.0
LOW_N = 30


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(max(0.0, c - h), 4), round(min(1.0, c + h), 4))


def two_prop_p(k1: int, n1: int, k2: int, n2: int) -> float:
    """Two-sided p-value of a pooled two-proportion z-test."""
    if n1 == 0 or n2 == 0:
        return 1.0
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return 1.0
    z = abs(k1 / n1 - k2 / n2) / se
    return math.erfc(z / math.sqrt(2))


def words(t: dict) -> int:
    return len(((t.get("subject") or "") + " " + (t.get("body") or "")).split())


def build_rows(run: dict, tickets: list) -> list:
    by_id = {t["ticket_id"]: t for t in tickets}
    rows = []
    for r in run["results"]:
        t = by_id.get(r["ticket_id"])
        if t:
            rows.append((r, t))
    return rows


def segment_fn(rows: list) -> dict:
    wc = sorted(words(t) for _, t in rows)
    median = wc[len(wc) // 2]
    return {
        "customer_tier": lambda t: t.get("customer_tier"),
        "language_fluency": lambda t: t.get("language_fluency"),
        "ticket_length": lambda t: ("short (<= %d words)" % median) if words(t) <= median else ("long (> %d words)" % median),
        "region": lambda t: t.get("customer_region"),
        "channel": lambda t: t.get("channel"),
    }


def stats_for(group: list) -> dict:
    n = len(group)
    lab = lambda t: t.get("labels") or {}
    auto = [(r, t) for r, t in group if r["decision"] == "auto_respond"]
    correct = sum(1 for r, t in group if r["decision"] == lab(t).get("expected_route"))
    false_auto = sum(1 for r, t in auto if lab(t).get("expected_route") == "escalate")
    good_auto = sum(1 for r, t in auto if lab(t).get("expected_route") == "auto_respond")
    ans = [(r, t) for r, t in group if lab(t).get("answerable_from_docs") and lab(t).get("expected_doc_ids")]
    hit = sum(1 for r, t in ans if r.get("passages") and r["passages"][0]["doc_id"] in lab(t)["expected_doc_ids"])
    lo, hi = wilson(correct, n)
    return {
        "n": n, "low_n": n < LOW_N,
        "auto_rate": round(len(auto) / n, 4) if n else None,
        "resolution_rate": round(good_auto / n, 4) if n else None,
        "false_auto_rate": round(false_auto / n, 4) if n else None,
        "quality_hit_at_1": round(hit / len(ans), 4) if ans else None, "quality_n": len(ans), "_hit": hit,
        "route_accuracy": round(correct / n, 4) if n else None, "route_ci95": [lo, hi],
        "_correct": correct,
    }


def audit(rows: list) -> dict:
    out = {}
    for dim, fn in segment_fn(rows).items():
        groups = {}
        for r, t in rows:
            groups.setdefault(fn(t), []).append((r, t))
        res = {g: stats_for(v) for g, v in sorted(groups.items())}
        eligible = [g for g in res if not res[g]["low_n"]] or list(res)   # all-small dimension: compare anyway, flagged
        all_low = all(res[g]["low_n"] for g in res)
        best_g = max(eligible, key=lambda g: res[g]["route_accuracy"] or 0)
        b = res[best_g]
        for g, s in res.items():
            # A segment that beats the reference (possible when the reference is the best among n >= 30 segments only)
            # has no disadvantage: gap 0, not negative.
            s["gap_pp"] = max(0.0, round(((b["route_accuracy"] or 0) - (s["route_accuracy"] or 0)) * 100, 1))
            p = two_prop_p(s["_correct"], s["n"], b["_correct"], b["n"]) if (g != best_g and s["gap_pp"] > 0) else 1.0
            s["p_vs_best"] = round(p, 4)
            s["significant"] = bool(g != best_g and p < 0.05)
            big = bool(s["gap_pp"] > TARGET_GAP_PP and s["significant"])
            s["finding"] = big and not s["low_n"]          # confirmed: large, significant, enough tickets
            s["suggestive"] = big and s["low_n"]           # large and significant but too few tickets to trust
        qbest = max([g for g in res if res[g]["quality_n"] >= LOW_N] or list(res), key=lambda g: res[g]["quality_hit_at_1"] or 0)
        qb = res[qbest]
        for g, s in res.items():
            s["quality_gap_pp"] = max(0.0, round(((qb["quality_hit_at_1"] or 0) - (s["quality_hit_at_1"] or 0)) * 100, 1))
            s["quality_p_vs_best"] = round(two_prop_p(s["_hit"], s["quality_n"], qb["_hit"], qb["quality_n"]), 4) if (g != qbest and s["quality_gap_pp"] > 0) else 1.0
            s["quality_finding"] = bool(s["quality_gap_pp"] > TARGET_GAP_PP and s["quality_p_vs_best"] < 0.05 and s["quality_n"] >= LOW_N)
        for s in res.values():
            s.pop("_correct"); s.pop("_hit")
        auto_rates = [res[g]["auto_rate"] for g in eligible]
        out[dim] = {"best_segment": best_g, "groups": res,
                    "all_segments_low_n": all_low,
                    "max_gap_pp_route_accuracy": max(res[g]["gap_pp"] for g in eligible),
                    "max_gap_pp_auto_rate": round((max(auto_rates) - min(auto_rates)) * 100, 1) if auto_rates else None}
    return out


def to_markdown(name: str, a: dict) -> str:
    L = [f"# Fairness audit: {name}", "",
         f"Target: route-accuracy gap <= {TARGET_GAP_PP} pp. A gap is a *finding* only if it is above target AND p < 0.05 vs the best segment. "
         f"Segments with n < {LOW_N} are marked low_n and excluded from 'best'.", ""]
    for dim, d in a.items():
        L += [f"## {dim}  (best: {d['best_segment']}; max route-acc gap {d['max_gap_pp_route_accuracy']} pp; max auto-rate spread {d['max_gap_pp_auto_rate']} pp)", "",
              "| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for g, s in d["groups"].items():
            ci = f"{s['route_accuracy']:.3f} ({s['route_ci95'][0]:.2f}-{s['route_ci95'][1]:.2f})"
            L.append(f"| {g}{' (low n)' if s['low_n'] else ''} | {s['n']} | {s['auto_rate']:.3f} | {s['resolution_rate']:.3f} | "
                     f"{s['false_auto_rate']:.3f} | {s['quality_hit_at_1']} | {ci} | {s['gap_pp']} | {s['p_vs_best']} | {'YES' if s['finding'] else ('suggestive (low n)' if s['suggestive'] else 'no')} | "
                     f"{s['quality_gap_pp']} ({s['quality_p_vs_best']}){' QUALITY FINDING' if s['quality_finding'] else ''} |")
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--tickets", required=True)
    ap.add_argument("--out", required=True, help="output path prefix; writes .json and .md")
    a = ap.parse_args()
    run = json.load(open(a.run))
    tickets = json.load(open(a.tickets))
    rows = build_rows(run, tickets)
    res = audit(rows)
    json.dump({"run": a.run, "n": len(rows), "target_gap_pp": TARGET_GAP_PP, "segments": res}, open(a.out + ".json", "w"), indent=2)
    open(a.out + ".md", "w").write(to_markdown(os.path.basename(a.run), res))
    print(f"audited {len(rows)} tickets -> {a.out}.json/.md")
    for dim, d in res.items():
        flagged = [g for g, s in d["groups"].items() if s["finding"]]
        sugg = [g for g, s in d["groups"].items() if s["suggestive"]]
        print(f"  {dim:18s} max route-acc gap {d['max_gap_pp_route_accuracy']:5.1f} pp | confirmed: {flagged or 'none'} | suggestive: {sugg or 'none'}")


if __name__ == "__main__":
    main()
