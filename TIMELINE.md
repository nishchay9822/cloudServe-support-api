# Project Timeline — FDE Capstone
**Deadline: 13 September 2026, 23:59**

> Tick off items as you complete them.
> Fill in **Actual hours** at the end of each day.
> Update `CONTEXT.md` at the end of every session.

---

## ⚠️ 8 Things That Kill Projects

1. 🚫 **Starting code before reading** → Spend Day 1 reading. Best performers spend 3 days on discovery and then build faster.
2. 🚫 **Treating PRD as paperwork** → Requirements determine what you build. Vague PRD = vague system, no recovery.
3. 🚫 **Never running the full end-to-end set** → Gate run MUST happen Week 2 Day 5. Most common avoidable failure.
4. 🚫 **Hardcoded input file path** → harness MUST accept `--input` arg. Already done ✅
5. 🚫 **Reporting accuracy and stopping** → Report business outcomes (FCR, escalation rate), not just classification %.
6. 🚫 **Governance on the final afternoon** → Governance decisions shape the architecture. Decide Week 1 what to log.
7. 🚫 **Effort log written from memory** → Update `CONTEXT.md` every 2 days. Takes 2 minutes.
8. 🚫 **One take on the video** → First take runs 28 min. Record twice. Budget half a day.

---

## WEEK 1 — Understand Before You Build

### Day 1 — Orientation + Environment Setup
**Target:** 5-6 hrs | **Actual:** ___

- [ ] Read `00_Start_Here.docx` (15 min)
- [ ] Read `01_Project_Brief.docx` fully — do NOT skim governance/evaluation sections (2-3 hrs)
- [ ] Skim `Submission_Guide.docx` — know the finish line now (30 min)
- [ ] Read `02_Build_Specification.docx` — memorise all 12 acceptance criteria (45 min)
- [ ] Work through `Setup_Guide.docx` — Python env, pip install, API key test
- [ ] Verify: `python -c "from src import ingest, classify, retrieve, route, generate, guardrails, logging_store; print('OK')"` ✅
- [ ] Verify: `python evaluation/harness.py --input data/validation_tickets.json --output evaluation/results/test.json` runs ✅
- [ ] Update `CONTEXT.md`

### Day 2 — Discovery: Stakeholder Interviews + Ticket Data
**Target:** 6-7 hrs | **Actual:** ___

- [ ] Read all 5 stakeholder transcripts in `Stakeholder_Interviews.docx` (1-2 hrs)
  - [ ] Marcus (Head of Support) — what he fears, FCR target, enterprise risk
  - [ ] Sofia (Tier 1 Agent) — 70% repeat tickets, broken search, private snippet files
  - [ ] Daniel (Tier 2 Engineer) — escalations arrive with no context, 50% resolvable by T1
  - [ ] Ines (Tech Writer) — 29 articles, vocabulary mismatch kills search
  - [ ] Ravi (Customer) — wants citations, wants honesty about automation, urgency varies
- [ ] Note the 3 tensions (Marcus vs Sofia on volume; Daniel vs Marcus on escalation content)
- [ ] Read `Dataset_Guide.docx` before loading any data
- [ ] Load `data/development_tickets.json` (500 tickets) — count by:
  - [ ] Intent class distribution (22 classes)
  - [ ] `expected_route`: auto_respond vs escalate
  - [ ] `answerable_from_docs`: what % can be answered
  - [ ] Channel distribution
  - [ ] `language_fluency`: fluent vs non-fluent
  - [ ] Customer tier distribution
- [ ] Start `Stage_1_Discovery_Workbook.docx` — interview evidence tables
- [ ] Update `CONTEXT.md`

### Day 3 — Discovery: Problem Statement + Finish Workbook
**Target:** 4-5 hrs | **Actual:** ___

- [ ] Write problem statement draft (what is actually broken — NOT "no chatbot exists")
- [ ] Validate: does the problem statement follow from ALL 5 interview transcripts?
- [ ] Validate: does the ticket data support the problem statement numerically?
- [ ] Complete `Stage_1_Discovery_Workbook.docx` — all sections filled in
- [ ] Update `CONTEXT.md`

