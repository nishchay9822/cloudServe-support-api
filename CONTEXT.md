# Project Context — CloudServe Capstone
> **Update this file at the END of every working session.**
> If you're starting a new session, **READ THIS FILE FIRST.**
> This is your persistent memory across sessions.

---

## 🗓 Last Updated
- **Date:** 9 November 2026
- **Session:** Stage 3 Prompt Library + Stage 4 Sprint Plan complete

---

## 📍 Current Position
| Field | Value |
|-------|-------|
| **Week** | 1 |
| **Day** | 5 |
| **Stage** | Stages 1-4 ALL COMPLETE |
| **Status** | Discovery, PRD, Prompt Library, and Sprint Plan all done. Week 1 is complete. **Ready for Week 2 build.** API key still needed before Week 2 Day 2. |

---

## ✅ Completed Tasks

| Date | Task |
|------|------|
| 7 Nov 2026 | Project scaffold: all directories, src stubs, harness, tests, CI, architecture diagram |
| 7 Nov 2026 | Python venv created, all packages installed, .env created |
| 7 Nov 2026 | Stage 1 Discovery: 5 interviews read, 500 tickets analysed, workbook filled |
| 7 Nov 2026 | Stage 1 + Stage 2 initial .docx generated |
| 9 Nov 2026 | Extraordinary Problem framework applied to both docs; FR-19 (resolution graph) added |
| 9 Nov 2026 | Stage 2 PRD rewritten in exact template format (9 sections, 18 FRs + 10 NFRs) |
| 9 Nov 2026 | **Stage 3 Prompt Library COMPLETE** — 4 actual prompts written (PR-CL-01, PR-GN-01, PR-RO-01, PR-EV-01), spec table for 16 FRs, traceability matrix, injection defence documented |
| 9 Nov 2026 | **Stage 4 Sprint Plan COMPLETE** — capacity, backlog B-01 to B-18, Week 2 day-by-day, Week 3 day-by-day, drop list, daily check-in template |

---

## 🔑 Key Decisions Made

| Decision | Rationale | Date |
|----------|-----------|------|
| SQLite for decision log | Sufficient at scale; no service to provision | 7 Nov |
| CONFIDENCE_THRESHOLD = 0.80 | Starting point; justify with calibration data Week 2 Day 5 | 7 Nov |
| Harness uses argparse --input/--output | A9 requirement — pointed at hidden 120-ticket set | 7 Nov |
| all-MiniLM-L6-v2 for embeddings | Local, no API cost, spec requirement | 7 Nov |
| meta-llama/llama-3.1-8b-instruct | Spec default; OpenRouter free tier | 7 Nov |
| **Extraordinary problem framing** | 71.4% answerable → collective intelligence waste, not delivery problem | 9 Nov |
| **FR-13: Resolution graph** | Network-effect exponent — FCR=True tickets logged as reusable records | 9 Nov |
| Escalation must carry context packet | Daniel: "context would make me twice as fast" | 7 Nov |
| Private snippet files excluded | Daniel: stale answers would scale mistakes | 7 Nov |
| 17.4% hard-blocked from auto-response | must_not_auto_respond=True on 87/500 tickets | 7 Nov |
| PR-RO-01 added as new prompt | Escalation context packet generation (FR-08) needs LLM for summary | 9 Nov |

---

## � Prompt Versions Active

| Prompt ID | Version | File | Status |
|-----------|---------|------|--------|
| PR-CL-01 | v1.0 (FULL) | `prompts/build/classify_v1.txt` | ✅ Written — 22 classes, 4 few-shot examples, confidence calibration |
| PR-GN-01 | v1.0 (FULL) | `prompts/build/generate_v1.txt` | ✅ Written — 8 rules, injection defence, citation format |
| PR-RO-01 | v1.0 (FULL) | `prompts/build/route_v1.txt` | ✅ Written — escalation context packet (summary + reason + docs) |
| PR-EV-01 | v1.0 (FULL) | `prompts/evaluation/eval_v1.txt` | ✅ Written — 4 evaluation criteria, JSON output |

---

## 📋 Requirement IDs (FR-01 to FR-18, NFR-01 to NFR-10)

