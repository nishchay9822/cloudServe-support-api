"""
Fill the official Stage_5_PRD_Revision_Log.docx template with the changes the build forced.
Every figure below comes from a run recorded in evaluation/results/ or from a script in evaluation/.

Run: venv/bin/python3 docs/generate_revision_log.py
"""
import copy
import os

from docx import Document
from docx.shared import Pt

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = "/Users/nishchaygupta/Downloads/FDE_Capstone_Complete/Capstone_Pack/02_Stage_Workbooks/Stage_5_PRD_Revision_Log.docx"
doc = Document(TEMPLATE)


def put(cell, text, size=9):
    p = cell.paragraphs[0]
    for extra in cell.paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    p.add_run(text).font.size = Pt(size)


def ensure_rows(table, n_data_rows):
    while len(table.rows) - 1 < n_data_rows:
        table._tbl.append(copy.deepcopy(table.rows[-1]._tr))


def fill(table, rows):
    ensure_rows(table, len(rows))
    for i, vals in enumerate(rows, start=1):
        for c, v in zip(table.rows[i].cells, vals):
            put(c, v)


t = doc.tables
summary, changes, assumptions, notchanged, reflection = t[2], t[3], t[4], t[5], t[6]

AGREED = "Author (self-review); reviewer pending"

# ---- 1 Revision summary
vals = {
    "Date of revision": "9 November 2026. Build and revision phase: 2 to 9 November 2026 (first phase, Stages 1 to 4: 27 October to 2 November 2026).",
    "Who carried out the revision": "Nishchay Gupta, drafted with AI assistance (Kiro). To be declared in the report's AI-tool-use statement.",
    "Who reviewed and agreed it": "Not yet reviewed. Needs the author's confirmation and, ideally, the head-of-support view on the auto-reply precision question (open question 1 in PRD v2.0).",
    "Number of requirements changed": "11 (FR-01, FR-02, FR-03, FR-04, FR-06, FR-07, FR-09, FR-11, FR-13, FR-14, NFR-01)",
    "Number of requirements added": "2 (FR-19 configurable provider and fail-fast on exhausted credit; FR-20 kill switch)",
    "Number of requirements removed": "0",
}
for r in summary.rows[1:]:
    k = r.cells[0].text.strip()
    if k in vals:
        put(r.cells[1], vals[k])

