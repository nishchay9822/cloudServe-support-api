#!/usr/bin/env python3
"""
Evaluation harness. Satisfies A9 (one unattended run over a whole ticket file) and A10 (metrics report
produced automatically).

    python evaluation/harness.py --input data/validation_tickets.json --output evaluation/results/run.json

- --input and --output are required: the file it is pointed at may be one it has never seen.
- Works on labelled or unlabelled ticket files: label-based metrics are skipped when labels are absent.
- A bad ticket, a provider outage or a logging error never stops the run; it is recorded and the run continues.
- Writes <output>.json (results + metrics), <output>.md (human-readable report) and, if --judge is used,
  <output>_human_review.csv for a second human assessor.
Exit codes: 0 = every ticket was processed (check the report for per-ticket errors), 2 = could not start.
"""
import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

from evaluation import metrics as M  # noqa: E402
from src import guardrails, ingest, llm, logging_store, pipeline  # noqa: E402


def parse_args():
    p = argparse.ArgumentParser(description="CloudServe support system evaluation harness")
    p.add_argument("--input", required=True, help="path to a JSON file containing a list of tickets")
    p.add_argument("--output", required=True, help="path of the results JSON to write")
    p.add_argument("--max-tickets", type=int, default=None, help="process only the first N tickets")
    p.add_argument("--judge", type=int, default=0, help="model-assess up to N auto-responses (hallucination/citations)")
    p.add_argument("--ground-truth", default=os.path.join(ROOT, "data", "ground_truth_responses.json"),
                   help="reference answers keyed by ticket_id (used only for tickets that appear in it)")
    p.add_argument("--run-id", default=None)
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()


def load_ground_truth(path: str) -> dict:
    try:
        return {g["ticket_id"]: g for g in json.load(open(path, encoding="utf-8"))}
    except (OSError, ValueError, KeyError, TypeError):
        return {}


def run_tickets(tickets: list, run_id: str, verbose: bool = False) -> list:
    rows = []
    for i, raw in enumerate(tickets):
        hist = (raw.get("history") or {}) if isinstance(raw, dict) else {}
        try:
            r = pipeline.process_ticket(raw, run_id=run_id, outcome_fcr=bool(hist.get("first_contact_resolution")),
                                        exclude_id=raw.get("ticket_id") if isinstance(raw, dict) else None)
        except Exception as e:  # pipeline.process_ticket should never raise; this is the last safety net
            r = {"ticket_id": (raw or {}).get("ticket_id", f"index-{i}") if isinstance(raw, dict) else f"index-{i}",
                 "status": "error", "decision": "escalate", "reason": "harness caught an unexpected exception",
                 "reason_code": "harness_error", "error": f"{type(e).__name__}: {e}", "passages": [], "citations": [],
                 "latency_ms": 0, "intent": None, "confidence": None, "guardrails": None, "response_text": None}
        rows.append((r, raw if isinstance(raw, dict) else {}))
        if verbose or (i + 1) % 10 == 0 or i + 1 == len(tickets):
            print(f"  [{i + 1:3d}/{len(tickets)}] {r['ticket_id']} -> {r['decision']} ({r.get('reason_code')}) {r.get('latency_ms')}ms", flush=True)
    return rows


def governance(rows: list, run_id: str) -> dict:
    # Independent audit: re-scan every outbound reply for PII, separately from the pipeline's own guardrail.
    pii_hits = []
    for r, t in rows:
        if r["decision"] == "auto_respond" and r.get("response_text"):
            nt = ingest.normalize_ticket(t) if t else {}
            res = guardrails.check_pii(r["response_text"], nt, [])
            if res["status"] == "block":
                pii_hits.append({"ticket_id": r["ticket_id"], "found": res["detected_patterns"]})
    blocks = {}
    for r, _ in rows:
        for name in ((r.get("guardrails") or {}).get("blocked_by") or []):
            blocks[name] = blocks.get(name, 0) + 1
    reasons = {}
    for r, _ in rows:
        reasons[r.get("reason_code") or "none"] = reasons.get(r.get("reason_code") or "none", 0) + 1
    esc = [r for r, _ in rows if r["decision"] == "escalate"]
    complete = [r for r in esc if (r.get("escalation_context") or {}).get("summary") and (r.get("escalation_context") or {}).get("uncertainty_reason")]
    logged = logging_store.count_decisions(run_id=run_id)
    return {"outbound_pii_findings": pii_hits, "pii_violations": len(pii_hits),
            "guardrail_blocks_by_type": blocks, "decision_reason_counts": reasons,
            "decisions_logged": logged, "tickets_processed": len(rows), "log_reconciles": logged == len(rows),
            "resolution_records_written": logging_store.count_resolutions(run_id),
            "escalations": len(esc), "escalations_with_complete_context": len(complete),
            "escalation_context_completeness": round(len(complete) / len(esc), 4) if esc else None}


