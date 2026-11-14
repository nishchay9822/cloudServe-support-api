"""
Fill the official Governance_Framework.docx template.
Numbers come from evaluation/results/*.json (fairness_dev.json, fairness_val.json, dev_run.json, gate_run_validation.json).
Run: venv/bin/python3 docs/generate_governance.py
"""
import copy
import json
import os
from docx import Document
from docx.shared import Pt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "evaluation", "results")
TEMPLATE = "/Users/nishchaygupta/Downloads/FDE_Capstone_Complete/Capstone_Pack/03_Reference/Governance_Framework.docx"
OUT = os.path.join(HERE, "Governance_Framework.docx")

dev = json.load(open(os.path.join(RES, "fairness_dev.json")))["segments"]
val = json.load(open(os.path.join(RES, "fairness_val.json")))["segments"]
doc = Document(TEMPLATE)


def put(cell, text, size=8.5):
    p = cell.paragraphs[0]
    for extra in cell.paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    p.add_run(text).font.size = Pt(size)


def ensure_rows(table, n):
    while len(table.rows) - 1 < n:
        table._tbl.append(copy.deepcopy(table.rows[-1]._tr))


def fill(table, rows):
    ensure_rows(table, len(rows))
    for i, vals in enumerate(rows, start=1):
        for c, v in zip(table.rows[i].cells, vals):
            put(c, v)


def para_after(anchor_el, text, like_para):
    """Insert a body paragraph (copy of like_para's formatting) after an element."""
    new = copy.deepcopy(like_para._element)
    anchor_el.addnext(new)
    from docx.text.paragraph import Paragraph
    p = Paragraph(new, like_para._parent)
    for r in list(p.runs)[1:]:
        r._element.getparent().remove(r._element)
    if p.runs:
        p.runs[0].text = text
    else:
        p.add_run(text)
    return p


T = doc.tables
risk, fair, incident, kill, decl = T[2], T[3], T[6], T[7], T[8]
body_like = next(p for p in doc.paragraphs if p.text.startswith("Count your logged decisions"))

# ------------------------------------------------------------------ 1 decision logging: coverage result
cov = next(p for p in doc.paragraphs if p.text.startswith("Count your logged decisions"))
para_after(cov._element,
           "Result. Every harness run reconciles: 80 of 80 validation tickets and 500 of 500 development tickets produced exactly one logged "
           "decision (the harness prints this check and the report records it). Unit tests assert it for the failure paths: provider outage, "
           "malformed input, and a batch containing failures each still write a decision, and the kill-switch drill checks the escalated ticket is retrievable from the log. The log stores the fields in the minimum record above, "
           "plus run_id and token use. It is a SQLite file (storage/decisions.db) and can be read per ticket with GET /decisions/{ticket_id}. "
           "Not yet done: the log is not tamper-evident and has no retention or deletion policy, which a production GDPR deployment would need.",
           body_like)

