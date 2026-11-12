# Evaluation report - dev-final

- Input: `data/development_tickets.json`  |  tickets: **500**  |  finished: 2026-11-11T19:41:55+00:00  |  wall time: 204.7s
- Model: `meta-llama/llama-3.1-8b-instruct`  |  confidence threshold: 0.8  |  labelled input: True

## Gate: unattended run

- Tickets processed: 500 / 500 | per-ticket errors: 0
- Decision log reconciles with tickets processed: **True** (500 logged)

## 1. Business outcomes (proxies, not live customer results)

- Escalation rate: system **0.206** vs baseline 0.562
- Auto-resolution proxy (auto-replied and docs can answer it): **0.628** vs baseline FCR 0.438
- Median time to first reply on auto-replies: **0.35 s** vs baseline median resolution 216 min
- Baseline repeat-contact rate 0.216; baseline CSAT 2.972; system CSAT: not measurable offline

## 2. Routing

- Auto-respond 397 / escalate 103 (auto rate 0.794)
- Route accuracy vs labels: **0.78**; false auto-respond 98; over-escalation 12; precision of auto-replies 0.7531
- Safety-flagged tickets (must_not_auto_respond): 87; **auto-replied to: 0** []

## 3. Classification

- Intent accuracy **0.998** (n=500); urgency accuracy 0.518
- Classes with precision below 85%: none; methods used: {'knn': 473, 'llm+knn': 27}
- Top confusions: [{'true': 'rate_limit', 'pred': 'performance_degradation', 'count': 1}]

## 4. Retrieval

- hit@1 0.9048, hit@3 0.9552, hit@5 0.972 (n=357 answerable tickets)

## 5. Confidence calibration (stated vs observed intent accuracy)

| band | n | stated | observed | gap (pp) | within 5pp |
|---|---|---|---|---|---|
| 0.0-0.5 | 2 | 0.174 | 0.5 | 32.6 | False |
| 0.9-1.0 | 498 | 0.99 | 1.0 | 1.0 | True |

## 6. Latency

- All tickets: p50 357 ms, p95 689 ms. Auto-replies: p50 355 ms, **p95 508 ms** (target < 3000 ms: True)
- Model provider: 542 calls, 0 retries, 0 failures, 456097 tokens

## 7. Citations and answer quality

- Auto-replies 397; with a citation 1.0; citations that resolve 1.0; cited the expected article 0.8743
- Model-assessed (openai/gpt-4o-mini (independent model; a human second assessor is still required)), n=100: hallucination rate **0.0**, citations resolve 1.0, prohibited claims 0.0, required-point coverage 0.95, pass 0.95

## 8. Governance

- Outbound PII findings (independent re-scan): **0**
- Guardrail blocks by type: {'grounding': 15}
- Why tickets were routed as they were: {'confident_and_grounded': 397, 'safety_intent': 87, 'guardrail_block': 15, 'low_confidence': 1}
- Escalations with a complete context packet: 103 / 103
- Resolution records written (compounding signal): 211

## 9. Fairness by segment (groups with n < 15 are flagged)

**customer_tier**  - max gap (pp): {'auto_rate': 5.7, 'route_accuracy': 9.4, 'intent_accuracy': 0.6, 'retrieval_hit@1': 6.3}
- business: n=164, auto rate 0.8049, route acc 0.8293, intent acc 0.9939, retrieval hit@1 0.8862
- enterprise: n=83, auto rate 0.8313, route acc 0.7349, intent acc 1.0, retrieval hit@1 0.9492
- standard: n=253, auto rate 0.7747, route acc 0.7628, intent acc 1.0, retrieval hit@1 0.9029

**language_fluency**  - max gap (pp): {'auto_rate': 2.5, 'route_accuracy': 3.7, 'intent_accuracy': 0.8, 'retrieval_hit@1': 5.6}
- fluent: n=380, auto rate 0.8, route acc 0.7711, intent acc 1.0, retrieval hit@1 0.9185
- non_fluent: n=120, auto rate 0.775, route acc 0.8083, intent acc 0.9917, retrieval hit@1 0.8621

**region**  - max gap (pp): {'auto_rate': 14.4, 'route_accuracy': 7.7, 'intent_accuracy': 0.6, 'retrieval_hit@1': 3.2}
- asia_pacific: n=119, auto rate 0.7395, route acc 0.7311, intent acc 1.0, retrieval hit@1 0.9079
- europe: n=151, auto rate 0.8079, route acc 0.8079, intent acc 1.0, retrieval hit@1 0.887
- latin_america: n=60, auto rate 0.8833, route acc 0.7667, intent acc 1.0, retrieval hit@1 0.907
- north_america: n=170, auto rate 0.7882, route acc 0.7941, intent acc 0.9941, retrieval hit@1 0.9187

**channel**  - max gap (pp): {'auto_rate': 9.5, 'route_accuracy': 7.1, 'intent_accuracy': 0.6, 'retrieval_hit@1': 4.9}
- chat: n=155, auto rate 0.8387, route acc 0.7871, intent acc 0.9935, retrieval hit@1 0.9076
- docs_comment: n=78, auto rate 0.7436, route acc 0.7308, intent acc 1.0, retrieval hit@1 0.9375
- email: n=212, auto rate 0.7689, route acc 0.8019, intent acc 1.0, retrieval hit@1 0.8889
- forum: n=55, auto rate 0.8364, route acc 0.7455, intent acc 1.0, retrieval hit@1 0.9189