def render_report(m: dict) -> str:
    L = []
    run, rt, cl, rv, cal = m["run"], m["routing"], m["classification"], m["retrieval"], m["calibration"]
    L += [f"# Evaluation report - {run['run_id']}", "",
          f"- Input: `{run['input']}`  |  tickets: **{run['tickets']}**  |  finished: {run['finished_at']}  |  wall time: {run['wall_seconds']}s",
          f"- Model: `{run['model']}`  |  confidence threshold: {run['threshold']}  |  labelled input: {run['labelled']}", ""]
    g = m["governance"]
    L += ["## Gate: unattended run", "",
          f"- Tickets processed: {g['tickets_processed']} / {run['tickets']} | per-ticket errors: {run['ticket_errors']}",
          f"- Decision log reconciles with tickets processed: **{g['log_reconciles']}** ({g['decisions_logged']} logged)", ""]
    L += ["## 1. Business outcomes (proxies, not live customer results)", ""]
    b = m["business"]
    L += [f"- Escalation rate: system **{b.get('system_escalation_rate')}** vs baseline {b.get('baseline_escalation_rate')}",
          f"- Auto-resolution proxy (auto-replied and docs can answer it): **{b.get('auto_resolution_proxy')}** vs baseline FCR {b.get('baseline_fcr')}",
          f"- Median time to first reply on auto-replies: **{b.get('median_time_to_first_reply_seconds_auto')} s** vs baseline median resolution {b.get('baseline_median_resolution_minutes')} min",
          f"- Baseline repeat-contact rate {b.get('baseline_repeat_contact_rate')}; baseline CSAT {b.get('baseline_csat')}; system CSAT: {b.get('csat')}", ""]
    L += ["## 2. Routing", "",
          f"- Auto-respond {rt['auto_respond']} / escalate {rt['escalated']} (auto rate {rt['auto_rate']})"]
    if "route_accuracy" in rt:
        L += [f"- Route accuracy vs labels: **{rt['route_accuracy']}**; false auto-respond {rt['false_auto_respond']}; over-escalation {rt['over_escalation']}; precision of auto-replies {rt['precision_of_auto_respond']}",
              f"- Safety-flagged tickets (must_not_auto_respond): {rt['safety_flagged_tickets']}; **auto-replied to: {rt['safety_violations']}** {rt['safety_violation_ids']}"]
    L += ["", "## 3. Classification", ""]
    if cl.get("n"):
        L += [f"- Intent accuracy **{cl['intent_accuracy']}** (n={cl['n']}); urgency accuracy {cl['urgency_accuracy']}",
              f"- Classes with precision below 85%: {cl['classes_below_85pct_precision'] or 'none'}; methods used: {cl['methods']}",
              f"- Top confusions: {cl['top_confusions'][:4]}"]
    L += ["", "## 4. Retrieval", "", f"- hit@1 {rv.get('hit@1')}, hit@3 {rv.get('hit@3')}, hit@5 {rv.get('hit@5')} (n={rv.get('n')} answerable tickets)", "",
          "## 5. Confidence calibration (stated vs observed intent accuracy)", "", "| band | n | stated | observed | gap (pp) | within 5pp |", "|---|---|---|---|---|---|"]
    for c in cal:
        L.append(f"| {c['band']} | {c['n']} | {c['stated']} | {c['observed']} | {c['gap_pp']} | {c['within_5pp']} |")
    lat, cit = m["latency"], m["citations"]
    L += ["", "## 6. Latency", "",
          f"- All tickets: p50 {lat['all_p50_ms']} ms, p95 {lat['all_p95_ms']} ms. Auto-replies: p50 {lat['auto_p50_ms']} ms, **p95 {lat['auto_p95_ms']} ms** (target < 3000 ms: {lat['p95_under_3s']})",
          f"- Model provider: {m['llm']['calls']} calls, {m['llm']['retries']} retries, {m['llm']['failures']} failures, {m['llm']['tokens']} tokens", "",
          "## 7. Citations and answer quality", "",
          f"- Auto-replies {cit.get('n_auto')}; with a citation {cit.get('responses_with_citation')}; citations that resolve {cit.get('citation_resolves_rate')}; cited the expected article {cit.get('cited_expected_doc_rate')}"]
    j = m.get("judge") or {}
    if j.get("n_judged"):
        L += [f"- Model-assessed ({j['assessor']}), n={j['n_judged']}: hallucination rate **{j['hallucination_rate']}**, citations resolve {j['all_citations_resolve_rate']}, "
              f"prohibited claims {j['prohibited_claims_rate']}, required-point coverage {j['coverage_of_required_points_rate']}, pass {j['pass_rate']}"]
    else:
        L += ["- Model-assessed hallucination check not run (use --judge N)."]
    L += ["", "## 8. Governance", "",
          f"- Outbound PII findings (independent re-scan): **{g['pii_violations']}**",
          f"- Guardrail blocks by type: {g['guardrail_blocks_by_type'] or 'none'}",
          f"- Why tickets were routed as they were: {g['decision_reason_counts']}",
          f"- Escalations with a complete context packet: {g['escalations_with_complete_context']} / {g['escalations']}",
          f"- Resolution records written (compounding signal): {g['resolution_records_written']}", "", "## 9. Fairness by segment (groups with n < 15 are flagged)", ""]
    for name, seg in m["segments"].items():
        L.append(f"**{name}**  - max gap (pp): {seg['max_gap_pp']}")
        for grp, v in seg["groups"].items():
            L.append(f"- {grp}: n={v['n']}{' (low n)' if v['low_n'] else ''}, auto rate {v['auto_rate']}, route acc {v['route_accuracy']}, intent acc {v['intent_accuracy']}, retrieval hit@1 {v['retrieval_hit@1']}")
        L.append("")
    return "\n".join(L)


