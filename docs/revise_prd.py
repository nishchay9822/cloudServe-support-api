"""
Produce Stage_2_PRD_v2_0.docx from Stage_2_PRD_v1.docx by editing the cells that the build proved wrong.
v1 is left untouched so the revision is traceable. Every edit here has a matching row in
Stage_5_PRD_Revision_Log.docx (same requirement ID, same trigger).

Run: venv/bin/python3 docs/revise_prd.py
"""
import copy
import os

from docx import Document
from docx.shared import Pt

HERE = os.path.dirname(os.path.abspath(__file__))
doc = Document(os.path.join(HERE, "Stage_2_PRD_v1.docx"))


def set_cell(cell, text, size=9, bold=None):
    """Replace a cell's text but keep its shading and font size."""
    p = cell.paragraphs[0]
    for extra in cell.paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    run = p.add_run(text)
    run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold


def table_with_headers(*headers):
    for t in doc.tables:
        cells = [c.text.strip() for c in t.rows[0].cells]
        if len(cells) >= len(headers) and cells[: len(headers)] == list(headers):
            return t
    raise KeyError(headers)


def row_by_id(table, rid):
    for r in table.rows[1:]:
        if r.cells[0].text.strip() == rid:
            return r
    raise KeyError(rid)


def add_row(table, values):
    new = copy.deepcopy(table.rows[-1]._tr)
    table._tbl.append(new)
    row = table.rows[-1]
    for c, v in zip(row.cells, values):
        set_cell(c, v)
    return row


# ---- 1 Document control
dc = table_with_headers("Field", "Value")
for r in dc.rows[1:]:
    k = r.cells[0].text.strip()
    if k == "Version":
        set_cell(r.cells[1], "2.0 (revised after the build; v1.0 retained in Stage_2_PRD_v1.docx)")
    elif k == "Date":
        set_cell(r.cells[1], "9 November 2026 (build and revision phase: 2 to 9 November 2026)")
    elif k == "Status":
        set_cell(r.cells[1], "Revised after build - draft for review")
    elif k == "Approved by":
        set_cell(r.cells[1], "Pending: author and reviewer sign-off (see Stage_5_PRD_Revision_Log.docx)")

# ---- 4 Functional requirements
fr = table_with_headers("ID", "Requirement", "Priority")

r = row_by_id(fr, "FR-01")
set_cell(r.cells[1], "The system shall accept tickets from all four channels - email, live chat, documentation comments (channel name docs_comment; api_comments is accepted as an alias) and community forum - and normalise them into a single internal representation. Ground-truth fields (labels, history) shall never be passed downstream.")

r = row_by_id(fr, "FR-02")
set_cell(r.cells[1], "The system shall classify every ticket into one of the 22 intent classes that occur in the data (listed in src/classify.py) and assign urgency (high/medium/low). Urgency shall be assigned and logged but is not an accuracy target.")
set_cell(r.cells[4], "Intent precision >=85% per class on the validation set (measured: 100% on 80 validation tickets, 99.8% on 500 dev tickets, leave-one-out). Urgency assigned and logged for 100% of tickets (measured accuracy 45% val / 52% dev, no better than a majority-per-intent baseline of ~55%, because the urgency labels are only ~68% consistent for identical text).")

r = row_by_id(fr, "FR-03")
set_cell(r.cells[1], "The system shall produce a calibrated confidence for each classification. Confidence shall come from agreement between two independent classifiers (nearest labelled tickets; the LLM is consulted only when the neighbour vote is below 0.85), not from the LLM's self-reported confidence. Stated confidence shall be within 5 percentage points of observed accuracy in every populated band.")
set_cell(r.cells[4], "Calibration table produced by the harness for every run. Measured: only the 0.9-1.0 band is populated on validation (80/80, stated 0.99, observed 1.00) so the check passes where it can be tested but is weak; a mid-confidence test set is still needed (open question).")

r = row_by_id(fr, "FR-04")
set_cell(r.cells[1], "The system shall perform semantic search over the 29 knowledge-base articles using embedding retrieval (all-MiniLM-L6-v2), matching on article sections, and returning one passage per article with doc_id, title and score. The reply generator shall be shown the whole article for the top result (and the runner-up only if it scores at least 0.6 times the best), not just the best-matching section.")
set_cell(r.cells[4], "Each returned passage resolves to a real document ID. hit@1 >=90% and hit@5 >=95% on answerable tickets (measured: 94.3% / 98.1% validation, 90.5% / 97.2% dev). Relevance floor 0.30 chosen from evaluation/eval_retrieval.py.")

r = row_by_id(fr, "FR-06")
set_cell(r.cells[1], "The system shall never auto-respond to a ticket whose predicted intent is security_incident, compliance_request, feature_request or unclear_request. The restriction is derived from the system's own prediction; the must_not_auto_respond label in the data is ground truth and is used only to score the system.")
set_cell(r.cells[4], "These four intents correspond exactly to the 87 of 500 dev tickets flagged must_not_auto_respond. 0 violations required (measured: 0 of 87 dev, 0 of 14 validation). A wrongly predicted intent is the residual risk and is covered by NFR-03.")

r = row_by_id(fr, "FR-07")
set_cell(r.cells[1], "The system shall route deterministically, checking in order: (1) restricted intent, (2) no relevant passage, (3) classification confidence below the threshold (default 0.80), otherwise auto-respond. A model reply of NO_ANSWER or a guardrail block also escalates. Every decision shall record its reason code and the threshold applied.")
set_cell(r.cells[4], "Same ticket always gives the same decision (tested 100 repeats). Threshold and reason code logged for every decision. Known limitation recorded: for non-safety tickets the labelled 'should escalate' outcome could not be predicted from text (see revision log); precision of auto-replies measured at 72% (validation) and 75% (dev).")

