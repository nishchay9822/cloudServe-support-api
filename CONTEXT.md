# Project Context — CloudServe Capstone
> **Update this file at the END of every working session.**
> If you're starting a new session, **READ THIS FILE FIRST.**
> This is your persistent memory across sessions.

---

## 🗓 Last Updated
- **Date:** 9 November 2026
- **Session:** Extraordinary Problem framework applied to Stage 1 + Stage 2 docs; both verified

---

## 📍 Current Position
| Field | Value |
|-------|-------|
| **Week** | 1 |
| **Day** | 4 |
| **Stage** | Stage 2 PRD v1 — COMPLETE (with Extraordinary Problem framework) |
| **Status** | Stage 1 Discovery Workbook (50KB, 24 tables, 99 rows) and Stage 2 PRD v1 (48KB, 28 tables, 102 rows) both regenerated with full Extraordinary Problem framework and verified on disk. FR-19 (resolution graph) added as the network-effect exponent. CONTEXT.md updated. **Ready for Stage 3: Prompt Library.** |

---

## ✅ Completed Tasks

| Date | Task |
|------|------|
| 7 Nov 2026 | Project directory + all directories scaffolded |
| 7 Nov 2026 | All 4 datasets copied → `data/`: dev_tickets (500), validation (80), ground_truth (200), documentation (29 articles) |
| 7 Nov 2026 | All 8 `src/` modules stubbed, `evaluation/harness.py` with `--input/--output` CLI, tests created |
| 7 Nov 2026 | `docs/architecture.md`, CI workflow, prompts register, CONTEXT.md, TIMELINE.md created |
| 7 Nov 2026 | Git repo initialized on `main`, first commit |
| 7 Nov 2026 | Python venv created, all packages installed (resolved version conflicts), `.env` created |
| 7 Nov 2026 | All 18 tests pass: 13 passed, 5 xfailed (as expected) |
| 7 Nov 2026 | Stage 1 Discovery COMPLETE — all 5 interviews read, 500 tickets analysed, `Stage_1_Discovery_Workbook_Filled.md` written |
| 7 Nov 2026 | Stage 1 + Stage 2 initial .docx generated (v1 — ordinary problem framing) |
| 9 Nov 2026 | **Extraordinary Problem framework applied** — both .docx files regenerated with IIT Roorkee FDE Module 1 Session 2 framework throughout |
| 9 Nov 2026 | **Both documents verified on disk** — all key markers confirmed present in both files |

---

## 🔑 Key Decisions Made

| Decision | Rationale | Date |
|----------|-----------|------|
| SQLite for decision log (not PostgreSQL) | Sufficient at this scale; no service to provision; spec says SQLite is fine | 7 Nov 2026 |
| Default `CONFIDENCE_THRESHOLD = 0.80` | Starting point; will be justified with evaluation data in report (Week 2 Day 5) | 7 Nov 2026 |
| Harness uses `--input` / `--output` args | A9 requirement — harness will be pointed at hidden 120-ticket evaluation set | 7 Nov 2026 |
| `all-MiniLM-L6-v2` for embeddings | Runs locally, no API cost, spec requirement | 7 Nov 2026 |
| `meta-llama/llama-3.1-8b-instruct` default model | Spec default; OpenRouter free tier | 7 Nov 2026 |
| **Extraordinary problem framing: collective intelligence waste, not delivery problem** | 71.4% of tickets already have KB answers. Problem is not missing answers — it is that every resolved ticket's knowledge is discarded. Each new ticket should benefit from all previous ones. Economic equation: Prevention = (Ticket history × Resolution patterns) ^ Cross-customer learning | 9 Nov 2026 |
| **FR-19 added: Resolution graph** | The network-effect exponent. FCR=True resolutions logged as reusable resolution records. Without this, the system is a SaaS feature, not an AI-native product. | 9 Nov 2026 |
| **Escalation must carry context packet** | Daniel: "If an escalation arrived with context I would be twice as fast." | 7 Nov 2026 |
| **Private snippet files excluded from retrieval** | Daniel: stale answers would scale mistakes. Only 29 reviewed KB articles used. | 7 Nov 2026 |
| **17.4% of tickets hard-blocked from auto-response** | `must_not_auto_respond=True` on 87/500: security, compliance, billing, unclear. | 7 Nov 2026 |

---

## 📊 Key Discovery Findings (for PRD and Report)

