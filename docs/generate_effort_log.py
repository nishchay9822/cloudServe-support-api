"""
Fill the official Effort_Log.docx with everything that is recorded fact: tasks, stages, what each produced,
what blocked it, and the planned hours from TIMELINE.md. Dates come from git commit times.
HOURS ARE NOT INVENTED: every actual-hours cell says 'author to enter'.
Run: venv/bin/python3 docs/generate_effort_log.py
"""
import copy
import os
from docx import Document
from docx.shared import Pt

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = "/Users/nishchaygupta/Downloads/FDE_Capstone_Complete/Capstone_Pack/04_Submission/Effort_Log.docx"
OUT = os.path.join(HERE, "Effort_Log.docx")
ENTER = "author to enter"

doc = Document(TEMPLATE)


def put(cell, text, size=8):
    p = cell.paragraphs[0]
    for extra in cell.paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    p.add_run(text).font.size = Pt(size)


def fill(table, rows, start=1):
    while len(table.rows) - start < len(rows):
        table._tbl.append(copy.deepcopy(table.rows[-1]._tr))
    for i, vals in enumerate(rows, start=start):
        for c, v in zip(table.rows[i].cells, vals):
            put(c, v)


T = doc.tables
details, summary, wk1, wk2, wk3, estimates, questions, decl = T[1], T[2], T[3], T[4], T[5], T[6], T[7], T[8]

# ---- 1 details
d = {
    "Full name": "Nishchay Gupta",
    "Project start date": "27 October 2026 as recorded by the author for Phase 1. The first repository commit is dated 7 November 2026.",
    "Target submission date": "13 September (as printed in the brief; confirm the year, because the recorded project dates are in October to November 2026)",
    "Hours available per week": ENTER,
}
for r in details.rows[1:]:
    k = r.cells[0].text.strip()
    if k in d:
        put(r.cells[1], d[k])

# ---- 2 summary (planned hours from TIMELINE.md; actuals left to the author)
fill(summary, [
    ["1. Discovery", "15 to 18 (includes the 5 to 6 h setup day)", ENTER, ENTER, ENTER],
    ["2. Requirements", "6 to 7", ENTER, ENTER, ENTER],
    ["3. Prompt library", "6 to 7 together with Stage 4 (one planned day)", ENTER, ENTER, ENTER],
    ["4. Sprint plan", "included in Stage 3", ENTER, ENTER, ENTER],
    ["5. Build and revision", "35 to 41 (week 2 plus the PRD revision day)", ENTER, ENTER, ENTER],
    ["6. Report, video, packaging", "21 to 26 (rest of week 3)", ENTER, ENTER, ENTER],
    ["Total", "83 to 99", ENTER, ENTER, ENTER],
])

# ---- 3 week one: Phase 1 (recorded 27 Oct to 2 Nov 2026), dates are real commit dates
fill(wk1, [
    ["7 Nov", "Scaffold: directories, data copy, module stubs, harness skeleton, tests, CI, TIMELINE and CONTEXT files", "Setup", ENTER,
     "Repository with 12 acceptance criteria mapped to modules (commits e6df9ba, 60d4d58)", "No"],
    ["7 Nov", "Python venv, resolve requirement conflicts, pytest.ini, .env", "Setup", ENTER, "Working environment on Python 3.9 (a5f0a1c)", "Dependency version conflicts; API key not yet available"],
    ["7 Nov", "Read 5 stakeholder interviews; analyse 500 tickets; fill Discovery Workbook", "1", ENTER, "Stage 1 workbook with 13 measurements and 4 disagreements settled by data (f399adc)", "No"],
    ["7 Nov", "Convert workbook and PRD to Word documents", "1, 2", ENTER, "Stage_1 workbook and Stage_2 PRD as .docx (0fe7b22)", "No"],
    ["9 Nov", "Apply the 'extraordinary problem' framework: rewrite Stage 1 and 2", "1, 2", ENTER, "Problem statement reframed; FR-19 resolution graph idea added (8be7196)", "No"],
    ["11 Nov", "Rewrite PRD in the exact Stage_2_PRD_Template format", "2", ENTER, "PRD v1.0 with FR-01 to FR-18 and NFR-01 to NFR-10 (aa1005c)", "Template format had to be matched exactly"],
    ["11 Nov", "Prompt library (4 prompts) and sprint plan", "3, 4", ENTER, "Stage 3 and Stage 4 workbooks (792a2e6)", "No"],
])