r = row_by_id(fr, "FR-09")
set_cell(r.cells[4], "Citation accuracy >=95%: every citation resolves to an article the model was shown (measured 100% val and dev) and the cited article is the expected one (87% val, 87% dev). Hallucination rate <=5% on >=50 replies assessed by two independent assessors: an independent model (openai/gpt-4o-mini, measured 0 of 50 val) plus a human second assessor using the CSV the harness writes. The human assessment has NOT yet been done.")

r = row_by_id(fr, "FR-11")
set_cell(r.cells[1], "The system shall run five guardrails on every outbound response and each shall be able to block it and escalate: (1) PII, (2) grounding - citations must resolve to the articles shown, and every figure in the reply must appear in those articles or in the customer's own ticket, (3) prompt injection - also screened before any model sees the ticket, (4) tone/scope - no commitments on refunds, credits or timelines, (5) confidence floor.")
set_cell(r.cells[4], "All five run on every response in every run; there is no switch to disable them. Engineered triggers for each are in tests/test_guardrails.py and tests/test_pipeline.py. Zero outbound PII (independent re-scan). In the 500-ticket dev run grounding blocked 15 replies (invented citations, a made-up plan-based refusal, invented figures).")

r = row_by_id(fr, "FR-13")
set_cell(r.cells[1], "For tickets with first_contact_resolution=True the system shall store a reusable resolution record (intent, doc_ids used, confidence, customer tier, language fluency; no customer identity). Using these records to improve classification or retrieval is deferred (Could); in this version they are write-only.")
set_cell(r.cells[2], "Should")
set_cell(r.cells[4], "Records written for every auto-reply whose simulated outcome is first-contact resolution (measured: 35 validation, 211 dev). The compounding effect is NOT demonstrated in this version: no later decision reads these records. The natural integration point is the nearest-ticket index used by the classifier.")

r = row_by_id(fr, "FR-14")
set_cell(r.cells[1], "The system shall handle failure without crashing: no retrieval hit, provider outage, rate limiting, exhausted credits, or malformed input shall degrade to escalation and the run shall continue. Transient provider errors are retried with backoff; non-transient errors (invalid key, no credits) fail fast; repeated failures open a circuit breaker.")
set_cell(r.cells[4], "Full validation set processed with the provider switched off: 80 of 80 processed, 0 errors, 80 escalated each with a context packet, 0 customer-facing replies. Malformed inputs (None, string, empty dict, unsupported channel) return an escalation and are logged. Non-transient errors are not retried.")

# new functional requirements
add_row(fr, ["FR-19", "The model provider shall be configurable (base URL, key, model) so the system can run on any OpenAI-compatible provider, and a provider that runs out of credit shall be detected as a non-transient failure.", "Should",
             "Build finding: the OpenRouter key ran out of credit part-way through evaluation (HTTP 402); the original client retried it and a judge run hung for 25 minutes.",
             "Setting LLM_BASE_URL, LLM_API_KEY and MODEL_NAME switches provider with no code change. A 402 response fails in under 1 second and the pipeline escalates. (Groq path untested: no key was available.)"])
add_row(fr, ["FR-20", "A kill switch shall exist that sends every new ticket to a human. It shall be operable by environment variable, by a flag file, and by an authenticated admin endpoint, take effect on the next ticket, and leave in-flight tickets to finish.", "Must",
             "Governance framework requirement (kill switch must exist, be documented and be tested). Omitted from v1.0.",
             "tests/test_pipeline.py::test_kill_switch_sends_everything_to_humans passes; admin endpoint refuses requests without ADMIN_TOKEN."])

# ---- 5 Non-functional requirements
nf = table_with_headers("ID", "Category")
r = row_by_id(nf, "NFR-01")
set_cell(r.cells[3], "Measured in the harness: end-to-end processing time per ticket, p95 over auto-replies. Result: 636 ms validation, 508 ms dev. This depends on provider routing: with default OpenRouter routing the same short reply took a median 11 s; asking for the highest-throughput provider took 0.4 s (evaluation/time_llm.py). The routing preference is configurable (LLM_PROVIDER_SORT).")

# ---- 9 Open questions (append)
oq = table_with_headers("Question", "Why it matters")
add_row(oq, ["Is 72-75% precision of auto-replies acceptable to the business, given that a quarter of auto-replies go to tickets the labels say need a person?", "Five methods failed to predict the 'should escalate' label for non-safety tickets. If it is not acceptable, the only lever left is a stricter, lower-automation policy.", "Nishchay with Marcus (head of support)", "Week 3 Day 1"])
add_row(oq, ["Does the near-perfect intent accuracy survive messy data?", "Dev and validation tickets are heavily templated (254 of 500 dev tickets share their text with another). The hidden set is from the same population but real tickets would not be.", "Nishchay", "After the hidden-set run"])
add_row(oq, ["Who is the human second assessor for hallucination, and when?", "The spec requires two independent assessors; so far only an independent model has assessed the replies.", "Nishchay", "Week 3 Day 2"])
add_row(oq, ["Which provider and how much credit will the final graded run use?", "The current OpenRouter key has no credit; the default model is not free and the :free Llama variants are no longer offered.", "Nishchay", "Week 3 Day 1"])

out = os.path.join(HERE, "Stage_2_PRD_v2_0.docx")
doc.save(out)
print("saved", out)
