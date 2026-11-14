# Evaluation report - dev-v4

- Input: `data/development_tickets.json`  |  tickets: **500**  |  finished: 2026-11-14T18:30:20+00:00  |  wall time: 1538.1s
- Model: `meta-llama/llama-3.1-8b-instruct`  |  confidence threshold: 0.85  |  labelled input: True

## Gate: unattended run

- Tickets processed: 500 / 500 | per-ticket errors: 0
- Decision log reconciles with tickets processed: **True** (500 logged)

## 1. Business outcomes (proxies, not live customer results)

- Escalation rate: system **0.184** vs baseline 0.562
- Auto-resolution proxy (auto-replied and docs can answer it): **0.646** vs baseline FCR 0.438
- Median time to first reply on auto-replies: **0.37 s** vs baseline median resolution 216 min
- Baseline repeat-contact rate 0.216; baseline CSAT 2.972; system CSAT: not measurable offline

## 2. Routing

- Auto-respond 408 / escalate 92 (auto rate 0.816)
- Route accuracy vs labels: **0.794**; false auto-respond 100; over-escalation 3; precision of auto-replies 0.7549
- Safety-flagged tickets (must_not_auto_respond): 87; **auto-replied to: 0** []

## 3. Classification

- Intent accuracy **0.998** (n=500); urgency accuracy 0.522
- Classes with precision below 85%: none; methods used: {'knn': 473, 'llm+knn': 27}
- Top confusions: [{'true': 'rate_limit', 'pred': 'performance_degradation', 'count': 1}]

## 4. Retrieval

- hit@1 0.902, hit@3 0.958, hit@5 0.9692 (n=357 answerable tickets)

## 5. Confidence calibration (stated vs observed intent accuracy)

| band | n | stated | observed | gap (pp) | within 5pp |
|---|---|---|---|---|---|
| 0.8-0.9 | 2 | 0.855 | 0.5 | 35.5 | False |
| 0.9-1.0 | 498 | 0.994 | 1.0 | 0.6 | True |

## 6. Latency

- All tickets: p50 371 ms, p95 644 ms. Auto-replies: p50 371 ms, **p95 572 ms** (target < 3000 ms: True)
- Model provider: 471 calls, 3 retries, 0 failures, 442142 tokens

## 7. Citations and answer quality

- Auto-replies 408; with a citation 1.0; citations that resolve 1.0; cited the expected article 0.871
- Model-assessed (openai/gpt-4o-mini (independent model; a human second assessor is still required)), n=100: hallucination rate **0.0**, citations resolve 1.0, prohibited claims 0.0, required-point coverage 0.94, pass 0.94

## 8. Governance

- Outbound PII findings (independent re-scan): **0**
- Guardrail blocks by type: {'security_language': 21}
- Why tickets were routed as they were: {'confident_and_grounded': 408, 'safety_intent': 66, 'safety_keyword': 21, 'safety_proximity': 4, 'no_passages': 1}
- Escalations with a complete context packet: 92 / 92
- Resolution records written (compounding signal): 216

## 9. Fairness by segment (groups with n < 15 are flagged)

**customer_tier**  - max gap (pp): {'auto_rate': 5.7, 'route_accuracy': 8.9, 'intent_accuracy': 0.6, 'retrieval_hit@1': 6.3}
- business: n=164, auto rate 0.7988, route acc 0.8476, intent acc 0.9939, retrieval hit@1 0.8862
- enterprise: n=83, auto rate 0.8554, route acc 0.759, intent acc 1.0, retrieval hit@1 0.9492
- standard: n=253, auto rate 0.8142, route acc 0.7708, intent acc 1.0, retrieval hit@1 0.8971

**language_fluency**  - max gap (pp): {'auto_rate': 1.2, 'route_accuracy': 6.3, 'intent_accuracy': 0.8, 'retrieval_hit@1': 5.3}
- fluent: n=380, auto rate 0.8132, route acc 0.7789, intent acc 1.0, retrieval hit@1 0.9148
- non_fluent: n=120, auto rate 0.825, route acc 0.8417, intent acc 0.9917, retrieval hit@1 0.8621

**region**  - max gap (pp): {'auto_rate': 10.2, 'route_accuracy': 9.5, 'intent_accuracy': 0.6, 'retrieval_hit@1': 2.4}
- asia_pacific: n=119, auto rate 0.7647, route acc 0.7395, intent acc 1.0, retrieval hit@1 0.9079
- europe: n=151, auto rate 0.8344, route acc 0.8344, intent acc 1.0, retrieval hit@1 0.887
- latin_america: n=60, auto rate 0.8667, route acc 0.7833, intent acc 1.0, retrieval hit@1 0.907
- north_america: n=170, auto rate 0.8176, route acc 0.8, intent acc 0.9941, retrieval hit@1 0.9106

**channel**  - max gap (pp): {'auto_rate': 7.0, 'route_accuracy': 7.2, 'intent_accuracy': 0.6, 'retrieval_hit@1': 4.9}
- chat: n=155, auto rate 0.8516, route acc 0.8, intent acc 0.9935, retrieval hit@1 0.8992
- docs_comment: n=78, auto rate 0.7821, route acc 0.7436, intent acc 1.0, retrieval hit@1 0.9375
- email: n=212, auto rate 0.8019, route acc 0.816, intent acc 1.0, retrieval hit@1 0.8889
- forum: n=55, auto rate 0.8182, route acc 0.7636, intent acc 1.0, retrieval hit@1 0.9189
