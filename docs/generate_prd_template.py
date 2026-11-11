"""
generate_prd_template.py — Regenerates Stage_2_PRD_v1.docx using the EXACT
structure from Stage_2_PRD_Template.docx (9 numbered sections, correct
column headers, pre-filled row labels, priority vocabulary Must/Should/Could/Will not).

Run:  venv/bin/python3 docs/generate_prd_template.py
"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__))


def set_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def add_para(doc, text, size=10, bold=False, italic=False, color=None, align=None, space_after=None):
    p = doc.add_paragraph()
    if align:
        p.alignment = align
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    return p


def heading(doc, text, level=1, color="1F3864"):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = RGBColor.from_string(color)
    return h


def callout(doc, text, bg="EBF3FB"):
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    cell = t.cell(0, 0)
    set_bg(cell, bg)
    p = cell.paragraphs[0]
    run = p.add_run(text)
    run.font.size = Pt(10)
    run.font.italic = True
    doc.add_paragraph()


def make_table(doc, headers, rows, col_widths=None, hdr_bg="2E4057"):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    # header
    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        set_bg(cell, hdr_bg)
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.font.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    # data
    for ri, row in enumerate(rows):
        bg = "F7F9FC" if ri % 2 == 0 else "FFFFFF"
        for ci, val in enumerate(row):
            cell = t.rows[ri + 1].cells[ci]
            set_bg(cell, bg)
            p = cell.paragraphs[0]
            run = p.add_run(str(val))
            run.font.size = Pt(9)
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in t.rows:
                row.cells[i].width = Inches(w)
    doc.add_paragraph()
    return t


def add_footer(doc, text):
    for section in doc.sections:
        footer = section.footer
        p = footer.paragraphs[0]
        p.text = ""
        run = p.add_run(text)
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)


def build_prd():
    doc = Document()
    s = doc.sections[0]
    s.top_margin = Cm(2)
    s.bottom_margin = Cm(2)
    s.left_margin = Cm(2.5)
    s.right_margin = Cm(2.5)

    # ── TITLE BLOCK ──────────────────────────────────────────────────────
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("FORWARD DEPLOYED AI ENGINEERING")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.add_run("Capstone Project").font.size = Pt(12)

    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p3.add_run("Stage Two: Requirements").font.size = Pt(12)

    p4 = doc.add_paragraph()
    p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r4 = p4.add_run("The product requirements document you write from your findings")
    r4.font.size = Pt(10)
    r4.font.italic = True

    add_para(doc,
        "Everything here must trace back to your discovery workbook. "
        "A requirement that cannot be traced is a preference, and preferences do not belong in a PRD.",
        size=10, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, color="666666")

    doc.add_paragraph()

    # ── CALLOUT 1 ────────────────────────────────────────────────────────
    callout(doc, "WEEK ONE  ·  DAYS FOUR AND FIVE", bg="D6E4F0")

    # ── INTRO ────────────────────────────────────────────────────────────
    heading(doc, "What this document is and why it matters", level=2)
    add_para(doc,
        "A product requirements document states what is being built, for whom, and how "
        "anyone will know when it is finished. It is not a design document and it is not a "
        "plan. It should be specific enough that two different engineers reading it would "
        "build broadly the same thing, and general enough that it does not dictate how they "
        "do it.", size=10)
    add_para(doc,
        "You will write version one at the end of week one and you will revise it during week "
        "two. That revision is compulsory. Write this version with the expectation that parts "
        "of it will turn out to be wrong, and record your assumptions clearly so that you can "
        "tell which ones failed when they do.", size=10)
    add_para(doc,
        "Figure 1. The requirements document is expected to change once building starts.",
        size=9, italic=True, color="999999")

    doc.add_page_break()

    # ════════════════════════════════════════════════════════════════════
    # SECTION 1: Document control
    # ════════════════════════════════════════════════════════════════════
    heading(doc, "1   Document control", level=2)
    make_table(doc,
        ["Field", "Value"],
        [
            ["Version", "1.0"],
            ["Written by", "Nishchay Gupta"],
            ["Date", "9 November 2026"],
            ["Status", "Draft for review"],
            ["Approved by", "(pending — revision after Week 2 Day 5 gate run)"],
        ],
        col_widths=[1.5, 6.6])

    # ════════════════════════════════════════════════════════════════════
    # SECTION 2: The problem in one paragraph
    # ════════════════════════════════════════════════════════════════════
    heading(doc, "2   The problem in one paragraph", level=2)
    add_para(doc,
        "Copy across the paragraph you wrote at the end of your discovery workbook. "
        "If you find yourself wanting to improve it as you copy, go back and improve it "
        "in the workbook first, so that the two do not drift apart.",
        size=10, italic=True)

    t = doc.add_table(rows=3, cols=1)
    t.style = "Table Grid"
    # row 0: label
    cell = t.rows[0].cells[0]
    set_bg(cell, "2E4057")
    p = cell.paragraphs[0]
    r = p.add_run("Problem statement")
    r.font.bold = True
    r.font.size = Pt(9)
    r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    # row 1: the paragraph
    cell1 = t.rows[1].cells[0]
    set_bg(cell1, "F0F9F4")
    p1 = cell1.paragraphs[0]
    r1 = p1.add_run(
        "CloudServe's support system treats every ticket as an isolated, memoryless event — "
        "discarding the resolution knowledge generated by every previous customer who had the "
        "same problem, and making each agent reconstruct from scratch an answer that was solved "
        "correctly yesterday. 500+ tickets per week, each one a data point thrown away at close. "
        "71% of them already have answers in existing documentation — yet the same problem reaches "
        "the queue again tomorrow. Every unnecessary escalation costs 4× a resolved ticket and "
        "arrives at tier-2 without the context that would have let them act in minutes. The correct "
        "solution does not exist yet: a system that turns each resolved ticket into a signal that "
        "makes every future ticket cheaper to resolve, gives every new customer the accumulated "
        "intelligence of everyone who came before them, and compresses a 12-hour problem into a "
        "2-minute one — without inventing new answers, only delivering the ones that already exist, "
        "grounded, cited, and verifiable."
    )
    r1.font.size = Pt(10)
    # row 2: blank continuation
    doc.add_paragraph()

    # ════════════════════════════════════════════════════════════════════
    # SECTION 3: Who this is for
    # ════════════════════════════════════════════════════════════════════
    heading(doc, "3   Who this is for", level=2)
    add_para(doc,
        "Describe each group of users separately. A requirement that serves everybody "
        "usually serves nobody particularly well.",
        size=10, italic=True)

    make_table(doc,
        ["User group", "What they need from this system", "What they currently do instead", "How you will know it worked for them"],
        [
            ["Customers raising tickets",
             "Fast, accurate, honest answers — especially for high-urgency issues. If automated, the answer must cite its source and state its uncertainty. (Ravi: 'If it says here is what I think, here is the page it came from — that is useful.')",
             "Wait 8–12 hours for a human response. Find the answer themselves in documentation ~50% of the time. 21.6% come back with a repeat contact because first response was insufficient.",
             "First response time <2 hrs for auto-responded tickets. Repeat contact rate falls from 22% to ≤10%. Customer reports the answer was correct and they could verify the source."],
            ["Tier one support agents",
             "A grounded draft answer + the relevant documentation page attached, so they can review and personalise rather than writing from scratch. NOT auto-send without their review. (Sofia: 'That would save me half of every ticket.')",
             "Skip KB search (keyword search fails on vocabulary mismatch) and use personal snippet files. Spend 2–15 min per ticket finding an answer they already know. 70% of tickets are repeats.",
             "Average handle time per ticket drops by ≥50% on answerable categories. Agents report they trust the drafts and use them. Agent attrition stabilises."],
            ["Tier two and specialist agents",
             "Escalations that arrive with context: 2-sentence summary + relevant docs + what tier-1 was uncertain about. Not a raw forwarded ticket. (Daniel: 'If an escalation arrived with context I would be twice as fast.')",
             "Spend first 15–30 min of every escalation re-reading the full thread and re-asking questions already asked. ~50% of what reaches tier-2 was resolvable at tier-1 (confidence gap, not knowledge gap).",
             "Time-to-resolution on escalated tickets drops by ≥50%. Daniel confirms escalation context is sufficient to act immediately. Escalation rate falls from 56% to ≤30%."],
            ["The head of support",
             "FCR rising to ≥60%, response time <2 hrs, and an explainable audit trail for every automated decision — autumn compliance review requires it. (Marcus: 'I need to be able to say why it did what it did.')",
             "Reports red numbers for 2 consecutive quarters. Cannot explain decisions to compliance reviewers. Has no breakdown of tickets by category. Prior attempts (hiring, canned responses) failed within a month.",
             "FCR ≥60%. Every automated decision has a logged, human-readable reason. Compliance review passes. Marcus reports a declining response-time trajectory to the executive team."],
            ["The technical writer",
             "Know which KB article each answer came from, so she can distinguish article errors from system errors and update the right thing. (Ines: 'I would want to know which article an answer came from.')",
             "Does not know whether the team uses her 29 articles or reconstructs from memory. Has asked twice for agents' private snippet files to be consolidated — they contain stale answers.",
             "Ines reports: 'DOC-DEPLOY-001 was cited 47 times this week, 3 incorrect — article needs updating.' Citation log enables her to audit KB quality systematically."],
        ],
        col_widths=[1.3, 2.5, 2.2, 2.1])

    doc.add_page_break()

    # ════════════════════════════════════════════════════════════════════
    # SECTION 4: Functional requirements
    # ════════════════════════════════════════════════════════════════════
    heading(doc, "4   Functional requirements", level=2)
    add_para(doc,
        "Each requirement gets an identifier, a statement, a priority and a link back to the "
        "discovery evidence that produced it. The identifiers matter because your specifications, "
        "your prompts and your test cases will all refer to them.",
        size=10, italic=True)
    add_para(doc,
        "Use the priority scale consistently. Must means the system is not acceptable without it. "
        "Should means it is expected but could be deferred with a stated consequence. Could means "
        "it would add value if time allows. Will not means it has been considered and deliberately "
        "excluded, and recording those is as useful as recording the rest.",
        size=10, italic=True)

    make_table(doc,
        ["ID", "Requirement", "Priority", "Discovery evidence", "Acceptance criteria"],
        [
            ["FR-01",
             "The system shall accept tickets from all four channels: email, live chat, API documentation comments, and community forum, and normalise them into a single internal representation.",
             "Must",
             "Section 2, Table 2-A: email 42.4%, chat 31.0%, docs_comment 15.6%, forum 11.0%. docs_comment channel underappreciated by all stakeholders.",
             "All four channel types present in the evaluation set are processed without error. Normalised ticket contains: ticket_id, channel, subject, body, received_at, customer_id, customer_tier, customer_region, language_fluency."],
            ["FR-02",
             "The system shall classify every ticket with one of 22 intent classes and assign urgency (high/medium/low).",
             "Must",
             "Section 4, Table 4-A: FCR is the primary metric. Data: 22 intent classes, 29.2% high-urgency. Marcus/Sofia both describe needing to know ticket type before acting.",
             "Classification precision ≥85% per class on validation set (confusion matrix provided). Urgency assigned and logged for 100% of processed tickets."],
            ["FR-03",
             "The system shall produce a calibrated confidence score 0.0–1.0 for each classification. Confidence bands must be accurate within 5 percentage points of observed accuracy.",
             "Must",
             "Marcus: 'I would rather it said nothing than said something wrong.' The routing threshold is only meaningful if confidence reflects actual probability of being correct.",
             "Calibration check: stated confidence within 5pp of measured accuracy per band (0.5–0.6, 0.6–0.7, 0.7–0.8, 0.8–0.9, 0.9–1.0). Run as part of Week 2 Day 5 evaluation."],
            ["FR-04",
             "The system shall perform semantic search over the 29 knowledge base articles using embedding-based retrieval (all-MiniLM-L6-v2), returning passages with doc_id, title, and score.",
             "Must",
             "Section 1, Table 1-B Row 1: 71.4% answerable from docs. Ines: keyword search fails on vocabulary mismatch ('my deployment keeps dying' vs 'resolving container health check failures'). Section 3, Table 3-B Step 3: this is where most agent time is wasted.",
             "Query using customer vocabulary returns the correct KB article. Each returned passage resolves to a real document ID in documentation.json. Recall ≥90% on 20 known-question/known-article pairs."],
            ["FR-05",
             "The system shall return an empty list when no article is sufficiently relevant. Returning irrelevant passages is worse than returning nothing.",
             "Must",
             "Ines: 'Feature requests — obviously, since there is no answer to retrieve.' System must recognise absence of content, not manufacture an answer.",
             "Feature-request query returns empty list. System escalates. Zero irrelevant retrievals in sampled evaluation."],
            ["FR-06",
             "The system shall check the must_not_auto_respond flag before any routing decision. Any ticket with this flag set to True shall be escalated regardless of confidence.",
             "Must",
             "Data: 17.4% (87/500) safety-flagged. Daniel: security incidents, billing disputes, data residency must always escalate.",
             "100% of must_not_auto_respond=True tickets in evaluation set routed to escalate. Zero violations."],
            ["FR-07",
             "The system shall route tickets using a confidence threshold (default 0.80, justified with evaluation data). The same input shall always produce the same routing decision (deterministic).",
             "Must",
             "Marcus: 'I would rather it said nothing.' Threshold justified by calibration data, not assumption. Threshold value logged with every decision.",
             "Same ticket always produces same routing decision. Threshold value logged in every decision record. Threshold value justified by calibration check in evaluation report."],
            ["FR-08",
             "Escalated tickets shall carry a context packet containing: (a) 2-sentence summary, (b) retrieved documentation passages with doc_ids, (c) human-readable reason why the system was not confident.",
             "Must",
             "Daniel: 'If an escalation arrived with context I would be twice as fast.' Currently escalations arrive as raw ticket forwards — 15–30 min lost reconstructing context.",
             "100% of escalated tickets in evaluation set have context packet with all three components populated."],
            ["FR-09",
             "Generated responses shall cite the specific KB article(s) used (doc_id inline). Citations must resolve to actually-retrieved passages — never hallucinated references.",
             "Must",
             "Ines: 'I would want to know which article an answer came from — so I can tell whether the article is wrong or the system misread it.' Ravi: 'Here is the page it came from.'",
             "Citation accuracy ≥95%: each citation checked against the passage it supports. Hallucination rate ≤5% on 50+ sampled responses (2 independent assessors, report agreement rate)."],
            ["FR-10",
             "The system shall not generate a response when no relevant passages were retrieved. If passages are empty, the ticket shall be routed to escalate before generation is called.",
             "Must",
             "Ines: topics with no article must not be manufactured. Ground truth only comes from verified KB content.",
             "ValueError raised if generate_response() called with empty passages. Zero manufactured answers on no-KB-match tickets."],
            ["FR-11",
             "The system shall run five guardrails on every outbound response. Each guardrail must be able to block the response and escalate: (1) PII detection, (2) Grounding check, (3) Prompt injection detection, (4) Tone/scope — no refund or timeline commitments, (5) Confidence floor — verify threshold was applied.",
             "Must",
             "Marcus: primary fear is confidently wrong answer. GDPR: customer PII in ticket data. Daniel: billing becomes contractual. Security: ticket body is untrusted input.",
             "All 5 guardrails run on every response during evaluation run. Engineered trigger tickets confirm each guardrail blocks when triggered. Zero PII violations. Zero commitment violations."],
            ["FR-12",
             "Every automated decision shall be written to a persistent SQLite log with the full schema: decision_id, timestamp, ticket_id, stage, model, prediction + confidence, sources_used, threshold_applied, action_taken, reason, guardrail_results, prompt_version, requirement_ids.",
             "Must",
             "Marcus: compliance review in autumn. Every automated decision must have a logged, human-readable reason. Governance requirement.",
             "count_decisions() == total tickets processed in every evaluation run. Logged decisions match processed tickets exactly — including failures and escalations."],
            ["FR-13",
             "For tickets with first_contact_resolution=True, the system shall log the resolution path (intent, doc_ids used, confidence, customer_tier, language_fluency) as a reusable resolution record. This is the input to future retrieval improvement and the compounding mechanism of the system.",
             "Should",
             "Section 6, Table 6-A Steps 2–4: extraordinary problem. Economic equation: Prevention = (Ticket history × Resolution patterns) ^ Cross-customer learning. This is the exponent — without it the system is a SaaS feature, not an AI-native product.",
             "Resolution records written for 100% of FCR=True tickets. Each record contains: intent, doc_ids_used, confidence, customer_tier (anonymised), language_fluency. Resolution graph grows over time (count checked per evaluation run)."],
            ["FR-14",
             "The system shall handle failure gracefully: no retrieval hit, model provider timeout, rate limiting, or malformed input shall crash the pipeline. The system shall degrade and continue processing rather than stopping.",
             "Must",
             "A11 acceptance criterion. A9 requires full evaluation set processed unattended — individual ticket failures must not crash the harness.",
             "No unhandled exceptions in full evaluation run. Failed tickets logged with status='error' and processing continues. Exit code 0 from harness when all tickets processed (even if some errored)."],
            ["FR-15",
             "The system shall provide a FastAPI HTTP interface with a /health endpoint and a POST /process endpoint that runs the full pipeline: ingest → classify → retrieve → route → generate → validate.",
             "Should",
             "A1 acceptance criterion: system runs from clean checkout following README.",
             "GET /health returns 200. POST /process returns routing decision with either a drafted response or escalation context. Every call writes to the decision log."],
            ["FR-16",
             "The evaluation harness shall accept --input and --output path arguments and process the full ticket set in a single unattended run, producing a metrics report automatically.",
             "Must",
             "A9 + A10 acceptance criteria. Harness will be pointed at a hidden 120-ticket evaluation set during grading. Hardcoded paths = A9 failure.",
             "python evaluation/harness.py --input <path> --output <path> processes all tickets without intervention. Output JSON contains 'metrics' and 'results' keys. Exit code 0 on success."],
            ["FR-17",
             "Tests shall run with a single documented command (pytest tests/ -v) and pass.",
             "Must",
             "A12 acceptance criterion.",
             "pytest tests/ -v exits 0. All non-xfail tests pass."],
            ["FR-18",
             "The system shall support monitoring via Prometheus metrics: tickets processed per hour by channel and outcome, auto-answer vs escalate rate, latency P50/P95, guardrail activations, confidence score distribution.",
             "Could",
             "Section 4, Table 4-A: explainability. Governance requirement for operational visibility.",
             "Prometheus endpoint /metrics exposes all listed counters and histograms. Grafana dashboard renders them. (Implementation in Week 3 if time allows.)"],
        ],
        col_widths=[0.5, 2.8, 0.5, 2.2, 2.1])

    doc.add_page_break()

    # ════════════════════════════════════════════════════════════════════
    # SECTION 5: Non-functional requirements
    # ════════════════════════════════════════════════════════════════════
    heading(doc, "5   Non-functional requirements", level=2)
    add_para(doc,
        "These describe how well the system must do the things it does. They are frequently "
        "what distinguishes a demonstration from something that could actually be deployed.",
        size=10, italic=True)

    make_table(doc,
        ["ID", "Category", "Requirement", "How it will be verified"],
        [
            ["NFR-01", "Latency",
             "95th-percentile end-to-end response latency for auto-responded tickets shall be under 3 seconds.",
             "Measured in evaluation harness: processing_time_ms field per ticket. P95 calculated across all auto-responded results."],
            ["NFR-02", "Availability",
             "System availability during operating hours shall be ≥99.5%. If model provider is unavailable, system shall degrade gracefully (route all to escalate) rather than fail.",
             "Provider outage test: disconnect API, run harness, verify all tickets escalate with status='degraded'. No unhandled exceptions."],
            ["NFR-03", "Accuracy",
             "Intent classification precision shall be ≥85% per class on the validation set. Hallucination rate shall be ≤5% on 50+ sampled auto-responses (two independent assessors, report inter-assessor agreement).",
             "Confusion matrix from evaluation harness. Hallucination assessment: two reviewers score 50+ responses independently, report agreement rate (Cohen's kappa)."],
            ["NFR-04", "Privacy",
             "Zero occurrences of PII (names, addresses, account numbers, API keys, email addresses) in any outbound response.",
             "PII guardrail log: count of blocked responses. Manual spot-check of 20 random auto-responses for PII presence."],
            ["NFR-05", "Auditability",
             "Every automated decision shall have a logged, human-readable reason. Decision log coverage shall be 100% (count_decisions() == tickets_processed). Confidence calibration shall be within 5pp per band.",
             "Reconciliation: run count_decisions() after each evaluation run, compare to total tickets. Calibration check: group predictions by confidence band, compare stated confidence to observed accuracy."],
            ["NFR-06", "Fairness",
             "Variation in FCR across customer tiers (enterprise vs business vs standard) shall not increase by more than 5 percentage points vs baseline. Variation in auto-respond accuracy between fluent and non-fluent English tickets shall be under 5 percentage points.",
             "Per-segment evaluation: run metrics separately for each tier and each fluency group. Compare to baseline (Enterprise FCR 37.3%, Business 48.2%, Standard 43.1%; Non-fluent CSAT 3.04, Fluent 2.95)."],
            ["NFR-07", "Cost",
             "Token usage shall be logged per decision for cost monitoring. The 1,000th ticket shall cost approximately the same as the 1st (zero marginal cost on retrieval; LLM cost only on generation).",
             "token_count field in decision log. Sum token usage across evaluation run. Report cost per ticket."],
            ["NFR-08", "Citation accuracy",
             "Proportion of citations that resolve to the actual retrieved passage supporting the claim shall be ≥95%.",
             "Each citation in sampled responses checked against the passage it supports in the retrieved context. Report: correct citations / total citations."],
            ["NFR-09", "Resolution graph growth",
             "Resolution records (FR-13) shall be written for 100% of FCR=True tickets. The resolution graph shall grow over time — if it is not growing, the system is not compounding.",
             "Count resolution records per evaluation run. Verify count ≥ (FCR rate × tickets processed). Plot growth over multiple runs."],
            ["NFR-10", "Graceful degradation",
             "The system shall handle no retrieval hit, provider timeout, rate limiting, and malformed input without crashing. Failed tickets shall be logged and processing shall continue.",
             "Engineered failure tests: submit ticket with no KB match, simulate provider timeout, submit malformed JSON. Verify harness continues and logs error."],
        ],
        col_widths=[0.7, 1.3, 3.5, 2.6])

    doc.add_page_break()

    # ════════════════════════════════════════════════════════════════════
    # SECTION 6: What is deliberately out of scope
    # ════════════════════════════════════════════════════════════════════
    heading(doc, "6   What is deliberately out of scope", level=2)
    add_para(doc,
        "Recording what you are not building is one of the most valuable things a requirements "
        "document does, because it is the section that prevents an argument in week three.",
        size=10, italic=True)

    make_table(doc,
        ["Not building", "Why not", "What would have to change for this to be reconsidered"],
        [
            ["Answering feature requests, roadmap questions, or novel incidents",
             "No KB article exists to retrieve from. System must escalate, not manufacture. Ines: 'Feature requests — obviously, since there is no answer to retrieve.' Data: feature_request 0% answerable.",
             "If CloudServe builds a product feedback pipeline separate from support — these tickets should route there, not be answered."],
            ["Auto-responding to security incidents, billing disputes, or compliance requests",
             "17.4% of tickets are safety-flagged (must_not_auto_respond=True). Contractual, legal, and security implications. Daniel: 'Billing becomes contractual quickly; security must always escalate.'",
             "If a legal review process is established that can pre-approve specific response templates for these categories — but this is a policy change, not a technical one."],
            ["Training on or retrieving from agents' personal snippet files",
             "Snippet files are unreviewed and contain known-stale answers. Daniel: 'Some answers were correct two years ago and have not been right since. If you learn from those you will scale up a mistake.'",
             "If snippet files are consolidated, reviewed by Ines, and merged into the official KB — at which point they become KB articles and are in scope."],
            ["Replacing human agents",
             "The system is agent-assist: draft + review. Sofia specifically described wanting draft + page, not auto-send. Marcus: primary fear is wrong answer reaching customer without review.",
             "If evaluation demonstrates ≥99% citation accuracy and ≤1% hallucination rate over 500+ tickets — at which point direct customer-facing response becomes a v2 discussion."],
            ["Customer-facing direct response (v1)",
             "Primary interface is agent-assist. Customer-facing direct response requires a higher confidence bar and is a future phase. Marcus: 'I would rather it said nothing than said something wrong.'",
             "After v1 demonstrates stable FCR ≥60% and hallucination ≤5% over a sustained period (30+ days of production data)."],
            ["Multi-language response generation",
             "Retrieval from English KB, draft in English. Translation pipeline adds complexity outside v1 scope. Non-fluent CSAT data inconclusive (Section 1, Table 1-B).",
             "If non-fluent ticket volume grows significantly or a translation API with sufficient quality becomes available at acceptable cost."],
        ],
        col_widths=[2.0, 3.3, 2.8])

    doc.add_page_break()

    # ════════════════════════════════════════════════════════════════════
    # SECTION 7: Assumptions and their consequences
    # ════════════════════════════════════════════════════════════════════
    heading(doc, "7   Assumptions and their consequences", level=2)
    add_para(doc,
        "Every assumption you are making is a place where this document could turn out to be "
        "wrong. Listing them now is what makes the revision in stage five a considered update "
        "rather than a scramble.",
        size=10, italic=True)

    make_table(doc,
        ["Assumption", "Why you believe it", "What happens if it is false", "How you will find out"],
        [
            ["The 29 KB articles remain current and reviewed by Ines throughout the project.",
             "Ines reviews on a rotation and has done so for 2 years.",
             "System retrieves stale content. Answer quality degrades silently — hard to detect.",
             "Log doc_id + last_reviewed date per decision. Alert if article >90 days since review."],
            ["Confidence threshold of 0.80 produces acceptable routing decisions.",
             "Starting point from spec .env.example. To be justified with calibration data.",
             "Too high: over-escalates (less value). Too low: auto-responds on uncertain cases (more wrong answers).",
             "Calibration check on validation set in Week 2 Day 5. Adjust threshold based on data."],
            ["OpenRouter free tier provides sufficient capacity for this workload.",
             "OpenRouter advertises free tier access to Llama 3.1 8B.",
             "Rate limiting causes timeouts. Harness fails to process all tickets unattended (A9 failure).",
             "Test harness against full 80-ticket validation set. Rate limit errors appear in logs."],
            ["all-MiniLM-L6-v2 captures sufficient semantic similarity for retrieval.",
             "Spec requirement. Runs locally, widely used for semantic search.",
             "Vocabulary mismatch problem persists despite semantic search. Retrieval quality is poor.",
             "Test with 20 known-question/known-article pairs. Recall should be ≥90%."],
            ["Resolution records from FCR=True tickets are reliable enough to feed back as a training signal (FR-13).",
             "FCR=True means the answer was confirmed correct on first contact.",
             "System reinforces incorrect resolutions if FCR=True is inaccurate or the customer accepted a wrong answer.",
             "Cross-check: resolutions that generated a subsequent repeat contact should be excluded from the reinforcement signal."],
            ["Enterprise tickets are more complex by nature, explaining their worse FCR.",
             "Enterprise has premium agreements but FCR 37.3% — worse than standard. Most likely because their tickets are harder.",
             "If enterprise FCR is driven by service failure (not complexity), the current design will not help enterprise customers.",
             "Compare FCR for enterprise tickets that ARE answerable from docs vs those that are not. If doc-answerable enterprise tickets still have poor FCR, the problem is not complexity."],
        ],
        col_widths=[2.2, 1.8, 2.0, 2.1])

    doc.add_page_break()

    # ════════════════════════════════════════════════════════════════════
    # SECTION 8: Success measures
    # ════════════════════════════════════════════════════════════════════
    heading(doc, "8   Success measures", level=2)
    add_para(doc,
        "State the measures this system will be judged on, with the baseline and the target for "
        "each, and say who is accountable for reporting them.",
        size=10, italic=True)

    make_table(doc,
        ["Measure", "Baseline", "Target", "Measured how", "Reported by"],
        [
            ["First contact resolution", "42%", "≥60%",
             "history.first_contact_resolution in evaluation set; business outcome reported in evaluation harness",
             "Marcus (Head of Support)"],
            ["Time to first reply", "8 to 12 hours", "<2 hours (auto-responded); <5 min for auto-responded",
             "history.resolution_time_minutes for auto-responded subset; P95 latency in harness",
             "Marcus (SLA obligation)"],
            ["Customer satisfaction", "3.2 / 5 (Marcus); 2.97 / 5 (data)", "≥4.0 / 5.0",
             "history.csat_rating in evaluation set (proxy measure — state sample size and method)",
             "Marcus (exec report)"],
            ["Escalation rate", "56.2%", "≤30%",
             "history.escalated in evaluation set; count of auto_respond vs escalate decisions",
             "Marcus (cost)"],
            ["Repeat contact rate", "21.6%", "≤10%",
             "history.repeat_contact in evaluation set",
             "Nishchay (new metric — introduce)"],
            ["Hallucination rate", "Not measured", "≤5%",
             "Two independent assessors on ≥50 sampled auto-responses; report inter-assessor agreement (Cohen's kappa)",
             "Nishchay (evaluation)"],
            ["Citation accuracy", "Not measured", "≥95%",
             "Each citation checked against the passage it supports in retrieved context",
             "Nishchay (evaluation)"],
            ["Resolution graph growth", "0 records", "≥FCR rate × tickets processed per run",
             "Count resolution records (FR-13) in decision log per evaluation run. Plot growth over time.",
             "Nishchay (extraordinary metric)"],
        ],
        col_widths=[1.8, 1.5, 1.5, 2.5, 1.5])

    doc.add_page_break()

    # ════════════════════════════════════════════════════════════════════
    # SECTION 9: Open questions
    # ════════════════════════════════════════════════════════════════════
    heading(doc, "9   Open questions", level=2)
    add_para(doc,
        "The things you do not yet know. Each one needs an owner and a date by which it will "
        "be resolved, otherwise it will still be open in week three.",
        size=10, italic=True)

    make_table(doc,
        ["Question", "Why it matters", "Owner", "Resolve by"],
        [
            ["What is the final confidence threshold value?",
             "0.80 is a starting point. Too high = over-escalation; too low = wrong auto-responses. Must be justified by calibration data.",
             "Nishchay", "Week 2 Day 5 (gate run)"],
            ["Is the OpenRouter free tier sufficient for 80+ sequential API calls without rate limiting?",
             "If rate-limited, harness fails A9 (unattended run). May need to add retry/backoff logic or switch provider.",
             "Nishchay", "Week 2 Day 3"],
            ["Should FR-13 (resolution graph) be implemented as a separate SQLite table or as additional fields in the decisions table?",
             "Affects logging_store.py implementation. Separate table is cleaner but adds query complexity.",
             "Nishchay", "Week 2 Day 3"],
            ["Does the non-fluent vocabulary mismatch actually produce worse retrieval results in practice?",
             "Data showed non-fluent outcomes are marginally better, but vocabulary mismatch may still affect semantic search quality. If it does, may need tiered embeddings.",
             "Nishchay", "Week 2 Day 5 (fairness audit)"],
            ["Can Ines's KB articles be updated mid-project if retrieval quality is poor on specific categories?",
             "If retrieval fails on deployment_failure tickets because the article is written differently from how customers phrase it, we may need to rephrase article titles or add synonyms.",
             "Nishchay / Ines", "Week 2 Day 2 (after retrieval testing)"],
        ],
        col_widths=[2.5, 3.0, 1.0, 1.6])

    doc.add_page_break()

    # ── CALLOUT 2 (end of document) ──────────────────────────────────────
    callout(doc,
        "The review before you move on / Read your finished PRD and ask, for each requirement "
        "in turn, whether an engineer who had not attended any of your interviews could build "
        "it from what is written. Where the answer is no, the requirement is not finished. "
        "This check takes twenty minutes and it is the single highest-value thing you can do "
        "at the end of week one.",
        bg="FEF9E7")

    # ── FOOTER ───────────────────────────────────────────────────────────
    add_footer(doc, "Forward Deployed AI Engineering  ·  Stage Two  ·  Product Requirements Document")

    path = os.path.join(OUTPUT_DIR, "Stage_2_PRD_v1.docx")
    doc.save(path)
    print(f"✅  Saved: {path}")
    return path


if __name__ == "__main__":
    print("Generating Stage 2 PRD v1 in template format...")
    build_prd()
    print("Done.")
