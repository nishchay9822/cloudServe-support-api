# Evaluation report - dev-final3

- Input: `data/development_tickets.json`  |  tickets: **500**  |  finished: 2026-11-13T06:50:09+00:00  |  wall time: 254.5s
- Model: `meta-llama/llama-3.1-8b-instruct`  |  confidence threshold: 0.85  |  labelled input: True

## Gate: unattended run

- Tickets processed: 500 / 500 | per-ticket errors: 0
- Decision log reconciles with tickets processed: **True** (500 logged)

## 1. Business outcomes (proxies, not live customer results)

- Escalation rate: system **0.21** vs baseline 0.562
- Auto-resolution proxy (auto-replied and docs can answer it): **0.628** vs baseline FCR 0.438
- Median time to first reply on auto-replies: **0.41 s** vs baseline median resolution 216 min
- Baseline repeat-contact rate 0.216; baseline CSAT 2.972; system CSAT: not measurable offline

## 2. Routing

- Auto-respond 395 / escalate 105 (auto rate 0.79)
- Route accuracy vs labels: **0.784**; false auto-respond 96; over-escalation 12; precision of auto-replies 0.757
- Safety-flagged tickets (must_not_auto_respond): 87; **auto-replied to: 0** []

## 3. Classification

- Intent accuracy **0.9979** (n=479); urgency accuracy 0.4969
- Classes with precision below 85%: none; methods used: {'knn': 452, 'llm+knn': 27}
- Top confusions: [{'true': 'rate_limit', 'pred': 'performance_degradation', 'count': 1}]

## 4. Retrieval

- hit@1 0.8739, hit@3 0.93, hit@5 0.9412 (n=357 answerable tickets)

## 5. Confidence calibration (stated vs observed intent accuracy)

| band | n | stated | observed | gap (pp) | within 5pp |
|---|---|---|---|---|---|
| 0.8-0.9 | 2 | 0.855 | 0.5 | 35.5 | False |
| 0.9-1.0 | 477 | 0.994 | 1.0 | 0.6 | True |

## 6. Latency

- All tickets: p50 421 ms, p95 931 ms. Auto-replies: p50 414 ms, **p95 859 ms** (target < 3000 ms: True)
- Model provider: 540 calls, 0 retries, 0 failures, 448760 tokens

## 7. Citations and answer quality

- Auto-replies 395; with a citation 1.0; citations that resolve 1.0; cited the expected article 0.8724
- Model-assessed (openai/gpt-4o-mini (independent model; a human second assessor is still required)), n=100: hallucination rate **0.0**, citations resolve 1.0, prohibited claims 0.0, required-point coverage 0.95, pass 0.95

## 8. Governance

- Outbound PII findings (independent re-scan): **0**
- Guardrail blocks by type: {'security_language': 21, 'grounding': 13}
- Why tickets were routed as they were: {'confident_and_grounded': 395, 'safety_intent': 66, 'safety_keyword': 21, 'guardrail_block': 13, 'safety_proximity': 4, 'no_passages': 1}
- Escalations with a complete context packet: 105 / 105
- Resolution records written (compounding signal): 212

## 9. Fairness by segment (groups with n < 15 are flagged)

**customer_tier**  - max gap (pp): {'auto_rate': 4.5, 'route_accuracy': 12.5, 'intent_accuracy': 0.6, 'retrieval_hit@1': 7.9}
- business: n=164, auto rate 0.7988, route acc 0.8476, intent acc 0.9936, retrieval hit@1 0.8537
- enterprise: n=83, auto rate 0.8193, route acc 0.7229, intent acc 1.0, retrieval hit@1 0.9322
- standard: n=253, auto rate 0.7747, route acc 0.7628, intent acc 1.0, retrieval hit@1 0.8686

**language_fluency**  - max gap (pp): {'auto_rate': 0.2, 'route_accuracy': 5.4, 'intent_accuracy': 0.9, 'retrieval_hit@1': 7.6}
- fluent: n=380, auto rate 0.7895, route acc 0.7711, intent acc 1.0, retrieval hit@1 0.8926
- non_fluent: n=120, auto rate 0.7917, route acc 0.825, intent acc 0.9911, retrieval hit@1 0.8161

**region**  - max gap (pp): {'auto_rate': 14.4, 'route_accuracy': 7.5, 'intent_accuracy': 0.6, 'retrieval_hit@1': 3.4}
- asia_pacific: n=119, auto rate 0.7227, route acc 0.7311, intent acc 1.0, retrieval hit@1 0.8947
- europe: n=151, auto rate 0.8013, route acc 0.8013, intent acc 1.0, retrieval hit@1 0.8609
- latin_america: n=60, auto rate 0.8667, route acc 0.7833, intent acc 1.0, retrieval hit@1 0.8837
- north_america: n=170, auto rate 0.8, route acc 0.8059, intent acc 0.9938, retrieval hit@1 0.8699

**channel**  - max gap (pp): {'auto_rate': 12.1, 'route_accuracy': 5.6, 'intent_accuracy': 0.7, 'retrieval_hit@1': 9.4}
- chat: n=155, auto rate 0.8516, route acc 0.8, intent acc 0.9933, retrieval hit@1 0.8908
- docs_comment: n=78, auto rate 0.7308, route acc 0.7436, intent acc 1.0, retrieval hit@1 0.9375
- email: n=212, auto rate 0.7594, route acc 0.7925, intent acc 1.0, retrieval hit@1 0.8431
- forum: n=55, auto rate 0.8182, route acc 0.7636, intent acc 1.0, retrieval hit@1 0.8649
