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
     "Replies are written only from the full text of the top retrieved article(s) (src/generate.py, prompt PR-GN-01 v3.0). The model may answer NO_ANSWER, which escalates. Grounding and figure checks block any number or claim not in the shown articles (src/guardrails.py). Confidence floor 0.80 from classifier agreement, not model self-report. Measured: 0 of 150 judged replies hallucinated (50 validation, 100 dev; independent model), citations resolve 100%. Known gap: 25-28% of auto-replies go to tickets whose label says escalate (R-09), and the human second assessment is still pending. Alerts: AutoRateDrift, LowConfidenceShift (defined; the Grafana stack has not been run, see report).",
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
     "Fairness audit (section 3) run on 500 dev and 80 validation tickets by tier, fluency, length, region and channel, with confidence intervals and significance tests (evaluation/fairness_audit.py). Findings: one borderline confirmed gap (short tickets retrieve worse); several directional gaps the sample cannot confirm. Dashboard can be sliced by channel. Mitigation still needed: per-segment live monitoring with a larger sample.",
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
     "Measured p95 for auto-replies: 673 ms on OpenRouter (target under 3 s). On the Groq free tier p95 was 11 s because of rate limits, so that fallback misses the target. Provider routing sorted by throughput. Alert: LatencyP95High. Not done: the harness runs tickets one at a time; no concurrent load test, so behaviour at 500+ tickets a week at peak is unmeasured.",
     "Nishchay Gupta (engineering)"],
    ["R-08", "Costs rise unexpectedly with volume", "Low",
     "Low",
     "Tokens are logged per decision (NFR-07). Dev run: about 912 tokens per ticket. At OpenRouter's listed price for the generator (USD 0.02 per million input tokens, 0.04 per million output, checked 12 Nov 2026) that is roughly USD 0.00002 per ticket; the independent judge is more expensive but runs offline on samples. Retrieval and classification by nearest tickets cost nothing per call. Set a monthly spend cap on the provider key.",
     "Marcus Adeyemi, Head of Support (budget); Nishchay Gupta (monitoring)"],
    ["R-09", "Auto-replies go to tickets that should have gone to a human (routing labels are partly unpredictable)", "High (observed)",
     "Medium to high",
     "Measured: auto-reply precision 71.9% on validation and 75% on dev; 18 and 98 false auto-responds. Five signals were tried to predict 'should escalate' for non-safety tickets and none worked (retrieval score AUC 0.51/0.47; LLM answerability AUC 0.46/0.42); identical ticket text carries the same route label only 87.8% of the time, so part of the label is not recoverable. Mitigation in the design: safety intents always escalate (0 violations of 101), replies must be grounded, and the first deployment should be draft-for-agent, not autonomous.",
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


short_k = next(k for k in dev["ticket_length"]["groups"] if k.startswith("short"))
long_k = next(k for k in dev["ticket_length"]["groups"] if k.startswith("long"))
fill(fair, [
    row("Enterprise customers", "customer_tier", "enterprise",
        "Highest auto-reply rate (83.1%) but the lowest route accuracy (73.5% vs 82.9% for business, gap 9.4 pp, p = 0.08, not significant) and the highest false-auto rate (24.1% vs 16.5%). Retrieval quality is the best of the tiers. The cause is not identified: enterprise tickets are not labelled 'escalate' more often (38.6% vs 35.4% for business), so it is not simply a label mix effect. With 83 tickets the gap cannot be confirmed or chased."),
    row("Small business customers", "customer_tier", "business",
        "Best tier on resolution (64.0%) and route accuracy (82.9%), but the lowest retrieval hit@1 (88.6%). No significant difference from other tiers."),
    row("Tickets in fluent English", "language_fluency", "fluent",
        "Reference group: route accuracy 77.1%, retrieval hit@1 91.9%."),
    row("Tickets in non-fluent English", "language_fluency", "non_fluent",
        "Retrieval hit@1 is 5.6 pp lower (86.2% vs 91.9%, p = 0.12, not significant), the direction the framework predicts for retrieval systems. Route accuracy is not lower (80.8% vs 77.1%). On the 80-ticket validation set the non-fluent group looked much worse (19 tickets, route accuracy 52.6%, 29 pp gap, p = 0.01) but this reversed on the 120 non-fluent dev tickets, so it is treated as small-sample noise. Pooled over both sets (139 non-fluent vs 441 fluent tickets) route accuracy is 77.0% vs 77.8%: no gap. The retrieval gap should be rechecked on live data."),
    row("Short tickets", "ticket_length", short_k,
        "CONFIRMED FINDING (borderline): retrieval hit@1 87.6% vs 93.9% for long tickets, a 6.2 pp gap, p = 0.046 before correcting for the roughly ten group comparisons made, so one chance result at this level is plausible. Short tickets give the retriever less text to match. They are escalated slightly more often (auto rate 75.8% vs 83.7%), which is the safe direction."),
    row("Long or complex tickets", "ticket_length", long_k,
        "Higher retrieval quality (93.9%) but a higher false-auto rate (23.4% vs 16.5%) and lower route accuracy (74.9% vs 80.6%, p = 0.13). Long and short tickets carry the same share of 'escalate' labels (37.9% vs 37.7%), so the difference is that long tickets are auto-answered more often (83.7% vs 75.8%): more text gives the retriever and classifier more to be confident about, including on tickets a human should have taken."),
    row("Standard customers", "customer_tier", "standard",
        "Lowest resolution proxy of the three tiers (57.3% vs 64.0% for business) and 6.7 pp below business on route accuracy (p = 0.10, not significant). Largest group (253)."),
    row("Asia-Pacific region (lowest resolution)", "region", "asia_pacific",
        "Lowest resolution proxy of any region (50.4% vs 65.0% best), 7.7 pp lower route accuracy than Europe (p = 0.13, not significant) and a 23.5% false-auto rate. Retrieval quality is normal (90.8%), so this is routing, not retrieval: 46.2% of Asia-Pacific tickets carry an 'escalate' label against 31.8% in Europe, so more of them are tickets the system should not have answered. The 21 Asia-Pacific validation tickets are too few to confirm or contradict it."),
    row("Docs-comment channel (lowest resolution)", "channel", "docs_comment",
        "Lowest resolution proxy of any channel (50.0%) and 7.1 pp lower route accuracy than email (p = 0.19, not significant). Retrieval quality is the best of any channel (93.8%), so documentation-comment tickets are matched well but 47.4% of them carry an 'escalate' label (32-42% in other channels): the system finds an article for tickets a human was expected to take."),
])
fair_note = para_after(fair._tbl,
    "Method. evaluation/fairness_audit.py segments a finished run and reports, per segment: auto-reply rate; resolution rate (an offline proxy: "
    "the system auto-replied and the labelled route was auto_respond; it is not a measure of customer outcomes); false-auto rate; quality "
    "(retrieval hit@1 on tickets answerable from the documentation); and route accuracy with a 95% Wilson interval, with the gap to the best "
    "segment and a two-proportion z-test. The table above uses the 500 development tickets (leave-one-out run). The same audit on the 80 "
    "validation tickets is in evaluation/results/fairness_val.md, and all segments (tier, fluency, length, region, channel) are in fairness_dev.md. "
    "Findings. (1) No route-accuracy gap is statistically significant on 500 tickets, but the 95% intervals span roughly 10 to 20 pp, so the audit "
    "could only detect gaps of about 10 pp or more: 'not significant' is not the same as 'fair'. The largest directional gaps are enterprise "
    "(9.4 pp), Asia-Pacific (7.7 pp) and docs-comment (7.1 pp). (2) One confirmed retrieval-quality gap: short tickets. (3) The non-fluent "
    "retrieval gap the framework warns about is present in direction (5.6 pp) but not significant. (4) The PRD target of under 5 pp variation "
    "(NFR-06) is met for fluent vs non-fluent route accuracy (3.7 pp, in favour of non-fluent) but not met for tier (9.4 pp) or region (7.7 pp) as point estimates; "
    "the evidence is too thin to call either a breach or a pass. (5) Ticket content, not demographics, drives some of this: the labels were generated, "
    "so a real deployment needs live per-segment monitoring before claiming parity.",
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
    "The mechanism that enforces that is ...": "Routing in deterministic code on the predicted intent (src/route.py), not on a model's say-so, with outbound guardrails that block and escalate (src/guardrails.py), and a kill switch. Evidence: 0 safety violations out of 101 safety tickets (87 dev, 14 validation) and 0 PII findings in 580 tickets.",
    "The most likely way it could still cause harm is ...": "A well-written, grounded reply that is incomplete or wrong for the customer's actual situation, sent to a ticket that needed a human: 25-28% of auto-replies in the evaluation went to tickets labelled 'escalate', and about half the route and urgency labels cannot be predicted from the text. Also: a safety ticket misclassified as an ordinary one. Both measurements come from synthetic, templated data, so real performance is probably lower.",
    "We would not deploy this without first ...": "running it in draft mode on live tickets, where agents see and edit the suggested reply, for several weeks while measuring acceptance and real accuracy; completing the human second assessment of replies; load testing on production hardware; agreeing named owners and the admin token holders; rotating all keys; setting provider spend caps; and deciding, with the Head of Support, whether to restrict auto-reply to the intents with the strongest measured precision.",
}
for r in decl.rows[1:]:
    k = r.cells[0].text.strip()
    if k in dc:
        put(r.cells[1], dc[k])

doc.save(OUT)
print("saved", OUT)
