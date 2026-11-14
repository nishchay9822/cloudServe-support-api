# CloudServe Intelligent Support System: FDE Capstone

An AI support system for CloudServe Solutions. It takes tickets from four channels (`email`, `chat`, `docs_comment`, `forum`), classifies intent and urgency, retrieves passages from the knowledge base, then either sends a grounded, cited reply or escalates to a human with a prepared context packet. Every decision is written to a persistent log.

Architecture: see `docs/architecture.md` and `docs/architecture.drawio` (open in draw.io / diagrams.net).

---

## Setup (Python 3.9 to 3.11; clean-checkout install and tests verified on 3.9 and 3.11)

```bash
git clone <your-repo-url>
cd Final_Capstone_Project
python3 -m venv venv
source venv/bin/activate          # macOS / Linux
pip install -r requirements.txt
cp .env.example .env              # then set OPENROUTER_API_KEY
```

Never commit `.env`. It is gitignored. All other variables have working defaults (see `.env.example`).

The first run downloads the `all-MiniLM-L6-v2` embedding model and builds the local Chroma index under `storage/`.

### No API key?
The pipeline still runs. With no key (or no credit), replies cannot be generated, so every ticket is escalated to a human with its context packet. No ticket is dropped and no unreviewed reply is sent (verified by the outage run: 80/80 processed, 80 escalated).

### Other providers
Any OpenAI-compatible endpoint works:
```bash
export LLM_BASE_URL=https://api.groq.com/openai/v1
export LLM_API_KEY=...
export MODEL_NAME=llama-3.1-8b-instant
```
(Groq switch is implemented but not tested against a live key.)

---

## Run the evaluation harness

```bash
python evaluation/harness.py \
  --input data/validation_tickets.json \
  --output evaluation/results/run_001.json
```

Options: `--max-tickets N`, `--judge N` (independent model assesses up to N replies), `--ground-truth PATH`, `--run-id ID`.

Outputs: the JSON file, a Markdown metrics report beside it, and a `*_human_review.csv` for the human second assessor. Exit code 0 means it finished the whole set; 2 means it could not start. The harness always takes `--input` and `--output`, so it can be pointed at any hidden set.

Provider-outage drill: run with the key unset. Expect every ticket processed, all escalated, no customer replies, no errors.

## Run the tests

```bash
pytest tests/ -v
```

115 tests, no network needed.

## Run the API

```bash
python -m src.api                 # or: uvicorn src.api:app --reload
```

Docs at `http://localhost:8000/docs`.

