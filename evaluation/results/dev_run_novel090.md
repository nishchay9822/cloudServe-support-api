# Evaluation report - dev-novel090-final

- Input: `data/development_tickets.json`  |  tickets: **500**  |  finished: 2026-11-13T07:15:27+00:00  |  wall time: 1511.0s
- Model: `meta-llama/llama-3.1-8b-instruct`  |  confidence threshold: 0.85  |  labelled input: True

## Gate: unattended run

- Tickets processed: 500 / 500 | per-ticket errors: 0
- Decision log reconciles with tickets processed: **True** (500 logged)

## 1. Business outcomes (proxies, not live customer results)

- Escalation rate: system **0.24** vs baseline 0.562
- Auto-resolution proxy (auto-replied and docs can answer it): **0.606** vs baseline FCR 0.438
- Median time to first reply on auto-replies: **0.41 s** vs baseline median resolution 216 min
- Baseline repeat-contact rate 0.216; baseline CSAT 2.972; system CSAT: not measurable offline

## 2. Routing

- Auto-respond 380 / escalate 120 (auto rate 0.76)
- Route accuracy vs labels: **0.77**; false auto-respond 92; over-escalation 23; precision of auto-replies 0.7579
- Safety-flagged tickets (must_not_auto_respond): 87; **auto-replied to: 0** []

## 3. Classification

- Intent accuracy **0.9896** (n=479); urgency accuracy 0.4656
- Classes with precision below 85%: ['configuration_help']; methods used: {'knn': 402, 'llm+knn': 77}
- Top confusions: [{'true': 'onboarding', 'pred': 'configuration_help', 'count': 4}, {'true': 'rate_limit', 'pred': 'performance_degradation', 'count': 1}]

## 4. Retrieval

- hit@1 0.8739, hit@3 0.93, hit@5 0.9412 (n=357 answerable tickets)

## 5. Confidence calibration (stated vs observed intent accuracy)

| band | n | stated | observed | gap (pp) | within 5pp |
|---|---|---|---|---|---|
| 0.8-0.9 | 24 | 0.869 | 0.792 | 7.7 | False |
| 0.9-1.0 | 455 | 0.994 | 1.0 | 0.6 | True |

## 6. Latency

- All tickets: p50 426 ms, p95 927 ms. Auto-replies: p50 415 ms, **p95 884 ms** (target < 3000 ms: True)
- Model provider: 590 calls, 1 retries, 0 failures, 547913 tokens

## 7. Citations and answer quality

- Auto-replies 380; with a citation 1.0; citations that resolve 1.0; cited the expected article 0.8809
- Model-assessed hallucination check not run (use --judge N).

## 8. Governance

- Outbound PII findings (independent re-scan): **0**
- Guardrail blocks by type: {'security_language': 21, 'grounding': 13}
- Why tickets were routed as they were: {'confident_and_grounded': 380, 'safety_intent': 66, 'safety_keyword': 21, 'safety_proximity': 17, 'guardrail_block': 13, 'low_confidence': 2, 'no_passages': 1}
- Escalations with a complete context packet: 120 / 120
- Resolution records written (compounding signal): 204

## 9. Fairness by segment (groups with n < 15 are flagged)

**customer_tier**  - max gap (pp): {'auto_rate': 3.3, 'route_accuracy': 16.7, 'intent_accuracy': 0.6, 'retrieval_hit@1': 7.9}
- business: n=164, auto rate 0.7805, route acc 0.8537, intent acc 0.9936, retrieval hit@1 0.8537
- enterprise: n=83, auto rate 0.759, route acc 0.6867, intent acc 0.9875, retrieval hit@1 0.9322
- standard: n=253, auto rate 0.747, route acc 0.7431, intent acc 0.9876, retrieval hit@1 0.8686

**language_fluency**  - max gap (pp): {'auto_rate': 4.6, 'route_accuracy': 2.8, 'intent_accuracy': 2.1, 'retrieval_hit@1': 7.6}
- fluent: n=380, auto rate 0.7711, route acc 0.7632, intent acc 0.9946, retrieval hit@1 0.8926
- non_fluent: n=120, auto rate 0.725, route acc 0.7917, intent acc 0.9732, retrieval hit@1 0.8161

**region**  - max gap (pp): {'auto_rate': 14.4, 'route_accuracy': 8.0, 'intent_accuracy': 1.9, 'retrieval_hit@1': 3.4}
- asia_pacific: n=119, auto rate 0.7059, route acc 0.7143, intent acc 0.9913, retrieval hit@1 0.8947
- europe: n=151, auto rate 0.7616, route acc 0.7881, intent acc 1.0, retrieval hit@1 0.8609
- latin_america: n=60, auto rate 0.85, route acc 0.7667, intent acc 0.9828, retrieval hit@1 0.8837
- north_america: n=170, auto rate 0.7647, route acc 0.7941, intent acc 0.9812, retrieval hit@1 0.8699

**channel**  - max gap (pp): {'auto_rate': 12.6, 'route_accuracy': 5.2, 'intent_accuracy': 2.7, 'retrieval_hit@1': 9.4}
- chat: n=155, auto rate 0.8129, route acc 0.7742, intent acc 0.9732, retrieval hit@1 0.8908
- docs_comment: n=78, auto rate 0.6923, route acc 0.7308, intent acc 0.987, retrieval hit@1 0.9375
- email: n=212, auto rate 0.7311, route acc 0.783, intent acc 1.0, retrieval hit@1 0.8431
- forum: n=55, auto rate 0.8182, route acc 0.7636, intent acc 1.0, retrieval hit@1 0.8649
