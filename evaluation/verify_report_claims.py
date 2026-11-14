"""
Recompute the factual claims the report and the discovery workbook make, from the raw data, the saved run results and the
interview transcripts, and write docs/CLAIMS_CHECK.md. Nothing here is typed from memory: each line compares a number or a quote
used in the report with a fresh computation.

Categories
  PASS / FAIL   recomputed now and compared with the figure stated in the report
  QUOTE         a quotation attributed to a stakeholder was found (or not) in the interview transcript
  MANUAL        cannot be checked by a script; the author must confirm (listed at the end)

Run: venv/bin/python3 evaluation/verify_report_claims.py
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

from docx import Document

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
PACK = os.path.expanduser("~/Downloads/FDE_Capstone_Complete/Capstone_Pack/05_Datasets/Stakeholder_Interviews.docx")
rows = []   # (status, area, claim, computed)


def load(p):
    return json.load(open(os.path.join(ROOT, p)))


def check(area, claim, computed, stated, tol=0.0005, fmt="{:.3f}"):
    ok = abs(computed - stated) <= tol
    rows.append(("PASS" if ok else "FAIL", area, claim, f"computed {fmt.format(computed)}, stated {fmt.format(stated)}"))


dev, val = load("data/development_tickets.json"), load("data/validation_tickets.json")
docs = load("data/documentation.json")
gt = load("data/ground_truth_responses.json")
n = len(dev)
frac = lambda f, ts=dev: sum(1 for t in ts if f(t)) / len(ts)

# ---------------------------------------------------------------- discovery facts (workbook and report sections 2 and 3)
check("data", "development tickets", n, 500, 0, "{:.0f}")
check("data", "validation tickets", len(val), 80, 0, "{:.0f}")
check("data", "knowledge-base articles", len(docs), 29, 0, "{:.0f}")
check("data", "reference answers", len(gt), 200, 0, "{:.0f}")
check("discovery", "answerable from documentation", frac(lambda t: t["labels"]["answerable_from_docs"]), 0.714)
check("discovery", "escalated (history)", frac(lambda t: t["history"]["escalated"]), 0.562)
check("discovery", "first-contact resolution (history)", frac(lambda t: t["history"]["first_contact_resolution"]), 0.438)
check("discovery", "repeat contacts", frac(lambda t: t["history"]["repeat_contact"]), 0.216)
check("discovery", "must-not-auto-respond share", frac(lambda t: t["labels"]["must_not_auto_respond"]), 0.174)
check("discovery", "must-not-auto-respond count", sum(t["labels"]["must_not_auto_respond"] for t in dev), 87, 0, "{:.0f}")
check("discovery", "high urgency share", frac(lambda t: t["labels"]["urgency"] == "high"), 0.292)
check("discovery", "mean CSAT", sum(t["history"]["csat_rating"] for t in dev) / n, 2.972, 0.005, "{:.3f}")
ch = Counter(t["channel"] for t in dev)
for name, cnt in (("email", 212), ("chat", 155), ("docs_comment", 78), ("forum", 55)):
    check("discovery", f"channel {name}", ch[name], cnt, 0, "{:.0f}")
ent = [t for t in dev if t["customer_tier"] == "enterprise"]
check("discovery", "enterprise first-contact resolution", frac(lambda t: t["history"]["first_contact_resolution"], ent), 0.373)
check("discovery", "enterprise escalated", frac(lambda t: t["history"]["escalated"], ent), 0.627)
nf = [t for t in dev if t["language_fluency"] == "non_fluent"]
fl = [t for t in dev if t["language_fluency"] == "fluent"]
check("discovery", "non-fluent tickets", len(nf), 120, 0, "{:.0f}")
check("discovery", "non-fluent FCR", frac(lambda t: t["history"]["first_contact_resolution"], nf), 0.458)
check("discovery", "fluent FCR", frac(lambda t: t["history"]["first_contact_resolution"], fl), 0.432)
check("discovery", "non-fluent CSAT", sum(t["history"]["csat_rating"] for t in nf) / len(nf), 3.04, 0.005, "{:.2f}")
check("discovery", "fluent CSAT", sum(t["history"]["csat_rating"] for t in fl) / len(fl), 2.95, 0.005, "{:.2f}")

# the four restricted intents are exactly the flagged tickets
from src.classify import SAFETY_INTENTS
mism = sum(1 for t in dev + val if (t["labels"]["intent"] in SAFETY_INTENTS) != bool(t["labels"]["must_not_auto_respond"]))
check("design", "restricted intents equal the must-not-auto-respond flag (mismatches)", mism, 0, 0, "{:.0f}")

# ---------------------------------------------------------------- label noise (section 5.3)
norm = lambda t: re.sub(r"\s+", " ", (t.get("subject", "") + " " + t.get("body", "")).lower()).strip()
groups = defaultdict(list)
for t in dev:
    groups[norm(t)].append(t)
dups = sum(len(g) for g in groups.values() if len(g) > 1)
check("data quality", "tickets sharing text with another ticket", dups, 254, 0, "{:.0f}")


def purity(key):
    tot = ok = 0
    for g in groups.values():
        if len(g) < 2:      # only texts that appear more than once can disagree (254 tickets)
            continue
        c = Counter(key(t) for t in g)
        tot += len(g)
        ok += c.most_common(1)[0][1]
    return ok / tot


check("data quality", "route label agreement for identical text", purity(lambda t: t["labels"]["expected_route"]), 0.878)
check("data quality", "urgency label agreement for identical text", purity(lambda t: t["labels"]["urgency"]), 0.685)
check("data quality", "share of tickets whose label says escalate", frac(lambda t: t["labels"]["expected_route"] == "escalate"), 0.378)
for tier, st in (("enterprise", 0.386), ("standard", 0.391), ("business", 0.354)):
    ts = [t for t in dev if t["customer_tier"] == tier]
    check("fairness context", f"{tier} share labelled escalate", frac(lambda t: t["labels"]["expected_route"] == "escalate", ts), st)
ap = [t for t in dev if t["customer_region"] == "asia_pacific"]
eu = [t for t in dev if t["customer_region"] == "europe"]
check("fairness context", "Asia-Pacific share labelled escalate", frac(lambda t: t["labels"]["expected_route"] == "escalate", ap), 0.462)
check("fairness context", "Europe share labelled escalate", frac(lambda t: t["labels"]["expected_route"] == "escalate", eu), 0.318)
dc = [t for t in dev if t["channel"] == "docs_comment"]
check("fairness context", "docs_comment share labelled escalate", frac(lambda t: t["labels"]["expected_route"] == "escalate", dc), 0.474)
check("data", "oldest article age in days (all articles fresh)", max(int(d["last_reviewed_days_ago"]) for d in docs), 0, 0, "{:.0f}")

# ---------------------------------------------------------------- results (report sections 1, 7, 8)
R = lambda f: load(f"evaluation/results/{f}.json")["metrics"]
dm, nm, vm, om = R("dev_run"), R("dev_run_novel090"), R("gate_run_validation"), R("outage_run_validation")
for label, m, nt in (("dev", dm, 500), ("dev unseen wording", nm, 500), ("validation", vm, 80), ("outage drill", om, 80)):
    check("results", f"{label}: tickets processed", m["routing"]["n"], nt, 0, "{:.0f}")
    check("results", f"{label}: per-ticket errors", m["run"]["ticket_errors"], 0, 0, "{:.0f}")
    rows.append(("PASS" if m["governance"]["log_reconciles"] else "FAIL", "results", f"{label}: decision log reconciles with tickets processed", str(m["governance"]["log_reconciles"])))
    check("results", f"{label}: safety violations", m["routing"].get("safety_violations", 0), 0, 0, "{:.0f}")
    check("results", f"{label}: PII findings", m["governance"]["pii_violations"], 0, 0, "{:.0f}")
check("results", "outage drill: automatic replies sent", om["routing"]["auto_respond"], 0, 0, "{:.0f}")
check("results", "outage drill: escalations", om["routing"]["escalated"], 80, 0, "{:.0f}")
for label, m in (("dev", dm), ("dev unseen wording", nm), ("validation", vm)):
    check("results", f"{label}: citations resolve", m["citations"]["citation_resolves_rate"], 1.0)
    check("results", f"{label}: escalations with a complete context packet", m["governance"]["escalation_context_completeness"], 1.0)
dj = R("dev_run").get("judge", {})
check("results", "dev judge: replies judged", dj.get("n_judged", 0), 100, 0, "{:.0f}")
check("results", "dev judge: hallucination rate", dj.get("hallucination_rate", 1), 0.0)
check("results", "dev judge: prohibited-claim rate", dj.get("prohibited_claims_rate", 1), 0.0)
check("results", "dev judge: required-point coverage", dj.get("coverage_of_required_points_rate", 0), 0.94)
vj = vm.get("judge", {})
check("results", "validation judge: replies judged", vj.get("n_judged", 0), 50, 0, "{:.0f}")
check("results", "validation judge: hallucination rate", vj.get("hallucination_rate", 1), 0.0)
sel = load("evaluation/results/threshold_selection.json")
check("calibration", "chosen threshold", sel["chosen"], 0.85, 0)
check("calibration", "expected calibration error is within 5 pp", min(sel["ece_pp"], 5.0), sel["ece_pp"], 0, "{:.2f}")
check("calibration", "restricted tickets misclassified at every threshold", sel["sweep"][0]["restricted_leaks"], 6, 0, "{:.0f}")
from src.route import DEFAULT_THRESHOLD, SAFETY_PROXIMITY
check("code", "default routing threshold in src/route.py", DEFAULT_THRESHOLD, 0.85, 0)
check("code", "safety-proximity weight in src/route.py", SAFETY_PROXIMITY, 0.10, 0)
for fname, label in (("fairness_dev", "plain dev run"), ("fairness_dev_novel", "unseen-wording run")):
    g = load(f"evaluation/results/{fname}.json")["segments"]["customer_tier"]["groups"]
    ok = g["enterprise"]["gap_pp"] > 5 and g["standard"]["gap_pp"] > 5
    rows.append(("PASS" if ok else "FAIL", "fairness", f"tier gap above 5 pp for enterprise and standard ({label})", f"enterprise {g['enterprise']['gap_pp']} pp (p={g['enterprise']['p_vs_best']}), standard {g['standard']['gap_pp']} pp (p={g['standard']['p_vs_best']})"))
gn = load("evaluation/results/fairness_dev_novel.json")["segments"]["customer_tier"]["groups"]
rows.append(("PASS" if gn["enterprise"]["finding"] and gn["standard"]["finding"] else "FAIL", "fairness", "tier gap is statistically significant with unseen wording", f"p={gn['enterprise']['p_vs_best']} / {gn['standard']['p_vs_best']}"))

# ---------------------------------------------------------------- quotations attributed to stakeholders
def text_of(path):
    d = Document(path)
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for r in t.rows:
            parts += [c.text for c in r.cells]
    s = " ".join(parts).lower().replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", s)


if os.path.exists(PACK):
    iv = text_of(PACK)
    quotes = [
        ("Marcus", "i picture it answering the easy ones"), ("Marcus", "i would rather it said nothing"),
        ("Marcus", "first contact resolution, if i am being honest, more than response time"), ("Daniel", "twice as fast"),
        ("Sofia", "that would save me half of every ticket"), ("Daniel", "those become contractual quickly"),
        ("Ines", "feature requests"), ("Ines", "which article an answer came from"),
    ]
    for who, q in quotes:
        rows.append(("QUOTE" if q in iv else "FAIL", "interviews", f"{who}: \"{q}\"", "found in transcript" if q in iv else "NOT FOUND (check wording)"))
else:
    rows.append(("MANUAL", "interviews", "interview transcript not found; quotations unchecked", PACK))

# ---------------------------------------------------------------- output
manual = [
    "Effort-log hours, hours available per week, signature and the four reflection answers (Effort_Log.docx).",
    "The human second assessment of replies (NFR-03): only the independent model has assessed replies so far.",
    "Named risk owners in the Governance Framework: proposed roles, not agreed with those people.",
    "Provider prices (USD 0.02 / 0.04 per million tokens) were read from OpenRouter's public model list on 12 November 2026; prices change.",
    "Groq free-tier latency (p50 7 s, p95 11 s) and the 11 s versus 0.4 s provider-routing comparison come from earlier runs whose result files are kept, not from this script.",
    "The five routing-signal AUCs (0.51/0.47 retrieval score, 0.46/0.42 model judge) come from evaluation/eval_*.py runs in an earlier session; re-run those scripts to reproduce.",
    "Interview content other than the quotations above (what each stakeholder said, paraphrased) was not machine-checked.",
    "The statement that the hidden evaluation set was not used and the validation set was used while debugging is a statement about the author's own process.",
    "Dates: the recorded project phases (27 Oct to 9 Nov 2026) differ from the git history (7 to 14 Nov 2026), and both are after the 13 September deadline printed in the brief.",
]
counts = Counter(r[0] for r in rows)
lines = ["# Report claims check", "",
         "Generated by `evaluation/verify_report_claims.py`. Each row recomputes a figure or a quotation that the report uses.", "",
         f"**{counts['PASS']} passed, {counts['QUOTE']} quotations found, {counts['FAIL']} failed.** Items a script cannot check are listed at the end.", "",
         "| Status | Area | Claim | Result |", "|---|---|---|---|"]
for s, a, c, r in rows:
    lines.append(f"| {s} | {a} | {c} | {r} |")
lines += ["", "## Needs the author (cannot be checked by a script)", ""] + [f"- {m}" for m in manual]
open(os.path.join(ROOT, "docs", "CLAIMS_CHECK.md"), "w").write("\n".join(lines) + "\n")
print(f"{counts['PASS']} passed, {counts['QUOTE']} quotes found, {counts['FAIL']} failed")
for s, a, c, r in rows:
    if s == "FAIL":
        print("FAIL:", a, "|", c, "|", r)
sys.exit(1 if counts["FAIL"] else 0)
