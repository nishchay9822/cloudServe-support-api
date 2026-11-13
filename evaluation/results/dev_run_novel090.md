# Evaluation report - dev-novel090-final4

- Input: `data/development_tickets.json`  |  tickets: **500**  |  finished: 2026-11-13T20:57:49+00:00  |  wall time: 235.5s
- Model: `meta-llama/llama-3.1-8b-instruct`  |  confidence threshold: 0.85  |  labelled input: True

## Gate: unattended run

- Tickets processed: 500 / 500 | per-ticket errors: 0
- Decision log reconciles with tickets processed: **True** (500 logged)

## 1. Business outcomes (proxies, not live customer results)

- Escalation rate: system **0.24** vs baseline 0.562
- Auto-resolution proxy (auto-replied and docs can answer it): **0.606** vs baseline FCR 0.438
- Median time to first reply on auto-replies: **0.37 s** vs baseline median resolution 216 min
- Baseline repeat-contact rate 0.216; baseline CSAT 2.972; system CSAT: not measurable offline

## 2. Routing

- Auto-respond 380 / escalate 120 (auto rate 0.76)
- Route accuracy vs labels: **0.77**; false auto-respond 92; over-escalation 23; precision of auto-replies 0.7579
- Safety-flagged tickets (must_not_auto_respond): 87; **auto-replied to: 0** []

## 3. Classification

- Intent accuracy **0.984** (n=500); urgency accuracy 0.478
- Classes with precision below 85%: ['configuration_help']; methods used: {'knn': 419, 'llm+knn': 81}
- Top confusions: [{'true': 'onboarding', 'pred': 'configuration_help', 'count': 4}, {'true': 'security_incident', 'pred': 'account_access', 'count': 3}, {'true': 'rate_limit', 'pred': 'performance_degradation', 'count': 1}]

## 4. Retrieval

- hit@1 0.902, hit@3 0.958, hit@5 0.9692 (n=357 answerable tickets)

## 5. Confidence calibration (stated vs observed intent accuracy)

| band | n | stated | observed | gap (pp) | within 5pp |
|---|---|---|---|---|---|
| 0.8-0.9 | 28 | 0.872 | 0.821 | 5.1 | False |
| 0.9-1.0 | 472 | 0.994 | 0.994 | 0.0 | True |

## 6. Latency

- All tickets: p50 373 ms, p95 866 ms. Auto-replies: p50 366 ms, **p95 760 ms** (target < 3000 ms: True)
- Model provider: 594 calls, 0 retries, 0 failures, 557243 tokens

## 7. Citations and answer quality

- Auto-replies 380; with a citation 1.0; citations that resolve 1.0; cited the expected article 0.8781
- Model-assessed hallucination check not run (use --judge N).

## 8. Governance

- Outbound PII findings (independent re-scan): **0**
- Guardrail blocks by type: {'security_language': 21, 'grounding': 13}
- Why tickets were routed as they were: {'confident_and_grounded': 380, 'safety_intent': 66, 'safety_keyword': 21, 'safety_proximity': 17, 'guardrail_block': 13, 'low_confidence': 2, 'no_passages': 1}
- Escalations with a complete context packet: 120 / 120
- Resolution records written (compounding signal): 204

## 9. Fairness by segment (groups with n < 15 are flagged)

**customer_tier**  - max gap (pp): {'auto_rate': 3.3, 'route_accuracy': 16.7, 'intent_accuracy': 1.8, 'retrieval_hit@1': 6.3}
- business: n=164, auto rate 0.7805, route acc 0.8537, intent acc 0.9939, retrieval hit@1 0.8862
- enterprise: n=83, auto rate 0.759, route acc 0.6867, intent acc 0.9759, retrieval hit@1 0.9492
- standard: n=253, auto rate 0.747, route acc 0.7431, intent acc 0.9802, retrieval hit@1 0.8971

**language_fluency**  - max gap (pp): {'auto_rate': 4.6, 'route_accuracy': 2.8, 'intent_accuracy': 3.4, 'retrieval_hit@1': 5.3}
- fluent: n=380, auto rate 0.7711, route acc 0.7632, intent acc 0.9921, retrieval hit@1 0.9148
- non_fluent: n=120, auto rate 0.725, route acc 0.7917, intent acc 0.9583, retrieval hit@1 0.8621

**region**  - max gap (pp): {'auto_rate': 14.4, 'route_accuracy': 8.0, 'intent_accuracy': 3.3, 'retrieval_hit@1': 2.4}
- asia_pacific: n=119, auto rate 0.7059, route acc 0.7143, intent acc 0.9832, retrieval hit@1 0.9079
- europe: n=151, auto rate 0.7616, route acc 0.7881, intent acc 1.0, retrieval hit@1 0.887
- latin_america: n=60, auto rate 0.85, route acc 0.7667, intent acc 0.9667, retrieval hit@1 0.907
- north_america: n=170, auto rate 0.7647, route acc 0.7941, intent acc 0.9765, retrieval hit@1 0.9106

**channel**  - max gap (pp): {'auto_rate': 12.6, 'route_accuracy': 5.2, 'intent_accuracy': 4.5, 'retrieval_hit@1': 4.9}
- chat: n=155, auto rate 0.8129, route acc 0.7742, intent acc 0.9548, retrieval hit@1 0.8992
- docs_comment: n=78, auto rate 0.6923, route acc 0.7308, intent acc 0.9872, retrieval hit@1 0.9375
- email: n=212, auto rate 0.7311, route acc 0.783, intent acc 1.0, retrieval hit@1 0.8889
- forum: n=55, auto rate 0.8182, route acc 0.7636, intent acc 1.0, retrieval hit@1 0.9189
