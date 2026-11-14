# Build Specification compliance

Checked line by line against `02_Build_Specification.docx` on 14 November 2026. Status: **MET** (verified by a test or a run), **PARTLY** (works, with a stated limit) or **GAP** (not delivered). Every "evidence" entry can be re-run.

## 01 The gate

| Requirement | Status | Evidence |
|---|---|---|
| Starts from the documented instructions on a clean checkout | MET | Fresh clone, new virtual environment, `pip install -r requirements.txt`, tests and harness: Python 3.9, 3.11 and 3.12 all pass (115 tests, 8 to 80 tickets processed, exit 0, log reconciles). No key needed to start: without one every ticket escalates. |
| Processes the whole set unattended | MET | 80 of 80 validation, 500 of 500 development, and 123 of 123 on a shuffled, relabelled, unlabelled file with malformed entries (`None`, `{}`, a string, an empty body, control characters, an unknown channel). Exit code 0. 3 malformed entries escalated and logged. |
| Provider trouble never counts against the project; degrade gracefully | MET | Outage drill (key unset): 80 of 80 processed, 80 escalated, 0 replies, 0 errors. Unit tests for 429 (waits `Retry-After`), a long 429 (fails fast), timeouts, and exhausted credit (402 fails fast and opens the breaker). |

## 02 The twelve acceptance criteria

| # | Status | How it is shown |
|---|---|---|
| A1 clean checkout from the README | MET | Clean clones on 3.9, 3.11, 3.12. `.env.example` uses the pack's variable names (`OPENROUTER_API_KEY`, `MODEL_NAME`, ...). |
| A2 four channels, one representation | MET | `tests/test_ingest.py`; live API test with one ticket per channel (email, chat, docs_comment, forum). `api_comments` accepted as an alias. |
| A3 intent, urgency, confidence 0 to 1 | MET | Every result carries all three. Fallback `unclear_request` with confidence 0 when nothing can classify. |
| A4 retrieval resolves to real passages | MET | Every returned `doc_id` exists in `documentation.json`; hit@1 90.2% dev, 94.3% validation. |
| A5 same input, same decision | MET | Routing is pure code (100 repeats in `tests/test_route.py`); the same ticket run 5 times through the whole pipeline gave identical outcomes. |
| A6 citations resolve to retrieved text | MET | Citation resolution 100% in every run; unresolved citations are blocked by the grounding guardrail. |
| A7 a guardrail blocks when triggered | MET | Live, on the generated reply: a ticket asking about a made-up "time travel / --restore-snapshot" feature made the model invent content and the grounding guardrail blocked it (`guardrail_block`, escalated). Also: injection text is blocked before any model call; security wording forces escalation; unit tests for every guardrail. No flag disables them. |
| A8 every decision logged with the required fields | MET | One row per ticket including failures and escalations; all 17 fields of the governance record present (checked on a live row). Log count equals tickets processed in every run. |
| A9 full set, single unattended run, then a file never seen | MET | See the gate row. `python evaluation/harness.py` or `python -m evaluation.harness`, taking `--input` and `--output`. |
| A10 metrics report with no manual work | MET | JSON and Markdown written automatically; contains every group the spec lists (below). |
| A11 failure without crashing | MET | No retrieval hit (escalates), provider outage, timeout, rate limit, exhausted credit, malformed input: each has a test or a drill. |
| A12 one documented test command | MET | `pytest tests/ -v` (also `python -m pytest tests/ -v`), 115 tests, about 35 s, no network. |

## 03 Component behaviour