**Hint:** The real problem is something like: *"Customers can't find answers already in documentation because vocabulary mismatch breaks keyword search, and escalations waste T2 time because they arrive without context or a draft answer."*

### Day 4 — PRD v1 + Architecture Diagram
**Target:** 6-7 hrs | **Actual:** ___

- [ ] Write `Stage_2_PRD_Template.docx` with all requirements
  - [ ] Every requirement has a unique ID: FR-01, FR-02 ... NFR-01, NFR-02 ...
  - [ ] Every requirement references a specific discovery evidence item
  - [ ] **Functional requirements cover:** ingest (4 channels), classify (intent + urgency + confidence), retrieve (RAG), route (threshold-based), generate (citations), 5 guardrails, decision logging (full schema), escalation context packet
  - [ ] **Non-functional requirements cover:** latency P95 <3s, availability 99.5%, hallucination ≤5%, citation accuracy ≥95%, PII = 0, fairness <5pp variation across groups
  - [ ] Out-of-scope section written
  - [ ] Assumptions + consequences written
- [ ] Update `docs/architecture.md` diagram if PRD decisions changed the architecture
- [ ] Update `CONTEXT.md` with all requirement IDs (FR-xx, NFR-xx)

### Day 5 — Prompt Library + Sprint Plan
**Target:** 6-7 hrs | **Actual:** ___

- [ ] Fill `Stage_3_Prompt_Library.docx` — convert each FR to a spec
- [ ] Write actual classification prompt in `prompts/build/classify_v1.txt` (not just stub)
- [ ] Write actual generation prompt in `prompts/build/generate_v1.txt`
- [ ] Write evaluation prompt in `prompts/evaluation/eval_v1.txt`
- [ ] Update `prompts/README.md` with real versions and dates
- [ ] Fill `Stage_4_Sprint_Plan.docx`
  - [ ] Day-by-day backlog for Week 2
  - [ ] Every item has definition of done written BEFORE work starts
  - [ ] Explicitly write what you will cut if you run out of time
- [ ] Update `CONTEXT.md`

**Week 1 target: 27-32 hrs total**

---

## WEEK 2 — Build and Measure

### Day 1 — Ingest Pipeline + Harness Wiring
**Target:** 6-7 hrs | **Actual:** ___

- [ ] Implement `src/ingest.py` → `normalize_ticket()` for all 4 channels
- [ ] Run `pytest tests/test_ingest.py -v` — xfail tests should now PASS
- [ ] Wire ingest into `evaluation/harness.py` → `process_ticket()` calls `normalize_ticket()`
- [ ] Run: `python evaluation/harness.py --input data/validation_tickets.json --output evaluation/results/run_001.json` — all 80 tickets processed
- [ ] **Demo checkpoint:** Print normalised object for one ticket from each of the 4 channels
- [ ] Update `CONTEXT.md`

### Day 2 — Retrieval Layer
**Target:** 6-7 hrs | **Actual:** ___

- [ ] Implement `src/retrieve.py` → `embed_corpus()` and `retrieve_passages()`
- [ ] Run: `python -c "from src.retrieve import embed_corpus; embed_corpus()"` — corpus embedded to Chroma
- [ ] Test: query with known question (e.g. "invalid credential errors") → confirm DOC-AUTH-001 returned
- [ ] Wire retrieval into harness
- [ ] **Demo checkpoint:** Query returns passage with `doc_id` traceable to `data/documentation.json`
- [ ] Update `CONTEXT.md`

### Day 3 — Classification + Routing + Decision Logging
**Target:** 7-8 hrs | **Actual:** ___

- [ ] Implement `src/classify.py` → `classify_ticket()` with LLM call via OpenRouter
- [ ] Implement `src/route.py` → `route_ticket()` — deterministic, reads threshold from `.env`
- [ ] Implement `src/logging_store.py` → `init_db()`, `log_decision()`, `get_decision()`, `count_decisions()`
- [ ] Wire classification + routing + logging into harness
- [ ] Run 20 tickets — read SQLite log — every decision has all required fields including `reason`
- [ ] **Demo checkpoint:** 20 tickets processed, `storage/decisions.db` shows every decision with full schema
- [ ] Update `CONTEXT.md`

