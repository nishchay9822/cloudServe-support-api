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
| Stage 6 | Governance, fairness audit, monitoring, report, effort log: DONE except author inputs. Video and packaging deliberately skipped for now. |
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

## Stage 6 Deliverables (done)
- `docs/Governance_Framework.docx`: 12 risks with proposed owners, fairness table, incident procedure (6 steps), kill switch answers, declaration.
- `evaluation/fairness_audit.py` + `results/fairness_dev|val.json/.md`: no significant route-accuracy gap on 500 tickets (intervals span 10-20 pp, so underpowered); one borderline confirmed retrieval gap (short tickets, p=0.046); val non-fluent gap (n=19) reversed on dev (n=120).
- Kill-switch drill `tests/test_kill_switch.py` (effect < 2 s, in-flight ticket finishes). Stale-article guard `DOC_MAX_AGE_DAYS` (R-05). Git history scanned: no credentials.
- `monitoring/`: Prometheus, alert rules, Grafana dashboard (5 views), replay script. NOT run (no Docker); `tests/test_monitoring.py` checks queried metrics exist.
- `docs/NishchayGupta_Capstone_Report.pdf`: 26 pages (24 to end of section 10), 7 figures, 17 tables; rebuild with `venv/bin/python3 docs/report/build_report.py` (needs `docs/requirements-report.txt`).
- `docs/Effort_Log.docx`: tasks/outputs filled from git; HOURS, hours available, signature and reflections to be confirmed by the author.
- 93 tests passing.

## Brief/Spec Audit and design alignment (second pass)
Design now follows the brief's figures: LangGraph orchestrator (src/pipeline.py), /tickets endpoint, response formatter, hybrid dense+BM25 retrieval (no measurable gain on 29 articles, weight 0.15), feedback loop (POST /feedback; corrections enter the neighbour index; feedback_total metric), routing order safety -> confidence -> evidence. SQLite kept instead of PostgreSQL (brief allows). Decision log now stores classifier alternatives.
Threshold: replaying routing showed 0.80 did nothing (confidence 0.99 on twins). evaluation/calibrate.py fits confidence on simulated unseen wording (twins + near-duplicates removed); chosen threshold 0.85 (lowest with >=99% intent accuracy of auto-answered); calibration error 0.3 pp. NOTE: the local .env still sets CONFIDENCE_THRESHOLD=0.80 and overrides the default; set it to 0.85 (all final runs used CONFIDENCE_THRESHOLD=0.85).
Safety: unseen wording exposed 3/87 restricted tickets auto-answered (former employee still has access). Added security-wording net + safety-proximity rule (0.10): now 0/87 in both settings.
Fairness (final system): CONFIRMED tier disparity - enterprise 12.5 pp and standard 8.5 pp below business in route accuracy (p=0.019, 0.036; unseen wording 16.7/11.1 pp, p=0.002/0.007). Exceeds 5-pp target. Cause not identified. Other dimensions not significant.
Grafana: Prometheus + Grafana run natively (no Docker) from /tmp/obs with the repo configs; datasource healthy, dashboard provisioned, 9 of 9 panel queries return data via Grafana API. (To stop: pkill -f prometheus; pkill -f "grafana server"; pkill -f "uvicorn src.api".)
Still true: validation set was used while debugging; hidden set never run; CSAT and repeat contacts not measurable offline.
PRD v2.0 docx and revision log do NOT yet include FR-21 (feedback loop), FR-22 (security wording/proximity), calibrated threshold, hybrid/LangGraph; they should become v2.1.

