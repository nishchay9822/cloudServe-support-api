"""
generate_docs_v2.py — Regenerates Stage 1 Discovery Workbook and Stage 2 PRD
with the EXTRAORDINARY PROBLEM framework applied throughout.

Framework source: extraordinaryproblem.pdf (IIT Roorkee, FDE, Module 1 Session 2)
6-Step Journey: Original → Levers → Rewrite → Equation → FP×JTBD → Extraordinary Problem
5 Tests: Challenges assumption | Reactive→Predictive | Non-obvious | Data advantage | New category
Economic Equation: (Data × Algorithms) ^ Network Effects

Run:  venv/bin/python3 docs/generate_docs_v2.py
"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__))

# ── helpers ─────────────────────────────────────────────────────────────────

def set_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)

def banner(doc, section_num, title, subtitle="", dark="1F3864"):
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    cell = t.cell(0, 0)
    set_bg(cell, dark)
    p = cell.paragraphs[0]
    run = p.add_run(f"  {section_num}  ·  {title.upper()}")
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    run.font.bold = True
    run.font.size = Pt(12)
    if subtitle:
        p2 = cell.add_paragraph()
        r2 = p2.add_run(f"  {subtitle}")
        r2.font.color.rgb = RGBColor(0xBF, 0xD7, 0xED)
        r2.font.size = Pt(9)
    doc.add_paragraph()

def callout(doc, text, bg="EBF3FB", italic=True):
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    cell = t.cell(0, 0)
    set_bg(cell, bg)
    p = cell.paragraphs[0]
    run = p.add_run(text)
    run.font.size = Pt(10)
    run.font.italic = italic
    doc.add_paragraph()

def heading(doc, text, level=2, color="1F3864"):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = RGBColor.from_string(color)

def table(doc, headers, rows, col_widths=None, hdr_bg="2E4057"):
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

def cover(doc, title, subtitle, badge):
    doc.add_paragraph()
    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p1.add_run("FORWARD DEPLOYED AI ENGINEERING")
    r.font.size = Pt(14); r.font.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.add_run(title).font.size = Pt(12)
    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    b = p3.add_run(badge)
    b.font.size = Pt(10)
    b.font.color.rgb = RGBColor(0x2E, 0x86, 0xAB)
    doc.add_paragraph()
    callout(doc, subtitle, bg="EBF3FB")
    doc.add_page_break()


# ═══════════════════════════════════════════════════════════════════════════
# DOCUMENT 1: Stage 1 Discovery Workbook — Extraordinary Problem Edition
# ═══════════════════════════════════════════════════════════════════════════

def build_discovery_v2():
    doc = Document()
    s = doc.sections[0]
    s.top_margin = Cm(2); s.bottom_margin = Cm(2)
    s.left_margin = Cm(2.5); s.right_margin = Cm(2.5)

    cover(doc,
        "Capstone Project  ·  Stage One: Discovery Workbook  ·  FILLED",
        "Evidence: 5 stakeholder interviews + data/development_tickets.json (500 tickets)\n"
        "Framework: Extraordinary Problem (IIT Roorkee, Module 1, Session 2)\n"
        "Every claim in Section 6 is traceable to a row in Sections 1–5. "
        "Problem statement reframed through the 6-Step Extraordinary Problem Journey.",
        "WEEK 1 · DAYS 2–3  |  CloudServe Solutions")

    # ── SECTION 1 ─────────────────────────────────────────────────────────
    banner(doc, 1, "What the Interviews Tell You")

    heading(doc, "Table 1-A: Interview Summary")
    table(doc,
        ["Stakeholder", "What they told you", "What they appear not to know", "What to verify in data"],
        [
            ["Marcus Adeyemi\nHead of Support",
             "500+ tickets/week, 6 agents. Avg first response 8–12 hrs vs 2-hr SLA. FCR 42% vs 65% industry benchmark. Escalation costs ~4× a resolved ticket. Prior attempts (hiring, canned responses) failed short-term. Primary fear: confidently wrong automated answers. Needs explainability for autumn compliance review. Enterprise customers on different SLA will notice degraded service immediately.",
             "Does not know ticket breakdown by category — admits he would be 'guessing'. Does not know what proportion of escalations are tier-2-resolvable vs genuinely complex. Does not know the non-fluent English volume issue. Has never asked: what if prevention was cheaper than resolution?",
             "Actual intent breakdown. What % of escalations are tier-1-resolvable. Do non-fluent tickets have worse outcomes. How much resolution knowledge is discarded after each closed ticket."],
            ["Sofia Restrepo\nTier One Agent",
             "~70% of tickets are repeats she could answer without looking anything up. Bottleneck is FINDING and rewriting the answer, not knowing it. KB is good but keyword search fails — every agent has private snippet files. Non-fluent tickets take longer; she believes those have worst CSAT. Wants draft + relevant doc, NOT auto-send without review.",
             "Whether non-fluent tickets statistically have worse outcomes. How often her escalations could have been resolved by her. That Daniel's tier-2 pipeline is 50% tier-1-resolvable. That her snippet file answers are already stale and are being passed forward incorrectly.",
             "Do non-fluent tickets have materially worse FCR/CSAT? Does data confirm her 70% estimate? Which intents are highest repeat volume?"],
            ["Daniel Okonkwo\nTier Two Engineer",
             "~50% of escalations are tier-1-resolvable — a confidence/findability gap, not a knowledge gap. Escalations arrive with no context: just the raw original ticket forwarded. First thing: re-read full thread, often re-ask questions already asked. Would be 'twice as fast' with context: summary + relevant docs + what tier-1 was uncertain about. Risk: snippet files contain stale answers that would scale mistakes.",
             "The overall FCR number. Whether non-fluent issue Sofia describes is measurable. How much of his time goes to context-reconstruction vs actual problem-solving. That the pattern of issues he sees IS data that could prevent tomorrow's issues.",
             "What escalation rate does data show? Which intents have highest escalation rates? Are there intents where escalation is high despite docs availability?"],
            ["Ines Varga\nTechnical Writer",
             "29 KB articles covering: auth, deployment, API, billing, data, security, account management. Internal team does not use them — agents reconstruct from memory. Root cause: keyword search fails on vocabulary mismatch. Wants citation of which article a system used. Feature requests/roadmap/novel incidents have NO article — system must recognise absence.",
             "That agents don't use docs because search is broken (she thought Sofia meant doc quality). The quantified gap. The escalation-without-context problem. That every closed ticket is resolution knowledge that could improve her docs — currently nobody feeds that back.",
             "What % of tickets are answerable from docs? For high doc-answerability intents, is escalation rate also high — meaning docs exist but aren't being reached?"],
            ["Ravi Menon\nCustomer (Business tier)",
             "Waits 8+ hrs; finds answers himself in docs ~50% of the time. Accepts automation IF honest: cites source, states uncertainty, identifies as automated. Urgency is asymmetric — doc question can wait; failing deployment at 9am cannot. Business customers will notice if enterprise–business gap widens.",
             "Internal mechanics of the delay. Non-fluent language problem. The escalation-without-context failure. CRITICAL: He does not know he could be experiencing a system that learns from every prior customer — he has no reference for that possibility.",
             "Is urgency correctly captured in ticket data? Do high-urgency tickets have worse SLA compliance? What would customer experience look like if his ticket was resolved in <2 min because 499 prior customers had the same problem?"],
        ],
        col_widths=[1.3, 2.7, 2.1, 2.0])

    heading(doc, "Table 1-B: Where the Accounts Disagree (Settled with Data)")
    table(doc,
        ["The disagreement", "Who says what", "How data settles it", "What follows"],
        [
            ["% of tickets that are repeat/answerable",
             "Sofia ~70% repeat. Marcus: 'I'd be guessing.'",
             "Data: 71.4% answerable_from_docs=True. Sofia's intuition confirmed.",
             "The system is discarding resolution knowledge on 71% of tickets. Not a delivery problem — a collective intelligence waste problem."],
            ["Non-fluent English ticket outcomes",
             "Sofia: non-fluent tickets have worst CSAT. Marcus: no data.",
             "Data: Non-fluent CSAT=3.04 vs Fluent=2.95. Non-fluent FCR=45.8% vs 43.2%. Sofia's belief NOT confirmed by outcomes.",
             "Per-ticket effort higher for non-fluent, but vocabulary mismatch affects retrieval quality — monitor per-segment from day 1."],
            ["Proportion of escalations that are tier-1-resolvable",
             "Daniel: 'about half' could be resolved at tier-1. Marcus sees only escalation rate.",
             "deployment_failure: 59% escalated, 70% answerable. authentication_failure: 70% answerable. api_key_issue: 67% answerable.",
             "Daniel is directionally correct. A confidence/findability gap — not a knowledge gap — is driving unnecessary escalations. Each unnecessary escalation is also knowledge waste."],
            ["Enterprise vs standard service quality",
             "Ravi: enterprise gets ~1hr answers. Marcus confirms different agreements.",
             "Enterprise: FCR 37.3%, avg 484 min, 62.7% escalated — WORSE than standard (43.1%, 442 min, 56.9%).",
             "Enterprise tickets are most complex. A system that learns from resolved tickets would compound faster on simpler categories, benefiting standard/business tier first."],
        ],
        col_widths=[1.6, 1.8, 2.3, 2.4])

    heading(doc, "Table 1-C: What Nobody Mentioned")
    table(doc,
        ["What was never mentioned", "Why you would have expected it", "What the data shows"],
        [
            ["Knowledge death after ticket close",
             "If 71% of tickets are already answered, the knowledge to prevent or instantly resolve them exists — but nobody described what happens to resolution knowledge when a ticket closes.",
             "Nothing. Every ticket resolved by an agent is effectively thrown away — the next agent (and next customer) starts from scratch. This is the core waste."],
            ["The docs_comment channel",
             "Sofia, Daniel, Ines all described documentation/search problems but nobody mentioned tickets arriving directly in documentation comments.",
             "Data: 15.6% of tickets arrive via docs_comment channel. These are high-intent, specific questions from active readers — highest probability of being answerable from the same page they're reading."],
            ["must_not_auto_respond safety flag",
             "Marcus mentioned wrong answers as a fear; Daniel mentioned security/billing. Nobody quantified the hard-block categories.",
             "Data: 17.4% (87/500) flagged must_not_auto_respond. These must be blocked before any routing decision."],
            ["Repeat contact rate",
             "With 44% FCR and 71% answerable tickets, significant re-contact is implied. Nobody flagged it explicitly.",
             "Data: 21.6% (108/500) are repeat contacts. 1 in 5 tickets is a customer who came back — the failure of first contact compounding into a second ticket."],
        ],
        col_widths=[2.0, 2.5, 3.6])

    doc.add_page_break()

    # ── SECTION 2 ─────────────────────────────────────────────────────────
    banner(doc, 2, "What the Ticket Data Shows",
           "Count before you interpret. development_tickets.json — 500 tickets.")

    heading(doc, "Table 2-A: Ticket Data Measurements")
    table(doc,
        ["What to measure", "Figure", "Source field", "What surprised you"],
        [
            ["Total tickets", "500", "development_tickets.json", "Large enough to be statistically meaningful across all 22 intent classes."],
            ["By channel", "Email 212 (42.4%) · Chat 155 (31.0%) · Docs_comment 78 (15.6%) · Forum 55 (11.0%)", "channel", "Docs_comment (15.6%) is significant and underappreciated — highest-intent users, reading documentation, hitting a wall."],
            ["By intent (22 classes)", "Even distribution 2.6–5.8% per class. Top: data_export 5.8%, data_residency 5.8%, rollback_request 5.6%, deployment_failure 5.4%", "labels.intent", "No single dominant category. Improvements must be horizontal — which favours a collective intelligence layer over any intent-specific fix."],
            ["By urgency", "High 146 (29.2%) · Medium 226 (45.2%) · Low 128 (25.6%)", "labels.urgency", "29.2% high-urgency with 8–12 hr response times = real customer harm every single day."],
            ["FCR rate", "43.8% (219/500)", "history.first_contact_resolution", "Close to Marcus's stated 42% — he was accurate even when 'guessing'. 21pp gap to industry benchmark of 65%."],
            ["Average CSAT", "2.97 / 5.0", "history.csat_rating", "Marcus quoted 3.2 — actual data is worse. Below 3.0 out of 5."],
            ["Answerable from existing docs", "71.4% (357/500)", "labels.answerable_from_docs", "THE single most important number. 71% of resolution knowledge already exists in 29 articles — but is being reconstructed from scratch every single time a ticket arrives."],
            ["Non-fluent outcomes", "Non-fluent 24% (120). FCR 45.8%, CSAT 3.04 vs Fluent FCR 43.2%, CSAT 2.95", "language_fluency, history.*", "Sofia's belief not confirmed — but vocabulary mismatch still affects retrieval quality. Monitor per-segment from day 1."],
            ["By customer tier", "Enterprise FCR 37.3%, 484 min, 62.7% escalated. Business FCR 48.2%, 359 min. Standard FCR 43.1%, 442 min.", "customer_tier, history.*", "Enterprise outcomes are worst despite premium agreements. They have the most complex tickets — benefit from a learning system compounds more slowly on complex cases."],
            ["Repeat contacts", "21.6% (108/500)", "history.repeat_contact", "1 in 5 tickets is a customer who came back. This is the downstream cost of knowledge waste — the same customer re-explaining the same problem."],
            ["must_not_auto_respond", "17.4% (87/500)", "labels.must_not_auto_respond", "87 tickets must never be auto-responded. Hard-block before any routing decision."],
            ["Escalation rate", "56.2% (281/500)", "history.escalated", "More than half escalate at ~4× cost. But more importantly: most of these escalations are knowledge-waste events — the answer existed but wasn't reachable."],
            ["Avg resolution time", "422 min overall. Security_incident 786 min, feature_request 724 min, compliance 679 min", "history.resolution_time_minutes", "The high-time categories are mostly safety-flagged (must always escalate). The highest-volume categories (deployment, auth) have lower times — exactly the categories most amenable to collective intelligence reuse."],
        ],
        col_widths=[1.7, 1.6, 1.3, 3.5])

    doc.add_page_break()

    # ── SECTION 3 ─────────────────────────────────────────────────────────
    banner(doc, 3, "Where the Time Actually Goes",
           "Volume ≠ effort. The hidden cost is knowledge reconstruction, not knowledge creation.")

    heading(doc, "Table 3-A: Effort vs Volume by Category")
    table(doc,
        ["Ticket category", "Volume", "Est. effort share", "Why they differ", "Evidence"],
        [
            ["security_incident", "5.2% (26)", "~12%", "100% escalation, avg 786 min. Legitimately complex — but a learning system would at least surface the 54% of docs-answerable cases instantly.", "786 min avg; 100% escalated; 54% answerable"],
            ["compliance_request", "5.2% (26)", "~11%", "100% escalation, 679 min avg. Legal/regulatory — always needs human judgement even when docs exist (65% answerable).", "679 min; 100% escalated; 65% answerable"],
            ["feature_request", "4.0% (20)", "~9%", "100% escalation, 724 min avg, 0% answerable. These are not support — they are product intelligence. Should be routed to product, not support.", "724 min; 0% answerable"],
            ["deployment_failure\n+ rollback_request", "11.0% combined (55)", "~10%", "HIGH YIELD. 59–75% answerable from docs but over-escalating. Each deployment failure is a product edge case — a learning system turns this into prevention data.", "Deployment 70% answerable, rollback 75%"],
            ["authentication_failure\n+ api_key_issue", "7.6% combined (38)", "~8%", "HIGH YIELD. 67–70% answerable. Sofia's most-mentioned repeats. Time goes to FINDING the answer, not knowing it — directly addressable by collective intelligence.", "Auth 70%, api_key 67% answerable"],
            ["performance_degradation", "4.6% (23)", "~8%", "70% escalation, 543 min avg. Investigation-heavy — but pattern-matching across prior incidents is exactly what algorithmic leverage encodes.", "543 min; 70% escalated"],
            ["unclear_request", "3.0% (15)", "~5%", "100% escalation, 516 min, 0% answerable. These are taxonomy failures — the system doesn't know what the customer is asking. A learning system reduces this over time.", "516 min; 0% answerable"],
        ],
        col_widths=[1.8, 0.8, 0.9, 3.0, 1.6])

    heading(doc, "Table 3-B: Steps in a Typical Agent Ticket — and Where the Waste Lives")
    callout(doc, "Reconstructed from Sofia's account. Steps 3 and 5 are where collective intelligence recovers time.", bg="EBF3FB")
    table(doc,
        ["Step", "What the agent does", "Time", "Collective intelligence impact"],
        [
            ["1", "Sort queue by age to avoid SLA breach", "1–2 min / session", "No change — human priority judgement. System can flag urgency."],
            ["2", "Read ticket, understand intent. Non-fluent: interpret before answering.", "1–10 min", "Classification reduces cognitive load. Non-fluent: semantic understanding helps."],
            ["3 ★", "Search docs for answer. IN PRACTICE: skip search, use personal snippet file because keyword search fails.", "2–15 min", "HIGH IMPACT. Semantic retrieval removes vocabulary mismatch. Collective resolution history supplements KB articles with agent-verified answers. Step 3 is the primary time recovery."],
            ["4 ★", "Write or adapt the answer from snippet file.", "2–5 min", "HIGH IMPACT. System drafts a grounded, cited response from retrieved docs + resolution history. Agent reviews, personalises, sends. Sofia: 'that would save me half of every ticket.'"],
            ["5 ★", "Decide to send or escalate. If escalating: forward raw ticket — no context, no summary.", "1–2 min", "HIGHEST ESCALATION IMPACT. Routing with confidence threshold. Escalation carries context packet (summary + docs + uncertainty). Daniel: 'context would make me twice as fast.' Each well-framed escalation also feeds resolution history."],
            ["6", "Handle follow-up from wrong or unclear first response.", "10–40 min", "PREVENTIVE. Better first-contact quality eliminates step 6 entirely. 21.6% repeat contact rate = 108 follow-up tickets eliminated by better resolution quality."],
        ],
        col_widths=[0.4, 2.2, 0.9, 4.6])

    doc.add_page_break()

    # ── SECTION 4 ─────────────────────────────────────────────────────────
    banner(doc, 4, "What the Client Counts as Success")

    heading(doc, "Table 4-A: Success Metrics")
    table(doc,
        ["Measure", "Who watches", "Current", "Target", "Confidence"],
        [
            ["First contact resolution (FCR)", "Marcus, executive team", "43.8%", "≥60%", "High — interview + data consistent"],
            ["Avg first response time", "Marcus, customers (SLA)", "8–12 hours", "<2 hrs", "High — consistent across Marcus and Ravi"],
            ["Escalation rate", "Marcus (cost)", "56.2%", "≤30%", "Medium — Marcus cited cost ratio, not a target rate"],
            ["Customer CSAT", "Marcus (exec report)", "2.97/5.0", "≥4.0/5.0", "Medium — Marcus's figure (3.2) is slightly optimistic vs data"],
            ["Repeat contact rate", "Not currently tracked", "21.6%", "≤10%", "Low — not a metric Marcus is watching; worth introducing"],
            ["Explainability / audit trail", "Marcus (compliance)", "None", "100% automated decisions logged with human-readable reason", "High — Marcus was explicit; autumn deadline"],
            ["Tier consistency", "Ravi (customer)", "Enterprise worst (37.3%)", "≤5pp variation vs baseline", "Medium — Ravi's concern; data confirms issue"],
        ],
        col_widths=[1.8, 1.3, 1.1, 1.7, 2.2])

    heading(doc, "Table 4-B: Sentence Test")
    table(doc,
        ["Prompt", "Your answer"],
        [
            ["This project will have been worth doing if, within three months of launch...",
             "FCR rises from 44% to 60%+, first response time falls below 2 hours for auto-responded tickets, repeat contact rate falls from 22% to 10%, and the system demonstrably improves with each ticket processed (calibration metrics improve over time)."],
            ["We will know it did not work if...",
             "A confidently wrong automated answer is screenshotted and circulated publicly; agent workload increases from handling corrections; escalation rate rises; or the system's accuracy does not improve over the first 60 days of operation."],
            ["The measure Marcus will actually be judged on internally is...",
             "First contact resolution. Marcus: 'First contact resolution, if I am being honest, more than response time. Response time is what is in the agreement so it is what gets reported.'"],
        ],
        col_widths=[2.5, 5.6])

    doc.add_page_break()

    # ── SECTION 5 ─────────────────────────────────────────────────────────
    banner(doc, 5, "Data, Constraints and Risk")

    heading(doc, "Table 5-A: Data Sources")
    table(doc,
        ["Data source", "What it contains", "Quality / gaps", "Constraints", "Private data?"],
        [
            ["Support tickets\n(development_tickets.json)", "500 labelled tickets: channel, subject, body, tier, region, language_fluency, intent, urgency, expected_route, answerable_from_docs, FCR, CSAT, resolution_time, escalated, repeat_contact.", "High quality — all fields populated, labels consistent. Real deployment would have noise and missing fields.", "Real: GDPR — customer_name and customer_id are PII; must never appear in outbound responses or logs.", "YES — customer_name, customer_id, customer_region."],
            ["Knowledge base\n(documentation.json)", "29 articles: title, category, body, doc_id. Categories: auth, deployment, api, performance, billing, data, security, account, integration, onboarding.", "Reviewed by Ines; current within review cycle. Gap: feature requests/roadmap/novel incidents have NO article. Vocabulary may mismatch customer language.", "Private snippet files OUT OF SCOPE (stale answers — Daniel's warning). System must learn from resolved tickets to supplement KB, not from unreviewed snippets.", "No."],
            ["Ground truth responses\n(ground_truth_responses.json)", "200 reference answers: required points, must_not_contain, expected_doc_ids. Written by senior agents.", "High quality but covers only 200/500 tickets. Cannot be used for training — only evaluation.", "Hold back for evaluation only. Using for training = overfitting to visible data.", "No."],
            ["Resolution history\n(derived from ticket data)", "history.* fields per ticket: resolution path, FCR, escalated, repeat_contact. Currently unused as a learning signal.", "Exists in development set. In production: every closed ticket adds to this. The compounding asset.", "Must not store customer PII in resolution history — store intent, resolution path, doc_id used, but not customer identity.", "Derived — PII stripped before storage."],
        ],
        col_widths=[1.5, 2.2, 2.0, 1.8, 0.6])

    heading(doc, "Table 5-B: Risk Register")
    table(doc,
        ["Risk", "Likelihood", "Severity", "Affected", "Prevention"],
        [
            ["System answers confidently and incorrectly", "Medium", "Very High", "All customers; reputation", "Grounding guardrail: every claim traces to retrieved passage. Confidence threshold 0.80. Citation required."],
            ["PII in outbound response", "Low", "Very High", "Customer; GDPR", "PII guardrail: scan every outbound response. Block + escalate if detected."],
            ["Some customer groups consistently get worse answers", "Medium", "High", "Non-fluent, enterprise", "Monitor per-segment continuously. Alert if any segment drops >5pp below average."],
            ["Documentation goes out of date", "Medium", "High", "All customers", "Log doc_id + last_reviewed per decision. Alert on articles >90 days since review."],
            ["Model provider unavailable", "Low", "High", "All customers", "Graceful degradation: route ALL tickets to escalate if provider unavailable."],
            ["Prompt injection", "Low", "Very High", "Any customer", "Injection guardrail: treat ticket body as untrusted input. Never inject directly into system prompt."],
            ["Confidence scores poorly calibrated", "Medium", "High", "All auto-responded", "Calibration check: verify stated confidence within 5pp of observed accuracy per band."],
            ["Resolution history feeds back incorrect resolutions (garbage in, garbage out)", "Low", "High", "Future customers receiving stale answers", "Only log CONFIRMED resolutions (FCR=True). Flag resolutions that generated repeat contacts — exclude from reinforcement."],
        ],
        col_widths=[2.0, 0.8, 0.8, 1.4, 3.1])

    doc.add_page_break()

    # ── SECTION 6 — EXTRAORDINARY PROBLEM FRAMEWORK ───────────────────────
    banner(doc, 6, "The Problem Statement",
           "Applied through the Extraordinary Problem 6-Step Journey (IIT Roorkee, FDE, Module 1, Session 2).",
           dark="0D3B66")

    callout(doc,
        "ORDINARY problem: 'CloudServe needs a better chatbot to answer tickets faster.'\n"
        "Rating: 1/5. Produces incremental answers. Keeps the same assumptions. No exponent in the equation.\n\n"
        "EXTRAORDINARY problem passes all 5 tests:\n"
        "  1. Challenges fundamental assumption\n  2. Reframes reactive → predictive → preventive\n"
        "  3. Non-obvious — customers don't want better support\n"
        "  4. Generates a data advantage that compounds\n  5. Creates a new category — no incumbent yet",
        bg="FEF9E7", italic=False)

    heading(doc, "Table 6-A: The 6-Step Extraordinary Problem Journey Applied")
    table(doc,
        ["Step", "Name", "Applied to CloudServe"],
        [
            ["1", "ORIGINAL PROBLEM",
             "'How do we build better customer support for CloudServe?' — This is the raw framing. It produces incremental answers: better routing, better chatbots, better SLAs. Useful. Ordinary. Not extraordinary."],
            ["2a", "LEVER 1 · DATA LIQUIDITY\n'What dormant data exists that no one is using?'",
             "Every ticket is a record of a product failure. The highest-fidelity dataset CloudServe has about its own broken edges. 500 tickets in the development set alone = 500 resolution paths. Every closed ticket is resolution knowledge — and it is entirely discarded. 71.4% of those tickets have answers already in the KB, solved from scratch every time."],
            ["2b", "LEVER 2 · NETWORK EFFECTS\n'Does each new user make it better for all?'",
             "As-is: Customer #500's experience is identical to Customer #1. Each ticket is stateless — an island. Redesigned: if every resolved issue feeds a shared resolution graph clustered by intent, Customer #500 gets a diagnosis in seconds because 499 near-identical cases already mapped the fastest path. The more customers CloudServe has, the smarter the system gets for everyone."],
            ["2c", "LEVER 3 · ALGORITHMIC LEVERAGE\n'What human judgement can be encoded?'",
             "Support agents pattern-match: 'this looks like the deployment issue we saw last Tuesday.' That judgement is repetitive, structured, and encodable. 71% of tickets are already answered by agents who pattern-match to existing docs. Encoding that pattern-matching frees the human for the 29% that genuinely requires judgement — security incidents, novel failures, complex compliance questions."],
            ["3", "NEW ECONOMICS REWRITE",
             "'How do we mine the resolution knowledge from every closed ticket, encode the pattern-recognition judgement of support agents, and turn each customer's friction into the prevention signal that makes every subsequent customer's experience faster — so that the system compounds in quality with every ticket it handles?'"],
            ["4", "ECONOMIC EQUATION",
             "Prevention = (Ticket history × Resolution patterns) ^ Cross-customer learning\n\nIf the equation has no exponent, it is a SaaS feature. The exponent here: each new resolved ticket makes ALL future tickets cheaper to resolve. The 500-ticket dataset already contains the seeds of this compounding. The hidden test: 71% answerable from docs × 21.6% repeat contacts = the system is throwing away its own compounding asset."],
            ["5", "FIRST PRINCIPLES × JTBD",
             "FP (structural truth): 71% of support failures are not complex problems. They are repeated failures of knowledge delivery, not knowledge creation. The answers already exist — and are discarded after every close.\n\nJTBD (human truth): Customers do not want better support. They want the problem to not exist. Filing a ticket is unwanted work. 'Support' is the failure mode of the real job — which is to use CloudServe without friction.\n\nFP × JTBD = Extraordinary Problem (what should exist but doesn't)"],
            ["6", "EXTRAORDINARY PROBLEM STATEMENT",
             "See Table 6-B."],
        ],
        col_widths=[0.5, 1.8, 5.8])

    heading(doc, "Table 6-B: The Extraordinary Problem Statement")
    callout(doc, "Write in language the Head of Support would recognise. No technical vocabulary. Rate it against the original.", bg="EBF3FB")

    # Original vs extraordinary
    t = doc.add_table(rows=2, cols=2)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    # headers
    for i, h in enumerate(["ORIGINAL STATEMENT  (Rating: 1/5)", "EXTRAORDINARY STATEMENT  (Rating: 4.5/5)"]):
        c = t.rows[0].cells[i]
        set_bg(c, "C0392B" if i == 0 else "1A6634")
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.font.bold = True; r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    # content
    orig = t.rows[1].cells[0]
    set_bg(orig, "FDF2F2")
    p = orig.paragraphs[0]
    r = p.add_run(
        "CloudServe needs a better chatbot to answer tickets faster. "
        "71% of tickets can be answered from their existing KB. The problem is that agents "
        "can't find the answers quickly because keyword search fails. "
        "We need a system that retrieves and surfaces existing answers to agents as a draft."
    )
    r.font.size = Pt(10); r.font.italic = True

    extr = t.rows[1].cells[1]
    set_bg(extr, "F0F9F4")
    p2 = extr.paragraphs[0]
    r2 = p2.add_run(
        "CloudServe's support system treats every ticket as an isolated, memoryless event — discarding "
        "the resolution knowledge generated by every previous customer who had the same problem, and "
        "making each agent reconstruct from scratch an answer that was solved correctly yesterday. "
        "500+ tickets per week, each one a data point thrown away at close. 71% of them already have "
        "answers in existing documentation — yet the same problem reaches the queue again tomorrow. "
        "Every unnecessary escalation costs 4× a resolved ticket and arrives at tier-2 without the "
        "context that would have let them act in minutes. The correct solution does not exist yet: "
        "a system that turns each resolved ticket into a signal that makes every future ticket "
        "cheaper to resolve, gives every new customer the accumulated intelligence of everyone who "
        "came before them, and compresses a 12-hour problem into a 2-minute one — without inventing "
        "new answers, only delivering the ones that already exist, grounded, cited, and verifiable."
    )
    r2.font.size = Pt(10)
    for c in t.columns:
        for cell in c.cells:
            cell.width = Inches(4.1)
    doc.add_paragraph()

    heading(doc, "Table 6-C: The 5-Test Extraordinary Problem Rubric")
    callout(doc, "A problem statement is extraordinary when it passes all 5 tests. (Source: Slide 12, extraordinaryproblem.pdf)", bg="FEF9E7")
    table(doc,
        ["Test", "What it checks", "Does our statement pass?", "Evidence"],
        [
            ["1. Challenges fundamental assumption",
             "Questions what the entire industry accepts as given.",
             "✅ YES — the industry assumes every ticket must be resolved individually from scratch. Our statement challenges 'support is necessary reactive work' and asserts that resolution knowledge should compound.",
             "71.4% answerable from docs — same answer reconstructed 357+ times/500 tickets."],
            ["2. Reframes reactive → predictive → preventive",
             "Shifts architectural generation, not just implementation.",
             "✅ YES — from 'answer tickets faster' (reactive) to 'make each ticket reduce the cost of the next' (predictive compound). Prevention = (Ticket history × Resolution patterns) ^ Cross-customer learning.",
             "Each resolved ticket should update the resolution graph. Currently: 0% of tickets feed back."],
            ["3. Non-obvious",
             "Customers don't actually want the product category they're paying for.",
             "✅ YES — customers don't want better support. They want the problem to not exist. Ravi: 'Waiting matters differently by urgency.' The JTBD is zero friction, not faster friction.",
             "Ravi interview: 'Slow but decent once you get there. The waiting is the problem.' The job is not 'get faster support' — the job is 'have no reason to contact support.'"],
            ["4. Generates a data advantage",
             "Every solved instance teaches the system. Competitors stay the same.",
             "✅ YES — every resolved ticket (FCR=True) feeds the resolution graph. CloudServe's 500 tickets/week = 26,000 data points/year compounding. A competitor starting from scratch has no equivalent head start.",
             "Network effect: Customer #1,000 should get answer in seconds because 999 near-identical cases already mapped the path."],
            ["5. Creates a new category",
             "Not 'better X' but a category that does not exist. No incumbent yet.",
             "✅ YES — not 'better support chatbot' but a collective intelligence layer that makes the product smarter with each customer interaction. The category: zero-support products, where the product heals itself.",
             "No incumbent currently converts resolution history into a compounding reuse asset across customers."],
        ],
        col_widths=[1.5, 1.8, 2.5, 2.3])

    heading(doc, "Self-Check Before Moving to Stage 2 (PRD)")
    checks = [
        "✅  Marcus would recognise this — FCR is his number; explainability is his requirement; system must not increase agent work",
        "✅  Sofia would recognise this — snippet file workaround, findability problem, draft-not-auto-send model",
        "✅  Daniel would recognise this — context-enriched escalations, tier-1-resolvable escalations, resolution knowledge reuse",
        "✅  Ines would recognise this — retrieval from her 29 articles, citation requirement, private files excluded",
        "✅  Ravi would recognise this — honest automated response, citations, urgency asymmetry",
        "✅  All 5 extraordinary problem tests pass",
        "✅  Economic equation has an exponent (network effect) — not a SaaS feature",
        "✅  Problem statement does not mention embeddings, retrieval, or LLMs — it describes the business problem",
        "✅  Every claim traceable to a section/row in Sections 1–5",
    ]
    for c in checks:
        p = doc.add_paragraph(c)
        p.paragraph_format.left_indent = Inches(0.3)
        p.runs[0].font.size = Pt(10)

    path = os.path.join(OUTPUT_DIR, "Stage_1_Discovery_Workbook_Filled.docx")
    doc.save(path)
    print(f"✅  Stage 1 saved: {path}")
    return path


# ═══════════════════════════════════════════════════════════════════════════
# DOCUMENT 2: Stage 2 PRD v1 — Extraordinary Problem Edition
# ═══════════════════════════════════════════════════════════════════════════

def build_prd_v2():
    doc = Document()
    s = doc.sections[0]
    s.top_margin = Cm(2); s.bottom_margin = Cm(2)
    s.left_margin = Cm(2.5); s.right_margin = Cm(2.5)

    cover(doc,
        "Capstone Project  ·  Product Requirements Document  ·  Version 1.0",
        "Framing: Collective intelligence layer (Extraordinary Problem — not 'better chatbot')\n"
        "Every requirement references its discovery evidence. "
        "Economic equation: Prevention = (Ticket history × Resolution patterns) ^ Cross-customer learning.\n"
        "Traceability chain: Discovery evidence → Requirement ID → Specification/Prompt → Code.",
        "CloudServe Solutions  |  Week 1, Day 4  |  STATUS: DRAFT")

    # ── SECTION A: DOCUMENT CONTROL ───────────────────────────────────────
    banner(doc, "A", "Document Control")
    table(doc,
        ["Field", "Value"],
        [
            ["Document title", "CloudServe Intelligent Support System — Product Requirements Document"],
            ["Version", "1.0 (initial)"],
            ["Status", "Draft — Week 1 Day 4"],
            ["Author", "Nishchay Gupta"],
            ["Date created", "7 November 2026"],
            ["Next scheduled revision", "After Week 2 Day 5 gate run (Stage 5: PRD Revision Log)"],
            ["Discovery evidence source", "docs/Stage_1_Discovery_Workbook_Filled.docx"],
            ["Extraordinary Problem framework", "extraordinaryproblem.pdf · FDE · IIT Roorkee · Module 1 Session 2"],
            ["Economic equation", "Prevention = (Ticket history × Resolution patterns) ^ Cross-customer learning"],
        ],
        col_widths=[2.2, 5.9])

    # ── SECTION B: THE PROBLEM ─────────────────────────────────────────────
    banner(doc, "B", "The Problem — Extraordinary Framing",
           "From ordinary ('faster chatbot') to extraordinary ('collective intelligence that compounds').")

    callout(doc,
        "ORIGINAL (Rating 1/5): 'CloudServe needs a better chatbot to answer tickets faster.'\n\n"
        "EXTRAORDINARY (Rating 4.5/5): CloudServe's support system treats every ticket as an isolated, "
        "memoryless event — discarding the resolution knowledge generated by every previous customer who "
        "had the same problem, and making each agent reconstruct from scratch an answer that was solved "
        "correctly yesterday. The correct solution does not exist yet: a system that turns each resolved "
        "ticket into a signal that makes every future ticket cheaper to resolve.",
        bg="F0F9F4", italic=False)

    p = doc.add_paragraph(
        "CloudServe receives 500+ support tickets per week with 6 agents. "
        "Average first response: 8–12 hours against a 2-hour SLA. FCR: 43.8% vs 65% industry benchmark. "
        "56.2% of tickets escalate at ~4× cost. 21.6% of tickets are repeat contacts. "
        "Most significantly: 71.4% of all tickets are answerable from 29 existing KB articles — "
        "yet each one is resolved from scratch, discarding the resolution knowledge entirely."
    )
    p.runs[0].font.size = Pt(10)
    p2 = doc.add_paragraph(
        "This is not a delivery problem that a better chatbot solves. "
        "It is a collective intelligence waste problem. The answers already exist. "
        "The resolution paths already exist (in 500 prior tickets). "
        "What does not exist is a system that mines that dormant resolution data, "
        "encodes the pattern-recognition judgement of agents, and turns each closed ticket "
        "into a compound signal that makes every future ticket cheaper — "
        "giving each new customer the accumulated intelligence of all who came before them."
    )
    p2.runs[0].font.size = Pt(10)
    doc.add_paragraph()

    # ── SECTION C: USER GROUPS ─────────────────────────────────────────────
    banner(doc, "C", "User Groups and Their Goals")
    table(doc,
        ["User group", "Primary goal", "Current pain", "What extraordinary looks like for them"],
        [
            ["Tier-1 Agent (Sofia)", "Answer accurately without reconstructing every time", "Spends most time FINDING answers she already knows. Private snippet file = personal workaround for a systemic failure.", "System presents a grounded draft + cited doc page + similar prior resolutions. She reviews, personalises, sends. Half the ticket time eliminated."],
            ["Tier-2 Engineer (Daniel)", "Handle genuinely complex escalations, fast", "Escalations arrive without context — 15–30 min reconstructing what was already asked.", "Escalation arrives with: 2-sentence summary + relevant docs + uncertainty reason + similar prior escalations. He acts immediately."],
            ["Head of Support (Marcus)", "FCR ≥60%, response <2 hrs, audit trail for compliance", "Red numbers for 2 quarters. Cannot explain decisions to compliance reviewers.", "System that gets better every week — measurable FCR improvement trajectory, full decision log, calibrated confidence."],
            ["Customer (Ravi, Business tier)", "Fast, accurate, honest answers — especially high-urgency", "Waits 8+ hrs. Finds answer himself 50% of the time.", "Failing deployment at 9am resolved in <2 min because 499 prior customers mapped that exact path. Cited, honest, verifiable."],
            ["Technical Writer (Ines)", "Accurate docs; understand where they're used and where they fail", "Does not know which articles the system uses or whether failures are article errors vs system errors.", "Every auto-response logs which doc_id was cited. She sees: 'DOC-DEPLOY-001 cited 47 times this week, 3 incorrect resolutions — article needs updating.'"],
        ],
        col_widths=[1.5, 1.7, 2.0, 3.0])

    doc.add_page_break()

    # ── SECTION D: FUNCTIONAL REQUIREMENTS ────────────────────────────────
    banner(doc, "D", "Functional Requirements",
           "FR-01 to FR-18. Every requirement references its discovery evidence.")

    heading(doc, "D1: Ingestion (FR-01 to FR-02)")
    table(doc,
        ["ID", "Requirement", "Acceptance criterion", "Discovery evidence", "Extraordinary connection"],
        [
            ["FR-01", "Accept tickets from all 4 channels: email, live chat, API docs comments, community forum.", "All 4 channel types in eval set processed without error.", "Data: email 42.4%, chat 31.0%, docs_comment 15.6%, forum 11.0%.", "docs_comment channel is highest-intent — users reading docs and hitting a wall. First touchpoint for compound learning."],
            ["FR-02", "Normalise all tickets into one internal representation regardless of channel.", "Normalised ticket contains: ticket_id, channel, subject, body, received_at, customer_id, customer_tier, customer_region, language_fluency.", "Architecture requirement — downstream components must not contain channel-specific logic.", "Uniform representation is required to build a cross-channel resolution graph."],
        ],
        col_widths=[0.6, 2.0, 1.8, 2.0, 1.7])

    heading(doc, "D2: Classification (FR-03 to FR-05)")
    table(doc,
        ["ID", "Requirement", "Acceptance criterion", "Discovery evidence", "Extraordinary connection"],
        [
            ["FR-03", "Classify every ticket with one of 22 intent classes.", "Classification precision ≥85% per class on validation set (confusion matrix provided).", "Data: 22 intent classes in corpus. Marcus and Sofia both describe needing to know 'what kind of ticket' before acting.", "Accurate intent classification is the key to the resolution graph — wrong intent = wrong resolution path retrieved."],
            ["FR-04", "Assign urgency (high/medium/low) to every ticket.", "Urgency assigned and logged for 100% of processed tickets.", "Data: 29.2% high-urgency. Ravi: 'Waiting matters differently by urgency.'", "High-urgency tickets need fastest retrieval path — compound learning should prioritise high-urgency resolution paths."],
            ["FR-05", "Produce calibrated confidence score 0.0–1.0. Confidence bands (0.5–0.6 etc.) must match observed accuracy within 5pp.", "Calibration check: stated confidence within 5pp of measured accuracy per band.", "Marcus: 'I would rather it said nothing than said something wrong.'", "Calibration is non-negotiable — the routing threshold is only meaningful if confidence reflects actual probability of being correct."],
        ],
        col_widths=[0.6, 1.8, 1.8, 1.8, 2.1])

    heading(doc, "D3: Retrieval (FR-06 to FR-07)")
    table(doc,
        ["ID", "Requirement", "Acceptance criterion", "Discovery evidence", "Extraordinary connection"],
        [
            ["FR-06", "Semantic search over 29 KB articles using all-MiniLM-L6-v2 embeddings. Returns passages with doc_id, title, score.", "Query using customer vocabulary ('my deployment keeps dying') returns correct KB article (e.g. DOC-DEPLOY-001).", "Ines: keyword search fails on vocabulary mismatch. Section 3 Step 3: most time wasted here. 71.4% answerable.", "Semantic retrieval is the first compounding component — it turns static KB articles into a queryable resolution asset."],
            ["FR-07", "Return empty list when no article is relevant. Never return plausible-but-irrelevant passages.", "Feature-request query returns empty list; system escalates. Zero irrelevant retrievals in sampled evaluation.", "Ines: 'Feature requests — obviously, since there is no answer to retrieve.' System must know what it doesn't know.", "Knowing what is not in the KB is as important as knowing what is. Return nothing → escalate → human resolves → feed back into resolution graph."],
        ],
        col_widths=[0.6, 1.8, 1.8, 1.8, 2.1])

    heading(doc, "D4: Routing (FR-08 to FR-10)")
    table(doc,
        ["ID", "Requirement", "Acceptance criterion", "Discovery evidence", "Extraordinary connection"],
        [
            ["FR-08", "Hard-check must_not_auto_respond flag before ANY routing. True = escalate regardless of confidence.", "100% of must_not_auto_respond=True tickets in eval set routed to escalate. Zero violations.", "Data: 17.4% safety-flagged. Daniel: security/billing/data residency must always escalate.", "Safety-flagged categories include the ones most likely to corrupt the resolution graph if wrong — keep them human-only."],
            ["FR-09", "Route using confidence threshold (default 0.80, justified with eval data). Same input = same output always (deterministic).", "Same ticket always produces same routing decision. Threshold value logged with every decision.", "Marcus: 'I would rather it said nothing.' Threshold justified by calibration data, not assumption.", "Threshold is the governor on the resolution graph — only high-confidence resolutions should feed back into the learning signal."],
            ["FR-10", "Escalated tickets MUST carry context packet: (a) 2-sentence summary, (b) retrieved passages with doc_ids, (c) reason for uncertainty.", "100% of escalated tickets in eval set have context packet with all 3 fields populated.", "Daniel: 'If an escalation arrived with context I would be twice as fast.' Currently: raw ticket forwarded.", "Context packet = the collective intelligence layer for tier-2. Each well-framed escalation is also data: what the system was uncertain about at that confidence level."],
        ],
        col_widths=[0.6, 1.8, 1.8, 1.8, 2.1])

    heading(doc, "D5: Generation (FR-11 to FR-12)")
    table(doc,
        ["ID", "Requirement", "Acceptance criterion", "Discovery evidence", "Extraordinary connection"],
        [
            ["FR-11", "Generated responses MUST cite the specific KB article(s) used (doc_id inline). Citations must resolve to actually-retrieved passages.", "Citation accuracy ≥95%. Hallucination rate ≤5% on 50+ sampled responses (2 independent assessors).", "Ines: 'I want to know which article — so I can tell whether the article is wrong or the system misread it.' Ravi: 'Here is the page it came from.'", "Citations are the audit trail of the resolution graph. Ines uses them to improve KB articles — which improves future retrievals — which improves future resolutions. Compounding."],
            ["FR-12", "MUST NOT generate without retrieved passages. Empty passages = escalate before calling generation.", "ValueError raised if generate called with empty passages. Zero manufactured answers on no-KB-match tickets.", "Ines: topics with no article must not be manufactured.", "Generating without grounding = introducing noise into the resolution graph. Ground truth only comes from verified KB content."],
        ],
        col_widths=[0.6, 1.8, 1.8, 1.8, 2.1])

    heading(doc, "D6: Guardrails (FR-13 to FR-17)")
    table(doc,
        ["ID", "Guardrail", "Requirement", "Acceptance criterion", "Discovery evidence"],
        [
            ["FR-13", "PII Detection", "Scan every outbound response for PII (names, addresses, account numbers, API keys, emails). Block + escalate if detected.", "Zero PII violations in eval set. Triggered test confirms block.", "GDPR. customer_name and customer_id in ticket data must never reach outbound responses."],
            ["FR-14", "Grounding Check", "Every factual claim must trace to a retrieved passage. Ungrounded claims = block + escalate.", "Hallucination rate ≤5% (NFR-04). Engineered trigger (question with no relevant passage) confirms block.", "Marcus primary fear. Ravi: 'I will act on it and break something.' Ungrounded answers corrupt the resolution graph."],
            ["FR-15", "Injection Detection", "Detect ticket text attempting to override system instructions. Block + log the attempt.", "Engineered injection ticket blocked and logged. Zero injection successes in eval set.", "Security — tickets are untrusted user input. System must never treat ticket body as trusted instructions."],
            ["FR-16", "Tone/Scope", "No refund commitments, timeline promises, or SLA exceptions. Block if detected.", "Engineered trigger with refund commitment confirms block.", "Daniel: 'Billing becomes contractual quickly.' Only logged resolutions feed back — blocked resolutions do not."],
            ["FR-17", "Confidence Floor", "Verify routing threshold was actually applied before auto-responding. Escalate if not.", "Bypass test confirms guardrail 5 catches and escalates.", "Governance — decision log must show threshold was applied, not just configured."],
        ],
        col_widths=[0.6, 1.0, 2.2, 2.0, 2.3])

    heading(doc, "D7: Decision Logging + Resolution Graph (FR-18 to FR-19)")
    table(doc,
        ["ID", "Requirement", "Acceptance criterion", "Discovery evidence", "Extraordinary connection"],
        [
            ["FR-18", "EVERY automated decision logged to SQLite with full schema (decision_id, timestamp, ticket_id, stage, model, prediction+confidence, sources_used, threshold_applied, action_taken, reason, guardrail_results, prompt_version, requirement_ids).", "count_decisions() == total tickets processed in every run. Logged decisions match processed tickets exactly — including failures and escalations.", "Marcus: compliance review. Autumn deadline. Every automated decision must have a human-readable reason.", "Decision log = the resolution graph seed. Every entry is a training signal for future routing. Without it, there is no compounding."],
            ["FR-19", "For tickets with FCR=True (confirmed first-contact resolution), log the resolution path (intent, passages_used, answer_summary) as a reusable resolution record. This is the input to future retrieval improvement.", "Resolution records written for 100% of FCR=True tickets. Each record contains: intent, doc_ids_used, confidence, customer_tier (anonymised), language_fluency.", "Data: 43.8% FCR = 219 confirmed resolutions in development set. Each is a proven answer path. Section 6 extraordinary problem: every closed ticket should make next ticket cheaper.", "THIS IS THE EXPONENT. This is what turns the system from a SaaS feature into an extraordinary AI-native product. Without FR-19, the economic equation has no network effect."],
        ],
        col_widths=[0.6, 2.2, 2.0, 1.8, 1.5])

    doc.add_page_break()

    # ── SECTION E: NON-FUNCTIONAL REQUIREMENTS ────────────────────────────
    banner(doc, "E", "Non-Functional Requirements",
           "NFR-01 to NFR-10. All figures traceable to discovery evidence.")
    table(doc,
        ["ID", "Category", "Requirement", "Target", "Discovery evidence"],
        [
            ["NFR-01", "Latency", "P95 end-to-end response latency for auto-responded tickets", "<3 seconds", "Ravi: urgency asymmetry — failing deployment at 9am cannot wait. Marcus: SLA breach ongoing."],
            ["NFR-02", "Availability", "System availability during operating hours", "≥99.5%", "SLA obligation. System downtime = full return to 8–12 hr response times."],
            ["NFR-03", "Intent precision", "Classification precision per class on validation set", "≥85% per class", "Routing quality depends on classification. At <85%, wrong tickets auto-respond."],
            ["NFR-04", "Hallucination rate", "Auto-responses containing ungrounded claims; 2 assessors; ≥50 samples", "≤5%", "Marcus primary fear. Ravi: 'I will act on it and break something.'"],
            ["NFR-05", "Citation accuracy", "Citations resolving to the actual retrieved passage supporting the claim", "≥95%", "Ines: citation is the audit trail for KB quality improvement."],
            ["NFR-06", "PII in responses", "Outbound responses containing PII", "Zero occurrences", "GDPR. Any PII in outbound response is a reportable breach."],
            ["NFR-07", "Tier consistency", "Variation in FCR across tiers (enterprise vs business vs standard)", "<5pp gap increase vs baseline", "Ravi: 'If this change makes that gap bigger, we will notice at renewal.' Enterprise already 37.3% FCR vs business 48.2%."],
            ["NFR-08", "Language consistency", "Variation in accuracy between fluent and non-fluent English tickets", "<5pp", "Sofia concern. Vocabulary mismatch affects retrieval quality for non-fluent tickets — monitor from day 1."],
            ["NFR-09", "Decision log coverage", "Automated decisions logged — including failures and escalations", "100% (count_decisions() == tickets_processed)", "Marcus: compliance review. Log that covers only successes is not an audit trail."],
            ["NFR-10", "Confidence calibration", "Stated confidence within observed accuracy per confidence band", "Within 5pp per band", "Routing threshold only meaningful if confidence reflects actual probability."],
        ],
        col_widths=[0.7, 1.2, 2.5, 1.1, 2.6])

    doc.add_page_break()

    # ── SECTION F: OUT OF SCOPE ────────────────────────────────────────────
    banner(doc, "F", "Out of Scope",
           "Explicitly excluded — not as omissions, but as deliberate decisions traceable to discovery.")
    table(doc,
        ["Excluded", "Why", "Discovery evidence"],
        [
            ["Feature requests, roadmap questions, novel incidents", "No KB article exists. System must escalate, not manufacture. These feed product intelligence, not support resolution.", "Ines: 'Feature requests — obviously, since there is no answer to retrieve.' Data: feature_request 0% answerable."],
            ["Auto-responding to security incidents, billing disputes, compliance requests", "17.4% safety-flagged must_not_auto_respond=True. Contractual/legal/security implications — wrong answer at scale.", "Data: 87/500 flagged. Daniel: 'Billing becomes contractual; security must always escalate.'"],
            ["Training on agents' personal snippet files", "Snippet files are unreviewed and contain known-stale answers. Training on them scales mistakes.", "Daniel: 'Some answers were correct two years ago and have not been right since. If you learn from those you scale up a mistake.'"],
            ["Replacing human agents", "The model is agent-assist: draft + review. Sofia specifically described wanting draft+page, not auto-send.", "Sofia: 'If it hands me a ticket with a draft and the relevant page attached, that would genuinely help.' Marcus: primary fear is wrong answer reaching customer without review."],
            ["Customer-facing direct response (v1)", "Primary interface is agent-assist. Customer-facing direct response requires higher confidence bar and is a future phase.", "Marcus: 'I would rather it said nothing than said something wrong.' Agent review is v1 safety layer."],
            ["Multi-language response generation", "Retrieval from English KB, draft in English. Translation pipeline adds complexity outside v1 scope.", "Non-fluent CSAT data inconclusive (Section 1, Table 1-B). Translation deferred."],
        ],
        col_widths=[1.8, 3.2, 3.1])

    doc.add_page_break()

    # ── SECTION G: ASSUMPTIONS ─────────────────────────────────────────────
    banner(doc, "G", "Assumptions and Consequences If Wrong")
    table(doc,
        ["Assumption", "Consequence if wrong", "How to detect"],
        [
            ["29 KB articles remain current and reviewed by Ines throughout the project.", "System retrieves stale content; answer quality degrades silently.", "Log doc_id + last_reviewed per decision. Alert if article >90 days since review."],
            ["Confidence threshold of 0.80 will produce acceptable routing decisions.", "Too high: over-escalates. Too low: auto-responds on uncertain cases.", "Calibration check on validation set. Adjust threshold based on data in Week 2 Day 5."],
            ["OpenRouter free tier provides sufficient capacity.", "Rate limiting causes timeouts; harness fails to process all tickets unattended.", "Test harness against full 80-ticket validation set. Rate limit errors appear in logs."],
            ["all-MiniLM-L6-v2 captures sufficient semantic similarity for retrieval.", "Vocabulary mismatch problem persists despite semantic search.", "Test with 20 known-question/known-article pairs. Recall should be >90%."],
            ["Resolution records from FCR=True tickets are reliable enough to feed back as training signal (FR-19).", "System reinforces incorrect resolutions if FCR=True is inaccurate.", "Cross-check: resolutions that generated a subsequent repeat contact should be excluded from the reinforcement signal."],
        ],
        col_widths=[2.3, 2.5, 3.3])

    doc.add_page_break()

    # ── SECTION H: SUCCESS MEASURES ───────────────────────────────────────
    banner(doc, "H", "Success Measures",
           "All baselines from Stage 1 discovery. Trajectory matters as much as the number.")
    table(doc,
        ["Measure", "Baseline", "Target", "How measured", "Extraordinary indicator"],
        [
            ["FCR", "43.8%", "≥60%", "history.first_contact_resolution in eval set", "FCR should improve over time as resolution graph grows — plot improvement trajectory, not just snapshot."],
            ["Avg first response", "8–12 hours", "<2 hrs (auto-responded)", "history.resolution_time_minutes for auto-responded subset", "As resolution graph matures, avg response time for top-10 intents should approach seconds, not minutes."],
            ["Escalation rate", "56.2%", "≤30%", "history.escalated in eval set", "Escalation rate should decline as the system routes with more confidence over time."],
            ["CSAT", "2.97/5.0", "≥4.0/5.0", "history.csat_rating (proxy; state sample size)", "CSAT improvement is a lagging indicator — set expectation with Marcus that it lags FCR improvement by ~30 days."],
            ["Repeat contact rate", "21.6%", "≤10%", "history.repeat_contact in eval set", "Repeat contact rate is the most direct measure of resolution quality — a system that learns should drive this toward zero on high-volume intents."],
            ["Hallucination rate", "Not measured", "≤5%", "2 independent assessors on ≥50 sampled auto-responses", "—"],
            ["Citation accuracy", "Not measured", "≥95%", "Each citation checked against the passage it supports", "Ines's audit: citation log enables her to identify which KB articles need updating — closing the loop."],
            ["PII in responses", "Not measured", "Zero", "PII guardrail log; manual spot-check", "—"],
            ["Decision log coverage", "0%", "100%", "count_decisions() == tickets_processed", "—"],
            ["Resolution graph growth (FR-19)", "0 records", "≥FCR×tickets processed per run", "Count resolution records in resolution log", "THIS IS THE EXTRAORDINARY METRIC. If resolution graph is not growing, the system is not compounding."],
        ],
        col_widths=[1.8, 1.0, 1.3, 2.2, 2.8])

    doc.add_page_break()

    # ── SECTION I: TRACEABILITY MATRIX ────────────────────────────────────
    banner(doc, "I", "Traceability Matrix",
           "Evidence → Requirement → Specification/Prompt → Code Module")
    table(doc,
        ["Requirement IDs", "Discovery evidence reference", "Specification / Prompt", "Code module"],
        [
            ["FR-01, FR-02", "Section 2, Table 2-A: channel distribution. docs_comment 15.6% — underappreciated.", "PR-IN-01 v1.0 (write Week 1 Day 5)", "src/ingest.py"],
            ["FR-03, FR-04, FR-05", "Section 4, Table 4-A: FCR metric. Data: urgency 29.2% high. Marcus: 'I picture it answering the easy ones.'", "PR-CL-01 v1.0", "src/classify.py"],
            ["FR-06, FR-07", "Section 1, Table 1-B Row 1: 71.4% answerable from docs. Ines: vocabulary mismatch kills keyword search. Section 3, Table 3-B Step 3.", "PR-RT-01 v1.0 (write Week 1 Day 5)", "src/retrieve.py"],
            ["FR-08, FR-09, FR-10", "Data: 17.4% must_not_auto_respond. Daniel: escalations arrive without context. Section 3, Table 3-B Step 5.", "PR-RO-01 v1.0 (write Week 1 Day 5)", "src/route.py"],
            ["FR-11, FR-12", "Ines: citation requirement. Ravi: source transparency. 71.4% answerable — generation only when passages exist.", "PR-GN-01 v1.0", "src/generate.py"],
            ["FR-13 – FR-17", "Marcus: compliance. GDPR. Daniel: security/billing. Section 5, Table 5-B: risk register.", "PR-GD-01 to PR-GD-05 (write Week 1 Day 5)", "src/guardrails.py"],
            ["FR-18", "Marcus: compliance review; autumn deadline. Section 5, Table 5-B: governance risk.", "Decision log schema (Governance_Framework.docx)", "src/logging_store.py"],
            ["FR-19 ★", "Section 6, Table 6-A Steps 2-4: extraordinary problem. Economic equation. Network effects exponent.", "Resolution graph spec (new — write Week 1 Day 5)", "src/logging_store.py (extension)"],
            ["NFR-01 to NFR-10", "Section 4, Table 4-A: success metrics. Ravi: urgency. Marcus: 4× escalation cost.", "Evaluation framework (Evaluation_Framework.docx)", "evaluation/harness.py"],
        ],
        col_widths=[1.2, 2.8, 1.9, 2.2])

    doc.add_page_break()

    # ── SECTION J: REVISION LOG PLACEHOLDER ───────────────────────────────
    banner(doc, "J", "Revision Log",
           "At least one substantive change required. Fill in during Week 3 Day 3.")
    table(doc,
        ["Version", "Date", "What changed", "What triggered the change", "What was NOT changed and why"],
        [
            ["1.0 → 1.x", "(Week 3 Day 3)", "(Fill in after Week 2 Day 5 gate run)", "(Code contact / evaluation data / discovery finding)", "(Fill in — record what you chose to keep and why — not all changes are improvements)"],
        ],
        col_widths=[0.7, 1.0, 2.2, 2.0, 2.2])

    callout(doc,
        "Reminder from Capstone Instructions: 'Requirements that survive three weeks of contact with real code "
        "without a single amendment almost always mean that nobody was reading them.' "
        "At least one substantive change is required before submission. "
        "Most likely candidate: FR-19 (resolution graph) may need revision once real-world FCR data is measured.",
        bg="FEF9E7")

    path = os.path.join(OUTPUT_DIR, "Stage_2_PRD_v1.docx")
    doc.save(path)
    print(f"✅  Stage 2 PRD saved: {path}")
    return path


# ───────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating Stage 1 Discovery Workbook (Extraordinary Problem edition)...")
    build_discovery_v2()

    print("Generating Stage 2 PRD v1 (Extraordinary Problem edition)...")
    build_prd_v2()

    print("\nDone. Both documents saved to docs/")
