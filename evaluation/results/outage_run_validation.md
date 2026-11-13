# Evaluation report - outage-final4

- Input: `data/validation_tickets.json`  |  tickets: **80**  |  finished: 2026-11-13T21:01:07+00:00  |  wall time: 1.2s
- Model: `meta-llama/llama-3.1-8b-instruct`  |  confidence threshold: 0.85  |  labelled input: True

## Gate: unattended run

- Tickets processed: 80 / 80 | per-ticket errors: 0
- Decision log reconciles with tickets processed: **True** (80 logged)

## 1. Business outcomes (proxies, not live customer results)

- Escalation rate: system **1.0** vs baseline 0.5375
- Auto-resolution proxy (auto-replied and docs can answer it): **0.0** vs baseline FCR 0.4625
- Median time to first reply on auto-replies: **None s** vs baseline median resolution 227 min
- Baseline repeat-contact rate 0.2125; baseline CSAT 2.6; system CSAT: not measurable offline

## 2. Routing

- Auto-respond 0 / escalate 80 (auto rate 0.0)
- Route accuracy vs labels: **0.4**; false auto-respond 0; over-escalation 48; precision of auto-replies None
- Safety-flagged tickets (must_not_auto_respond): 14; **auto-replied to: 0** []

## 3. Classification

- Intent accuracy **1.0** (n=80); urgency accuracy 0.45
- Classes with precision below 85%: none; methods used: {'knn': 78, 'knn_fallback': 2}
- Top confusions: []

## 4. Retrieval

- hit@1 0.9434, hit@3 0.9811, hit@5 0.9811 (n=53 answerable tickets)

## 5. Confidence calibration (stated vs observed intent accuracy)

| band | n | stated | observed | gap (pp) | within 5pp |
|---|---|---|---|---|---|
| 0.9-1.0 | 80 | 0.994 | 1.0 | 0.6 | True |

## 6. Latency

- All tickets: p50 14 ms, p95 14 ms. Auto-replies: p50 None ms, **p95 None ms** (target < 3000 ms: None)
- Model provider: 0 calls, 0 retries, 0 failures, 0 tokens

## 7. Citations and answer quality

- Auto-replies 0; with a citation None; citations that resolve None; cited the expected article None
- Model-assessed hallucination check not run (use --judge N).

## 8. Governance

- Outbound PII findings (independent re-scan): **0**
- Guardrail blocks by type: {'security_language': 4}
- Why tickets were routed as they were: {'provider_unavailable': 66, 'safety_intent': 10, 'safety_keyword': 4}
- Escalations with a complete context packet: 80 / 80
- Resolution records written (compounding signal): 0

## 9. Fairness by segment (groups with n < 15 are flagged)

**customer_tier**  - max gap (pp): {'auto_rate': 0.0, 'route_accuracy': 20.0, 'intent_accuracy': 0.0, 'retrieval_hit@1': 8.0}
- business: n=30, auto rate 0.0, route acc 0.3, intent acc 1.0, retrieval hit@1 1.0
- enterprise: n=8 (low n), auto rate 0.0, route acc 0.25, intent acc 1.0, retrieval hit@1 0.8333
- standard: n=42, auto rate 0.0, route acc 0.5, intent acc 1.0, retrieval hit@1 0.92

**language_fluency**  - max gap (pp): {'auto_rate': 0.0, 'route_accuracy': 23.5, 'intent_accuracy': 0.0, 'retrieval_hit@1': 6.8}
- fluent: n=61, auto rate 0.0, route acc 0.3443, intent acc 1.0, retrieval hit@1 0.9318
- non_fluent: n=19, auto rate 0.0, route acc 0.5789, intent acc 1.0, retrieval hit@1 1.0

**region**  - max gap (pp): {'auto_rate': 0.0, 'route_accuracy': 19.6, 'intent_accuracy': 0.0, 'retrieval_hit@1': 10.5}
- asia_pacific: n=21, auto rate 0.0, route acc 0.2857, intent acc 1.0, retrieval hit@1 1.0
- europe: n=25, auto rate 0.0, route acc 0.36, intent acc 1.0, retrieval hit@1 0.8947
- latin_america: n=7 (low n), auto rate 0.0, route acc 0.5714, intent acc 1.0, retrieval hit@1 1.0
- north_america: n=27, auto rate 0.0, route acc 0.4815, intent acc 1.0, retrieval hit@1 0.9286

**channel**  - max gap (pp): {'auto_rate': 0.0, 'route_accuracy': 17.7, 'intent_accuracy': 0.0, 'retrieval_hit@1': 15.4}
- chat: n=22, auto rate 0.0, route acc 0.4091, intent acc 1.0, retrieval hit@1 0.8462
- docs_comment: n=16, auto rate 0.0, route acc 0.5, intent acc 1.0, retrieval hit@1 1.0
- email: n=31, auto rate 0.0, route acc 0.3226, intent acc 1.0, retrieval hit@1 0.9545
- forum: n=11 (low n), auto rate 0.0, route acc 0.4545, intent acc 1.0, retrieval hit@1 1.0
