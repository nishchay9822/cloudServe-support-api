"""
Metric calculations for the evaluation harness. Pure functions: results + tickets in, numbers out.
Every metric that needs a label is skipped (None) when the input tickets carry no labels,
so the harness works on any file with the ticket schema, labelled or not.
"""
from collections import Counter, defaultdict
from typing import Optional

BANDS = [(0.0, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0001)]


def pct(values: list, p: float) -> Optional[float]:
    if not values:
        return None
    s = sorted(values)
    k = min(len(s) - 1, max(0, int(round(p / 100.0 * (len(s) - 1)))))
    return s[k]


def _lab(t: dict) -> dict:
    return (t or {}).get("labels") or {}


def _hist(t: dict) -> dict:
    return (t or {}).get("history") or {}


def _ratio(a: int, b: int) -> Optional[float]:
    return round(a / b, 4) if b else None


def routing_metrics(rows: list) -> dict:
    lab = [(r, t) for r, t in rows if _lab(t).get("expected_route")]
    n = len(rows)
    auto = [r for r, _ in rows if r["decision"] == "auto_respond"]
    out = {"n": n, "auto_respond": len(auto), "escalated": n - len(auto),
           "auto_rate": _ratio(len(auto), n), "escalation_rate": _ratio(n - len(auto), n)}
    if lab:
        correct = sum(1 for r, t in lab if r["decision"] == _lab(t)["expected_route"])
        false_auto = sum(1 for r, t in lab if r["decision"] == "auto_respond" and _lab(t)["expected_route"] == "escalate")
        over_esc = sum(1 for r, t in lab if r["decision"] == "escalate" and _lab(t)["expected_route"] == "auto_respond")
        a = [1 for r, _ in lab if r["decision"] == "auto_respond"]
        out.update({"route_accuracy": _ratio(correct, len(lab)), "false_auto_respond": false_auto,
                    "over_escalation": over_esc, "precision_of_auto_respond": _ratio(len(a) - false_auto, len(a))})
        safety = [(r, t) for r, t in lab if _lab(t).get("must_not_auto_respond")]
        viol = [r["ticket_id"] for r, _ in safety if r["decision"] == "auto_respond"]
        out["safety_flagged_tickets"] = len(safety)
        out["safety_violations"] = len(viol)
        out["safety_violation_ids"] = viol
    return out


def classification_metrics(rows: list) -> dict:
    lab = [(r, t) for r, t in rows if _lab(t).get("intent") and r.get("intent")]
    if not lab:
        return {"n": 0}
    true = [_lab(t)["intent"] for _, t in lab]
    pred = [r["intent"] for r, _ in lab]
    acc = _ratio(sum(a == b for a, b in zip(true, pred)), len(lab))
    per = {}
    for c in sorted(set(true) | set(pred)):
        tp = sum(1 for a, b in zip(true, pred) if a == c and b == c)
        fp = sum(1 for a, b in zip(true, pred) if a != c and b == c)
        fn = sum(1 for a, b in zip(true, pred) if a == c and b != c)
        per[c] = {"support": true.count(c), "precision": _ratio(tp, tp + fp), "recall": _ratio(tp, tp + fn)}
    conf = Counter((a, b) for a, b in zip(true, pred) if a != b)
    ulab = [(r, t) for r, t in lab if _lab(t).get("urgency") and r.get("urgency")]
    return {"n": len(lab), "intent_accuracy": acc, "per_class": per,
            "classes_below_85pct_precision": sorted(c for c, v in per.items() if v["precision"] is not None and v["precision"] < 0.85),
            "top_confusions": [{"true": a, "pred": b, "count": n} for (a, b), n in conf.most_common(8)],
            "urgency_accuracy": _ratio(sum(1 for r, t in ulab if r["urgency"] == _lab(t)["urgency"]), len(ulab)),
            "methods": dict(Counter(r.get("classify_method") for r, _ in lab))}


def retrieval_metrics(rows: list) -> dict:
    ans = [(r, t) for r, t in rows if _lab(t).get("answerable_from_docs") and _lab(t).get("expected_doc_ids")]
    if not ans:
        return {"n": 0}
    out = {"n": len(ans)}
    for k in (1, 3, 5):
        hit = sum(1 for r, t in ans if set(_lab(t)["expected_doc_ids"]) & {p["doc_id"] for p in r["passages"][:k]})
        out[f"hit@{k}"] = _ratio(hit, len(ans))
    return out


def calibration(rows: list) -> list:
    lab = [(r, t) for r, t in rows if _lab(t).get("intent") and r.get("confidence") is not None and r.get("intent")]
    out = []
    for lo, hi in BANDS:
        b = [(r, t) for r, t in lab if lo <= r["confidence"] < hi]
        if not b:
            continue
        stated = sum(r["confidence"] for r, _ in b) / len(b)
        observed = sum(1 for r, t in b if r["intent"] == _lab(t)["intent"]) / len(b)
        out.append({"band": f"{lo:.1f}-{min(hi, 1.0):.1f}", "n": len(b), "stated": round(stated, 3),
                    "observed": round(observed, 3), "gap_pp": round(abs(stated - observed) * 100, 1),
                    "within_5pp": abs(stated - observed) <= 0.05})
    return out