| ID | Description | Code Module |
|----|-------------|-------------|
| FR-01 | Accept tickets from all 4 channels | src/ingest.py |
| FR-02 | Normalise all tickets to single representation | src/ingest.py |
| FR-03 | Classify with 22 intent classes | src/classify.py |
| FR-04 | Assign urgency (high/medium/low) | src/classify.py |
| FR-05 | Calibrated confidence score 0.0-1.0 | src/classify.py |
| FR-06 | Semantic search over 29 KB articles | src/retrieve.py |
| FR-07 | Return empty list when no match | src/retrieve.py |
| FR-08 | Hard-block must_not_auto_respond | src/route.py |
| FR-09 | Route using confidence threshold | src/route.py |
| FR-10 | Escalation context packet | src/route.py |
| FR-11 | Generated responses cite KB articles | src/generate.py |
| FR-12 | No generation without passages | src/generate.py |
| FR-13 | Guardrail 1: PII detection | src/guardrails.py |
| FR-14 | Guardrail 2: Grounding check | src/guardrails.py |
| FR-15 | Guardrail 3: Injection detection | src/guardrails.py |
| FR-16 | Guardrail 4: Tone/scope | src/guardrails.py |
| FR-17 | Guardrail 5: Confidence floor | src/guardrails.py |
| FR-18 | Every decision logged to SQLite | src/logging_store.py |
| NFR-01 | Latency P95 < 3s | evaluation/harness.py |
| NFR-02 | Availability ≥ 99.5% | Monitoring |
| NFR-03 | Intent precision ≥ 85% per class | evaluation/harness.py |
| NFR-04 | Hallucination rate ≤ 5% | evaluation/harness.py |
| NFR-05 | Citation accuracy ≥ 95% | evaluation/harness.py |
| NFR-06 | Zero PII in responses | src/guardrails.py |
| NFR-07 | Tier consistency < 5pp | evaluation/harness.py |
| NFR-08 | Language consistency < 5pp | evaluation/harness.py |
| NFR-09 | Decision log coverage 100% | src/logging_store.py |
| NFR-10 | Confidence calibration within 5pp | evaluation/harness.py |

> Note: FR-19 (resolution graph) was in the previous PRD version as a "Should" priority item. In the template-format PRD it is FR-13 (Should). The numbering shifted because the template uses the original FR-01 to FR-18 sequence from the capstone pack.

---

## 📊 Evaluation Results
> ⚠️ Fill in after Week 2 Day 5 gate run

| Metric | Target | Result | Run Date |
|--------|--------|--------|----------|
| Intent precision | ≥85% per class | — | — |
| Hallucination rate | ≤5% | — | — |
| Citation accuracy | ≥95% | — | — |
| Latency P95 | <3s | — | — |
| Escalation rate | ≤30% | — | — |
| FCR rate | ≥60% | — | — |

---

## ❓ Open Questions / Blockers

1. **⚠️ API key needed:** Open `.env`, replace `your_key_here` with OpenRouter key (https://openrouter.ai/ → Keys → Create key). Required before Week 2 Day 2 (retrieval) and Day 3 (classification).
2. **Threshold calibration:** `CONFIDENCE_THRESHOLD=0.80` is starting point. Final value set after Week 2 Day 5 gate run.
3. **Architecture diagram update:** `docs/architecture.md` predates extraordinary problem reframing. Update after Week 2 build starts.

---

## ⏭ Next Immediate Action
> **START HERE next session:**

**Week 2 — BUILD. Day 1 (Monday): Ingest + Harness Wiring**

1. Add OpenRouter API key to `.env` (5 min — do this FIRST)
2. Implement `src/ingest.py` → `normalize_ticket()` for all 4 channels
3. Run `pytest tests/test_ingest.py -v` — xfail tests should now PASS
4. Wire ingest into `evaluation/harness.py` → `process_ticket()` calls `normalize_ticket()`
5. Run: `python evaluation/harness.py --input data/validation_tickets.json --output evaluation/results/run_001.json`
6. Demo checkpoint: Print normalised object for one ticket from each of the 4 channels
7. Fill in daily check-in row in `Stage_4_Sprint_Plan.docx`
8. Update CONTEXT.md

**Sprint Plan reference:** B-01 (env setup — already done ✅) + B-02 (ingest) + B-05 (harness wiring)

---

## 📅 Session Log

| Date | Duration | What Was Done | Next Session Goal |
|------|----------|--------------|-------------------|
| 7 Nov | ~2 hrs | Full project scaffold created | Read project docs + set up env |
| 7 Nov | ~30 min | Python venv + packages installed, .env created | Add OpenRouter API key |
| 7 Nov | ~3 hrs | Stage 1 Discovery complete — 5 interviews, 500 tickets, workbook filled | Write PRD v1 |
| 7 Nov | ~2 hrs | Stage 1 + Stage 2 initial .docx generated | Apply Extraordinary Problem framework |
| 9 Nov | ~2 hrs | Extraordinary Problem framework applied; FR-19 (resolution graph) added | Rewrite PRD in template format |
| 9 Nov | ~1 hr | Stage 2 PRD rewritten in exact template format | Write Stage 3 + Stage 4 |
| 9 Nov | ~2 hrs | Stage 3 Prompt Library (4 prompts written) + Stage 4 Sprint Plan (backlog, day-by-day, drop list) | **Week 2 Day 1: Implement ingest.py + wire harness** |