### Day 4 — Generation + Guardrails
**Target:** 7-8 hrs | **Actual:** ___

- [ ] Implement `src/generate.py` → `generate_response()` with LangChain/LangGraph
- [ ] Implement all 5 guardrails in `src/guardrails.py`
  - [ ] G1: PII detection
  - [ ] G2: Grounding check
  - [ ] G3: Injection detection
  - [ ] G4: Tone/scope check
  - [ ] G5: Confidence floor check
  - [ ] `run_guardrails()` runs all 5 and returns combined result
- [ ] Wire generation + guardrails into harness
- [ ] Implement `src/api.py` → `POST /process` fully
- [ ] **Test guardrails:** craft a trigger ticket for G2 (question not in docs) → confirm block
- [ ] **Demo checkpoint:** `POST /process` returns 200 for a normal ticket; G2 blocks a hallucination attempt
- [ ] Update `CONTEXT.md`

### Day 5 — ⭐ GATE: Full Unattended Run + Evaluation
**Target:** 6-7 hrs | **Actual:** ___

**THIS IS THE GATE. THE MOST IMPORTANT DAY OF WEEK 2.**

- [ ] **Run the gate:**
  ```
  python evaluation/harness.py \
    --input data/validation_tickets.json \
    --output evaluation/results/gate_run.json
  ```
- [ ] Start it. Leave the room. Come back to a complete metrics report. No intervention.
- [ ] **If it crashes on any ticket: fix it today.** Systems that work on 5 tickets routinely fail on the 40th.
- [ ] Implement full `compute_metrics()` in harness — real numbers, not None
- [ ] Run calibration check: group confidence predictions by band (0.5-0.6, 0.6-0.7, etc.), check accuracy per band
- [ ] Record ALL results honestly, including bad ones
- [ ] Set up Prometheus metrics collection
- [ ] **Demo checkpoint:** 80-ticket validation set processed unattended, metrics report auto-generated
- [ ] Update `CONTEXT.md` with ALL evaluation results

**Week 2 target: 32-37 hrs total**

---

## WEEK 3 — Governance, Polish, Submission

### Days 1-2 — Governance Framework + Monitoring
**Target:** 5-6 hrs | **Actual:** ___

- [ ] Fill `Governance_Framework.docx`:
  - [ ] **Risk register** — all 8 risks (R-01 to R-08) with likelihood, impact, mitigation, owner
  - [ ] **Fairness audit** — run metrics separately for: enterprise/business/standard tiers; fluent/non-fluent English; short/long tickets; NA/EU/APAC/LATAM regions. Accept that non-fluent English will likely perform worse — document it honestly.
  - [ ] **Kill switch** — document: who operates it, how long to take effect, what happens to in-flight tickets, tested? ✓
  - [ ] **Incident response** — 6 steps (Detect → Contain → Assess → Notify → Remediate → Review), written so someone unfamiliar can follow at 2am
- [ ] Set up Grafana dashboard: tickets/hr, auto-answer rate, latency P50+P95, guardrail activations, confidence distribution
- [ ] Verify GitHub Actions CI runs on push
- [ ] Update `CONTEXT.md`

### Day 3 — PRD Revision (Compulsory)
**Target:** 3-4 hrs | **Actual:** ___

- [ ] Fill `Stage_5_PRD_Revision_Log.docx`
  - [ ] At least **one substantive change** (what changed, what triggered it, what you decided NOT to change and why)
  - [ ] Short reflection paragraph for the report
- [ ] Update the PRD itself (increment version number, update any changed requirements)
- [ ] Update `CONTEXT.md`

### Days 4-5 — Report Writing
**Target:** 8-10 hrs | **Actual:** ___