# ------------------------------------------------------------------ 2 risk register
AG = "Owners are proposed roles from the discovery interviews and the author; they have not been asked to accept them."
fill(risk, [
    ["R-01", "The system answers confidently and incorrectly", "Medium",
     "Very high",
     "Replies are written only from the full text of the top retrieved article(s) (src/generate.py, prompt PR-GN-01 v4.0, JSON output with a status field). The model may decline (status no_answer), which escalates. Grounding and figure checks block any number or claim not in the shown articles (src/guardrails.py). Confidence floor 0.85, calibrated on simulated unseen wording (error 0.3 pp), from classifier agreement, not model self-report. Measured: 0 of 150 judged replies hallucinated (50 validation, 100 dev; independent model), citations resolve 100%. Known gap: 25-28% of auto-replies go to tickets whose label says escalate (R-09), and the human second assessment is still pending. Alerts: AutoRateDrift, LowConfidenceShift (defined; the Grafana stack has not been run, see report).",
     "Marcus Adeyemi, Head of Support (accepts residual risk); engineering owner Nishchay Gupta"],
    ["R-02", "Private data appears in an outbound response", "Low",
     "Very high",
     "PII guardrail on every outbound reply (names, emails, addresses, account numbers, keys). Block and escalate, never redact and send. A test checks that the customer's name never appears in the reply. Measured: 0 findings across 580 tickets. Limit: the check is pattern-based; it cannot know that an ordinary-looking name belongs to another customer.",
     "Nishchay Gupta (engineering); weekly review of blocks by Daniel Okonkwo, Tier Two Engineer"],
    ["R-03", "A customer's input is treated as an instruction", "Low to medium",
     "Very high",
     "Ticket text is screened for instruction-override patterns before any model sees it (reason code injection_screen) and is passed to prompts as quoted data, never as system text. The injection check runs again in the guardrail stage before any reply is sent. Unit tests cover override phrases and the pre-model screen. Limit: no adversarial red-team beyond the unit tests; screening is pattern-based, so novel phrasing could pass the screen and rely on the other guardrails.",
     "Nishchay Gupta (engineering)"],
    ["R-04", "Some customer groups receive worse answers", "Medium",
     "High",
     "Fairness audit (section 3) run on 500 dev and 80 validation tickets by tier, fluency, length, region and channel, with confidence intervals and significance tests (evaluation/fairness_audit.py). Findings: one CONFIRMED tier disparity (enterprise and standard below business, above the 5-point target); other dimensions not significant, but the sample is underpowered. Dashboard can be sliced by channel. Mitigation still needed: per-segment live monitoring with a larger sample.",
     "Marcus Adeyemi, Head of Support"],
    ["R-05", "The documentation the system relies on goes stale", "High over time",
     "High",
     "Every reply cites its source doc_id, so a stale answer can be traced to one article. Guard added in src/retrieve.py: an article not reviewed within DOC_MAX_AGE_DAYS (default 180) is never quoted; the ticket escalates instead (unit-tested). The shipped corpus is a snapshot (every article reviewed 0 days ago), so the guard has not fired on real data. No process yet connects documentation edits to re-running the evaluation.",
     "Ines Varga, Technical Writer (documentation currency); engineering to re-run the gate after any documentation change"],
    ["R-06", "The model provider becomes unavailable", "High (it happened twice)",
     "Medium (degrades to humans, no wrong answers)",
     "Retries with backoff, Retry-After handling for rate limits, circuit breaker, and fail-fast on 401/402 (src/llm.py). Provider, base URL and model are configuration (FR-19); Groq was tested as a fallback. Outage drill: with the provider off, 80 of 80 tickets processed, all 80 escalated, 0 customer replies, 0 errors. Observed in practice: OpenRouter credit ran out (402) mid-project; Groq free tier rate-limited (429). Alert: ProviderUnavailable.",
     "Nishchay Gupta (engineering)"],
    ["R-07", "Latency degrades under load", "Medium",
     "Medium",
     "Measured p95 for auto-replies: about 0.7 to 1.1 s on OpenRouter (target under 3 s). On the Groq free tier p95 was 11 s because of rate limits, so that fallback misses the target. Provider routing sorted by throughput. Alert: LatencyP95High. Not done: the harness runs tickets one at a time; no concurrent load test, so behaviour at 500+ tickets a week at peak is unmeasured.",
     "Nishchay Gupta (engineering)"],
    ["R-08", "Costs rise unexpectedly with volume", "Low",
     "Low",
     "Tokens are logged per decision (NFR-07). Dev run: about 912 tokens per ticket. At OpenRouter's listed price for the generator (USD 0.02 per million input tokens, 0.04 per million output, checked 12 Nov 2026) that is roughly USD 0.00002 per ticket; the independent judge is more expensive but runs offline on samples. Retrieval and classification by nearest tickets cost nothing per call. Set a monthly spend cap on the provider key.",
     "Marcus Adeyemi, Head of Support (budget); Nishchay Gupta (monitoring)"],
    ["R-09", "Auto-replies go to tickets that should have gone to a human (routing labels are partly unpredictable)", "High (observed)",
     "Medium to high",
     "Measured: auto-reply precision about 71% on validation and 75% on dev; 18 and 99 false auto-responds. Five signals were tried to predict 'should escalate' for non-safety tickets and none worked (retrieval score AUC 0.51/0.47; LLM answerability AUC 0.46/0.42); identical ticket text carries the same route label only 87.8% of the time, so part of the label is not recoverable. Mitigation in the design: safety intents always escalate (0 violations of 101), replies must be grounded, and the first deployment should be draft-for-agent, not autonomous.",
     "Marcus Adeyemi, Head of Support"],
    ["R-10", "A credential is exposed", "Medium (an API key was pasted in chat once)",
     "High",
     ".env is gitignored; .env.example holds placeholders only; the git history was scanned for key patterns before submission. The exposed keys must be rotated at project end. Set a spend cap on every key.",
     "Nishchay Gupta"],
    ["R-11", "The evaluation overstates real-world performance", "High",
     "High",
     "254 of 500 dev tickets share their exact text with another dev ticket, so nearest-ticket classification (99.8% intent accuracy) is flattered; leave-one-out was used and a separate validation set held out, but both come from the same generator. Urgency labels are only 45-52% predictable (baseline 55%). The report states these limits. Mitigation: measure on live tickets in shadow mode before any claim.",
     "Nishchay Gupta"],
    ["R-12", "The learning loop stores bad resolutions and scales mistakes", "Low today",
     "Medium",
     "Resolution records (FR-13) are written but nothing reads them, so they cannot influence a reply today (compounding is therefore not demonstrated). Before they are used, Daniel Okonkwo's concern applies: outdated agent snippets would scale. Only resolutions confirmed by a good customer rating should feed the index.",
     "Daniel Okonkwo, Tier Two Engineer"],
])
para_after(risk._tbl, AG, body_like)

