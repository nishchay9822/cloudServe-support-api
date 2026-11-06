# Prompt Register

All prompts are versioned here. Format: `PR-{MODULE}-{NUMBER} v{MAJOR}.{MINOR}`

**Never modify a prompt file in-place.** Always:
1. Copy the file with the next version number (e.g. `classify_v2.txt`)
2. Make your changes in the new file
3. Update the table below with the new version and reason for change

---

## Active Prompts

| Prompt ID | Version | Purpose | File | Module | Requirement IDs | Last Updated |
|-----------|---------|---------|------|--------|-----------------|--------------|
| PR-CL-01 | v1.0 | Ticket intent + urgency classification | `prompts/build/classify_v1.txt` | `src/classify.py` | FR-03, FR-04 | [DATE] |
| PR-GN-01 | v1.0 | Grounded response generation with citations | `prompts/build/generate_v1.txt` | `src/generate.py` | FR-06, FR-07 | [DATE] |
| PR-EV-01 | v1.0 | Response quality evaluation / hallucination check | `prompts/evaluation/eval_v1.txt` | `evaluation/harness.py` | NFR-08, NFR-09 | [DATE] |

---

## Version History

| Prompt ID | Old Version | New Version | Change Summary | Reason | Date |
|-----------|-------------|-------------|---------------|--------|------|
| PR-CL-01 | — | v1.0 | Initial stub created | Scaffold | [DATE] |
| PR-GN-01 | — | v1.0 | Initial stub created | Scaffold | [DATE] |
| PR-EV-01 | — | v1.0 | Initial stub created | Scaffold | [DATE] |

---

## Traceability Check (complete before Week 2)

- [ ] Every functional requirement (FR-xx) has at least one prompt
- [ ] Every prompt has at least one requirement ID listed above
- [ ] Every prompt has been manually tested on at least 5 tickets
- [ ] Version numbers are incrementing (no in-place edits)
- [ ] Stage 3 Prompt Library workbook is filled in and matches this register

---

## Planned Prompts (add as needed)

| Prompt ID | Purpose | Required by |
|-----------|---------|-------------|
| PR-GD-01 | PII detection guardrail | FR-09 (guardrail 1) |
| PR-GD-02 | Grounding check guardrail | FR-10 (guardrail 2) |
| PR-GD-03 | Prompt injection detection | FR-11 (guardrail 3) |
