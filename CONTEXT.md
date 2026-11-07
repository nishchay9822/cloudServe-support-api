# Project Context — CloudServe Capstone
> **Update this file at the END of every working session.**
> If you're starting a new session, **READ THIS FILE FIRST.**
> This is your persistent memory across sessions.

---

## 🗓 Last Updated
- **Date:** 7 November 2026
- **Session:** Stage 1 Discovery — all 5 interviews read, ticket data analysed, workbook filled

---

## 📍 Current Position
| Field | Value |
|-------|-------|
| **Week** | 1 |
| **Day** | 2-3 |
| **Stage** | Stage 1 Discovery — COMPLETE |
| **Status** | All 5 interviews read. Ticket data analysed (500 tickets). Discovery workbook fully filled. Problem statement written and self-checked against all 5 stakeholders. Ready for Stage 2: PRD v1. |

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
| 7 Nov 2026 | Python venv created at `venv/` (Python 3.9.6) |
| 7 Nov 2026 | All dependencies installed — resolved version conflicts in original requirements.txt (langchain-openai/openai conflict, psycopg2 dropped in favour of SQLite) |
| 7 Nov 2026 | `pytest.ini` created — asyncio_mode=auto, warnings suppressed |
| 7 Nov 2026 | `.env` created from `.env.example` — **OpenRouter API key still needs to be filled in** |
| 7 Nov 2026 | All 18 tests pass: 13 passed, 5 xfailed (as expected) using venv |
| 7 Nov 2026 | **Stage 1 Discovery COMPLETE** — All 5 stakeholder interviews read, 500 tickets analysed, `docs/Stage_1_Discovery_Workbook_Filled.md` written with all 6 sections fully populated, problem statement written and self-checked |

---

## 🔑 Key Decisions Made

| Decision | Rationale | Date |
|----------|-----------|------|
| SQLite for decision log (not PostgreSQL) | Sufficient at this scale; no service to provision; spec says SQLite is fine | 7 Nov 2026 |
| Default `CONFIDENCE_THRESHOLD = 0.80` | Starting point from spec `.env.example`; will be justified with evaluation data in report | 7 Nov 2026 |
| Harness uses argparse `--input`/`--output` | A9 requirement — harness will be pointed at hidden 120-ticket set | 7 Nov 2026 |
| `all-MiniLM-L6-v2` for embeddings | Runs locally, no API cost, spec requirement | 7 Nov 2026 |
| `meta-llama/llama-3.1-8b-instruct` default model | Spec default; OpenRouter free tier | 7 Nov 2026 |
| **Build a retrieval system, NOT a generative chatbot** | 71.4% of tickets are answerable from existing 29 KB articles. The problem is delivery/findability, not knowledge generation. Confirmed by data against all 5 stakeholder accounts. | 7 Nov 2026 |
| **Escalation must carry context packet** | Daniel: "If an escalation arrived with context I would be twice as fast." Currently escalations are just raw ticket forwards. Context packet = summary + relevant docs + uncertainty reason. | 7 Nov 2026 |
| **Private snippet files excluded from retrieval corpus** | Daniel's explicit warning: snippet files contain outdated answers. Only the 29 reviewed KB articles are safe retrieval sources. | 7 Nov 2026 |
| **17.4% of tickets are hard-blocked from auto-response** | `must_not_auto_respond=True` on 87/500 tickets: security incidents, compliance requests, billing disputes, unclear requests. System must check this flag before any routing decision. | 7 Nov 2026 |

---

## � Key Discovery Findings (for PRD and Report)

| Finding | Evidence | Implication for design |
|---------|----------|----------------------|
| **71.4% of tickets are answerable from existing 29 KB articles** | `answerable_from_docs=True` in 357/500 tickets | Build a retrieval system, not a generative one. The answers exist — the system needs to find and surface them. |
| **Agents bypass KB search — use private snippet files instead** | Sofia + Ines interviews | Keyword search fails on vocabulary mismatch ("deployment keeps dying" ≠ "resolving container health check failures"). Semantic (embedding) search solves this directly. |
| **56.2% escalation rate; ~50% of those are tier-1 resolvable** | `history.escalated` = 281/500; Daniel interview; deployment 59% escalated but 70% answerable from docs | Reducing unnecessary escalations is the primary cost lever (4× cost ratio). Confidence threshold + draft response reduces this. |
| **Escalations arrive with no context** | Daniel interview (explicit) | Escalation must carry: 2-sentence summary + retrieved docs + reason for uncertainty. Non-negotiable design requirement. |
| **17.4% of tickets must never be auto-responded** | `must_not_auto_respond=True` on 87/500 | Security incidents, compliance, billing disputes, unclear requests. Hard block before routing. |
| **Enterprise FCR is worst (37.3%) despite premium agreements** | `customer_tier=enterprise`: FCR 37.3%, escalation 62.7% | Enterprise tickets are most complex. System should not claim to fix enterprise FCR — it helps standard/business most. Enterprise benefit comes from better escalation context. |
| **21.6% repeat contact rate** | `history.repeat_contact=True` on 108/500 | 1 in 5 tickets is a follow-up from insufficient first response. Improving first-contact quality directly eliminates this work. |
| **Sofia's non-fluent CSAT claim not confirmed by data** | Non-fluent CSAT: 3.04 vs Fluent: 2.95 | Vocabulary mismatch still affects retrieval quality for non-fluent customers; monitor per-segment metrics but do not over-engineer for non-fluent in v1. |

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