# ------------------------------------------------------------------ 3 fairness audit
D = lambda dim, g: dev[dim]["groups"][g]
pct = lambda x: f"{x * 100:.1f}%"


def res_gap(dim, g):
    best = max(s["resolution_rate"] for s in dev[dim]["groups"].values())
    return f"{(best - D(dim, g)['resolution_rate']) * 100:.1f} pp"


def row(label, dim, g, expl):
    s = D(dim, g)
    return [label, str(s["n"]), pct(s["resolution_rate"]), pct(s["quality_hit_at_1"]), res_gap(dim, g), expl]


dn = json.load(open(os.path.join(RES, "fairness_dev_novel.json")))["segments"]
short_k = next(k for k in dev["ticket_length"]["groups"] if k.startswith("short"))
long_k = next(k for k in dev["ticket_length"]["groups"] if k.startswith("long"))


def row(label, dim, g, note):
    s_, n_ = D(dim, g), dn[dim]["groups"][g]
    expl = (f"Route accuracy {s_['route_accuracy']*100:.1f}% ({s_['gap_pp']:.1f} pp below the best segment, p = {s_['p_vs_best']:.3f}); "
            f"false-automatic-reply rate {s_['false_auto_rate']*100:.1f}%; retrieval hit@1 {s_['quality_hit_at_1']*100:.1f}% "
            f"(gap {s_['quality_gap_pp']:.1f} pp, p = {s_['quality_p_vs_best']:.3f}). With unseen wording: route accuracy {n_['route_accuracy']*100:.1f}% "
            f"({n_['gap_pp']:.1f} pp, p = {n_['p_vs_best']:.3f}). " + note)
    return [label, str(s_["n"]), pct(s_["resolution_rate"]), pct(s_["quality_hit_at_1"]), res_gap(dim, g), expl]


fill(fair, [
    row("Enterprise customers", "customer_tier", "enterprise", "Trails business customers by more than the 5-point target in every run (significant with unseen wording, borderline in the plain run). Cause not identified: enterprise tickets are not labelled 'escalate' more often (38.6% vs 35.4%), but they are auto-answered more often when a human was expected."),
    row("Small business customers", "customer_tier", "business", "Best tier on route accuracy and the reference for the tier comparison."),
    row("Tickets in fluent English", "language_fluency", "fluent", "Not significantly different from non-fluent tickets."),
    row("Tickets in non-fluent English", "language_fluency", "non_fluent", "Retrieval is weaker, the direction the framework predicts, but only borderline. On the 80-ticket validation set this group (19 tickets) looked about 28 points worse; that did not replicate on the 120 development tickets, so it is treated as small-sample noise."),
    row("Short tickets", "ticket_length", short_k, "No significant gap in the final system. An earlier run showed a borderline retrieval gap for short tickets that did not persist."),
    row("Long or complex tickets", "ticket_length", long_k, "Long and short tickets carry the same share of 'escalate' labels; long tickets are auto-answered more often."),
    row("Standard customers", "customer_tier", "standard", "Trails business customers by more than the 5-point target in every run (significant with unseen wording, borderline in the plain run)."),
    row("Asia-Pacific region (lowest resolution)", "region", "asia_pacific", "Not significant. 46.2% of its tickets carry an 'escalate' label against 31.8% in Europe, so the system answers more tickets it should not."),
    row("Docs-comment channel (lowest resolution)", "channel", "docs_comment", "Not significant. 47.4% of its tickets carry an 'escalate' label (32 to 42% in other channels)."),
])
fair_note = para_after(fair._tbl,
    "Method. evaluation/fairness_audit.py segments a finished run and reports, per segment: auto-reply rate; resolution rate (an offline proxy: the system "
    "auto-replied and the labelled route was auto_respond; it is not a measure of customer outcomes); false-automatic-reply rate; quality (retrieval hit@1 on tickets "
    "answerable from the documentation); and route accuracy with a 95% Wilson interval, with the gap to the best segment and a two-proportion z-test. The table uses the 500 "
    "development tickets with plain leave-one-out, and also quotes the harder setting where each ticket is classified as if its wording were new. Validation results are in "
    "evaluation/results/fairness_val.md. Findings. (1) Enterprise and standard customers trail business customers in routing accuracy by roughly 8 to 13 points in every run, "
    "above the 5-point target, so the tier condition is not met as a point estimate; it is statistically significant with unseen wording and borderline in the plain run, and the audit makes about ten comparisons "
    "per run, so it is a consistent shortfall that needs live data, not a settled finding. "
    "correction. (2) No other dimension is consistently significant (the ticket-length gap appeared in one run and not the other), but the 95% intervals span roughly 10 to 20 pp, so the audit could only detect gaps of about 10 pp or more: "
    "'not significant' is not the same as 'fair'. (3) The non-fluent retrieval gap the framework warns about is present in direction but borderline. (4) Part of the apparent "
    "unequal treatment is label mix: segments differ in how many of their tickets carry an escalate label. A real deployment needs live per-segment monitoring and a stricter "
    "policy for the affected tiers before claiming parity.",
    body_like)

