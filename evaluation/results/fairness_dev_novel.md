# Fairness audit: dev_run_novel090.json

Target: route-accuracy gap <= 5.0 pp. A gap is a *finding* only if it is above target AND p < 0.05 vs the best segment. Segments with n < 30 are marked low_n and excluded from 'best'.

## customer_tier  (best: business; max route-acc gap 16.7 pp; max auto-rate spread 3.3 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| business | 164 | 0.780 | 0.640 | 0.140 | 0.8537 | 0.854 (0.79-0.90) | 0.0 | 1.0 | no | 7.9 (0.1281) |
| enterprise | 83 | 0.759 | 0.530 | 0.229 | 0.9322 | 0.687 (0.58-0.78) | 16.7 | 0.002 | YES | 0.0 (1.0) |
| standard | 253 | 0.747 | 0.549 | 0.198 | 0.8686 | 0.743 (0.69-0.79) | 11.1 | 0.0071 | YES | 6.4 (0.1858) |

## language_fluency  (best: non_fluent; max route-acc gap 2.8 pp; max auto-rate spread 4.6 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| fluent | 380 | 0.771 | 0.571 | 0.200 | 0.8926 | 0.763 (0.72-0.80) | 2.8 | 0.5177 | no | 0.0 (1.0) |
| non_fluent | 120 | 0.725 | 0.592 | 0.133 | 0.8161 | 0.792 (0.71-0.85) | 0.0 | 1.0 | no | 7.6 (0.0615) |

## ticket_length  (best: short (<= 28 words); max route-acc gap 1.4 pp; max auto-rate spread 8.5 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| long (> 28 words) | 227 | 0.806 | 0.595 | 0.211 | 0.8957 | 0.762 (0.70-0.81) | 1.4 | 0.7024 | no | 0.0 (1.0) |
| short (<= 28 words) | 273 | 0.722 | 0.560 | 0.161 | 0.8557 | 0.777 (0.72-0.82) | 0.0 | 1.0 | no | 4.0 (0.2563) |

## region  (best: north_america; max route-acc gap 8.0 pp; max auto-rate spread 14.4 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| asia_pacific | 119 | 0.706 | 0.479 | 0.227 | 0.8947 | 0.714 (0.63-0.79) | 8.0 | 0.1172 | no | 0.0 (1.0) |
| europe | 151 | 0.762 | 0.616 | 0.146 | 0.8609 | 0.788 (0.72-0.85) | 0.6 | 0.8943 | no | 3.4 (0.4895) |
| latin_america | 60 | 0.850 | 0.633 | 0.217 | 0.8837 | 0.767 (0.65-0.86) | 2.7 | 0.6553 | no | 1.1 (0.8532) |
| north_america | 170 | 0.765 | 0.588 | 0.176 | 0.8699 | 0.794 (0.73-0.85) | 0.0 | 1.0 | no | 2.5 (0.6015) |

## channel  (best: email; max route-acc gap 5.2 pp; max auto-rate spread 12.6 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| chat | 155 | 0.813 | 0.632 | 0.181 | 0.8908 | 0.774 (0.70-0.83) | 0.9 | 0.8404 | no | 4.7 (0.353) |
| docs_comment | 78 | 0.692 | 0.474 | 0.218 | 0.9375 | 0.731 (0.62-0.82) | 5.2 | 0.3492 | no | 0.0 (1.0) |
| email | 212 | 0.731 | 0.571 | 0.160 | 0.8431 | 0.783 (0.72-0.83) | 0.0 | 1.0 | no | 9.4 (0.0944) |
| forum | 55 | 0.818 | 0.582 | 0.236 | 0.8649 | 0.764 (0.64-0.86) | 1.9 | 0.7575 | no | 7.3 (0.2555) |
