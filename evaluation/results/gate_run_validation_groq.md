# Evaluation report - gate-groq-validation

- Input: `data/validation_tickets.json`  |  tickets: **80**  |  finished: 2026-11-12T15:33:02+00:00  |  wall time: 743.5s
- Model: `qwen/qwen3.8-27b`  |  confidence threshold: 0.8  |  labelled input: True

## Gate: unattended run

- Tickets processed: 80 / 80 | per-ticket errors: 0
- Decision log reconciles with tickets processed: **True** (80 logged)

## 1. Business outcomes (proxies, not live customer results)

- Escalation rate: system **0.2125** vs baseline 0.5375
- Auto-resolution proxy (auto-replied and docs can answer it): **0.5875** vs baseline FCR 0.4625
- Median time to first reply on auto-replies: **6.76 s** vs baseline median resolution 227 min
- Baseline repeat-contact rate 0.2125; baseline CSAT 2.6; system CSAT: not measurable offline

## 2. Routing

- Auto-respond 63 / escalate 17 (auto rate 0.7875)
- Route accuracy vs labels: **0.7625**; false auto-respond 17; over-escalation 2; precision of auto-replies 0.7302
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

- All tickets: p50 7103 ms, p95 11062 ms. Auto-replies: p50 6757 ms, **p95 11062 ms** (target < 3000 ms: False)
- Model provider: 85 calls, 76 retries, 0 failures, 65788 tokens

## 7. Citations and answer quality

- Auto-replies 63; with a citation 1.0; citations that resolve 1.0; cited the expected article 0.8545
- Model-assessed (openai/gpt-oss-120b (independent model; a human second assessor is still required)), n=50: hallucination rate **0.0**, citations resolve 1.0, prohibited claims 0.0, required-point coverage 1.0, pass 1.0

## 8. Governance

- Outbound PII findings (independent re-scan): **0**
- Guardrail blocks by type: {'grounding': 1}
- Why tickets were routed as they were: {'confident_and_grounded': 63, 'safety_intent': 14, 'model_declined': 2, 'guardrail_block': 1}
- Escalations with a complete context packet: 17 / 17
- Resolution records written (compounding signal): 35

## 9. Fairness by segment (groups with n < 15 are flagged)

**customer_tier**  - max gap (pp): {'auto_rate': 26.7, 'route_accuracy': 2.9, 'intent_accuracy': 0.0, 'retrieval_hit@1': 8.0}
- business: n=30, auto rate 0.9333, route acc 0.7667, intent acc 1.0, retrieval hit@1 1.0
- enterprise: n=8 (low n), auto rate 0.875, route acc 0.875, intent acc 1.0, retrieval hit@1 0.8333
- standard: n=42, auto rate 0.6667, route acc 0.7381, intent acc 1.0, retrieval hit@1 0.92

**language_fluency**  - max gap (pp): {'auto_rate': 7.2, 'route_accuracy': 24.1, 'intent_accuracy': 0.0, 'retrieval_hit@1': 6.8}
- fluent: n=61, auto rate 0.7705, route acc 0.8197, intent acc 1.0, retrieval hit@1 0.9318
- non_fluent: n=19, auto rate 0.8421, route acc 0.5789, intent acc 1.0, retrieval hit@1 1.0

**region**  - max gap (pp): {'auto_rate': 14.5, 'route_accuracy': 14.3, 'intent_accuracy': 0.0, 'retrieval_hit@1': 10.5}
- asia_pacific: n=21, auto rate 0.9048, route acc 0.8095, intent acc 1.0, retrieval hit@1 1.0
- europe: n=25, auto rate 0.76, route acc 0.8, intent acc 1.0, retrieval hit@1 0.8947
- latin_america: n=7 (low n), auto rate 0.5714, route acc 0.8571, intent acc 1.0, retrieval hit@1 1.0
- north_america: n=27, auto rate 0.7778, route acc 0.6667, intent acc 1.0, retrieval hit@1 0.9286

**channel**  - max gap (pp): {'auto_rate': 18.4, 'route_accuracy': 7.1, 'intent_accuracy': 0.0, 'retrieval_hit@1': 15.4}
- chat: n=22, auto rate 0.7273, route acc 0.7727, intent acc 1.0, retrieval hit@1 0.8462
- docs_comment: n=16, auto rate 0.6875, route acc 0.8125, intent acc 1.0, retrieval hit@1 1.0
- email: n=31, auto rate 0.871, route acc 0.7419, intent acc 1.0, retrieval hit@1 0.9545
- forum: n=11 (low n), auto rate 0.8182, route acc 0.7273, intent acc 1.0, retrieval hit@1 1.0