# ------------------------------------------------------------------ 5 incident response
fill(incident, [
    ["1. Detect",
     "Sources: a Grafana/Prometheus alert (monitoring/alerts.yml: ProviderUnavailable, LatencyP95High, GuardrailBlocksSpike, AutoRateDrift, LowConfidenceShift); an agent or customer reporting a wrong automated reply; the daily check of the dashboard. Confirm on a single ticket with GET /health and GET /decisions/<ticket_id>. Decide severity. SEV1: a customer may have received a wrong, unsafe or personal-data reply, or a safety ticket was auto-answered. SEV2: provider down, slow, or a spike in blocks (customers are protected because everything escalates).",
     "Whoever sees it raises it; on-call engineer confirms severity (author for this project).",
     "Acknowledge within 15 minutes of the alert."],
    ["2. Contain",
     "If SEV1, or you are not sure: turn the kill switch on first, diagnose second. Run: curl -X POST http://<host>:8000/admin/kill-switch -H 'Content-Type: application/json' -d '{\"on\": true, \"token\": \"<ADMIN_TOKEN>\"}'. No token or no API? On the server, create the file storage/KILL_SWITCH. Check GET /health shows kill_switch true, then send one test ticket and confirm it escalates with reason kill_switch. Tickets already being processed finish; every later ticket goes to a human. Tell the support agents that all tickets are manual until further notice.",
     "On-call engineer, or the Head of Support (holds the admin token).",
     "Within 5 minutes of confirming SEV1; takes effect on the next ticket (tested under 2 s)."],
    ["3. Assess",
     "Find every automated reply in the window. On the server: sqlite3 storage/decisions.db \"SELECT timestamp, ticket_id, reason, prompt_version, guardrail_results FROM decisions WHERE action_taken='auto_respond' AND timestamp >= '<window start>' ORDER BY timestamp\". For each ticket call GET /decisions/<ticket_id> and compare the reply with the cited article. Record: how many customers received a bad reply; which prompt version and model; whether any personal data left (SEV1 PII); whether the cause is the prompt, the documentation, the threshold, the model or an attack.",
     "On-call engineer with Daniel Okonkwo (Tier Two Engineer) reading the replies.",
     "First assessment within 60 minutes; full list of affected tickets within 4 hours."],
    ["4. Notify",
     "Tell the Head of Support at once for any SEV1 (he decides customer contact). Support agents contact each affected customer personally with a correction; the system does not send the correction. If any customer's personal data was disclosed, the company's data-protection contact must decide on regulator notification: under GDPR this is due within 72 hours of becoming aware (Art. 33), and affected people must be told if the risk to them is high (Art. 34). For SEV2, post a short note to the support channel and the status owner.",
     "Head of Support (Marcus Adeyemi) leads; the data-protection contact for personal data.",
     "Head of Support within 1 hour; regulator within 72 hours if personal data."],
    ["5. Remediate",
     "Fix the cause (prompt, threshold, documentation, model or screen). Add a regression test that reproduces the ticket. Run pytest tests/ -v, then python evaluation/harness.py on data/validation_tickets.json and compare with the gate: 0 safety violations, 0 PII findings, 100% citations resolving, no log gap. Register any prompt change as a new version in prompts/README.md. Turn the kill switch off only after the Head of Support signs off, then watch the dashboard for the first hour.",
     "Engineer fixes; Head of Support signs off; technical writer if the cause is documentation.",
     "Same day for a configuration fix; days for a prompt or model change."],
    ["6. Review",
     "Blameless post-mortem: timeline taken from the decision log, root cause, how it was detected and how late, what would have caught it earlier. Update the risk register, add or tune an alert, and record the incident. Re-run the fairness audit if the cause involved a customer group.",
     "Engineer, Head of Support, and the technical writer or Tier Two engineer if involved.",
     "Within 5 working days."],
])

