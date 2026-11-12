"""Tests for evaluation/fairness_audit.py: statistics and segment logic on a tiny fixture."""
from evaluation import fairness_audit as fa


def test_wilson_interval_contains_point_estimate_and_widens_with_small_n():
    lo, hi = fa.wilson(80, 100)
    assert lo < 0.8 < hi
    lo2, hi2 = fa.wilson(8, 10)
    assert (hi2 - lo2) > (hi - lo)
    assert fa.wilson(0, 0) == (None, None)


def test_two_proportion_test_detects_big_gap_and_ignores_equal():
    assert fa.two_prop_p(90, 100, 50, 100) < 0.001
    assert fa.two_prop_p(50, 100, 50, 100) == 1.0
    assert fa.two_prop_p(0, 0, 5, 10) == 1.0


def _row(i, tier, fluency, decision, expected, body="word " * 10):
    t = {"ticket_id": f"T{i}", "customer_tier": tier, "language_fluency": fluency, "customer_region": "europe",
         "channel": "chat", "subject": "", "body": body,
         "labels": {"expected_route": expected, "answerable_from_docs": True, "expected_doc_ids": ["D1"]}}
    r = {"ticket_id": f"T{i}", "decision": decision, "passages": [{"doc_id": "D1", "score": 0.9}]}
    return r, t


def test_audit_flags_large_significant_gap_only_with_enough_tickets():
    rows = []
    # 'good' group: 60/60 correct. 'bad' group: 20/60 correct. Both n >= 30, gap far above 5 pp.
    for i in range(60):
        rows.append(_row(i, "enterprise", "fluent", "auto_respond", "auto_respond"))
    for i in range(60, 120):
        rows.append(_row(i, "standard", "fluent", "auto_respond", "auto_respond" if i < 80 else "escalate"))
    res = fa.audit(rows)["customer_tier"]
    assert res["best_segment"] == "enterprise"
    assert res["groups"]["standard"]["finding"] is True
    assert res["groups"]["standard"]["false_auto_rate"] > 0.5
    assert res["groups"]["enterprise"]["finding"] is False


def test_small_segment_is_suggestive_not_a_confirmed_finding():
    rows = [_row(i, "enterprise", "fluent", "auto_respond", "auto_respond") for i in range(60)]
    rows += [_row(100 + i, "standard", "fluent", "auto_respond", "escalate") for i in range(10)]  # n=10 < 30
    g = fa.audit(rows)["customer_tier"]["groups"]["standard"]
    assert g["low_n"] is True and g["finding"] is False and g["suggestive"] is True


def test_dimension_with_all_small_segments_does_not_crash():
    rows = [_row(i, "enterprise", "fluent", "auto_respond", "auto_respond") for i in range(5)]
    rows += [_row(10 + i, "standard", "fluent", "escalate", "auto_respond") for i in range(5)]
    d = fa.audit(rows)["customer_tier"]
    assert d["all_segments_low_n"] is True