# ---- 2 The changes
fill(changes, [
    ["FR-01", "Accept tickets from email, chat, API documentation comments and forum.",
     "Channel is docs_comment (api_comments kept as an alias). Ground-truth fields are never passed downstream.",
     "The data's channel name is docs_comment. The first scaffold used api_comments, which would have rejected 78 of 500 tickets (15.6%) on the hidden set. Found when inspecting the ticket schema before writing ingest.", AGREED],
    ["FR-02", "Classify into 22 intent classes at >=85% precision; assign urgency.",
     "Classify into the 22 intent classes that actually occur in the data. Urgency is assigned and logged but is not an accuracy target.",
     "My first classification prompt used 22 invented class names; the real labels (deployment_failure, data_residency ...) differ. Urgency: nearest-ticket vote 51%, LLM about 50%, majority-per-intent baseline 55%; identical ticket text carries the same urgency label only 68.5% of the time, so the label is not recoverable from text.", AGREED],
    ["FR-03", "Calibrated 0-1 confidence, probably from the model.",
     "Confidence comes from agreement of two independent classifiers (nearest labelled tickets; the LLM only when the neighbour vote is below 0.85). The LLM's self-reported confidence is not used.",
     "On 300 dev tickets the classifiers agreed on 290 and were right every time; on the 10 where they disagreed the LLM was right once. A regression that included the LLM's own confidence gave it a negative weight (an artefact of ~10 negatives), so it was dropped. Nearest-ticket classifier alone: 99.8% dev, 100% validation.", AGREED],
    ["FR-04", "Semantic search returning passages from the 29 articles.",
     "Search matches article sections but the generator is shown the whole top article (and a close runner-up), not the matching section.",
     "VAL-0012: retrieval returned only the 'Symptoms' section of the rollback article, so the model never saw the fix and improvised from an unrelated second article. Showing whole articles and dropping low-scoring runners-up fixed this.", AGREED],
    ["FR-06", "Check the must_not_auto_respond flag before routing.",
     "Never auto-respond to a predicted security_incident, compliance_request, feature_request or unclear_request. The label is used only for scoring.",
     "The flag is ground truth and would not exist on a live ticket. Analysis showed the flagged tickets are exactly those four intents (87 of 500), so the rule can be derived from the system's own prediction. Result: 0 violations in 87 dev and 14 validation tickets.", AGREED],
    ["FR-07", "Route by confidence threshold (0.80), safety flag and passages.",
     "Ordered, deterministic rules (restricted intent, no passage, low confidence). A model NO_ANSWER or a guardrail block also escalates. Known limit recorded: 72-75% of auto-replies are on tickets the labels say are answerable; the remainder could not be predicted.",
     "For non-safety tickets I tried five signals to predict the 'should escalate' label: classifier, nearest-ticket route vote, nearest-ticket answerable vote, retrieval score (AUC 0.51 dev / 0.47 val) and an LLM answerability judge (AUC 0.46 / 0.42, worse than chance). None worked. Identical text has the same route label only 87.8% of the time, so the label itself is partly unpredictable.", AGREED],
    ["FR-09", "Citations >=95%, hallucination <=5% on >=50 replies by two assessors.",
     "Same targets. Assessors are now an independent model (openai/gpt-4o-mini) plus a human second assessor using a CSV the harness writes. Human assessment still to do.",
     "A small same-family model as judge flagged 4 of 50 replies (8%). I checked all four against the cited articles: every flagged statement is in the source. The independent model found 0 of 50. This showed a single weak judge is unreliable in both directions. Separately, my first generation prompt made the model append a refusal sentence after good answers (VAL-0005); fixed with a NO_ANSWER sentinel, then v3 raised required-point coverage from 80% to 95% on 100 reference-checked replies.", AGREED],
    ["FR-11", "Five guardrails, each able to block.",
     "Grounding now checks figures in every sentence, allows figures the customer wrote, and checks against exactly what the model was shown. Injection is also screened before any model sees the ticket.",
     "My own unit test showed 'Cursors expire after 45 minutes' (docs say one hour) passed, because figures were only checked in sentences of six or more words. In the dev run two correct replies were blocked for repeating the customer's own '14:00' and '400 GB'.", AGREED],
    ["FR-13", "Store a resolution record for each first-contact resolution; presented as the compounding mechanism.",
     "Records are written (35 validation, 211 dev) but nothing reads them yet. Using them to improve classification or retrieval is deferred.",
     "Late in the build I checked whether any component consumes the records. None does, so the 'gets better with every ticket' claim is not demonstrated by this version. The natural integration is adding resolved tickets to the nearest-ticket index.", AGREED],
    ["FR-14", "Degrade gracefully on provider failure, bad input, no retrieval hit.",
     "Same, with explicit behaviour: transient errors retried; invalid key or exhausted credit fail fast; repeated failures open a circuit breaker; everything degrades to escalation.",
     "The OpenRouter key ran out of credit (HTTP 402) mid-evaluation. The client retried 402, so a judge run hung for 25 minutes. Outage test with the provider off: 80 of 80 tickets processed, 0 errors, 80 escalations each with a context packet.", AGREED],
    ["NFR-01", "p95 latency under 3 seconds.",
     "Same target. Verification now records the provider routing setting it depends on.",
     "Default provider routing gave a median 11 s for a short reply; requesting the highest-throughput provider gave 0.4 s. Measured p95 for auto-replies: 636 ms validation, 508 ms dev.", AGREED],
    ["FR-19 (new)", "Not in v1.",
     "Provider (base URL, key, model) is configurable, and exhausted credit is a non-transient failure.",
     "Same 402 incident. Free Llama variants on OpenRouter are no longer offered, and the default model is not free, so a single hard-wired provider is a delivery risk.", AGREED],
    ["FR-20 (new)", "Not in v1.",
     "A kill switch (environment variable, flag file, authenticated admin endpoint) sends every new ticket to a human.",
     "The governance framework requires a documented and tested kill switch; v1 did not mention it. Tested in tests/test_pipeline.py.", AGREED],
])

# ---- 3 Assumptions that turned out to be wrong
fill(assumptions, [
    ["The 29 knowledge-base articles remain current and reviewed.", "Held (not stressed).",
     "No stale answers surfaced. The articles carry a last-reviewed field, which is now stored with each passage.",
     "Nothing yet. A staleness alert (article not reviewed in 90 days) is still only a plan."],
    ["A confidence threshold of 0.80 will give acceptable routing, justified by calibration data.", "Held, but not for the reason I expected.",
     "Confidence turned out to be almost two-valued: about 0.99 when the two classifiers agree, about 0.17 when they do not. Any threshold between roughly 0.2 and 0.98 would route identically, so the calibration data cannot actually justify 0.80 over 0.60. On validation every ticket fell in one band.",
     "Kept 0.80. Recorded that the threshold is untested in the middle range and that a mid-confidence test set is needed."],
    ["OpenRouter's free tier provides enough capacity.", "FALSE.",
     "The default model is not a free model, the :free Llama variants are no longer offered, and the key ran out of credit (HTTP 402) during evaluation. The model work cost cents, but without credit nothing works.",
     "Added FR-19 and fail-fast on 402. Made the provider configurable (Groq is the obvious free alternative, untested here)."],
    ["all-MiniLM-L6-v2 retrieves well enough (recall >=90%).", "Held.",
     "hit@1 94.3% validation / 90.5% dev; hit@5 98.1% / 97.2%. Misses are mostly a neighbouring article for tickets that sit between two topics.",
     "Changed how retrieved text is given to the model (whole article), not the retrieval itself."],
    ["Resolution records from first-contact-resolution tickets are reliable enough to feed back as a training signal.", "Not tested.",
     "Records are written but never read, so reliability could not be tested and the compounding benefit is unproven.",
     "Reworded FR-13 so it no longer claims a compounding effect."],
    ["Enterprise tickets are harder, which explains their worse first-contact resolution.", "Not resolved.",
     "The system auto-replies to enterprise tickets at 83% (dev), the same or higher than other tiers, although enterprise tickets historically escalate more. Route accuracy for enterprise is 75.9% against 83.5% for business.",
     "Nothing changed. Recorded as an open risk: enterprise customers may deserve a stricter threshold."],
])