# ---- 4 week two: Stage 5 (recorded 2 to 9 Nov 2026), real dates 11 to 12 Nov
fill(wk2, [
    ["11 Nov", "Foundation modules: provider client, ingest, retrieval, classifier; inspect real data against the scaffold", "5", ENTER,
     "Found channel name docs_comment and the 22 real intent labels (invented ones in my first prompt); retrieval hit@1 90.5%", "OpenRouter key set up"],
    ["11 Nov", "Classifier investigation: nearest-ticket classifier vs model; urgency", "5", ENTER,
     "Nearest-ticket classifier 99.8% dev; urgency found unpredictable (below majority baseline)", "No"],
    ["11 Nov", "Routing experiments: five signals to predict 'should escalate'", "5", ENTER,
     "None beat chance (AUC 0.42 to 0.51). A dead end that produced the main limitation of the project", "No"],
    ["11 Nov", "Generation: prompt v1 to v3, NO_ANSWER sentinel, whole-article context, provider speed fix (11 s to 0.4 s)", "5", ENTER,
     "Coverage of required points 80% to 95%; p95 latency under 1 s", "Default provider routing very slow"],
    ["11 Nov", "Harness, metrics, judge, guardrails and 82 tests", "5", ENTER, "Unattended harness; a unit test caught the short-sentence figure bug", "No"],
    ["11 to 12 Nov", "Gate run (80/80), provider-outage run (80/80 escalated), dev run (500/500)", "5", ENTER, "Metrics reports and human-review sheets in evaluation/results", "No"],
    ["12 Nov", "Judge investigation: same-family judge false positives; switch to an independent judge", "5", ENTER, "8B judge 4 of 50 false flags; independent judge 0 of 50", "OpenRouter credit ran out (HTTP 402); a retry bug caused a 25-minute hang"],
    ["12 Nov", "PRD v2.0 and Stage 5 revision log (11 changed, 2 added, 0 removed)", "5", ENTER, "Stage_2_PRD_v2_0.docx; Stage_5_PRD_Revision_Log.docx (4853373)", "No"],
])

# ---- 5 week three: Stage 6 so far (video and packaging not yet done)
fill(wk3, [
    ["12 Nov", "README, .env.example, architecture notes and draw.io diagram; clean-checkout test", "6", ENTER, "Clean checkout passes (82 tests, harness exit 0) (63b67af)", "System Python 3.15 could not install pinned requirements"],
    ["12 Nov", "Switch to Groq (OpenRouter had no credit): 429 handling, judge token budget, gate run", "6", ENTER, "Groq gate run 80/80, judge 0 of 50; latency misses target on the free tier (0297e25)", "Account had no Llama models; free-tier rate limits"],
    ["12 Nov", "Credit restored; final OpenRouter gate and dev judge on 100 replies", "6", ENTER, "Final figures: p95 673 ms, 0 of 150 hallucinated (6698933)", "No"],
    ["12 to 13 Nov", "Fairness audit script, tests, validation and dev audits", "6", ENTER, "One borderline confirmed gap (short tickets); others unconfirmed", "No"],
    ["13 Nov", "Kill-switch drill test; stale-article guard; credential scan of git history", "6", ENTER, "Drill passes (effect under 2 s); history clean", "No"],
    ["13 Nov", "Governance Framework workbook (12 risks, fairness table, incident procedure, kill switch, declaration)", "6", ENTER, "docs/Governance_Framework.docx", "No"],
    ["13 Nov", "Prometheus, alert rules and Grafana dashboard; test that queried metrics exist", "6", ENTER, "monitoring/ (stack not run: Docker unavailable)", "Docker not installed"],
    ["13 Nov", "Report: figures, layout engine, 10 sections and appendices", "6", ENTER, "26-page PDF with 7 figures and 17 tables", "No PDF converter installed; built the PDF directly"],
    ["Not done", "Video recording", "6", "0", "Not started (deliberately skipped for now)", "n/a"],
    ["Not done", "Packaging, submission archive, final checklist", "6", "0", "Not started (deliberately skipped for now)", "n/a"],
])

# ---- 6 estimates against reality (estimates from TIMELINE.md)
fill(estimates, [
    ["Classification, routing and decision logging", "7 to 8", ENTER, ENTER],
    ["Generation and guardrails", "7 to 8", ENTER, ENTER],
    ["Gate: full unattended run and evaluation", "6 to 7", ENTER, ENTER],
    ["Governance framework and monitoring", "5 to 6", ENTER, ENTER],
    ["Report writing", "8 to 10", ENTER, ENTER],
    ["PRD revision", "3 to 4", ENTER, ENTER],
])

# ---- 7 reflections: drafts from the build record; the author should confirm against their own memory of time spent
q = {
    "Which task took far longer than you expected, and why?":
        "Draft, confirm: evaluation and the routing investigation. Five attempts to predict which tickets should escalate all failed, and the judge, provider credit and latency problems each needed a separate diagnosis before the numbers could be trusted.",
    "Which task was easier than you expected, and why?":
        "Draft, confirm: retrieval. A small local embedding model gave 90.5% hit@1 on the first run, and the nearest-ticket classifier was accurate without any tuning.",
    "What would you allocate differently if you started again on Monday?":
        "Draft, confirm: profile the real data before writing any prompt (it would have avoided the invented labels and the channel name), keep a clean untouched hold-out set from day one, and check provider credit and rate limits before the evaluation week.",
    "What did you spend time on that turned out not to matter?":
        "Draft, confirm: trying to predict urgency and the 'should escalate' label from text. Both labels are partly noise, so the effort produced a documented limitation but no improvement.",
}
for r in questions.rows[1:]:
    k = r.cells[0].text.strip()
    if k in q:
        put(r.cells[1], q[k])

# ---- 8 declaration: left for the author
put(decl.rows[1].cells[0], "Nishchay Gupta")
put(decl.rows[1].cells[1], "author to sign")
put(decl.rows[1].cells[2], "author to enter")
put(decl.rows[1].cells[3], ENTER)

doc.save(OUT)
print("saved", OUT)