- [ ] Section 1: Executive summary (1 page)
- [ ] Section 2: The problem (2-3 pages) — what they asked for vs what you found, why the difference matters
- [ ] Section 3: Discovery findings (3-4 pages) — 2-3 findings that changed your design, with evidence cited
- [ ] Section 4: Requirements (2-3 pages) — key requirements with IDs + traceability to evidence
- [ ] Section 5: Architecture and design (3-4 pages) — 6-component diagram + design decisions
- [ ] Section 6: Implementation (2-3 pages) — what you built, where it lives in the repo
- [ ] Section 7: Evaluation (3-4 pages) — **business outcomes FIRST**, then technical, then governance; state uncertainty; include calibration
- [ ] Section 8: Governance and risk (2-3 pages) — risk register summary, fairness audit findings
- [ ] Section 9: Requirements revision (1-2 pages) — what changed, why
- [ ] Section 10: Conclusions (1-2 pages) — what you'd do next, what you got wrong
- [ ] AI tool use declaration (half page)
- [ ] Number all figures and tables, reference them in text
- [ ] State when hidden evaluation set was used and how many times
- [ ] Export to PDF: `NishchayGupta_Capstone_Report.pdf`
- [ ] Update `CONTEXT.md`

### Day 6 — Video Recording
**Target:** 5-6 hrs | **Actual:** ___

- [ ] **First take** (expect ~28 min — exposes gaps)
- [ ] Fix what first take revealed (expect ~30 min)
- [ ] **Second take** — aim for 18-22 minutes
- [ ] Required structure (order matters):
  - [ ] 0-2 min: The problem — what they asked for vs what you found, why it matters
  - [ ] 2-5 min: Discovery — 2-3 findings that changed your design, evidence cited
  - [ ] 5-7 min: The system — architecture explained to a non-engineer
  - [ ] 7-14 min: **Live demo** — auto-answer success + escalation + guardrail blocking + evidence of full unattended run
  - [ ] 14-17 min: The numbers — business outcomes first, then technical, then governance; state uncertainty
  - [ ] 17-18 min: Risk and governance — what could go wrong, what stops it
  - [ ] 18-20 min: What's next — what you got wrong, what PRD revision changed
- [ ] On camera for intro and close
- [ ] Export: `NishchayGupta_Capstone_Video.mp4` (1080p+)
- [ ] Update `CONTEXT.md`

### Day 7 — Packaging + Final Checklist + Submit
**Target:** 3-4 hrs | **Actual:** ___

**FINAL CHECKLIST — do not skip any item:**

- [ ] Archive named: `NishchayGupta_Capstone_Submission.zip` (no spaces, no dates, no versions)
- [ ] Exactly 4 top-level folders: `01_Video/`, `02_Report/`, `03_Workbooks/`, `04_Source_Code/`
- [ ] **TEST ON CLEAN CHECKOUT:** Clone repo into a fresh empty directory, follow README literally, verify it runs
- [ ] No credentials anywhere in repo or git history: `git log --all -p | grep -i "api_key\|secret\|password"`
- [ ] All 12 acceptance criteria verified (check against `02_Build_Specification.docx`)
- [ ] Video: 18-22 min, audio audible, screen legible at 1080p
- [ ] Live demo includes: auto-answer success, escalation, guardrail blocking
- [ ] Report: single PDF, prescribed section order, all figures numbered
- [ ] Effort log: entries throughout 3 weeks (not just at end — will be obvious)
- [ ] All 5 stage workbooks completed and included in `03_Workbooks/`
- [ ] PRD revision log shows at least 1 substantive change
- [ ] Hidden evaluation set used at most once; report states when
- [ ] AI tool use declaration in report
- [ ] **Submit before 23:59 on 13 September 2026**

**Week 3 target: 24-30 hrs total**

---

## Effort Summary

| Week | Target Hours | Actual Hours | Delta |
|------|-------------|-------------|-------|
| Week 1 | 27-32 hrs | ___ | ___ |
| Week 2 | 32-37 hrs | ___ | ___ |
| Week 3 | 24-30 hrs | ___ | ___ |
| **Total** | **83-99 hrs** | **___** | **___** |

---

## Grading Reminder

| Area | Weight | What earns the marks |
|------|--------|---------------------|
| Implementation | 35% | All 12 ACs pass, runnable on clean checkout |
| Evaluation | 20% | Honest measurement, business outcomes, calibration |
| Discovery | 15% | Evidence gathered first, problem statement follows from it |
| Requirements | 10% | Specific enough to build from, traceable chain |
| Governance | 10% | Decisions logged, risks real, fairness tested |
| Communication | 10% | Video and report a non-technical stakeholder could follow |
