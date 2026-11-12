# Evaluation report - gate-validation-final

- Input: `data/validation_tickets.json`  |  tickets: **80**  |  finished: 2026-11-11T19:36:28+00:00  |  wall time: 38.0s
- Model: `meta-llama/llama-3.1-8b-instruct`  |  confidence threshold: 0.8  |  labelled input: True

## Gate: unattended run

- Tickets processed: 80 / 80 | per-ticket errors: 0
- Decision log reconciles with tickets processed: **True** (80 logged)

## 1. Business outcomes (proxies, not live customer results)

- Escalation rate: system **0.2** vs baseline 0.5375
- Auto-resolution proxy (auto-replied and docs can answer it): **0.5875** vs baseline FCR 0.4625
- Median time to first reply on auto-replies: **0.39 s** vs baseline median resolution 227 min
- Baseline repeat-contact rate 0.2125; baseline CSAT 2.6; system CSAT: not measurable offline

## 2. Routing

- Auto-respond 64 / escalate 16 (auto rate 0.8)
- Route accuracy vs labels: **0.75**; false auto-respond 18; over-escalation 2; precision of auto-replies 0.7188
- Safety-flagged tickets (must_not_auto_respond): 14; **auto-replied to: 0** []

## 3. Classification

- Intent accuracy **1.0** (n=80); urgency accuracy 0.45
- Classes with precision below 85%: none; methods used: {'knn': 78, 'llm+knn': 2}
- Top confusions: []

## 4. Retrieval

- hit@1 0.9434, hit@3 0.9623, hit@5 0.9811 (n=53 answerable tickets)

## 5. Confidence calibration (stated vs observed intent accuracy)

| band | n | stated | observed | gap (pp) | within 5pp |
|---|---|---|---|---|---|
| 0.9-1.0 | 80 | 0.99 | 1.0 | 1.0 | True |

## 6. Latency

- All tickets: p50 392 ms, p95 733 ms. Auto-replies: p50 387 ms, **p95 636 ms** (target < 3000 ms: True)
- Model provider: 84 calls, 0 retries, 0 failures, 65803 tokens

## 7. Citations and answer quality

- Auto-replies 64; with a citation 1.0; citations that resolve 1.0; cited the expected article 0.8654
- Model-assessed (openai/gpt-4o-mini (independent model; a human second assessor is still required)), n=50: hallucination rate **0.0**, citations resolve 1.0, prohibited claims 0.0, required-point coverage 1.0, pass 1.0

## 8. Governance

- Outbound PII findings (independent re-scan): **0**
- Guardrail blocks by type: {'grounding': 2}
- Why tickets were routed as they were: {'confident_and_grounded': 64, 'safety_intent': 14, 'guardrail_block': 2}
- Escalations with a complete context packet: 16 / 16
- Resolution records written (compounding signal): 35

## 9. Fairness by segment (groups with n < 15 are flagged)

**customer_tier**  - max gap (pp): {'auto_rate': 18.6, 'route_accuracy': 0.5, 'intent_accuracy': 0.0, 'retrieval_hit@1': 8.0}
- business: n=30, auto rate 0.9, route acc 0.7333, intent acc 1.0, retrieval hit@1 1.0
- enterprise: n=8 (low n), auto rate 0.875, route acc 0.875, intent acc 1.0, retrieval hit@1 0.8333
- standard: n=42, auto rate 0.7143, route acc 0.7381, intent acc 1.0, retrieval hit@1 0.92

**language_fluency**  - max gap (pp): {'auto_rate': 1.4, 'route_accuracy': 29.3, 'intent_accuracy': 0.0, 'retrieval_hit@1': 6.8}
- fluent: n=61, auto rate 0.8033, route acc 0.8197, intent acc 1.0, retrieval hit@1 0.9318
- non_fluent: n=19, auto rate 0.7895, route acc 0.5263, intent acc 1.0, retrieval hit@1 1.0

**region**  - max gap (pp): {'auto_rate': 3.0, 'route_accuracy': 9.6, 'intent_accuracy': 0.0, 'retrieval_hit@1': 10.5}
- asia_pacific: n=21, auto rate 0.8095, route acc 0.7143, intent acc 1.0, retrieval hit@1 1.0
- europe: n=25, auto rate 0.84, route acc 0.8, intent acc 1.0, retrieval hit@1 0.8947
- latin_america: n=7 (low n), auto rate 0.5714, route acc 0.8571, intent acc 1.0, retrieval hit@1 1.0
- north_america: n=27, auto rate 0.8148, route acc 0.7037, intent acc 1.0, retrieval hit@1 0.9286

**channel**  - max gap (pp): {'auto_rate': 21.6, 'route_accuracy': 8.7, 'intent_accuracy': 0.0, 'retrieval_hit@1': 15.4}
- chat: n=22, auto rate 0.7273, route acc 0.7727, intent acc 1.0, retrieval hit@1 0.8462
- docs_comment: n=16, auto rate 0.6875, route acc 0.6875, intent acc 1.0, retrieval hit@1 1.0
- email: n=31, auto rate 0.9032, route acc 0.7742, intent acc 1.0, retrieval hit@1 0.9545
- forum: n=11 (low n), auto rate 0.8182, route acc 0.7273, intent acc 1.0, retrieval hit@1 1.0