# ------------------------------------------------------------------ kill switch
ks = {
    "What is the mechanism?": "Three routes into one check that runs first on every ticket (src/pipeline.py kill_switch_on): (1) POST /admin/kill-switch with the admin token; (2) a file at storage/KILL_SWITCH; (3) environment variable KILL_SWITCH=1 (needs a restart). While on, every ticket is escalated with reason code kill_switch and a context packet, and no model is called. Each such ticket is still logged.",
    "Who is authorised to use it?": "Anyone holding ADMIN_TOKEN: proposed as the Head of Support and the on-call engineer. With no ADMIN_TOKEN set the API route refuses everyone (403), so the default is closed. Anyone with shell access to the server can create the file. The token is not shared in the repository.",
    "How long until it takes effect?": "The next ticket. Measured in the drill: under 2 seconds from the HTTP call to the next ticket being escalated, with no deployment or restart. Limits: the switch is a file on one host, so a deployment with several API instances would need a shared store to switch them all.",
    "What happens to tickets in flight?": "A ticket already past the switch check finishes normally, including its guardrails, and may still send its reply; all later tickets go to a human. If an in-flight reply must also be stopped, stop the API process. The drill confirmed both behaviours.",
    "How is it tested?": "Automated drill tests/test_kill_switch.py: starts a ticket and holds it mid-generation, switches on over HTTP, checks the next ticket escalates with reason kill_switch in under 2 s, releases the first ticket and checks it completes, switches off and checks automatic replies resume; also checks that a wrong or missing token cannot switch it. test_pipeline.py and test_api.py cover the env switch and the token. Not tested: a drill by a person unfamiliar with the system, or a multi-instance deployment.",
}
for r in kill.rows[1:]:
    k = r.cells[0].text.strip()
    if k in ks:
        put(r.cells[1], ks[k])

# ------------------------------------------------------------------ declaration
dc = {
    "This system must never ...": "...send an automated reply to a ticket whose predicted intent is a security incident, compliance or data-residency request, feature request or unclear request, or send any reply that contains personal data, a figure or claim not in the cited article, or a promise about refunds or timelines.",
    "The mechanism that enforces that is ...": "Routing in deterministic code on the predicted intent (src/route.py), not on a model's say-so, with outbound guardrails that block and escalate (src/guardrails.py), and a kill switch. Evidence: 0 safety violations out of 101 safety tickets (87 dev, 14 validation, and 87 more with unseen wording) and 0 PII findings in 580 tickets.",
    "The most likely way it could still cause harm is ...": "A well-written, grounded reply that is incomplete or wrong for the customer's actual situation, sent to a ticket that needed a human: 25-29% of auto-replies in the evaluation went to tickets labelled 'escalate', and about half the route and urgency labels cannot be predicted from the text. Also: a safety ticket misclassified as an ordinary one. Both measurements come from synthetic, templated data, so real performance is probably lower.",
    "We would not deploy this without first ...": "running it in draft mode on live tickets, where agents see and edit the suggested reply, for several weeks while measuring acceptance and real accuracy; completing the human second assessment of replies; load testing on production hardware; agreeing named owners and the admin token holders; rotating all keys; setting provider spend caps; and deciding, with the Head of Support, whether to restrict auto-reply to the intents with the strongest measured precision.",
}
for r in decl.rows[1:]:
    k = r.cells[0].text.strip()
    if k in dc:
        put(r.cells[1], dc[k])

doc.save(OUT)
print("saved", OUT)
