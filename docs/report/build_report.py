"""
Build the capstone report PDF.
  venv/bin/python3 docs/report/build_report.py [--out path.pdf]
Every number in the text comes from evaluation/results/*.json via the context below, or is a constant
that was checked against those files when the text was written.
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
from reportlab.platypus import Spacer, Paragraph, PageBreak, Table, TableStyle
from reportlab.lib.units import mm
from engine import Report, ST, ACCENT, LIGHT
import figures
import part1, part2, part3
from evaluation.fairness_audit import wilson

RES = os.path.join(ROOT, "evaluation", "results")
J = lambda n: json.load(open(os.path.join(RES, n)))

TABLE_ORDER = ["asked", "findings", "disagree", "reqs", "alts", "modules", "bugs", "results", "runs", "judge", "calib", "sweep",
               "risks", "fairsum", "changes", "appfair", "appprompts", "apptests"]
FIG_ORDER = ["disc", "arch", "signals", "outcomes", "latency", "risk", "fair"]


def facts(name, tickets_file):
    d = J(name + ".json")
    m = d["metrics"]
    r, g, l, b, ret, c = m["routing"], m["governance"], m["latency"], m["business"], m["retrieval"], m["citations"]
    return {"n": r["n"], "auto": r["auto_respond"], "esc": r["escalated"], "auto_pct": r["auto_rate"] * 100, "esc_pct": r["escalation_rate"] * 100,
            "route": r["route_accuracy"] * 100, "prec": r["precision_of_auto_respond"] * 100, "fa": r["false_auto_respond"], "oe": r["over_escalation"],
            "viol": r["safety_violations"], "safe_n": r["safety_flagged_tickets"], "intent": m["classification"]["intent_accuracy"] * 100,
            "hit1": ret["hit@1"] * 100, "hit3": ret["hit@3"] * 100, "hit5": ret["hit@5"] * 100, "cite": c["cited_expected_doc_rate"] * 100,
            "blocks": sum(g["guardrail_blocks_by_type"].values()), "blocks_txt": ", ".join(f"{v} {k.replace('_', ' ')}" for k, v in g["guardrail_blocks_by_type"].items()) or "none",
            "ctx_n": g["escalations_with_complete_context"] if "escalations_with_complete_context" in g else g.get("escalations"),
            "esc_n": g.get("escalations"), "resrec": g.get("resolution_records_written"), "p50": l["auto_p50_ms"], "p95": l["auto_p95_ms"], "mean": l["auto_mean_ms"],
            "tok": round(m["llm"]["tokens"] / r["n"]), "proxy": b["auto_resolution_proxy"] * 100, "brief": b["fcr_brief_formula"] * 100,
            "minprec": min(v["precision"] for v in m["classification"]["per_class"].values()) * 100, "reasons": g["decision_reason_counts"]}


def context():
    dev, val = J("dev_run.json"), J("gate_run_validation.json")
    dm, vm = dev["metrics"], val["metrics"]
    t = {"dev": {x["ticket_id"]: x for x in json.load(open(os.path.join(ROOT, "data", "development_tickets.json")))},
         "val": {x["ticket_id"]: x for x in json.load(open(os.path.join(ROOT, "data", "validation_tickets.json")))}}

    def unans(run, key):
        auto = [r for r in run["results"] if r["decision"] == "auto_respond"]
        return len(auto), sum(1 for r in auto if not t[key][r["ticket_id"]]["labels"]["answerable_from_docs"])
    ad, ud = unans(dev, "dev")
    av, uv = unans(val, "val")
    nd, nv = dm["routing"]["n"], vm["routing"]["n"]
    fd, fv = dm["business"]["auto_resolution_proxy"], vm["business"]["auto_resolution_proxy"]
    ci = lambda p, n: (lambda lo_hi: f"{lo_hi[0]*100:.0f} to {lo_hi[1]*100:.0f}%")(wilson(round(p * n), n))
    minp = lambda m: min(v["precision"] for v in m["classification"]["per_class"].values()) * 100
    sel = J("threshold_selection.json")
    return {
        "dv": facts("dev_run", "development_tickets"), "dn": facts("dev_run_novel090", "development_tickets"), "vl": facts("gate_run_validation", "validation_tickets"),
        "sel": sel,
        "fair_dn": J("fairness_dev_novel.json")["segments"],
        "gaps": {k: v["max_gap_pp_route_accuracy"] for k, v in J("fairness_dev.json")["segments"].items()},
        "dev_date": "11 November 2026", "gate_date": "12 November 2026", "model": "meta-llama/llama-3.1-8b-instruct (OpenRouter)",
        "commit": "0297e25",
        "p95_val_ms": vm["latency"]["auto_p95_ms"], "p95_dev_ms": dm["latency"]["auto_p95_ms"],
        "med_val_ms": vm["latency"]["auto_p50_ms"], "med_dev_ms": dm["latency"]["auto_p50_ms"],
        "mean_val_ms": vm["latency"]["auto_mean_ms"], "mean_dev_ms": dm["latency"]["auto_mean_ms"],
        "brief_fcr_dev": dm["business"]["fcr_brief_formula"] * 100, "brief_fcr_val": vm["business"]["fcr_brief_formula"] * 100,
                "med_dev": dm["business"]["median_time_to_first_reply_seconds_auto"], "med_val": vm["business"]["median_time_to_first_reply_seconds_auto"],
        "fcr_dev": fd * 100, "fcr_val": fv * 100, "fcr_dev_ci": ci(fd, nd), "fcr_val_ci": ci(fv, nv),
        "esc_dev": dm["business"]["system_escalation_rate"] * 100, "esc_val": vm["business"]["system_escalation_rate"] * 100,
        "auto_dev": ad, "auto_val": av, "unans_dev": ud, "unans_val": uv,
        "unans_dev_pct": ud / ad * 100, "unans_val_pct": uv / av * 100,
        "adj_dev": (nd - ad + ud) / nd * 100, "adj_val": (nv - av + uv) / nv * 100,
        "minprec_dev": minp(dm), "minprec_val": minp(vm),
        "fair_dev": J("fairness_dev.json")["segments"],
        "tests_rows": tests_rows(),
    }


TEST_DESC = {
    "test_api.py": "HTTP interface: health, process, audit trail, validation errors, admin token.",
    "test_fairness_audit.py": "Wilson interval, significance test, confirmed vs suggestive findings, small-segment handling.",
    "test_guardrails.py": "Privacy, grounding, figures in every sentence, injection, tone, confidence floor.",
    "test_harness.py": "Command-line contract, exit codes, output schema, metrics report.",
    "test_ingest.py": "Four channels and the alias, malformed input, no ground-truth leakage.",
    "test_kill_switch.py": "Kill-switch drill over HTTP with a ticket in flight; token required.",
    "test_logging.py": "Decision log schema, coverage and resolution records.",
    "test_monitoring.py": "Dashboard and alert metrics exist in /metrics; Prometheus config.",
    "test_pipeline.py": "End to end paths: auto-reply, safety, outage, no key, malformed, injection, kill switch, guardrail block, NO_ANSWER, batch logging.",
    "test_retrieve_classify_generate.py": "Retrieval floor and empty results, stale-article guard, classifier, generator and citations.",
    "test_route.py": "Ordered deterministic routing rules and escalation packet.",
}


def tests_rows():
    out = subprocess.run([sys.executable, "-m", "pytest", "tests", "--collect-only", "-q"], cwd=ROOT, capture_output=True, text=True).stdout
    counts = {}
    for line in out.splitlines():
        m = re.match(r"tests/(test_\w+\.py)::", line)
        if m:
            counts[m.group(1)] = counts.get(m.group(1), 0) + 1
    rows = [[f, str(n), TEST_DESC.get(f, "")] for f, n in sorted(counts.items())]
    rows.append(["Total", str(sum(counts.values())), ""])
    return rows


def title_page(r):
    s = r.story
    s.append(Spacer(1, 55 * mm))
    s.append(Paragraph("CloudServe Intelligent Support System", ST["title"]))
    s.append(Spacer(1, 4 * mm))
    s.append(Paragraph("A retrieval-first, auditable support pipeline: from a chatbot request to a system that knows when to stay silent", ST["sub"]))
    s.append(Spacer(1, 22 * mm))
    for line in ("<b>Forward Deployed AI Engineering: Capstone Project</b>", "Report", "",
                 "Nishchay Gupta", "November 2026", "",
                 "Repository commit of the evaluated code: 0297e25"):
        s.append(Paragraph(line, ST["meta"]))
    s.append(Spacer(1, 40 * mm))
    t = Table([[Paragraph("Read this first. Headline results are on validation (80 tickets) and development (500 tickets, leave-one-out). "
                          "The hidden evaluation set was not used. Business outcomes are offline proxies. The human second assessment of reply quality "
                          "is outstanding. Sections 7 and 8 state the limits of every figure.", ST["note"])]], colWidths=[150 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("LINEBEFORE", (0, 0), (0, -1), 2.5, ACCENT),
                           ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    s.append(t)
    s.append(PageBreak())
    toc = [("1", "Executive summary"), ("2", "The problem"), ("3", "Discovery findings"), ("4", "Requirements"), ("5", "Architecture and design"),
           ("6", "Implementation"), ("7", "Evaluation"), ("8", "Governance and risk"), ("9", "The requirements revision"), ("10", "Conclusions"),
           ("", "Appendices")]
    s.append(Paragraph("Contents", ST["h1"]))
    for n, name in toc:
        s.append(Paragraph(f"{n + '  ' if n else ''}{name}", ST["body"]))
    s.append(Spacer(1, 6))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "NishchayGupta_Capstone_Report.pdf"))
    a = ap.parse_args()
    figs = figures.make_all()
    figs["arch"] = os.path.join(figures.OUT, "architecture_fig2.png")
    r = Report(a.out, TABLE_ORDER, FIG_ORDER, "CloudServe Intelligent Support System: Capstone Report", "Nishchay Gupta")
    ctx = context()
    title_page(r)
    part1.build(r, figs, ctx)
    part2.build(r, figs, ctx)
    part3.build(r, figs, ctx)
    pages = r.build()
    body_end = pages["app"] - 1
    print(f"built {a.out}")
    print(f"total pages {r.last_page}; body (cover to end of section 10) {body_end} pages; appendices from page {pages['app']}")
    print("section start pages:", {k: v for k, v in pages.items()})


if __name__ == "__main__":
    main()