def main() -> int:
    args = parse_args()
    if not os.path.exists(args.input):
        print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
        return 2
    try:
        tickets = ingest.load_tickets(args.input)
    except Exception as e:
        print(f"ERROR: could not read tickets: {e}", file=sys.stderr)
        return 2
    if args.max_tickets:
        tickets = tickets[: args.max_tickets]

    run_id = args.run_id or pipeline.new_run_id()
    print("=" * 64 + f"\nCloudServe harness  run={run_id}\n  input : {args.input} ({len(tickets)} tickets)\n  output: {args.output}\n" + "=" * 64, flush=True)
    logging_store.init_db()
    print("warm-up:", pipeline.warm_up(), flush=True)
    llm.reset_breaker()

    t0 = time.time()
    rows = run_tickets(tickets, run_id, args.verbose)
    wall = round(time.time() - t0, 1)

    results = [r for r, _ in rows]
    gt = load_ground_truth(args.ground_truth)
    labelled = any(((t or {}).get("labels") or {}).get("intent") for _, t in rows)
    m = {
        "run": {"run_id": run_id, "input": args.input, "tickets": len(rows), "labelled": labelled, "wall_seconds": wall,
                "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "model": llm.model_name(),
                "threshold": pipeline.route.get_threshold(), "ticket_errors": sum(1 for r in results if r.get("status") != "ok")},
        "routing": M.routing_metrics(rows), "classification": M.classification_metrics(rows),
        "retrieval": M.retrieval_metrics(rows), "calibration": M.calibration(rows), "latency": M.latency_metrics(rows),
        "citations": M.citation_metrics(rows), "business": M.business_proxies(rows),
        "segments": M.segment_metrics(rows, {
            "customer_tier": lambda r, t: t.get("customer_tier"), "language_fluency": lambda r, t: t.get("language_fluency"),
            "region": lambda r, t: t.get("customer_region"), "channel": lambda r, t: r.get("channel")}),
        "governance": governance(rows, run_id), "llm": dict(llm.stats),
    }
    if args.judge:
        print(f"model-assessing up to {args.judge} auto-replies ...", flush=True)
        m["judge"] = judge_many_safe(results, gt, args.judge)

    out_dir = os.path.dirname(os.path.abspath(args.output))
    os.makedirs(out_dir, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"metrics": m, "results": results}, f, indent=2, default=str)
    stem = os.path.splitext(args.output)[0]
    with open(stem + ".md", "w", encoding="utf-8") as f:
        f.write(render_report(m))
    if args.judge and (m.get("judge") or {}).get("verdicts"):
        write_review_csv(stem + "_human_review.csv", results, m["judge"]["verdicts"])

    print("\n" + render_report(m).split("## 1.")[0])
    print(f"Saved: {args.output}\n       {stem}.md")
    return 0


def judge_many_safe(results, gt, n):
    try:
        from evaluation.judge import judge_many
        return judge_many(results, gt, n)
    except Exception as e:
        return {"n_judged": 0, "error": f"{type(e).__name__}: {e}"}


def write_review_csv(path, results, verdicts):
    by = {r["ticket_id"]: r for r in results}
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ticket_id", "reply", "cited_docs", "model_hallucination_flag", "model_missing_points", "human_hallucination (Y/N)", "human_notes"])
        for tid, v in verdicts.items():
            r = by.get(tid, {})
            w.writerow([tid, (r.get("response_text") or "").replace("\n", " "), ",".join(c["doc_id"] for c in r.get("citations", [])),
                        v.get("hallucinations_detected"), "; ".join(v.get("missing_points", []) or []), "", ""])


if __name__ == "__main__":
    sys.exit(main())
