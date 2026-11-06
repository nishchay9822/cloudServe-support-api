# CloudServe Intelligent Support System — FDE Capstone

An AI-powered customer support routing and response system built for CloudServe Solutions. The system receives support tickets from four channels (email, live chat, API documentation comments, and community forum), classifies each ticket for intent and urgency, retrieves relevant passages from the knowledge base, and decides whether to auto-generate a grounded response or escalate to a human agent with a prepared context packet. Every automated decision is logged for governance and audit purposes.

---

## Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd Final_Capstone_Project
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate       # macOS / Linux
# venv\Scripts\activate        # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```
Then open `.env` and fill in your `OPENROUTER_API_KEY`. All other values have working defaults.

> **Never commit `.env` to git.** It is in `.gitignore`.

### 5. Run the evaluation harness (validates the full pipeline)
```bash
python evaluation/harness.py \
  --input data/validation_tickets.json \
  --output evaluation/results/run_001.json
```

> **Note:** The evaluation harness always accepts `--input` and `--output` arguments. Never hardcode file paths. The harness will be pointed at a hidden evaluation set during grading.

---

## Running Tests

```bash
pytest tests/ -v
```

Tests in `tests/test_ingest.py` are marked `xfail` until Week 2 Day 1 implementation — that is expected.
Tests in `tests/test_harness.py` should pass immediately.

---

## Running the API

```bash
uvicorn src.api:app --reload
```

The API starts at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

Endpoints:
- `GET /health` — health check
- `POST /process` — process a support ticket through the full pipeline
- `GET /decisions/{ticket_id}` — retrieve decision log entries for a ticket

---

## Directory Structure

```
Final_Capstone_Project/
├── README.md                    ← This file
├── requirements.txt             ← Pinned dependencies
├── .env.example                 ← Environment variable template
├── .gitignore
├── CONTEXT.md                   ← Persistent session memory (update every session)
├── TIMELINE.md                  ← 3-week checklist with effort tracking
│
├── src/                         ← Core pipeline modules
│   ├── __init__.py
│   ├── ingest.py                ← Channel normalisation (A2)
│   ├── classify.py              ← Intent + urgency + confidence (A3)
│   ├── retrieve.py              ← Chroma RAG retrieval (A4)
│   ├── route.py                 ← Auto-respond vs escalate decision (A5)
│   ├── generate.py              ← Grounded response with citations (A6)
│   ├── guardrails.py            ← 5 guardrails, can block response (A7)
│   ├── logging_store.py         ← SQLite decision log (A8)
│   └── api.py                   ← FastAPI HTTP interface
│
├── prompts/                     ← Versioned prompt library
│   ├── README.md                ← Prompt register (version table)
│   ├── build/
│   │   ├── classify_v1.txt      ← Classification prompt
│   │   └── generate_v1.txt      ← Generation prompt
│   └── evaluation/
│       └── eval_v1.txt          ← Evaluation prompt
│
├── tests/
│   ├── __init__.py
│   ├── test_ingest.py           ← Ingest tests (xfail until Week 2 Day 1)
│   └── test_harness.py          ← Harness CLI tests (pass immediately)
│
├── evaluation/
│   ├── __init__.py
│   ├── harness.py               ← Evaluation harness (accepts --input/--output)
│   └── results/                 ← Output JSON files (gitignored via storage/)
│
├── docs/
│   └── architecture.md          ← System architecture diagram (Mermaid)
│
├── data/                        ← Datasets (never commit production secrets here)
│   ├── development_tickets.json ← 500 labelled tickets for development
│   ├── validation_tickets.json  ← 80 labelled tickets for validation
│   ├── ground_truth_responses.json ← 200 reference answers
│   └── documentation.json       ← 29 knowledge base articles
│
├── storage/                     ← Generated at runtime, NEVER committed
│   ├── chroma/                  ← Chroma vector store
│   └── decisions.db             ← SQLite decision log
│
└── .github/
    └── workflows/
        └── ci.yml               ← GitHub Actions CI
```

---

## Acceptance Criteria Reference

| Criterion | What it requires | Module |
|-----------|-----------------|--------|
| A1 | Runs from clean checkout following README | `README.md` |
| A2 | All 4 channels ingested and normalised | `src/ingest.py` |
| A3 | Every ticket classified with confidence 0–1 | `src/classify.py` |
| A4 | Retrieval runs against documentation corpus | `src/retrieve.py` |
| A5 | Routing applies threshold; deterministic | `src/route.py` |
| A6 | Generated answers cite retrieved passages | `src/generate.py` |
| A7 | At least one guardrail blocks when triggered | `src/guardrails.py` |
| A8 | Every decision written to persistent log | `src/logging_store.py` |
| A9 | Full evaluation set processed unattended | `evaluation/harness.py` |
| A10 | Metrics report produced automatically | `evaluation/harness.py` |
| A11 | Graceful failure on errors, no crashes | All modules |
| A12 | Tests run with one documented command | `pytest tests/ -v` |