def latency_metrics(rows: list) -> dict:
    all_ms = [r["latency_ms"] for r, _ in rows if r.get("latency_ms") is not None]
    auto_ms = [r["latency_ms"] for r, _ in rows if r["decision"] == "auto_respond" and r.get("latency_ms") is not None]
    return {"all_p50_ms": pct(all_ms, 50), "all_p95_ms": pct(all_ms, 95), "all_max_ms": max(all_ms) if all_ms else None,
            "auto_p50_ms": pct(auto_ms, 50), "auto_p95_ms": pct(auto_ms, 95),
            "p95_under_3s": (pct(auto_ms, 95) or 0) < 3000 if auto_ms else None}


def citation_metrics(rows: list) -> dict:
    auto = [(r, t) for r, t in rows if r["decision"] == "auto_respond"]
    if not auto:
        return {"n_auto": 0}
    cites = [(c, r, t) for r, t in auto for c in r.get("citations", [])]
    resolves = sum(1 for c, _, _ in cites if c["resolves"])
    with_exp = [(c, _lab(t).get("expected_doc_ids")) for c, r, t in cites if _lab(t).get("expected_doc_ids")]
    return {"n_auto": len(auto), "n_citations": len(cites),
            "responses_with_citation": _ratio(sum(1 for r, _ in auto if r.get("citations")), len(auto)),
            "citation_resolves_rate": _ratio(resolves, len(cites)),
            "cited_expected_doc_rate": _ratio(sum(1 for c, exp in with_exp if c["doc_id"] in exp), len(with_exp)) if with_exp else None}


def segment_metrics(rows: list, key_fn_by_name: dict) -> dict:
    out = {}
    for name, fn in key_fn_by_name.items():
        groups = defaultdict(list)
        for r, t in rows:
            groups[fn(r, t) or "unknown"].append((r, t))
        seg = {}
        for g, items in sorted(groups.items()):
            rm, cm, rt = routing_metrics(items), classification_metrics(items), retrieval_metrics(items)
            seg[g] = {"n": len(items), "auto_rate": rm["auto_rate"], "route_accuracy": rm.get("route_accuracy"),
                      "intent_accuracy": cm.get("intent_accuracy"), "retrieval_hit@1": rt.get("hit@1"),
                      "low_n": len(items) < 15}
        usable = [v for v in seg.values() if not v["low_n"]]

        def spread(field):
            vals = [v[field] for v in usable if v.get(field) is not None]
            return round((max(vals) - min(vals)) * 100, 1) if len(vals) > 1 else None
        out[name] = {"groups": seg, "max_gap_pp": {"auto_rate": spread("auto_rate"), "route_accuracy": spread("route_accuracy"),
                                                     "intent_accuracy": spread("intent_accuracy"), "retrieval_hit@1": spread("retrieval_hit@1")}}
    return out


def business_proxies(rows: list) -> dict:
    """
    Proxies only: there are no real customers here. Baseline comes from the tickets' own history block.
    - auto_resolution_proxy: auto-responded AND the label says the docs can answer it.
    """
    hist = [t for _, t in rows if _hist(t)]
    n = len(rows)
    out = {"note": "proxy measures on labelled tickets, not live customer outcomes"}
    if hist:
        h = [_hist(t) for t in hist]
        out["baseline_fcr"] = _ratio(sum(1 for x in h if x.get("first_contact_resolution")), len(h))
        out["baseline_escalation_rate"] = _ratio(sum(1 for x in h if x.get("escalated")), len(h))
        out["baseline_repeat_contact_rate"] = _ratio(sum(1 for x in h if x.get("repeat_contact")), len(h))
        csat = [x["csat_rating"] for x in h if x.get("csat_rating") is not None]
        out["baseline_csat"] = round(sum(csat) / len(csat), 3) if csat else None
        rt = [x["resolution_time_minutes"] for x in h if x.get("resolution_time_minutes") is not None]
        out["baseline_median_resolution_minutes"] = pct(rt, 50)
    lab = [(r, t) for r, t in rows if _lab(t).get("answerable_from_docs") is not None]
    if lab:
        good = sum(1 for r, t in lab if r["decision"] == "auto_respond" and _lab(t)["answerable_from_docs"])
        out["auto_resolution_proxy"] = _ratio(good, len(lab))
    out["system_escalation_rate"] = _ratio(sum(1 for r, _ in rows if r["decision"] == "escalate"), n)
    auto_ms = [r["latency_ms"] for r, _ in rows if r["decision"] == "auto_respond" and r.get("latency_ms") is not None]
    out["median_time_to_first_reply_seconds_auto"] = round(pct(auto_ms, 50) / 1000, 2) if auto_ms else None
    out["csat"] = "not measurable offline"
    return out