1. **⚠️ API key needed NOW:** Open `.env` and replace `your_key_here` with your OpenRouter key. Get one free at https://openrouter.ai/ → Sign in → Keys → Create key. Without this, Week 2 Day 2 (retrieval) and Day 3 (classification) will not work.
2. **Threshold decision:** Set final `CONFIDENCE_THRESHOLD` value after first evaluation run (Week 2 Day 5) — default 0.80 is a starting point
3. **Architecture review:** Review `docs/architecture.md` diagram after PRD v1 is written (Week 1 Day 4) to ensure it matches requirements

---

## ⏭ Next Immediate Action
> **START HERE next session:**

**Step 1 — Add your OpenRouter API key (5 minutes):**
1. Go to **https://openrouter.ai/** → Sign in with Google
2. Click **Keys** in left sidebar → **Create key** → name it `capstone` → copy the key (`sk-or-...`)
3. Open `.env` in the project root and replace `your_key_here` with your key
4. Verify it works:
```bash
cd /Users/nishchaygupta/Documents/Final_Capstone_Project
source venv/bin/activate
python -c "
from dotenv import load_dotenv; import os; load_dotenv()
from openai import OpenAI
client = OpenAI(base_url='https://openrouter.ai/api/v1', api_key=os.getenv('OPENROUTER_API_KEY'))
r = client.chat.completions.create(model='meta-llama/llama-3.1-8b-instruct', messages=[{'role':'user','content':'Say OK'}], max_tokens=5)
print('API works:', r.choices[0].message.content.strip())
"
```

**Step 2 — Read all core project documents IN THIS ORDER:**
1. `00_Start_Here.docx` in Downloads/FDE_Capstone_Complete (15 min)
2. `01_Project_Brief.docx` (2-3 hrs — do NOT skim governance/evaluation sections)
3. `Submission_Guide.docx` (30 min — know the finish line)
4. `02_Build_Specification.docx` (45 min — all 12 acceptance criteria)

---

## 📅 Session Log

| Date | Duration | What Was Done | Next Session Goal |
|------|----------|--------------|-------------------|
| 7 Nov 2026 | ~2 hrs | Full project scaffold created. All files stubbed, datasets copied, git initialized. | Read all project docs + set up Python env + test OpenRouter API |
| 7 Nov 2026 | ~30 min | Python venv created, all packages installed (resolved version conflicts in requirements.txt), .env created, 18 tests passing. | Add OpenRouter API key to .env, then read project docs |

---

## 📋 Requirement IDs Defined
> ⚠️ Fill this in during **Week 1 Day 4** when writing the PRD.

| ID | Description | Discovery Evidence | Acceptance Test |
|----|-------------|-------------------|-----------------|
| FR-01 | *(pending — Week 1 Day 4)* | | |

---

## ⏭ Next Immediate Action (updated after Stage 1)

**Stage 1 Discovery is complete.** Next: write PRD v1 (Stage 2, Week 1 Day 4).

**Tasks for next session:**
1. Open `Stage_2_PRD_Template.docx` from Downloads
2. Write all functional requirements (FR-01 through ~FR-15) with unique IDs and discovery evidence references — use findings in `docs/Stage_1_Discovery_Workbook_Filled.md`
3. Write non-functional requirements (NFR-01 through ~NFR-08): latency, availability, hallucination rate, citation accuracy, PII=0, fairness
4. Write out-of-scope section (feature requests, roadmap, novel incidents, private snippet files)
5. Update CONTEXT.md with all requirement IDs

**Key discovery inputs to use in PRD:**
- `71.4% answerable from docs` → drives retrieval requirement (FR)
- `Vocabulary mismatch (Sofia + Ines)` → drives semantic/embedding search requirement
- `Escalations without context (Daniel)` → drives escalation context packet requirement
- `17.4% must_not_auto_respond` → drives hard-block safety requirement
- `Explainability for compliance review (Marcus)` → drives decision logging requirement
- `Citation required (Ravi + Ines)` → drives grounding and citation requirements
- `Confidence calibration` → drives threshold + calibration requirement
- `Enterprise FCR worst (37.3%)` → drives per-tier monitoring in NFR

**Also still needed:** Add OpenRouter API key to `.env` before Week 2 Day 2 builds start.

---

## 📅 Session Log (updated)

| Date | Duration | What Was Done | Next Session Goal |
|------|----------|--------------|-------------------|
| 7 Nov 2026 | ~2 hrs | Full project scaffold created | Read project docs + set up Python env |
| 7 Nov 2026 | ~30 min | Python venv + all packages installed, .env created | Add OpenRouter API key, read project docs |
| 7 Nov 2026 | ~3 hrs | Stage 1 Discovery COMPLETE — all 5 interviews read, 500 tickets analysed, full workbook written at `docs/Stage_1_Discovery_Workbook_Filled.md` | Write PRD v1 (Stage 2) — use discovery findings |
