# Project Context — CloudServe Capstone
> **Update this file at the END of every working session.**
> If you're starting a new session, **READ THIS FILE FIRST.**
> This is your persistent memory across sessions.

---

## 🗓 Last Updated
- **Date:** 7 November 2026
- **Session:** Initial scaffold

---

## 📍 Current Position
| Field | Value |
|-------|-------|
| **Week** | 1 |
| **Day** | 1 |
| **Stage** | Setup complete |
| **Status** | Scaffold done. Ready to begin reading project documents. No implementation code yet. |

---

## ✅ Completed Tasks

| Date | Task |
|------|------|
| 7 Nov 2026 | Project directory created at `/Users/nishchaygupta/Documents/Final_Capstone_Project` |
| 7 Nov 2026 | All directories scaffolded: `src/`, `prompts/`, `tests/`, `evaluation/`, `docs/`, `data/`, `storage/`, `.github/workflows/` |
| 7 Nov 2026 | All 4 datasets copied from Downloads → `data/`: `development_tickets.json` (500), `validation_tickets.json` (80), `ground_truth_responses.json` (200), `documentation.json` (29 articles) |
| 7 Nov 2026 | `requirements.txt` and `.env.example` copied from Capstone_Pack |
| 7 Nov 2026 | All 8 `src/` modules stubbed with correct signatures and docstrings (all import cleanly) |
| 7 Nov 2026 | `evaluation/harness.py` created with `--input`/`--output` CLI (A9-ready from day 1) |
| 7 Nov 2026 | `tests/test_ingest.py` created (channel validation tests pass; implementation tests marked xfail) |
| 7 Nov 2026 | `tests/test_harness.py` created (all tests pass immediately) |
| 7 Nov 2026 | `docs/architecture.md` created with full Mermaid diagram |
| 7 Nov 2026 | `.github/workflows/ci.yml` created |
| 7 Nov 2026 | `prompts/` register created with 3 prompt stubs |
| 7 Nov 2026 | `CONTEXT.md` and `TIMELINE.md` created |
| 7 Nov 2026 | `README.md`, `.gitignore` created |
| 7 Nov 2026 | Git repo initialized on `main` branch, first commit made |

---

## 🔑 Key Decisions Made

| Decision | Rationale | Date |
|----------|-----------|------|
| SQLite for decision log (not PostgreSQL) | Sufficient at this scale; no service to provision; spec says SQLite is fine | 7 Nov 2026 |
| Default `CONFIDENCE_THRESHOLD = 0.80` | Starting point from spec `.env.example`; will be justified with evaluation data in report | 7 Nov 2026 |
| Harness uses argparse `--input`/`--output` | A9 requirement — harness will be pointed at hidden 120-ticket set | 7 Nov 2026 |
| `all-MiniLM-L6-v2` for embeddings | Runs locally, no API cost, spec requirement | 7 Nov 2026 |
| `meta-llama/llama-3.1-8b-instruct` default model | Spec default; OpenRouter free tier | 7 Nov 2026 |

---

## 📋 Requirement IDs Defined
> ⚠️ Fill this in during **Week 1 Day 4** when writing the PRD.

| ID | Description | Discovery Evidence | Acceptance Test |
|----|-------------|-------------------|-----------------|
| FR-01 | *(pending — Week 1 Day 4)* | | |

---

## 📝 Prompt Versions Active

| Prompt ID | Version | File | Status |
|-----------|---------|------|--------|
| PR-CL-01 | v1.0 (stub) | `prompts/build/classify_v1.txt` | Stub only — write fully Week 1 Day 5 |
| PR-GN-01 | v1.0 (stub) | `prompts/build/generate_v1.txt` | Stub only — write fully Week 1 Day 5 |
| PR-EV-01 | v1.0 (stub) | `prompts/evaluation/eval_v1.txt` | Stub only — write fully Week 1 Day 5 |

---

## 📊 Evaluation Results
> ⚠️ Fill in after **Week 2 Day 5** gate run

| Metric | Target | Result | Run Date |
|--------|--------|--------|----------|
| Intent precision | ≥85% | — | — |
| Hallucination rate | ≤5% | — | — |
| Citation accuracy | ≥95% | — | — |
| Latency P95 | <3s | — | — |
| Escalation rate | ≤30% | — | — |
| FCR rate | ≥60% | — | — |

---

## ❓ Open Questions / Blockers

1. **API key needed:** Get OpenRouter API key before Week 2 Day 2 (retrieval + classification require LLM calls)
2. **Threshold decision:** Set final `CONFIDENCE_THRESHOLD` value after first evaluation run (Week 2 Day 5) — default 0.80 is a starting point
3. **Architecture review:** Review `docs/architecture.md` diagram after PRD v1 is written (Week 1 Day 4) to ensure it matches requirements

---

## ⏭ Next Immediate Action
> **START HERE next session:**

**Week 1 Day 1 — Afternoon: Read all core project documents IN THIS ORDER:**

1. Open: `/Users/nishchaygupta/Downloads/FDE_Capstone_Complete/Capstone_Pack/01_Read_First/00_Start_Here.docx` — 15 minutes
2. Open: `/Users/nishchaygupta/Downloads/FDE_Capstone_Complete/Capstone_Pack/01_Read_First/01_Project_Brief.docx` — 2-3 hours, do NOT skim
3. Open: `/Users/nishchaygupta/Downloads/FDE_Capstone_Complete/Capstone_Pack/04_Submission/Submission_Guide.docx` — 30 minutes
4. Open: `/Users/nishchaygupta/Downloads/FDE_Capstone_Complete/Capstone_Pack/01_Read_First/02_Build_Specification.docx` — 45 minutes (all 12 ACs)

**Then:** Set up Python virtual environment:
```bash
cd /Users/nishchaygupta/Documents/Final_Capstone_Project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Then:** Test that API key works (get one from https://openrouter.ai/ — free tier):
```bash
cp .env.example .env
# edit .env and add your OPENROUTER_API_KEY
python -c "from src import ingest, classify, retrieve; print('All imports OK')"
python evaluation/harness.py --input data/validation_tickets.json --output evaluation/results/test.json
```

---

## 📅 Session Log

| Date | Duration | What Was Done | Next Session Goal |
|------|----------|--------------|-------------------|
| 7 Nov 2026 | ~2 hrs | Full project scaffold created. All files stubbed, datasets copied, git initialized. | Read all project docs + set up Python env + test OpenRouter API |