| Finding | Data | Design implication |
|---------|------|-------------------|
| **71.4% of tickets answerable from 29 existing KB articles** | 357/500 `answerable_from_docs=True` | Resolution knowledge already exists — system must surface it, not invent it |
| **Resolution knowledge discarded after every ticket close** | No current mechanism to reuse closed-ticket resolutions | FR-19: log FCR=True resolutions as reusable records — this is the compounding exponent |
| **56.2% escalation rate; ~50% tier-1 resolvable** | 281/500 escalated; deployment 59% escalated but 70% answerable | Confidence threshold + grounded draft reduces unnecessary escalations |
| **Agents use private snippet files, not KB** | Sofia + Ines interviews; keyword search vocabulary mismatch | Semantic retrieval (all-MiniLM-L6-v2) solves vocabulary mismatch |
| **Escalations arrive with no context** | Daniel interview (explicit) | Escalation context packet: summary + docs + uncertainty reason |
| **17.4% must never be auto-responded** | 87/500 safety-flagged | Hard-block before routing — not after |
| **Enterprise FCR 37.3% (worst tier)** | Enterprise: FCR 37.3%, avg 484 min, 62.7% escalated | System benefits standard/business most; enterprise benefit via better escalation context |
| **21.6% repeat contact rate** | 108/500 `repeat_contact=True` | Better first-contact quality eliminates 108 follow-up tickets in this sample alone |
| **Non-fluent CSAT claim not confirmed by data** | Non-fluent CSAT 3.04 vs Fluent 2.95 | Monitor per-segment but don't over-engineer for non-fluent in v1 |
| **docs_comment is 15.6% of traffic** | 78/500 via docs_comment | Highest-intent users — best candidates for compound learning |

---

## � Requirement IDs (FR-01 to FR-19, NFR-01 to NFR-10)

| ID | Description | Discovery Evidence | Code Module |
|----|-------------|-------------------|-------------|
| FR-01 | Accept tickets from all 4 channels (email, chat, docs_comment, forum) | Data: channel distribution (Section 2, Table 2-A) | src/ingest.py |
| FR-02 | Normalise all tickets to single internal representation | Architecture; cross-channel resolution graph requires uniform format | src/ingest.py |
| FR-03 | Classify every ticket with one of 22 intent classes (≥85% precision) | Marcus/Sofia interviews; Section 4 success metrics | src/classify.py |
| FR-04 | Assign urgency (high/medium/low) to every ticket | Data: 29.2% high-urgency; Ravi: urgency asymmetry | src/classify.py |
| FR-05 | Calibrated confidence score 0.0–1.0 (within 5pp per band) | Marcus: "rather it said nothing than said something wrong" | src/classify.py |
| FR-06 | Semantic search over 29 KB articles (all-MiniLM-L6-v2) | Ines: vocab mismatch; 71.4% answerable from docs | src/retrieve.py |
| FR-07 | Return empty list when no article relevant — never hallucinate a retrieval | Ines: feature requests have no article | src/retrieve.py |
| FR-08 | Hard-block must_not_auto_respond=True before routing | Data: 17.4% safety-flagged; Daniel: security/billing always escalate | src/route.py |
| FR-09 | Route using confidence threshold (default 0.80); deterministic | Marcus: threshold justified by calibration data, not assumption | src/route.py |
| FR-10 | Escalated tickets carry context packet (summary + passages + uncertainty reason) | Daniel: "context would make me twice as fast" | src/route.py |
| FR-11 | Generated responses cite KB articles (doc_id inline); citations resolve to retrieved passages | Ines: citation requirement; Ravi: source transparency | src/generate.py |
| FR-12 | MUST NOT generate without retrieved passages | Ines: no article → must not manufacture | src/generate.py |
| FR-13 | Guardrail 1: PII scan; block + escalate | GDPR; Marcus compliance | src/guardrails.py |
| FR-14 | Guardrail 2: Grounding check; every claim traces to passage; block if not | Marcus primary fear; Ravi: "I will act on it" | src/guardrails.py |
| FR-15 | Guardrail 3: Prompt injection detection; block + log | Security — ticket body is untrusted input | src/guardrails.py |
| FR-16 | Guardrail 4: Tone/scope — no refund or timeline commitments | Daniel: "billing becomes contractual quickly" | src/guardrails.py |
| FR-17 | Guardrail 5: Confidence floor — verify threshold was applied | Governance; decision log must show threshold applied | src/guardrails.py |
| FR-18 | Every automated decision logged to SQLite (full schema) | Marcus: compliance review; autumn deadline | src/logging_store.py |
| **FR-19** ★ | **Resolution graph: FCR=True resolutions logged as reusable records (intent, doc_ids, confidence, tier, fluency)** | **Section 6: extraordinary problem. Economic equation exponent. "THIS IS THE EXPONENT."** | **src/logging_store.py (extension)** |
| NFR-01 | Latency P95 < 3 seconds | Ravi: urgency asymmetry; SLA context | evaluation/harness.py |
| NFR-02 | Availability ≥ 99.5% | SLA obligation | Monitoring |
| NFR-03 | Intent precision ≥ 85% per class | Routing quality depends on classification | evaluation/harness.py |
| NFR-04 | Hallucination rate ≤ 5% | Marcus primary fear | evaluation/harness.py |
| NFR-05 | Citation accuracy ≥ 95% | Ines: citation = KB audit trail | evaluation/harness.py |
| NFR-06 | Zero PII in outbound responses | GDPR | src/guardrails.py |
| NFR-07 | Tier consistency: <5pp FCR gap increase | Ravi: enterprise–business gap | evaluation/harness.py |
| NFR-08 | Language consistency: <5pp fluent vs non-fluent | Sofia concern; vocab mismatch affects retrieval | evaluation/harness.py |
| NFR-09 | Decision log coverage: 100% (count_decisions() == tickets_processed) | Marcus: compliance audit trail | src/logging_store.py |
| NFR-10 | Confidence calibration: within 5pp per band | Threshold only meaningful if calibrated | evaluation/harness.py |