# ---- 4 What I decided not to change
fill(notchanged, [
    ["Intent accuracy of 100% on validation looked too good to be true.",
     "It is a property of the data, not proof of a robust model: 254 of 500 dev tickets share their exact text with another, so nearest-neighbour lookup is very strong. The hidden set is drawn from the same population.",
     "Collecting messier data, which is not possible inside this project.", "When the hidden-set result is known. The report states this plainly."],
    ["The 72-75% precision of auto-replies.",
     "Five different methods failed to recover the 'should escalate' label for non-safety tickets, and identical text carries the same route label only 87.8% of the time. Tuning further would be fitting noise.",
     "More experiments with no evidence they would help.", "If the business says the precision is unacceptable, switch to a lower-automation policy (a business decision, not a modelling one)."],
    ["The fairness target of under 5 percentage points between groups.",
     "Several dev gaps exceed it (tier route accuracy 9.4 pp, region auto-reply rate 14.4 pp, channel 9.5 pp). I kept the target rather than relax it to fit the result; much of the gap is label noise and some groups are small.",
     "Nothing to change; relaxing it would hide a real finding.", "When label noise can be separated from real disparity. Non-fluent retrieval hit@1 is 5.6 pp lower than fluent and is worth watching."],
    ["Hard-coding the four always-escalate intents.",
     "They match the discovery evidence exactly and a wrong auto-reply on these is the most costly error. A learned rule could drift.",
     "Little, but it removes a guarantee.", "If a new always-escalate category appears."],
    ["Using the small default model for replies despite occasional preamble.",
     "It is the specified model, the guardrails catch the real errors, and required-point coverage reached 95% after one prompt change.",
     "A larger model costs more and was not needed for the targets.", "If a human assessor finds unsupported claims the guardrails missed."],
    ["Urgency accuracy of about 50%.",
     "It equals a baseline that already knows the true intent, and identical text carries the same urgency label only 68.5% of the time. Urgency does not drive routing.",
     "Effort with no available signal.", "If urgency starts to drive routing or prioritisation."],
])

# ---- 5 Reflection
answers = [
    "I expected the hard part to be getting good answers out of the model. It was knowing when not to answer. The labelled 'should escalate' outcome for ordinary tickets could not be recovered from the text by five different methods. I also expected the language model to be the classifier; a plain nearest-ticket lookup beat it (99.8% against 97%) and was faster and free. The other surprises were operational: the same model took 11 s or 0.4 s depending on provider routing, and the API key ran out of credit.",
    "Two cheap analyses in week one would have caught most of it: checking how consistent the labels are for identical ticket text (it exposed the ceiling on routing and urgency), and a crosstab of expected route against answerable-from-docs (it shows 46 answerable tickets that are still escalated). A one-hour probe of provider latency and credit limits before designing the pipeline would have caught the operational surprises.",
    "Build the evaluation harness and the label-consistency analysis on day one, and the nearest-ticket baseline before any language-model code. Probe the provider for latency and cost first. Run the independent judge from the start rather than trusting a single small-model judge, and check a sample of its flags by hand.",
    "Whether near-perfect intent accuracy survives messy, untemplated tickets; whether 72-75% auto-reply precision is acceptable to the head of support; whether confidence is calibrated in the middle range (no mid-confidence cases exist in the data I have); whether the resolution records would actually improve results once something reads them; and the human second assessment of hallucination, which the spec requires and which has not been done. Resolving these needs the hidden-set result, a conversation with the business, and the author's own review of the CSV.",
]
for r, a in zip(reflection.rows[1:], answers):
    put(r.cells[1], a)

out = os.path.join(HERE, "Stage_5_PRD_Revision_Log.docx")
doc.save(out)
print("saved", out)
