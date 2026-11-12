# Project Context: CloudServe Capstone
> Update this file at the END of every working session.
> If you're starting a new session, READ THIS FILE FIRST.

---

## Last Updated
- Session: Stage 5 build + revision complete (code, gate, dev run, PRD v2.0, revision log)

## Current Position
| Field | Value |
|-------|-------|
| Phase 1 | Stages 1-4, 27 Oct to 2 Nov 2026 (done) |
| Phase 2 | Stage 5 Build + Revision, 2 Nov to 9 Nov 2026 (done, recorded as instructed) |
| Next | Stage 6: governance, report, video, packaging |
| Deadline | 13 Sept 2026, 23:59 (as set in the brief) |

NOTE: git commit and run timestamps show real dates of 7 to 11 Nov. Recorded phase dates were set by the user. Reconcile the effort log honestly. Do not rewrite git history.

## Completed (Stage 5)
- All `src/` modules: llm, prompts, ingest, retrieve, classify, route, generate, guardrails, logging_store, pipeline, telemetry, api.
- Harness `evaluation/harness.py` (unattended; exit 0 finished, 2 cannot start), metrics, independent judge, rejudge.
- 82 tests passing (`venv/bin/python3 -m pytest tests/ -q`).
- `docs/Stage_2_PRD_v2_0.docx` (v1 untouched) and `docs/Stage_5_PRD_Revision_Log.docx` (11 changed, 2 added, 0 removed).

## Key Decisions
- Channel is `docs_comment` (`api_comments` kept as alias); intent labels are the real 22.
- Classifier: kNN over dev tickets primary when vote share >= 0.85, else LLM combined. Confidence from classifier agreement (`data/calibration.json`).
- Safety rule from predicted intent: security_incident, compliance_request, feature_request, unclear_request.
- Routing is deterministic code: safety, no passages, confidence < 0.80, else auto_respond.
- Generator sees the full top article (+ runner-up if score >= 0.6x top). Prompt `generate_v3.txt`.
- Judge is `openai/gpt-4o-mini` (env `JUDGE_MODEL`), independent of the generator. Human second assessor still required.
- Provider configurable: `LLM_BASE_URL`, `LLM_API_KEY`, `MODEL_NAME`, `JUDGE_MODEL`, `LLM_PROVIDER_SORT`, `KILL_SWITCH`, `ADMIN_TOKEN`. HTTP 401/402 fail fast.
- Requirement numbering follows the PRD docx: FR-01..FR-18 plus FR-19, FR-20; NFR-01..NFR-10.

## Prompt Versions Active
PR-CL-01 v2.0, PR-GN-01 v3.0, PR-RO-01 v1.0, PR-EV-01 v1.0 (see `prompts/README.md`).

## Results
| | Validation (n=80, gate) | Dev (n=500, leave-one-out) |
|---|---|---|
| Processed | 80/80, 0 errors | 500/500, 0 errors |
| Intent accuracy | 100% | 99.8% |
| Urgency accuracy | 45% | 52% |
| Retrieval hit@1/@3/@5 | 94.3/96.2/98.1% | 90.5/95.5/97.2% |
| Auto-reply p95 latency | 636 ms | 508 ms |
| Route accuracy | 75% | 78% |
| Auto-reply precision | 72% | 75% |
| Safety violations | 0/14 | 0/87 |
| Outbound PII | 0 | 0 |
| Citations resolve | 100% | 100% |
| Judge | gpt-4o-mini: 0/50 hallucinated | n=25 only (credit ran out); earlier n=100: 0% halluc, 95% coverage |

Outage run (provider off): 80/80 processed, 80 escalated, 0 customer replies.

## Known Limitations (report honestly)
- Route and urgency labels are partly unpredictable: five signals failed; identical text has the same route label only 87.8% of the time, urgency 68.5%.
- Headline numbers flattered by templated data (254/500 dev tickets share text with another).
- FR-13 resolution records are write-only; compounding is NOT demonstrated.
- Fairness gaps on dev exceed the 5pp target (tier route-acc 9.4, region auto-rate 14.4, channel 9.5).
- Calibration populated only in the 0.9-1.0 band.
- Provider switch to Groq is built but untested.

## Blockers
1. OpenRouter key has no credit (HTTP 402). Add credit at openrouter.ai/settings/credits, or get a free Groq key.
2. Human second-assessor hallucination review pending: `evaluation/results/gate_run_validation_human_review.csv`.
3. Key was pasted in chat: rotate it after the project.

## Next Immediate Actions
1. After credit restored: `venv/bin/python3 evaluation/rejudge.py evaluation/results/dev_run.json --n 100`; optionally re-run the gate.
2. Still to update: root `README.md` run commands and env vars, `.env.example`, `docs/architecture.md` (kNN-first design), check `.github/workflows/ci.yml`.
3. Verify a clean checkout (clone, venv, pip install, pytest, harness per README).
4. Stage 6: Governance_Framework (risk register, fairness audit, kill switch, incident response), Prometheus/Grafana, report (20-30 pages), 20-minute video, effort log, package `NishchayGupta_Capstone_Submission.zip`. See `TIMELINE.md`.

## Session Log
- Stages 1-4 sessions: discovery, PRD v1, prompt library, sprint plan (commits up to c158448).
- Stage 5 session: built modules, found and fixed channel/label/prompt/chunking/latency bugs, ran gate (80/80), outage run, dev run (500/500), swapped to independent judge, hit 402 credit limit, produced PRD v2.0 and revision log, updated prompt register and this file.
