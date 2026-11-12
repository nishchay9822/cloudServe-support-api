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
| Judge | gpt-4o-mini: 0/50 hallucinated, 0 prohibited | n=100: 0% halluc, 0% prohibited, 95% coverage |

Outage run (provider off): 80/80 processed, 80 escalated, 0 customer replies.

## Known Limitations (report honestly)
- Route and urgency labels are partly unpredictable: five signals failed; identical text has the same route label only 87.8% of the time, urgency 68.5%.
- Headline numbers flattered by templated data (254/500 dev tickets share text with another).
- FR-13 resolution records are write-only; compounding is NOT demonstrated.
- Fairness gaps on dev exceed the 5pp target (tier route-acc 9.4, region auto-rate 14.4, channel 9.5).
- Calibration populated only in the 0.9-1.0 band.
- Groq free tier: rate limits (429) make latency p50 7.1 s, p95 11 s, max 244 s; NFR p95 < 3 s NOT met on this tier. Daily token cap unknown; a 500-ticket dev run is ~400k tokens and may need splitting.
- Judge on Groq is gpt-oss-120b, a different family from the Qwen generator.

## Blockers
1. RESOLVED: OpenRouter credit added and working (Llama 3.1 8B generator, gpt-4o-mini judge). Groq kept as a zero-cost fallback (qwen/qwen3.8-27b, openai/gpt-oss-120b); free tier misses the p95 < 3 s target.
2. Human second-assessor hallucination review pending: `evaluation/results/gate_run_validation_human_review.csv`.
3. Key was pasted in chat: rotate it after the project.

## Next Immediate Actions
1. Done: gate re-run on OpenRouter (80/80, route acc 75%, auto precision 71.9%, p95 673 ms, judge 0/50) and dev judge n=100 (0% halluc, 95% coverage). Remaining: human second assessor.
2. Stage 6: Governance_Framework (risk register, fairness audit, kill switch, incident response), Prometheus/Grafana, report (20-30 pages), 20-minute video, effort log, package `NishchayGupta_Capstone_Submission.zip`. See `TIMELINE.md`.
3. Done this session: README, `.env.example`, `docs/architecture.md`, `docs/architecture.drawio`, CI imports. A1 verified from a fresh clone (Python 3.9, no key): 82 tests passed, harness exit 0. Needs Python 3.9 to 3.11 (3.15 fails dependency resolution).

## Session Log
- Stages 1-4 sessions: discovery, PRD v1, prompt library, sprint plan (commits up to c158448).
- Stage 5 session: built modules, found and fixed channel/label/prompt/chunking/latency bugs, ran gate (80/80), outage run, dev run (500/500), swapped to independent judge, hit 402 credit limit, produced PRD v2.0 and revision log, updated prompt register and this file.
- Wrap-up session: committed Stage 5, rewrote README/.env.example/architecture, added draw.io diagram, verified clean checkout (A1).
- Groq switch session: found Groq account has no Llama chat models; chose qwen/qwen3.8-27b (generator) and openai/gpt-oss-120b (judge). Added 429 Retry-After handling and gpt-oss reasoning_effort=low in src/llm.py; judge max_tokens 350 -> 900. Gate re-run on Groq (evaluation/results/gate_run_validation_groq.*): 80/80, 0 errors, intent 100%, route acc 76.3%, auto precision 73.0%, safety violations 0/14, PII 0, citations resolve 100%, judge 0/50 hallucination, 0 prohibited, 0 judge errors. 63 auto, 14 safety, 2 model_declined, 1 guardrail block.
- OpenRouter restored: final gate run (gate-openrouter-final) and dev rejudge n=100 completed; 82 tests passing.