## Stage 6 Deliverables (done)
- `docs/Governance_Framework.docx`: 12 risks with proposed owners, fairness table, incident procedure (6 steps), kill switch answers, declaration.
- `evaluation/fairness_audit.py` + `results/fairness_dev|val.json/.md`: no significant route-accuracy gap on 500 tickets (intervals span 10-20 pp, so underpowered); one borderline confirmed retrieval gap (short tickets, p=0.046); val non-fluent gap (n=19) reversed on dev (n=120).
- Kill-switch drill `tests/test_kill_switch.py` (effect < 2 s, in-flight ticket finishes). Stale-article guard `DOC_MAX_AGE_DAYS` (R-05). Git history scanned: no credentials.
- `monitoring/`: Prometheus, alert rules, Grafana dashboard (5 views), replay script. NOT run (no Docker); `tests/test_monitoring.py` checks queried metrics exist.
- `docs/NishchayGupta_Capstone_Report.pdf`: 26 pages (24 to end of section 10), 7 figures, 17 tables; rebuild with `venv/bin/python3 docs/report/build_report.py` (needs `docs/requirements-report.txt`).
- `docs/Effort_Log.docx`: tasks/outputs filled from git; HOURS, hours available, signature and reflections to be confirmed by the author.
- 93 tests passing.

## Brief/Spec Audit (after reading 01_Project_Brief and 02_Build_Specification)
On track: all 12 acceptance criteria covered, unattended harness takes --input/--output and handles unlabelled and malformed input, graceful degradation, guardrails block, decision log reconciles.
Gaps found and handled: mean response time added to metrics (was missing); threshold_sweep.py shows the 0.80 threshold does no work on this data (confidence is ~0.99 for nearly all tickets), reported honestly; repeat-contacts row and the brief's FCR formula added to report; LangChain/LangGraph not used (justified in report + architecture.md); attribution added to README; Python 3.11 verified.
Not fixable / must be disclosed: the brief says do not look at or tune against the 80 validation tickets and use a hidden 120-ticket set once; validation WAS used while debugging. Hidden set never run. CSAT and repeat contacts not measurable offline. No response cache (spec encourages one). Generation output is text with inline citations, not JSON.

## Next Immediate Actions
1. AUTHOR: enter actual hours in `docs/Effort_Log.docx`, confirm the reflection drafts, sign. Export to `NishchayGupta_Effort_Log.pdf`.
2. AUTHOR: human second assessment of replies (`evaluation/results/gate_run_validation_human_review.csv`), then add the agreement figure to report section 7.
3. AUTHOR: read the report fully and confirm every claim; confirm risk owners; check dates (see below).
4. DATES: recorded phases (27 Oct to 9 Nov 2026) differ from git (7 to 12 Nov 2026), and both are after the printed deadline 13 Sept. Confirm the deadline year; commit history spans 6 days, not 3 weeks.
5. Run the Grafana stack once Docker is available; push to a remote and confirm GitHub Actions passes.
6. Skipped on request: video (18-22 min, structure in TIMELINE.md) and packaging (`NishchayGupta_Capstone_Submission.zip`: 01_Video, 02_Report, 03_Workbooks, 04_Source_Code).
7. Rotate the OpenRouter and Groq keys at project end.

## Session Log
- Stages 1-4 sessions: discovery, PRD v1, prompt library, sprint plan (commits up to c158448).
- Stage 5 session: built modules, found and fixed channel/label/prompt/chunking/latency bugs, ran gate (80/80), outage run, dev run (500/500), swapped to independent judge, hit 402 credit limit, produced PRD v2.0 and revision log, updated prompt register and this file.
- Wrap-up session: committed Stage 5, rewrote README/.env.example/architecture, added draw.io diagram, verified clean checkout (A1).
- Groq switch session: found Groq account has no Llama chat models; chose qwen/qwen3.8-27b (generator) and openai/gpt-oss-120b (judge). Added 429 Retry-After handling and gpt-oss reasoning_effort=low in src/llm.py; judge max_tokens 350 -> 900. Gate re-run on Groq (evaluation/results/gate_run_validation_groq.*): 80/80, 0 errors, intent 100%, route acc 76.3%, auto precision 73.0%, safety violations 0/14, PII 0, citations resolve 100%, judge 0/50 hallucination, 0 prohibited, 0 judge errors. 63 auto, 14 safety, 2 model_declined, 1 guardrail block.
- OpenRouter restored: final gate run (gate-openrouter-final) and dev rejudge n=100 completed; 82 tests passing.
- Stage 6 session: fairness audit, kill-switch drill, stale guard, governance workbook, monitoring config, 26-page report PDF, effort log (hours left for author). Video and packaging skipped on request.