| Endpoint | Purpose |
|---|---|
| `GET /health` | Status, provider configured, kill switch state |
| `POST /tickets` (alias `/process`) | Run one ticket through the pipeline; always returns a decision |
| `POST /feedback`, `GET /feedback/summary` | A human correction returns to the system (stored, counted, added to the classifier's neighbour index) |
| `GET /decisions/{ticket_id}` | Decision log entries for a ticket |
| `GET /metrics` | Prometheus metrics |
| `POST /admin/kill-switch` | Body `{"on": true, "token": "<ADMIN_TOKEN>"}`. Sends all later tickets to humans |

Kill switch can also be set with `KILL_SWITCH=1` or by creating `storage/KILL_SWITCH`.

---

## How a ticket is decided

1. Ingest: normalise channel and fields, screen for prompt injection.
2. Classify: nearest labelled tickets; if vote share is below `KNN_TRUST` the LLM is also called and the two are combined. Confidence is calibrated on simulated unseen wording (`evaluation/calibrate.py`).
3. Retrieve: hybrid search (Chroma dense + BM25, reciprocal rank), one passage per document, minimum score `RETRIEVAL_MIN_SCORE`.
4. Route (deterministic code): safety wording or intent, restricted-topic neighbours, confidence below `CONFIDENCE_THRESHOLD` (0.85, chosen from data), then no passages, else auto-respond.
5. Generate: cited reply from the full top article. A `NO_ANSWER` reply escalates.
6. Guardrails: PII, grounding, figures, injection, tone. Any block escalates.
7. Log: decision, reason, sources, prompt version and requirement IDs go to SQLite.

Safety intents that always escalate: `security_incident`, `compliance_request`, `feature_request`, `unclear_request`.

---

## Evaluation settings, calibration, fairness audit, monitoring and the report

```bash
# Harder evaluation: classify each ticket as if its wording were new (removes same-text twins and near-duplicates)
python evaluation/harness.py --input data/development_tickets.json --output evaluation/results/dev_novel.json --novel-cap 0.90

# Refit confidence and choose the threshold from data (makes a few hundred model calls)
python evaluation/calibrate.py

# Segment a finished run by tier, fluency, length, region and channel (intervals + significance tests)
python evaluation/fairness_audit.py --run evaluation/results/dev_run.json \
  --tickets data/development_tickets.json --out evaluation/results/fairness_dev

# Prometheus + Grafana (needs Docker; start the API on port 8000 first)
docker compose -f monitoring/docker-compose.yml up -d     # Grafana http://localhost:3000
python monitoring/replay_traffic.py --n 60                 # send validation tickets so the dashboard has data

# Rebuild the report PDF (extra packages: pip install -r docs/requirements-report.txt)
python docs/report/build_report.py
```

The completed governance workbook is `docs/Governance_Framework.docx`; the effort log template is `docs/Effort_Log.docx`.

---
## Directory structure

```
Final_Capstone_Project/
├── README.md, requirements.txt, .env.example, CONTEXT.md, TIMELINE.md
├── src/
│   ├── ingest.py, classify.py, retrieve.py, route.py, generate.py
│   ├── guardrails.py, logging_store.py
│   ├── llm.py          ← provider client, retries, circuit breaker
│   ├── prompts.py      ← versioned prompt loader
│   ├── pipeline.py     ← process_ticket(), kill switch
│   ├── telemetry.py    ← Prometheus metrics
│   └── api.py          ← FastAPI
├── prompts/            ← versioned prompts + register (prompts/README.md)
├── evaluation/         ← harness.py, metrics.py, judge.py, analysis scripts, results/
├── tests/              ← 124 tests
├── monitoring/         ← Prometheus config, alert rules, Grafana dashboard, traffic replay
├── docs/               ← stage documents, architecture.md, architecture.drawio
├── data/               ← tickets, ground truth, documentation, calibration.json
├── storage/            ← runtime only (Chroma, decisions.db), never committed
└── .github/workflows/ci.yml
```

---

## Acceptance criteria map

| Criterion | Requirement | Module |
|---|---|---|
| A1 | Runs from clean checkout following this README | `README.md` |
| A2 | All 4 channels ingested and normalised | `src/ingest.py` |
| A3 | Every ticket classified with confidence 0 to 1 | `src/classify.py` |
| A4 | Retrieval against the documentation corpus | `src/retrieve.py` |
| A5 | Deterministic routing with threshold | `src/route.py` |
| A6 | Answers cite retrieved passages | `src/generate.py` |
| A7 | Guardrails block when triggered | `src/guardrails.py` |
| A8 | Every decision written to a persistent log | `src/logging_store.py` |
| A9 | Full set processed unattended | `evaluation/harness.py` |
| A10 | Metrics report produced automatically | `evaluation/harness.py`, `metrics.py` |
| A11 | Graceful failure, no crashes | all modules |
| A12 | Tests run with one command | `pytest tests/ -v` |

## Known limitations

See `CONTEXT.md`. In short: route and urgency labels are partly unpredictable from ticket text, headline accuracy is flattered by templated data, and the resolution-record learning loop (FR-13) is not demonstrated.

---
## Attribution and AI use

- Most of the source code, tests, evaluation scripts, workbook text and the report were drafted by **Kiro**, an AI coding assistant, in conversation with the author, who set the goals, supplied the data and decisions, and is responsible for the submission. The commit history shows the work as it happened.
- Runtime models: Llama 3.1 8B Instruct (generation and fallback classification, via OpenRouter), GPT-4o-mini and GPT-OSS-120B (independent judges), Qwen3.8-27B (Groq fallback), and `all-MiniLM-L6-v2` (local embeddings).
- Third-party libraries are listed in `requirements.txt` (FastAPI, Chroma, sentence-transformers, prometheus-client, python-docx and others). `langgraph` is the pipeline orchestrator (`src/pipeline.py`); `langchain` packages are listed because the brief suggests them but are not imported.
- No external code was knowingly copied. Templates for the workbooks come from the course pack.

