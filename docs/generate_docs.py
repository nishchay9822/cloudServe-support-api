"""
Script to generate Stage 1 Discovery Workbook and Stage 2 PRD as .docx files.
Run from project root:  venv/bin/python3 docs/generate_docs.py
"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__))


# ─────────────────────────── HELPERS ────────────────────────────────────────

def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def add_heading(doc, text, level=1, color="1F3864"):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = RGBColor.from_string(color)
    return h


def add_callout(doc, text, bg="EBF3FB"):
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    cell = table.cell(0, 0)
    set_cell_bg(cell, bg)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.font.size = Pt(10)
    run.font.italic = True
    doc.add_paragraph()


def add_section_banner(doc, section_num, title, subtitle=""):
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    cell = table.cell(0, 0)
    set_cell_bg(cell, "1F3864")
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(f"SECTION {section_num}   {title.upper()}")
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    run.font.bold = True
    run.font.size = Pt(12)
    if subtitle:
        p2 = cell.add_paragraph()
        r2 = p2.add_run(subtitle)
        r2.font.color.rgb = RGBColor(0xBF, 0xD7, 0xED)
        r2.font.size = Pt(9)
    doc.add_paragraph()


def make_table(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    # header row
    hdr_row = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr_row.cells[i]
        set_cell_bg(cell, "2E4057")
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.font.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    # data rows
    for ri, row in enumerate(rows):
        bg = "F7F9FC" if ri % 2 == 0 else "FFFFFF"
        for ci, val in enumerate(row):
            cell = table.rows[ri + 1].cells[ci]
            set_cell_bg(cell, bg)
            p = cell.paragraphs[0]
            run = p.add_run(str(val))
            run.font.size = Pt(9)
    # column widths
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Inches(w)
    doc.add_paragraph()
    return table


# ═══════════════════════════════════════════════════════════════════════════
# DOCUMENT 1: Stage 1 Discovery Workbook
# ═══════════════════════════════════════════════════════════════════════════

def build_discovery_workbook():
    doc = Document()

    # Page margins
    section = doc.sections[0]
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    # Cover
    doc.add_paragraph()
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tr = title_p.add_run("FORWARD DEPLOYED AI ENGINEERING")
    tr.font.size = Pt(14)
    tr.font.bold = True
    tr.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_p.add_run("Capstone Project  ·  Stage One: Discovery Workbook").font.size = Pt(12)

    filled_p = doc.add_paragraph()
    filled_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr = filled_p.add_run("FILLED — Week 1, Days 2–3  |  CloudServe Solutions")
    fr.font.size = Pt(10)
    fr.font.color.rgb = RGBColor(0x2E, 0x86, 0xAB)

    doc.add_paragraph()
    add_callout(doc,
        "Evidence sources: 5 stakeholder interview transcripts (Stakeholder_Interviews.docx) "
        "+ data/development_tickets.json (500 labelled tickets).\n"
        "Every claim in Section 6 (Problem Statement) is traceable to a row in Sections 1–5.",
        bg="EBF3FB")

    doc.add_page_break()

    # ── SECTION 1 ────────────────────────────────────────────────────────
    add_section_banner(doc, 1, "What the Interviews Tell You",
                       "Fill in from the five transcripts before opening the ticket data.")

    add_heading(doc, "Table 1-A: Interview Summary", level=2)

    make_table(doc,
        ["Stakeholder", "What they told you", "What they appear not to know", "What to verify in the data"],
        [
            ["Marcus Adeyemi\nHead of Support",
             "500+ tickets/week, 6 agents. Avg first response 8–12 hrs vs 2-hr SLA. FCR 42% vs 65% industry benchmark. Escalation costs ~4× a resolved ticket. Tried hiring (short-lived) and canned responses (agents hated searching them). Primary fear: confidently wrong automated answers. Needs explainability for autumn compliance review. Enterprise customers have different SLA and will notice degraded service.",
             "Does not know ticket breakdown by category — admits he'd be 'guessing'. Does not know what proportion of escalations are tier-2-resolvable vs genuinely complex. Unaware of the non-fluent English volume issue.",
             "(1) Actual breakdown by intent category. (2) Proportion of escalations that are tier-1-resolvable. (3) Do non-fluent tickets have worse outcomes?"],
            ["Sofia Restrepo\nTier One Agent",
             "~70% of tickets are repeats she could answer without looking anything up. Bottleneck is finding and rewriting the answer, not knowing it. Documentation is good but keyword search fails — agents don't use it. Everyone maintains private snippet files. Non-fluent tickets take longer; she believes those have worst CSAT. Wants draft + relevant doc page, NOT auto-send without agent review.",
             "Whether non-fluent tickets statistically have worse CSAT (she believes this but it is an impression). How often her escalations could have been resolved at tier-1. That Daniel's tier-2 pipeline is 50% filled with tier-1-resolvable issues.",
             "(1) Do non-fluent tickets have materially worse FCR/CSAT? (2) Does the actual repeat rate match her 70% estimate? (3) Which intents most commonly reach her as repeats?"],
            ["Daniel Okonkwo\nTier Two Engineer",
             "~50% of escalations are tier-1-resolvable — a confidence or findability gap, not a knowledge gap. Escalations arrive with no context: just the raw original ticket forwarded. First thing he does is re-read the full thread and often re-asks something already asked. Would be 'twice as fast' with context: summary + relevant docs + what tier-1 was uncertain about. Risk: snippet files contain outdated answers that would scale mistakes if trained on.",
             "The overall FCR number Marcus watches. Whether the non-fluent issue Sofia describes is measurable. How much of his own time goes to context-gathering vs actual problem-solving.",
             "(1) What escalation rate does data show? (2) Which intents have highest escalation rates? (3) Are there intents where escalation rate is high despite docs availability?"],
            ["Ines Varga\nTechnical Writer",
             "29 KB articles covering: authentication, deployment, API, billing, data, security, account management. Internal team does not use them — agents reconstruct answers from memory. Root cause: keyword search fails on vocabulary mismatch (e.g. 'my deployment keeps dying' vs 'Resolving container health check failures'). Wants citation of which article an answer came from. Feature requests, roadmap, novel incidents have NO article.",
             "That agents don't use docs because search is broken (she thought Sofia was complaining about doc quality, not search). The quantified gap between agent answers and KB answers. The escalation-without-context problem Daniel describes.",
             "(1) What % of tickets are answerable from docs? (2) For intents with high doc-answerability, is escalation rate also high — meaning docs exist but aren't being reached?"],
            ["Ravi Menon\nCustomer (Business tier)",
             "Waits 8+ hrs routinely; finds answers himself in docs ~50% of the time. Accepts automation IF honest: cites source page, states uncertainty, identifies itself as automated. Urgency is asymmetric — documentation question can wait; failing deployment at 9am cannot. Business customers will notice if the enterprise–business service gap widens.",
             "Internal mechanics of why response is slow. The non-fluent language problem. The escalation-without-context problem (sees it as 'the waiting is the problem', not a context failure).",
             "(1) Is urgency correctly captured in ticket data? (2) Do high-urgency tickets have worse SLA compliance than low-urgency ones?"],
        ],
        col_widths=[1.3, 2.8, 2.0, 2.0]
    )

    add_heading(doc, "Table 1-B: Where the Accounts Disagree", level=2)
    add_callout(doc,
        "At least three disagreements run through the transcripts. Each is settled with ticket data — not by deciding whose account sounds more convincing.",
        bg="FEF9E7")

    make_table(doc,
        ["The disagreement", "Who says what", "How the data settles it", "What follows from the answer"],
        [
            ["Proportion of tickets that are repeat / answerable from docs",
             "Sofia estimates ~70% are questions she has answered before. Marcus admits he'd be 'guessing' about the breakdown.",
             "Data: 71.4% of tickets marked answerable_from_docs=True. Sofia's intuition is confirmed — most tickets already have KB answers.",
             "The problem is DELIVERY, not KNOWLEDGE. CloudServe does not lack answers; it lacks a way of reaching customers with answers that already exist. A generative chatbot misses the point."],
            ["Non-fluent English ticket outcomes",
             "Sofia believes non-fluent tickets have the worst CSAT and 'nobody has noticed'. Marcus has no data to confirm or deny.",
             "Data: Non-fluent CSAT = 3.04 vs Fluent CSAT = 2.95. Non-fluent FCR = 45.8% vs Fluent FCR = 43.2%. Sofia's belief is NOT confirmed — non-fluent outcomes are marginally better.",
             "Sofia likely experiences a per-ticket effort problem (more time per ticket) without that effort translating to worse outcomes. Vocabulary-mismatch retrieval still affects non-fluent more — monitor per-segment but don't over-engineer for v1."],
            ["What proportion of escalations are tier-1-resolvable",
             "Daniel says 'about half' of what reaches him could have been resolved at tier-1. Marcus sees only escalation rate, not the content of escalations.",
             "Data: Deployment_failure is 59% escalated but 70% doc-answerable. Authentication_failure: 70% doc-answerable. api_key_issue: 67% doc-answerable. These categories should NOT be escalating this often.",
             "Daniel's estimate is directionally correct. A significant portion of escalations involve issues WITH documentation answers. The confidence/findability gap is driving unnecessary escalations."],
            ["Enterprise vs standard service quality",
             "Ravi (business tier) says enterprise customers get answers in ~1 hr and will notice if gap widens. Marcus confirms different agreements but gives no gap detail.",
             "Data: Enterprise FCR = 37.3%, avg resolution = 484 min — WORSE than Standard (43.1% FCR, 442 min). Enterprise escalation rate = 62.7% vs Standard 56.9%.",
             "Enterprise customers already get the worst outcomes. This reflects ticket complexity, not tier priority. System should not claim to fix enterprise FCR — it helps standard/business most. Enterprise benefit comes from better escalation context."],
        ],
        col_widths=[1.6, 2.0, 2.5, 2.0]
    )

    add_heading(doc, "Table 1-C: What Nobody Mentioned", level=2)
    make_table(doc,
        ["What was never mentioned", "Why you would have expected it", "How you checked it"],
        [
            ["Volume of repeat contacts",
             "If 70% of tickets are answerable and FCR is only 44%, a significant portion of customers must be coming back. Nobody flagged this.",
             "Data: 21.6% of tickets (108/500) are repeat contacts. 1 in 5 tickets is a customer who did not get a sufficient answer on first contact."],
            ["The docs_comment channel",
             "Sofia, Daniel, and Ines all described documentation and search problems but none mentioned that a significant number of tickets arrive directly in documentation comments.",
             "Data: 15.6% of tickets arrive via docs_comment channel — people asking questions while reading docs. High-intent, specific questions — prime candidate for automated response."],
            ["The must_not_auto_respond safety flag",
             "Marcus described confidently wrong answers as a fear but did not enumerate which categories must always be blocked. Daniel mentioned security/billing but did not quantify.",
             "Data: 17.4% of tickets (87/500) have must_not_auto_respond=True. Includes security_incident, compliance_request, billing disputes, unclear_request. Hard-block required before any routing decision."],
            ["Ticket volume by urgency",
             "Marcus and Ravi both discussed urgency differently, but no one described what proportion of volume is actually high-urgency.",
             "Data: 29.2% high-urgency, 45.2% medium, 25.6% low. With 8–12 hr response times, nearly 1 in 3 tickets represents real customer harm, not just inconvenience."],
        ],
        col_widths=[2.0, 2.5, 3.6]
    )

    doc.add_page_break()

    # ── SECTION 2 ────────────────────────────────────────────────────────
    add_section_banner(doc, 2, "What the Ticket Data Shows",
                       "Count before you interpret. development_tickets.json — 500 tickets.")

    add_heading(doc, "Table 2-A: Ticket Data Measurements", level=2)
    make_table(doc,
        ["What to measure", "Figure", "Where it came from", "What surprised you"],
        [
            ["Total tickets in sample", "500", "development_tickets.json", "Large enough to be statistically meaningful across all 22 intent categories."],
            ["Split by channel", "Email: 212 (42.4%)\nChat: 155 (31.0%)\nDocs comment: 78 (15.6%)\nForum: 55 (11.0%)", "channel field", "Email dominates — also the channel with longest response time. Docs comments (15.6%) are significant and underappreciated — nobody in interviews mentioned them."],
            ["Split by intent category", "Even distribution across 22 classes (2.6%–5.8% each). Top: data_export 29 (5.8%), data_residency 29 (5.8%), rollback_request 28 (5.6%), deployment_failure 27 (5.4%).", "labels.intent", "No single dominant category — improvements must work broadly, not just target one intent."],
            ["Split by urgency", "High: 146 (29.2%)\nMedium: 226 (45.2%)\nLow: 128 (25.6%)", "labels.urgency", "Nearly 30% high-urgency. With 8–12 hr response times, this represents real customer harm — not inconvenience."],
            ["First contact resolution (FCR)", "43.8% (219/500)", "history.first_contact_resolution", "Very close to Marcus's stated 42% — he was accurate even when 'guessing'. Industry benchmark is 65% — a 21pp gap."],
            ["Average satisfaction rating", "2.97 / 5.0", "history.csat_rating", "Marcus quoted 3.2 in interview — actual data is worse. Below 3.0 out of 5."],
            ["Most frequent single intent", "data_export and data_residency tied (29 each, 5.8%)", "labels.intent count", "Less concentrated than expected. No single 'easy win' intent — broad improvements needed."],
            ["Proportion answerable from existing docs", "71.4% (357/500)", "labels.answerable_from_docs", "THE most important number. 71 in every 100 tickets could be resolved from the 29 existing KB articles. Problem is delivery, not content."],
            ["Proportion non-fluent + outcomes", "Non-fluent: 120 (24%)\nFCR: 45.8%, CSAT: 3.04\nFluent FCR: 43.2%, CSAT: 2.95", "language_fluency, history.*", "Sofia's belief that non-fluent tickets have worst outcomes is NOT confirmed. Non-fluent outcomes are marginally better. Effort cost may be higher without showing in outcome metrics."],
            ["Outcomes by customer tier", "Enterprise: FCR 37.3%, 484 min, 62.7% escalated\nBusiness: FCR 48.2%, 359 min, 51.8% escalated\nStandard: FCR 43.1%, 442 min, 56.9% escalated", "customer_tier, history.*", "Enterprise has the WORST FCR despite premium agreements. They have the most complex tickets. System must not further degrade enterprise experience."],
            ["Proportion that are repeat contacts", "21.6% (108/500)", "history.repeat_contact", "1 in 5 tickets is a customer coming back because first response was insufficient. Direct measure of FCR failure."],
            ["Safety-flagged tickets", "17.4% (87/500) must_not_auto_respond=True", "labels.must_not_auto_respond", "87 tickets must never be auto-responded. Must be hard-blocked before any routing decision — not after."],
            ["Escalation rate", "56.2% (281/500)", "history.escalated", "More than half of all tickets escalate to tier-2. Combined with 4× cost ratio, this is the primary financial lever."],
        ],
        col_widths=[1.8, 1.5, 1.5, 3.3]
    )

    doc.add_page_break()

    # ── SECTION 3 ────────────────────────────────────────────────────────
    add_section_banner(doc, 3, "Where the Time Actually Goes",
                       "Volume ≠ effort. Work out where the hours go, not just the ticket counts.")

    add_heading(doc, "Table 3-A: Effort vs Volume by Category", level=2)
    make_table(doc,
        ["Ticket category", "Share of volume", "Est. share of effort", "Why they differ", "Evidence"],
        [
            ["security_incident", "5.2% (26)", "~12%", "100% escalation, avg 786 min resolution — longest in dataset. Always escalated regardless of docs availability.", "Avg 786 min; escalation 100%"],
            ["compliance_request", "5.2% (26)", "~11%", "100% escalation, 679 min avg. Legal/regulatory implications require human judgement even when docs exist (65% answerable).", "Avg 679 min; escalation 100%"],
            ["feature_request", "4.0% (20)", "~9%", "100% escalation, 724 min avg. Zero docs-answerable. Generates discussion, product backlog entries, follow-ups.", "Avg 724 min; 0% answerable"],
            ["performance_degradation", "4.6% (23)", "~8%", "70% escalation, 543 min avg. Requires investigation of logs/infrastructure — high diagnosis time.", "Avg 543 min; 70% escalated"],
            ["unclear_request", "3.0% (15)", "~5%", "100% escalation, 516 min avg. Agent must first clarify what customer is asking — double pass before solving.", "Avg 516 min; 0% answerable"],
            ["authentication_failure + api_key_issue", "7.6% combined (38)", "~8%", "High repetition (Sofia's most-mentioned), high docs-answerability (67–70%). Time goes to FINDING the answer, not knowing it.", "Auth 70% answerable; api_key 67%"],
            ["deployment_failure + rollback_request", "11.0% combined (55)", "~10%", "High volume, 59–75% answerable from docs. Should be high-yield RAG targets — currently over-escalated.", "Deployment 70% answerable; rollback 75%"],
            ["billing_query + quota_or_overage", "9.4% combined (47)", "~6%", "High doc-answerability (87–88%) but billing disputes must never be auto-responded — Daniel: 'those become contractual quickly'.", "88% answerable but safety-flagged"],
        ],
        col_widths=[1.8, 0.9, 0.9, 2.5, 2.0]
    )

    add_heading(doc, "Table 3-B: Steps an Agent Takes on a Typical Ticket", level=2)
    add_callout(doc, "Reconstructed from Sofia's account (Interview 2). The steps that sound trivial are where the minutes accumulate.", bg="EBF3FB")
    make_table(doc,
        ["Step", "What the agent does", "Roughly how long", "Could this be automated?"],
        [
            ["1", "Open queue, sort by age (oldest-first to avoid SLA breach)", "1–2 min per session", "No — humans judge severity. System can flag urgency but should not reorder human work."],
            ["2", "Read ticket, understand intent. Non-fluent tickets: interpret intent before answering.", "1–3 min (simple) to 10+ min (ambiguous/non-fluent)", "Partially — classification reduces cognitive load. Cannot fully automate interpretation."],
            ["3", "Search docs for answer. In practice: SKIP SEARCH, open personal snippet file instead (keyword search fails on vocabulary mismatch).", "2–5 min (snippet) to 15+ min (if actually searching docs)", "YES — HIGH VALUE. Semantic/embedding search removes the vocabulary mismatch barrier. Most reclaimed time lives here."],
            ["4", "Write or adapt the answer. Copy from snippet, rewrite for this customer.", "2–5 min", "Partially — HIGH VALUE. System drafts a grounded answer from retrieved docs, agent reviews. Sofia: 'That would save me half of every ticket.'"],
            ["5", "Decide to send or escalate. If escalating: forward raw original ticket — no summary, no context.", "1–2 min", "Partially. Routing automated with confidence threshold. Escalation context packet (summary + retrieved docs + uncertainty) can be generated — addresses Daniel's complaint."],
            ["6", "Handle follow-up if answer was wrong or unclear.", "10–40 min", "YES (preventive). Better first-contact answers reduce step 6 entirely. 21.6% repeat contact rate = 108 tickets that represent step 6 work."],
        ],
        col_widths=[0.4, 2.2, 1.4, 4.1]
    )

    doc.add_page_break()

    # ── SECTION 4 ────────────────────────────────────────────────────────
    add_section_banner(doc, 4, "What the Client Counts as Success",
                       "You cannot improve a number nobody is watching.")

    add_heading(doc, "Table 4-A: Success Metrics", level=2)
    make_table(doc,
        ["Measure", "Who watches it", "Current value", "What they would call success", "Confidence"],
        [
            ["First contact resolution (FCR)", "Marcus (primary), executive team", "43.8% (data) / 42% (Marcus)", "60%+ (industry benchmark 65%). Marcus: 'FCR, if I am being honest, more than response time.'", "High — both interview and data consistent"],
            ["Average first response time", "Marcus, customers (SLA)", "8–12 hours", "Under 2 hours (SLA target). Ravi would accept sub-1-hour for doc queries.", "High — consistent across Marcus and Ravi"],
            ["Escalation rate", "Marcus (indirectly, via cost)", "56.2%", "30% or lower. At 4× cost per escalation, each percentage point is financially material.", "Medium — Marcus cited cost ratio, not a target rate"],
            ["Customer satisfaction (CSAT)", "Marcus (reports to exec team)", "2.97/5.0 (data) / 3.2/5.0 (Marcus)", "4.0+ for meaningful improvement. Marcus's exact threshold unstated.", "Medium — Marcus's figure is slightly optimistic vs data"],
            ["Repeat contact rate", "Not currently tracked", "21.6%", "Halved to ~10%. Implied by FCR improvement — worth introducing as a new metric.", "Low — not on Marcus's dashboard today"],
            ["Explainability of decisions", "Marcus (compliance review)", "None (no current decision log)", "Every automated decision must have a logged, human-readable reason. Autumn compliance deadline.", "High — Marcus was explicit"],
            ["Consistency across tiers", "Ravi (customer), implicitly Marcus", "Enterprise FCR 37.3% is worst", "Variation between tiers should not increase. Current gap already concerning.", "Medium — Ravi's concern; data confirms issue exists"],
        ],
        col_widths=[1.8, 1.3, 1.3, 2.4, 1.3]
    )

    add_heading(doc, "Table 4-B: The Sentence Test", level=2)
    add_callout(doc, "Complete each sentence using only figures you have already recorded. If you cannot complete it, discovery is not finished.", bg="FEF9E7")
    make_table(doc,
        ["Prompt", "Your answer"],
        [
            ["This project will have been worth doing if, within three months of launch...",
             "FCR rises from 44% to 60%+, first response time falls below 2 hours for auto-responded tickets, and repeat contact rate falls from 22% to 10% or below."],
            ["We will know it did not work if we see...",
             "A confidently wrong automated answer screenshotted and circulated publicly by an engineer-customer; or if agent workload increases because they are handling corrections to auto-responses; or if escalation rate rises rather than falls."],
            ["The measure the client will actually be judged on internally is...",
             "First contact resolution. Marcus: 'FCR, if I am being honest, more than response time. Response time is what is in the agreement so it is what gets reported.'"],
        ],
        col_widths=[2.5, 5.6]
    )

    doc.add_page_break()

    # ── SECTION 5 ────────────────────────────────────────────────────────
    add_section_banner(doc, 5, "Data, Constraints and Risk",
                       "Everything you build depends on data that already exists.")

    add_heading(doc, "Table 5-A: Data Sources", level=2)
    make_table(doc,
        ["Data source", "What it contains", "Quality and gaps", "Access constraints", "Private data?"],
        [
            ["Support tickets\n(development_tickets.json)",
             "500 labelled tickets: channel, subject, body, customer tier, region, language fluency, intent, urgency, expected_route, answerable_from_docs, FCR, CSAT, resolution_time, escalated, repeat_contact.",
             "High quality — all fields populated, labels consistent. Real deployment would have missing fields and noise.",
             "None in this project. Real: GDPR — customer names and account IDs present; must not appear in logs or outbound responses.",
             "YES — customer_name, customer_id, customer_region. Must never appear in outbound responses."],
            ["Knowledge base\n(documentation.json)",
             "29 articles: title, category, body, doc_id. Categories: authentication, deployment, api, performance, billing, data, security, account, integration, onboarding.",
             "Reviewed by Ines — current and accurate within review cycle. Gap: feature requests, roadmap, novel incidents have NO article. Vocabulary may not match customer language.",
             "None. Private snippet files are OUT OF SCOPE (Daniel's warning: stale answers).",
             "No — documentation is intentionally public-facing."],
            ["Ground truth responses\n(ground_truth_responses.json)",
             "200 reference answers: required points, must_not_contain, expected_doc_ids. Written by senior agents.",
             "High quality — written by experienced humans. Covers 200 of 500 development tickets only.",
             "Must be held back — only used to evaluate, never to train (would overfit to visible data).",
             "No."],
            ["Customer records",
             "Customer tier, region, account identifiers derived from ticket data.",
             "Derived from ticket fields — no separate CRM access.",
             "GDPR-relevant — tier data can inform routing; PII must not appear in outbound responses.",
             "Yes — customer_name, customer_id are PII."],
            ["Agents' personal snippet files",
             "Answers written by agents outside the official KB.",
             "Not reviewed, some outdated. Daniel: 'Some answers in snippet files were correct two years ago and have not been right since.'",
             "Not in dataset — intentionally excluded.",
             "Unknown — likely yes."],
        ],
        col_widths=[1.5, 2.2, 1.8, 1.8, 0.8]
    )

    add_heading(doc, "Table 5-B: Initial Risk Register", level=2)
    make_table(doc,
        ["What could go wrong", "Likelihood", "Severity", "Who it affects", "First thought on preventing it"],
        [
            ["System answers confidently and incorrectly", "Medium", "Very High", "All customers; CloudServe reputation", "Grounding guardrail: every claim must trace to a retrieved passage. Confidence threshold 0.80 — below threshold, escalate. Citation required in every response."],
            ["Private data (PII) appears in outbound response", "Low", "Very High", "Affected customer; CloudServe (GDPR)", "PII guardrail: scan every outbound response for emails, account numbers, names, API keys before sending. Block and escalate if detected."],
            ["Some customer groups consistently get worse answers", "Medium", "High", "Non-fluent customers, enterprise tier", "Monitor performance per-segment continuously. Alert if any segment drops >5pp below overall average. Embed customer tier and urgency in routing context."],
            ["Documentation goes out of date; system retrieves stale answers", "Medium", "High", "All customers receiving answers from affected article", "Log which doc_id answered each ticket — Ines can audit. Flag articles not reviewed in >90 days."],
            ["Model provider (OpenRouter) unavailable", "Low", "High", "All customers", "Graceful degradation: if provider unavailable, route ALL tickets to escalate. Never surface a provider error to a customer."],
            ["Prompt injection — ticket text hijacks system instructions", "Low", "Very High", "Any customer receiving poisoned response", "Injection guardrail: scan ticket body for instruction-override patterns. Treat all ticket text as untrusted input — never inject directly into system prompt."],
            ["Confidence scores poorly calibrated — auto-responds when it should escalate", "Medium", "High", "All auto-responded customers", "Calibration check: group predictions by confidence band (0.5–0.6 etc.) and verify observed accuracy matches. Adjust threshold based on data, not assumption."],
        ],
        col_widths=[2.0, 0.8, 0.8, 1.5, 3.0]
    )

    doc.add_page_break()

    # ── SECTION 6 ────────────────────────────────────────────────────────
    add_section_banner(doc, 6, "The Problem Statement",
                       "Now, and only now. Every clause must be supported by a row in Sections 1–5.")

    add_heading(doc, "Table 6-A: Problem Statement Elements", level=2)
    make_table(doc,
        ["Element", "Your statement", "Supporting evidence (section and row)"],
        [
            ["What the client asked for",
             "A chatbot to handle support tickets.",
             "Marcus interview: 'I picture it answering the easy ones so my people can do the hard ones.'"],
            ["What the evidence suggests they actually need",
             "A retrieval system that surfaces existing documentation answers reliably, combined with a context-enriched escalation pipeline that gives tier-2 engineers what they need to resolve complex tickets faster.",
             "Section 2, Table 2-A: 71.4% of tickets already answerable from KB. Section 3, Table 3-B Step 3: agents skip docs because keyword search fails. Daniel interview: escalations arrive without context, adding 15–30 min of re-reading."],
            ["The gap between those two",
             "A generative chatbot would add hallucination risk on top of a delivery problem. The answers already exist. The failure is that agents cannot find them quickly, and escalations arrive stripped of context that tier-2 needs to act.",
             "Table 1-B Row 1: data confirms Sofia's 70% estimate. Section 3 Step 3: agents use snippet files as workaround. Daniel: 'If an escalation arrived with context, I would be twice as fast.'"],
            ["Who is affected and how",
             "6 tier-1 agents spend most of their time finding and rewriting answers they already know. Tier-2 engineers spend the first 15–30 min of every escalation reconstructing context. 500+ customers per week wait 8–12 hrs; 22% contact a second time because the first response was insufficient. Enterprise customers paradoxically get the worst FCR (37.3%) despite premium agreements.",
             "Marcus: 8–12 hr avg vs 2-hr SLA. Data: 43.8% FCR, 2.97/5 CSAT, 21.6% repeat contact, enterprise FCR 37.3% (Section 2, Table 2-A)."],
            ["What will change if this is solved",
             "FCR rises to 60%+, first response time falls below 2 hrs for the 71% of doc-answerable tickets, escalation rate falls from 56% toward 30%, tier-2 handles only genuinely complex tickets (with context pre-attached), and repeat contact rate halves.",
             "Table 4-B Sentence Test. Marcus: 4× cost of escalation vs resolution — a 26pp drop in escalation rate recovers significant cost."],
            ["What is explicitly not in scope",
             "Answering feature requests, roadmap questions, or novel incidents (no KB article exists). Automating responses to security incidents, billing disputes, or compliance requests (must_not_auto_respond = 17.4%). Building a new knowledge base (Ines's 29 articles are sufficient; private snippet files must not be used). Replacing human agents.",
             "Ines: 'Feature requests — obviously, since there is no answer to retrieve.' Data: 17.4% safety-flagged. Daniel: 'Billing becomes contractual; security must always escalate.'"],
        ],
        col_widths=[1.5, 3.8, 2.8]
    )

    add_heading(doc, "Table 6-B: One-Paragraph Problem Statement", level=2)
    add_callout(doc,
        "Write in language the Head of Support would recognise and agree with. No technical vocabulary. "
        "If you cannot express the problem without mentioning retrieval or embeddings, you are describing your solution, not their problem.",
        bg="FEF9E7")

    prob_table = doc.add_table(rows=1, cols=1)
    prob_table.style = "Table Grid"
    cell = prob_table.cell(0, 0)
    set_cell_bg(cell, "F0F7FF")
    p = cell.paragraphs[0]
    run = p.add_run(
        "CloudServe's support function receives more than 500 tickets a week and takes 8–12 hours to reply, "
        "against a two-hour service agreement. First contact resolution sits at 44%, which means more than half "
        "of all tickets escalate to tier-2 at roughly four times the cost. The root cause is not a shortage of "
        "answers: 71% of tickets can already be answered from the 29 articles in the existing knowledge base. "
        "The failure is delivery. Agents cannot reach those articles through keyword search because customers do "
        "not phrase problems in documentation vocabulary, so every agent has built a private workaround file. "
        "When they do escalate, the escalation arrives without context, so tier-2 engineers spend 15–30 minutes "
        "reconstructing what was already asked before they can act. What CloudServe needs is not a system that "
        "generates new answers; it is one that reliably retrieves the answers that already exist and presents them "
        "to agents as a grounded, citable draft — and that packages escalations with enough context for tier-2 "
        "engineers to act immediately."
    )
    run.font.size = Pt(10)
    doc.add_paragraph()

    add_heading(doc, "Self-Check Before Moving to Stage 2 (PRD)", level=2)
    checks = [
        "✅  Marcus would recognise this — FCR is his number, explainability is his requirement",
        "✅  Sofia would recognise this — snippet-file workaround, findability problem, draft-not-auto-send model",
        "✅  Daniel would recognise this — context-enriched escalations, tier-1-resolvable escalations",
        "✅  Ines would recognise this — retrieval from her 29 articles, citation requirement, private files excluded",
        "✅  Ravi would recognise this — honest automated response, citations, urgency asymmetry acknowledged",
        "✅  Every claim in the problem statement is supported by a numbered table row above",
        "✅  Three key disagreements are resolved with data (not interview preference)",
        "✅  Problem statement does not mention embeddings, retrieval, or LLMs — it describes the business problem",
    ]
    for c in checks:
        p = doc.add_paragraph(c)
        p.paragraph_format.left_indent = Inches(0.3)
        p.runs[0].font.size = Pt(10)

    path = os.path.join(OUTPUT_DIR, "Stage_1_Discovery_Workbook_Filled.docx")
    doc.save(path)
    print(f"✅  Saved: {path}")
    return path


# ═══════════════════════════════════════════════════════════════════════════
# DOCUMENT 2: Stage 2 — Product Requirements Document v1
# ═══════════════════════════════════════════════════════════════════════════

def build_prd():
    doc = Document()

    section = doc.sections[0]
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    # Cover
    doc.add_paragraph()
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tr = title_p.add_run("FORWARD DEPLOYED AI ENGINEERING")
    tr.font.size = Pt(14)
    tr.font.bold = True
    tr.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_p.add_run("Capstone Project  ·  Product Requirements Document  ·  Version 1.0").font.size = Pt(12)

    meta_p = doc.add_paragraph()
    meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    mr = meta_p.add_run("CloudServe Solutions  |  Week 1, Day 4  |  Status: DRAFT")
    mr.font.size = Pt(10)
    mr.font.color.rgb = RGBColor(0x2E, 0x86, 0xAB)

    doc.add_paragraph()
    add_callout(doc,
        "Document control: Every requirement has a unique ID (FR-xx or NFR-xx). "
        "Every requirement references the discovery evidence row that produced it. "
        "Traceability chain: Discovery evidence → Requirement ID → Specification/Prompt → Code.",
        bg="EBF3FB")

    doc.add_page_break()

    # ── SECTION A: DOCUMENT CONTROL ──────────────────────────────────────
    add_section_banner(doc, "A", "Document Control")
    make_table(doc,
        ["Field", "Value"],
        [
            ["Document title", "CloudServe Intelligent Support System — Product Requirements Document"],
            ["Version", "1.0 (initial)"],
            ["Status", "Draft — Week 1 Day 4"],
            ["Author", "Nishchay Gupta"],
            ["Date created", "7 November 2026"],
            ["Last updated", "7 November 2026"],
            ["Next scheduled revision", "After Week 2 Day 5 gate run (Stage 5: PRD Revision Log)"],
            ["Discovery evidence source", "docs/Stage_1_Discovery_Workbook_Filled.md (and .docx)"],
        ],
        col_widths=[2.0, 6.1]
    )

    # ── SECTION B: THE PROBLEM ────────────────────────────────────────────
    add_section_banner(doc, "B", "The Problem",
                       "From Stage 1 discovery — every sentence here is traceable to Section 6 of the Discovery Workbook.")

    p = doc.add_paragraph(
        "CloudServe Solutions receives more than 500 support tickets per week with 6 agents, "
        "achieving an average first response time of 8–12 hours against a 2-hour SLA commitment. "
        "First contact resolution (FCR) is 43.8% against an industry benchmark of 65%. "
        "56.2% of tickets escalate to tier-2 at approximately 4× the cost of a resolved ticket. "
        "21.6% of tickets are repeat contacts — customers who did not receive a sufficient first response."
    )
    p.runs[0].font.size = Pt(10)

    p2 = doc.add_paragraph(
        "Ticket data analysis reveals that 71.4% of incoming tickets are already answerable from the 29 articles "
        "in CloudServe's existing knowledge base. The problem is not a shortage of answers; it is that agents "
        "cannot reliably reach those answers because keyword search fails on vocabulary mismatch (customers phrase "
        "problems differently from documentation titles). Agents work around this with personal, unreviewed snippet "
        "files. Escalations arrive at tier-2 without context — just the raw original ticket forwarded — causing "
        "tier-2 engineers to spend 15–30 minutes reconstructing context before acting."
    )
    p2.runs[0].font.size = Pt(10)
    doc.add_paragraph()

    # ── SECTION C: USER GROUPS ────────────────────────────────────────────
    add_section_banner(doc, "C", "User Groups and Their Goals")
    make_table(doc,
        ["User group", "Primary goal", "Current pain", "Key quote"],
        [
            ["Tier-1 Support Agent (Sofia)", "Answer tickets accurately and quickly without creating rework", "Spends most time FINDING answers she already knows; personal snippet file is the only usable workaround", "'If it hands me a ticket with a draft and the relevant page attached, that would genuinely help. That would save me half of every ticket.'"],
            ["Tier-2 Support Engineer (Daniel)", "Handle genuinely complex escalations efficiently", "Escalations arrive without context — 15–30 min lost reconstructing what was already asked", "'If I had context, I would be twice as fast. I do not need it to be right. I need it to show its working.'"],
            ["Head of Support (Marcus)", "FCR ≥60%, response time <2 hrs, explainable decisions for compliance", "Reporting red numbers for 2 quarters; unable to explain decisions to compliance reviewers", "'I would rather it said nothing than said something wrong.'"],
            ["Customer (Ravi, Business tier)", "Get fast, accurate, honest answers — especially for high-urgency issues", "Waits 8+ hrs; finds answers himself in docs 50% of the time", "'If it says here is what I think, here is the page it came from, and a person will confirm — that is useful.'"],
            ["Technical Writer (Ines)", "Maintain accurate documentation; understand when and where it is used", "Does not know which articles the system uses or whether article errors vs system errors are causing wrong answers", "'I would want to know which article an answer came from, so I can tell whether the article is wrong or the system misread it.'"],
        ],
        col_widths=[1.6, 1.7, 2.1, 2.7]
    )

    doc.add_page_break()

    # ── SECTION D: FUNCTIONAL REQUIREMENTS ───────────────────────────────
    add_section_banner(doc, "D", "Functional Requirements",
                       "FR-01 through FR-15. Every requirement references its discovery evidence.")

    add_heading(doc, "D1: Ingestion (Channels)", level=2)
    make_table(doc,
        ["ID", "Requirement", "Acceptance criterion", "Discovery evidence"],
        [
            ["FR-01", "The system MUST accept tickets from all four channels: email, live chat, API documentation comments, and community forum.", "All four channel types present in the evaluation set are processed without error.", "Data: email 42.4%, chat 31.0%, docs_comment 15.6%, forum 11.0% (Section 2, Table 2-A)."],
            ["FR-02", "The system MUST normalise all tickets into a single internal representation regardless of channel of origin.", "A normalised ticket from any channel contains: ticket_id, channel, subject, body, received_at, customer_id, customer_tier, customer_region, language_fluency.", "Ingest module requirement — downstream components must not contain channel-specific logic. Architecture decision."],
        ],
        col_widths=[0.7, 2.5, 2.3, 2.6]
    )

    add_heading(doc, "D2: Classification", level=2)
    make_table(doc,
        ["ID", "Requirement", "Acceptance criterion", "Discovery evidence"],
        [
            ["FR-03", "The system MUST classify every ticket with one of 22 intent classes.", "Classification precision ≥85% per class on the validation set (confusion matrix provided).", "Data: 22 intent categories identified in ticket corpus. Marcus and Sofia both describe needing to know 'what kind of ticket' before acting."],
            ["FR-04", "The system MUST assign urgency (high / medium / low) to every ticket.", "Urgency assigned and logged for 100% of processed tickets.", "Data: 29.2% high-urgency. Ravi: 'Waiting matters differently by urgency.' Marcus needs priority routing."],
            ["FR-05", "The classification MUST produce a calibrated confidence score 0.0–1.0. Confidence bands (0.5–0.6, 0.6–0.7 etc.) must be accurate within 5 percentage points of observed accuracy.", "Calibration check run as part of evaluation: stated confidence in each band within 5pp of measured accuracy.", "Marcus: 'I would rather it said nothing than said something wrong.' Routing threshold is only meaningful if confidence is calibrated."],
        ],
        col_widths=[0.7, 2.5, 2.3, 2.6]
    )

    add_heading(doc, "D3: Retrieval", level=2)
    make_table(doc,
        ["ID", "Requirement", "Acceptance criterion", "Discovery evidence"],
        [
            ["FR-06", "The system MUST perform semantic search over the 29 knowledge base articles using embedding-based retrieval (all-MiniLM-L6-v2).", "A query using customer vocabulary (e.g. 'my deployment keeps dying') returns the correct KB article (e.g. DOC-DEPLOY-001). Each returned passage resolves to a real document ID.", "Ines: keyword search fails on vocabulary mismatch. Section 3, Table 3-B Step 3: this is where the most time is wasted. 71.4% of tickets answerable from existing KB."],
            ["FR-07", "Retrieval MUST return an empty list when no article is sufficiently relevant. Returning irrelevant passages is worse than returning nothing.", "When triggered with a query about a topic with no KB article (e.g. feature request), retrieval returns empty list and system escalates.", "Ines: 'Feature requests — obviously, since there is no answer to retrieve.' System must recognise the absence of content."],
        ],
        col_widths=[0.7, 2.5, 2.3, 2.6]
    )

    add_heading(doc, "D4: Routing", level=2)
    make_table(doc,
        ["ID", "Requirement", "Acceptance criterion", "Discovery evidence"],
        [
            ["FR-08", "The system MUST check the must_not_auto_respond flag before any routing decision. Any ticket with this flag set to True MUST be escalated, regardless of confidence score.", "100% of must_not_auto_respond=True tickets in the evaluation set are routed to escalate. Zero violations.", "Data: 17.4% of tickets safety-flagged. Daniel: security, billing disputes, data residency must always escalate. Safety check must be first — not last."],
            ["FR-09", "The system MUST route tickets using a confidence threshold. Tickets with confidence ≥ threshold AND relevant passages found AND not safety-flagged are auto-responded. All others are escalated.", "Same input ticket always produces same routing decision (deterministic). Threshold value logged with every decision.", "Marcus: 'I would rather it said nothing than said something wrong.' Threshold value 0.80 as starting point — to be justified with evaluation data."],
            ["FR-10", "Escalated tickets MUST carry a context packet containing: (a) 2-sentence summary of the ticket, (b) retrieved documentation passages with doc_ids, (c) human-readable reason why the system was not confident.", "100% of escalated tickets in evaluation set have a context packet with all three components populated.", "Daniel: 'If an escalation arrived with context I would be twice as fast.' Currently escalations are just raw ticket forwards — this is a first-class feature, not an afterthought."],
        ],
        col_widths=[0.7, 2.5, 2.3, 2.6]
    )

    add_heading(doc, "D5: Generation", level=2)
    make_table(doc,
        ["ID", "Requirement", "Acceptance criterion", "Discovery evidence"],
        [
            ["FR-11", "Generated responses MUST cite the specific KB article(s) used, with doc_id inline. Citations must resolve to actually-retrieved passages — never hallucinated references.", "Citation accuracy ≥95%: each citation checked against the passage it supports. Hallucination rate ≤5% on 50+ sampled responses assessed by two independent reviewers.", "Ines: 'I would want to know which article an answer came from.' Ravi: 'Here is the page it came from — that is useful.' Both require citation transparency."],
            ["FR-12", "The system MUST NOT generate a response when no relevant passages were retrieved. If passages are empty, the request must be routed to escalate before generation is called.", "ValueError raised and ticket escalated if generate_response() is called with empty passages. Zero hallucinated responses on tickets with no KB match.", "Ines: topics with no article must not be manufactured. Grounding guardrail requirement."],
        ],
        col_widths=[0.7, 2.5, 2.3, 2.6]
    )

    add_heading(doc, "D6: Guardrails", level=2)
    make_table(doc,
        ["ID", "Requirement", "Acceptance criterion", "Discovery evidence"],
        [
            ["FR-13", "Guardrail 1 (PII): The system MUST scan every outbound response for PII (names, addresses, account numbers, API keys, email addresses). Detection MUST block the response and escalate.", "Zero PII violations in any evaluation set run. Triggered test with PII-containing response confirms block.", "Marcus: explainability and compliance. GDPR: customer_name and customer_id present in ticket data — must never appear in outbound responses."],
            ["FR-14", "Guardrail 2 (Grounding): Every factual claim in an outbound response MUST be traceable to a retrieved passage. Ungrounded claims MUST cause the response to be blocked and escalated.", "Hallucination rate ≤5% (Section NFR-04). Engineered trigger ticket (question with no relevant passage) confirms block.", "Marcus primary fear: 'confidently incorrect answer'. Ravi: 'I will act on it and break something.' Both require grounding."],
            ["FR-15", "Guardrail 3 (Injection): The system MUST detect attempts to override system instructions within ticket text (prompt injection). Detection MUST block and log the attempt.", "Engineered prompt-injection ticket is blocked and logged. Zero injection successes in evaluation set.", "Security requirement — tickets are untrusted user input. System must never treat ticket body as trusted instructions."],
            ["FR-16", "Guardrail 4 (Tone/Scope): Responses MUST NOT contain commitments about refunds, timelines, SLA exceptions, or billing adjustments. Detection MUST block the response.", "Engineered trigger with refund commitment confirms block. Zero commitment violations in evaluation set.", "Daniel: 'Billing disputes become contractual quickly — nothing automated should make commitments about money.'"],
            ["FR-17", "Guardrail 5 (Confidence Floor): The system MUST verify that the routing threshold was applied before auto-responding. If a response is sent without the threshold check, it MUST be escalated.", "Bypass test confirms guardrail 5 catches and escalates any response where threshold was not applied.", "Governance requirement — audit trail must show threshold was actually applied, not just configured."],
        ],
        col_widths=[0.7, 2.5, 2.3, 2.6]
    )

    add_heading(doc, "D7: Decision Logging", level=2)
    make_table(doc,
        ["ID", "Requirement", "Acceptance criterion", "Discovery evidence"],
        [
            ["FR-18", "EVERY automated decision MUST be written to a persistent SQLite log with the required schema (decision_id, timestamp, ticket_id, stage, model, prediction + confidence, sources_used, threshold_applied, action_taken, reason, guardrail_results, prompt_version, requirement_ids).", "count_decisions() == total tickets processed in any evaluation run. Logged decisions must match processed tickets exactly — including failures and escalations.", "Marcus: compliance review requires every automated decision to have a logged, human-readable reason. Autumn deadline. Governance requirement."],
        ],
        col_widths=[0.7, 2.5, 2.3, 2.6]
    )

    doc.add_page_break()

    # ── SECTION E: NON-FUNCTIONAL REQUIREMENTS ────────────────────────────
    add_section_banner(doc, "E", "Non-Functional Requirements",
                       "NFR-01 through NFR-08.")
    make_table(doc,
        ["ID", "Category", "Requirement", "Target", "Discovery evidence"],
        [
            ["NFR-01", "Latency", "95th-percentile end-to-end response latency for auto-responded tickets", "<3 seconds", "Ravi: wants near-immediate first response for high-urgency issues. Marcus: current 8–12 hr response is the SLA breach."],
            ["NFR-02", "Availability", "System availability during operating hours", "≥99.5%", "SLA obligation. Marcus: current SLA breach; system must not introduce additional downtime."],
            ["NFR-03", "Intent precision", "Classification precision per intent class on validation set", "≥85% per class", "Routing quality depends on classification. At <85%, the wrong tickets get auto-responded."],
            ["NFR-04", "Hallucination rate", "Proportion of auto-responses containing claims not supported by retrieved passages, assessed by two independent reviewers on ≥50 samples", "≤5%", "Marcus primary fear. Ravi: 'I will act on it and break something.' Must be measured, not assumed."],
            ["NFR-05", "Citation accuracy", "Proportion of citations that resolve to the actual retrieved passage that supports the claim", "≥95%", "Ines: citations must identify which article — she needs this to audit article quality vs system quality."],
            ["NFR-06", "PII in responses", "Number of outbound responses containing PII (names, account numbers, API keys)", "Zero occurrences", "GDPR obligation. Any PII in outbound response is a reportable breach."],
            ["NFR-07", "Fairness — tier consistency", "Variation in FCR across customer tiers (enterprise vs business vs standard)", "<5 percentage points gap increase vs baseline", "Ravi: 'If this change makes that gap bigger, we will notice, and it will come up at renewal.' Enterprise already at 37.3% FCR vs 48.2% business."],
            ["NFR-08", "Fairness — language consistency", "Variation in auto-respond accuracy between fluent and non-fluent English tickets", "<5 percentage points", "Section 1, Table 1-B Row 2: Sofia's concern. Data did not confirm worse outcomes but vocabulary mismatch still affects retrieval — monitor from day 1."],
            ["NFR-09", "Decision log coverage", "All automated decisions logged — including failures and escalations", "100% coverage (count_decisions() == tickets_processed)", "Marcus: compliance review. Governance requirement. A decision log that only covers successes is not an audit trail."],
            ["NFR-10", "Confidence calibration", "Stated confidence within 5 percentage points of observed accuracy per confidence band", "Within 5pp per band", "Routing threshold is meaningless if confidence scores don't reflect actual probability of being correct."],
        ],
        col_widths=[0.7, 1.2, 2.4, 1.2, 2.6]
    )

    doc.add_page_break()

    # ── SECTION F: OUT OF SCOPE ────────────────────────────────────────────
    add_section_banner(doc, "F", "Out of Scope",
                       "Explicitly excluded from this version — not as omissions, but as deliberate decisions.")
    make_table(doc,
        ["What is excluded", "Why excluded", "Discovery evidence"],
        [
            ["Answering feature requests, roadmap questions, or novel incidents",
             "No KB article exists to retrieve from. System must escalate these, not manufacture an answer.",
             "Ines: 'Feature requests — obviously, since there is no answer to retrieve. Anything about roadmap or timing. Genuinely novel incidents.'"],
            ["Auto-responding to security incidents, billing disputes, compliance requests",
             "17.4% of tickets safety-flagged must_not_auto_respond=True. These have contractual, legal, or security implications.",
             "Data: 87/500 tickets safety-flagged. Daniel: 'Billing becomes contractual; security must always escalate.'"],
            ["Training on or retrieving from agents' personal snippet files",
             "Snippet files are unreviewed and contain known-stale answers.",
             "Daniel: 'Some answers were correct two years ago and have not been right since. If you learn from those you will scale up a mistake.'"],
            ["Replacing human agents",
             "Automation augments agent capacity — it does not replace agents. Sofia and Marcus both framed this as a draft/assist model.",
             "Sofia: 'If it hands me a ticket with a draft and the relevant page attached, that would genuinely help.' NOT auto-send without review for all tickets."],
            ["Customer-facing chatbot interface",
             "The primary interface is agent-assist — a drafted response the agent reviews before sending. Customer-facing direct response is a future phase.",
             "Marcus: primary fear is confidently wrong answer reaching customer. Agent review is a guardrail against this in v1."],
            ["Multi-language response generation",
             "The system retrieves from English documentation and drafts in English. Non-English response generation requires translation pipeline outside scope of v1.",
             "Section 1, Table 1-C: non-fluent issue noted but not confirmed as acute. Translation adds complexity; excluded from v1."],
        ],
        col_widths=[2.0, 3.0, 3.1]
    )

    doc.add_page_break()

    # ── SECTION G: ASSUMPTIONS + CONSEQUENCES ─────────────────────────────
    add_section_banner(doc, "G", "Assumptions and Consequences If Wrong")
    make_table(doc,
        ["Assumption", "Consequence if wrong", "How to detect"],
        [
            ["The 29 KB articles will remain current and reviewed by Ines throughout the project.",
             "System retrieves stale content; answer quality degrades silently and is hard to detect.",
             "Log doc_id and last_reviewed date per decision. Alert if article >90 days since review."],
            ["The confidence threshold of 0.80 will produce acceptable routing decisions.",
             "Threshold too high → system over-escalates (less value to agents). Threshold too low → auto-responds on uncertain cases (more wrong answers).",
             "Evaluate routing accuracy on validation set. Run calibration check. Adjust threshold based on data in Week 2 Day 5."],
            ["OpenRouter free tier provides sufficient capacity for this workload.",
             "Rate limiting causes timeouts; harness fails to process all tickets unattended.",
             "Test harness against full 80-ticket validation set by end of Week 2 Day 5. Rate limit errors will appear in logs."],
            ["The all-MiniLM-L6-v2 embedding model will capture sufficient semantic similarity for retrieval.",
             "Vocabulary mismatch problem persists despite semantic search; retrieval quality is poor.",
             "Test with 20 known-question/known-article pairs. Recall should be >90%."],
            ["Enterprise tickets are more complex by nature, explaining their worse FCR — not poor service.",
             "If enterprise FCR is actually driven by service failure (not complexity), the current design won't help enterprise customers.",
             "Compare FCR for enterprise tickets that ARE answerable from docs vs those that are not. If doc-answerable enterprise tickets still have poor FCR, the problem is not complexity."],
        ],
        col_widths=[2.3, 2.5, 3.3]
    )

    doc.add_page_break()

    # ── SECTION H: SUCCESS MEASURES ──────────────────────────────────────
    add_section_banner(doc, "H", "Success Measures",
                       "All figures from Section 4 of the Discovery Workbook.")
    make_table(doc,
        ["Measure", "Baseline", "Target", "How measured", "Who owns"],
        [
            ["First contact resolution (FCR)", "43.8%", "≥60%", "history.first_contact_resolution in evaluation set; business outcome reported in evaluation harness", "Marcus"],
            ["Average first response time", "8–12 hours", "<2 hours for auto-responded tickets\n<5 minutes for auto-responded", "history.resolution_time_minutes for auto-responded subset", "Marcus / SLA"],
            ["Escalation rate", "56.2%", "≤30%", "history.escalated in evaluation set", "Marcus (cost)"],
            ["Customer satisfaction (CSAT)", "2.97/5.0", "≥4.0/5.0", "history.csat_rating in evaluation set (proxy measure — state sample size and method)", "Marcus"],
            ["Repeat contact rate", "21.6%", "≤10%", "history.repeat_contact in evaluation set", "New metric — introduce"],
            ["Hallucination rate", "Not measured", "≤5%", "Two independent assessors on ≥50 sampled auto-responses; report inter-assessor agreement rate", "Nishchay (evaluation)"],
            ["Citation accuracy", "Not measured", "≥95%", "Each citation checked against the sentence it supports in the retrieved passage", "Nishchay (evaluation)"],
            ["PII in outbound responses", "Not measured", "Zero occurrences", "PII guardrail activation log; manual spot-check", "Nishchay (governance)"],
            ["Decision log coverage", "0%", "100%", "count_decisions() == tickets_processed for every evaluation run", "Nishchay (governance)"],
        ],
        col_widths=[2.0, 1.1, 1.5, 2.5, 1.0]
    )

    doc.add_page_break()

    # ── SECTION I: TRACEABILITY MATRIX ────────────────────────────────────
    add_section_banner(doc, "I", "Traceability Matrix",
                       "Evidence → Requirement → Specification prompt → Code module. Assessors will trace this chain.")
    make_table(doc,
        ["Requirement ID", "Discovery evidence reference", "Specification / Prompt", "Code module"],
        [
            ["FR-01, FR-02", "Section 2, Table 2-A: Channel distribution (email 42.4%, chat 31.0%, docs_comment 15.6%, forum 11.0%)", "PR-IN-01 v1.0 (stub — write Week 1 Day 5)", "src/ingest.py"],
            ["FR-03, FR-04, FR-05", "Section 4, Table 4-A: FCR metric. Section 2, Table 2-A: urgency 29.2% high. Marcus: 'I picture it answering the easy ones.'", "PR-CL-01 v1.0", "src/classify.py"],
            ["FR-06, FR-07", "Section 1, Table 1-B Row 1: 71.4% answerable from docs. Ines: vocabulary mismatch kills keyword search. Section 3, Table 3-B Step 3.", "PR-RT-01 v1.0 (stub — write Week 1 Day 5)", "src/retrieve.py"],
            ["FR-08, FR-09, FR-10", "Data: 17.4% must_not_auto_respond. Daniel: escalations arrive without context. Section 3, Table 3-B Step 5.", "PR-RO-01 v1.0 (stub)", "src/route.py"],
            ["FR-11, FR-12", "Ines: citation requirement. Ravi: citable source. Section 1, Table 1-B Row 1: 71.4% answerable.", "PR-GN-01 v1.0", "src/generate.py"],
            ["FR-13 – FR-17", "Marcus: compliance. GDPR. Daniel: security/billing must always escalate. Section 5, Table 5-B: risk register.", "PR-GD-01 through PR-GD-05 (stub — write Week 1 Day 5)", "src/guardrails.py"],
            ["FR-18", "Marcus: compliance review, autumn deadline. Governance requirement. Section 5, Table 5-B: R-02 risk.", "Decision log schema (Governance_Framework.docx)", "src/logging_store.py"],
            ["NFR-01 – NFR-10", "Section 4, Table 4-A: success metrics. Ravi: urgency asymmetry. Marcus: 4× cost of escalation.", "Evaluation framework (Evaluation_Framework.docx)", "evaluation/harness.py"],
        ],
        col_widths=[1.2, 2.8, 2.0, 2.1]
    )

    doc.add_page_break()

    # ── SECTION J: REVISION LOG PLACEHOLDER ──────────────────────────────
    add_section_banner(doc, "J", "Revision Log",
                       "Requirements must be revised at least once during the build. Fill this in during Week 3 Day 3.")
    make_table(doc,
        ["Version", "Date", "What changed", "What triggered the change", "What was decided NOT to change and why"],
        [
            ["1.0 → 1.x", "(Fill in Week 3 Day 3)", "(Fill in after Week 2 Day 5 gate run)", "(Code contact / evaluation data / discovery finding)", "(Fill in — not all changes are improvements; record what you chose to keep and why)"],
        ],
        col_widths=[0.7, 1.0, 2.2, 2.0, 2.2]
    )

    add_callout(doc,
        "Reminder: 'Requirements that survive three weeks of contact with real code without a single amendment "
        "almost always mean that nobody was reading them.' At least one substantive change is required in the "
        "revision log before submission.",
        bg="FEF9E7")

    path = os.path.join(OUTPUT_DIR, "Stage_2_PRD_v1.docx")
    doc.save(path)
    print(f"✅  Saved: {path}")
    return path


# ───────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating Stage 1 Discovery Workbook (.docx)...")
    build_discovery_workbook()

    print("Generating Stage 2 PRD v1 (.docx)...")
    build_prd()

    print("\nDone. Both documents saved to docs/")