---

## 📝 Prompt Versions Active

| Prompt ID | Version | File | Status |
|-----------|---------|------|--------|
| PR-CL-01 | v1.0 (stub) | `prompts/build/classify_v1.txt` | Write fully — Week 1 Day 5 |
| PR-GN-01 | v1.0 (stub) | `prompts/build/generate_v1.txt` | Write fully — Week 1 Day 5 |
| PR-EV-01 | v1.0 (stub) | `prompts/evaluation/eval_v1.txt` | Write fully — Week 1 Day 5 |

---

## 📊 Evaluation Results
> ⚠️ Fill in after **Week 2 Day 5** gate run

| Metric | Target | Result | Run Date |
|--------|--------|--------|----------|
| Intent precision | ≥85% per class | — | — |
| Hallucination rate | ≤5% | — | — |
| Citation accuracy | ≥95% | — | — |
| Latency P95 | <3s | — | — |
| Escalation rate | ≤30% | — | — |
| FCR rate | ≥60% | — | — |
| Resolution graph growth (FR-19) | ≥FCR × tickets/run | — | — |

---

## ❓ Open Questions / Blockers

1. **⚠️ API key needed:** Open `.env`, replace `your_key_here` with your OpenRouter key (https://openrouter.ai/ → Keys → Create key). Required before Week 2 Day 2 (retrieval) and Day 3 (classification).
2. **Threshold calibration:** `CONFIDENCE_THRESHOLD=0.80` is the starting point. Final value set after Week 2 Day 5 gate run — justify with calibration check data.
3. **FR-19 implementation scope:** Resolution graph (FR-19) is a v1 seed — the logging mechanism. The actual retrieval-from-resolution-graph is a v2 enhancement. Clarify in PRD revision log after Week 2 Day 5.
4. **Architecture diagram update needed:** `docs/architecture.md` predates the extraordinary problem reframing. Update after Stage 3 Prompt Library is written (Week 1 Day 5).

---

## ⏭ Next Immediate Action
> **START HERE next session:**

**Stage 3: Write the Prompt Library (Week 1 Day 5)**

1. Open `Stage_3_Prompt_Library.docx` from Downloads/FDE_Capstone_Complete/Capstone_Pack/02_Stage_Workbooks/
2. Convert each FR into a specification — write actual prompts (not stubs) for:
   - `prompts/build/classify_v1.txt` (FR-03, FR-04, FR-05) — classify intent, urgency, confidence
   - `prompts/build/generate_v1.txt` (FR-11, FR-12) — grounded response with doc_id citations
   - `prompts/evaluation/eval_v1.txt` (NFR-03 to NFR-05) — hallucination + citation check
   - Add new: `prompts/build/route_v1.txt` (FR-08 to FR-10)
3. Update `prompts/README.md` version register with real content, dates, requirement IDs
4. Fill `Stage_4_Sprint_Plan.docx` — Day-by-Day Week 2 backlog with definitions of done
5. Update CONTEXT.md with prompt versions

**Also: API key still needed for Week 2 Day 2.**

---

## 📅 Session Log

| Date | Duration | What Was Done | Next Session Goal |
|------|----------|--------------|-------------------|
| 7 Nov 2026 | ~2 hrs | Full project scaffold created. All files stubbed, datasets copied, git initialized. | Read project docs + set up Python env |
| 7 Nov 2026 | ~30 min | Python venv + all packages installed, .env created, 18 tests passing | Add OpenRouter API key, read project docs |
| 7 Nov 2026 | ~3 hrs | Stage 1 Discovery COMPLETE — all 5 interviews read, 500 tickets analysed, workbook written | Write PRD v1 (Stage 2) |
| 7 Nov 2026 | ~2 hrs | Stage 1 + Stage 2 initial .docx generated | Apply Extraordinary Problem framework |
| 9 Nov 2026 | ~2 hrs | Extraordinary Problem framework applied to both .docx files. FR-19 (resolution graph exponent) added. Both documents verified on disk. CONTEXT.md updated. | Write Stage 3 Prompt Library + Stage 4 Sprint Plan |