| Component | Requirement | Status | Note |
|---|---|---|---|
| Ingest | Four channels | MET | |
| | One normalised representation | MET | |
| | Preserves the original text and channel | MET (fixed in this review) | The cleaned fields are used downstream; untouched originals travel in `ticket["original"]`. Ground-truth fields are never copied. |
| | Missing fields, odd characters, empty bodies | MET | Tested, including an empty-ticket path. |
| Classify | Intent and urgency for every ticket | MET | Urgency accuracy is poor (about 50%, below the majority baseline) and is reported as a failure; it is not used for routing. |
| | Confidence reflects the probability of being right | MET, with a limit | Calibration error 0.3 pp on 1,500 simulated unseen-wording samples. Not yet checked on live traffic. |
| | Defined fallback, no exception | MET | |
| | Records the alternatives considered | MET (fixed in this review) | Alternatives were computed but written to the log as an empty list; now stored. They are empty when every neighbour agrees. |
| Retrieve | Ranked passages with scores | MET | |
| | Identifiers resolve to the real corpus | MET | |
| | Relevance threshold, returns nothing rather than something irrelevant | PARTLY | Floor 0.30 returns nothing for only 10 of 143 non-answerable development tickets. Raising it removes more but also loses correct hits (eval table in `evaluation/eval_retrieval.py`). The generator's NO_ANSWER and the guardrails are the second line. |
| | Chunking is a justified decision | MET | Section-level chunks for matching, whole article for generation; reasoning and the failure that motivated it are in report section 5. |
| Route | Threshold determined from data | MET (fixed in this review) | 0.85, from `evaluation/calibrate.py`. |
| | Deterministic | MET | |
| | Reason in language a support manager could read | MET | Plain-English reason plus a reason code on every decision. |
| | Escalations carry a drafted summary and the sources | MET (fixed in this review) | Escalations stopped early by the security-wording screen used to carry no sources; they now do. |
| Generate | Grounded, with citations on claims | MET | |
| | States plainly when it does not know | MET | NO_ANSWER sentinel escalates instead of replying. |
| | Customer text cannot redirect the system | MET | Injection screen before any model call; ticket passed as delimited data; guardrail re-check. |
| | Output in a defined structure the code can parse | PARTLY | The model writes plain text with inline `[DOC-ID]` markers and a NO_ANSWER sentinel; code turns that into a structured result (answer, citations, declined). Citations parse 100% of the time, but there is no JSON output contract. |
| Validate | Runs on every generated response | MET | There is no switch to disable it. |
| | Checks private data and unsupported claims | MET | Plus figures, injection, tone, confidence floor. |
| | Can block | MET | |
| | Records what it checked and found, blocked or not | MET | The full guardrail result is stored in the decision log for passes as well as blocks. |

## 04 The end-to-end run

| Requirement | Status |
|---|---|
| One documented command with input and output paths | MET |
| Every ticket produces a sent answer or a logged escalation; none dropped | MET (123 of 123 including malformed) |
| No intervention, restarts or skips | MET |
| Reasonable time | MET: 80 tickets about 40 s, 500 tickets about 4 minutes, on a laptop |
| Metrics report: volume (processed, answered, escalated, blocked) | MET |
| Business (first-contact resolution, mean and median response time, escalation rate) | MET (mean response time added in this review) |
| Technical (precision and recall per class, retrieval hit rate, latency p50 and p95) | MET |
| Governance (decisions logged, guardrail activations by type, private-data detections) | MET |
| Hallucination rate in the automatic report | PARTLY: needs an independent model, so it is produced with `--judge N`, not by default |

## 06 How it will be tested (procedure)

| Step | Status |
|---|---|
| Clean clone, README followed literally | MET (3.9, 3.11, 3.12) |
| Environment and dependencies as described | MET; all requirements pinned |
| Configuration from `.env.example` with a working key | MET. Defaults match the pack's own `.env.example`. |
| Started with the documented command | MET: `python -m src.api` now works (it did nothing before this review) |
| One ticket per channel | MET |
| A ticket engineered to trigger a guardrail | MET (see A7) |
| Full validation run left alone | MET |
| Metrics report and decision log reconciled | MET |
| Test suite with the documented command | MET |
| Repository searched for credentials and for attribution | MET: no keys in files or history; attribution section in the README |

## 07 Cost and free tiers

| Requirement | Status | Note |
|---|---|---|
| Free tiers only; nothing requires paid capacity | PARTLY | The pack's default (`meta-llama/llama-3.1-8b-instruct` on OpenRouter) needs credit on our account. Groq's free tier works (80 of 80, judged clean) but misses the 3-second p95 target there (11 s) because of rate limits. Embeddings and the vector store are free and local. |
| Rate limits handled by backoff, queuing, caching | PARTLY | Backoff, `Retry-After`, circuit breaker and a response cache (added in this review) are in. There is no request queue. |
| Local models permitted | NOT USED | Embeddings are local; generation is remote. |

## 08 What does not count as working (self-check)

| Item | Our position |
|---|---|
| Notebook run by hand | Not applicable; everything is scripted. |
| Five hand-picked tickets | Full sets of 80, 500 and 123. |
| Guardrails disabled by a flag during the run | No such flag exists. |
| Plausible-looking citations | Citations are resolved from retrieval and verified. |
| Retrieval that always returns something | See the PARTLY above. |
| Log written only for successes | Every ticket is logged, including failures, escalations and malformed input. |
| README written from memory | Followed literally on three Python versions. |
| Tuning against the hidden set | The hidden set was never available or used. The 80 validation tickets were used while debugging; this is disclosed in the report. |

## Open items that need a person
Human second assessment of replies (NFR-03), effort log hours and signature, risk owners, confirming the deadline year, and a live run of the Grafana stack on a machine with Docker. See `CONTEXT.md`.
