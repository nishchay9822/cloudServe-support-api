# Evaluation report - gate-final3

- Input: `data/validation_tickets.json`  |  tickets: **80**  |  finished: 2026-11-13T07:16:14+00:00  |  wall time: 38.2s
- Model: `meta-llama/llama-3.1-8b-instruct`  |  confidence threshold: 0.85  |  labelled input: True

## Gate: unattended run

- Tickets processed: 80 / 80 | per-ticket errors: 0
- Decision log reconciles with tickets processed: **True** (80 logged)

## 1. Business outcomes (proxies, not live customer results)

- Escalation rate: system **0.2125** vs baseline 0.5375
- Auto-resolution proxy (auto-replied and docs can answer it): **0.575** vs baseline FCR 0.4625
- Median time to first reply on auto-replies: **0.39 s** vs baseline median resolution 227 min
- Baseline repeat-contact rate 0.2125; baseline CSAT 2.6; system CSAT: not measurable offline

## 2. Routing

- Auto-respond 63 / escalate 17 (auto rate 0.7875)
- Route accuracy vs labels: **0.7375**; false auto-respond 18; over-escalation 3; precision of auto-replies 0.7143
- Safety-flagged tickets (must_not_auto_respond): 14; **auto-replied to: 0** []

## 3. Classification

- Intent accuracy **1.0** (n=76); urgency accuracy 0.4342
- Classes with precision below 85%: none; methods used: {'knn': 74, 'llm+knn': 2}
- Top confusions: []

## 4. Retrieval

- hit@1 0.8868, hit@3 0.9245, hit@5 0.9245 (n=53 answerable tickets)

## 5. Confidence calibration (stated vs observed intent accuracy)

| band | n | stated | observed | gap (pp) | within 5pp |
|---|---|---|---|---|---|
| 0.9-1.0 | 76 | 0.994 | 1.0 | 0.6 | True |

## 6. Latency

- All tickets: p50 387 ms, p95 874 ms. Auto-replies: p50 389 ms, **p95 682 ms** (target < 3000 ms: True)
- Model provider: 85 calls, 0 retries, 0 failures, 65500 tokens

## 7. Citations and answer quality

- Auto-replies 63; with a citation 1.0; citations that resolve 1.0; cited the expected article 0.88
- Model-assessed (openai/gpt-4o-mini (independent model; a human second assessor is still required)), n=50: hallucination rate **0.0**, citations resolve 1.0, prohibited claims 0.0, required-point coverage 1.0, pass 1.0

## 8. Governance

- Outbound PII findings (independent re-scan): **0**
- Guardrail blocks by type: {'grounding': 3, 'security_language': 4}
- Why tickets were routed as they were: {'confident_and_grounded': 63, 'safety_intent': 10, 'guardrail_block': 3, 'safety_keyword': 4}
- Escalations with a complete context packet: 17 / 17
- Resolution records written (compounding signal): 34

## 9. Fairness by segment (groups with n < 15 are flagged)

**customer_tier**  - max gap (pp): {'auto_rate': 18.6, 'route_accuracy': 0.5, 'intent_accuracy': 0.0, 'retrieval_hit@1': 11.5}
- business: n=30, auto rate 0.9, route acc 0.7333, intent acc 1.0, retrieval hit@1 0.9545
- enterprise: n=8 (low n), auto rate 0.75, route acc 0.75, intent acc 1.0, retrieval hit@1 0.8333
- standard: n=42, auto rate 0.7143, route acc 0.7381, intent acc 1.0, retrieval hit@1 0.84

**language_fluency**  - max gap (pp): {'auto_rate': 0.3, 'route_accuracy': 27.7, 'intent_accuracy': 0.0, 'retrieval_hit@1': 0.3}
- fluent: n=61, auto rate 0.7869, route acc 0.8033, intent acc 1.0, retrieval hit@1 0.8864
- non_fluent: n=19, auto rate 0.7895, route acc 0.5263, intent acc 1.0, retrieval hit@1 0.8889

**region**  - max gap (pp): {'auto_rate': 6.2, 'route_accuracy': 13.3, 'intent_accuracy': 0.0, 'retrieval_hit@1': 15.2}
- asia_pacific: n=21, auto rate 0.8095, route acc 0.7143, intent acc 1.0, retrieval hit@1 0.9412
- europe: n=25, auto rate 0.84, route acc 0.8, intent acc 1.0, retrieval hit@1 0.7895
- latin_america: n=7 (low n), auto rate 0.5714, route acc 0.8571, intent acc 1.0, retrieval hit@1 1.0
- north_america: n=27, auto rate 0.7778, route acc 0.6667, intent acc 1.0, retrieval hit@1 0.9286

**channel**  - max gap (pp): {'auto_rate': 18.4, 'route_accuracy': 8.5, 'intent_accuracy': 0.0, 'retrieval_hit@1': 6.3}
- chat: n=22, auto rate 0.7273, route acc 0.7727, intent acc 1.0, retrieval hit@1 0.8462
- docs_comment: n=16, auto rate 0.6875, route acc 0.6875, intent acc 1.0, retrieval hit@1 0.9
- email: n=31, auto rate 0.871, route acc 0.7419, intent acc 1.0, retrieval hit@1 0.9091
- forum: n=11 (low n), auto rate 0.8182, route acc 0.7273, intent acc 1.0, retrieval hit@1 0.875
