# Fairness audit: dev_run_novel090.json

Target: route-accuracy gap <= 5.0 pp. A gap is a *finding* only if it is above target AND p < 0.05 vs the best segment. Segments with n < 30 are marked low_n and excluded from 'best'.

## customer_tier  (best: business; max route-acc gap 13.1 pp; max auto-rate spread 1.5 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| business | 164 | 0.780 | 0.640 | 0.140 | 0.8862 | 0.854 (0.79-0.90) | 0.0 | 1.0 | no | 6.3 (0.1718) |
| enterprise | 83 | 0.795 | 0.566 | 0.229 | 0.9492 | 0.723 (0.62-0.81) | 13.1 | 0.0134 | YES | 0.0 (1.0) |
| standard | 253 | 0.787 | 0.573 | 0.213 | 0.8971 | 0.751 (0.69-0.80) | 10.3 | 0.0117 | YES | 5.2 (0.2268) |

## language_fluency  (best: non_fluent; max route-acc gap 3.7 pp; max auto-rate spread 3.6 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| fluent | 380 | 0.795 | 0.587 | 0.208 | 0.9148 | 0.771 (0.73-0.81) | 3.7 | 0.3901 | no | 0.0 (1.0) |
| non_fluent | 120 | 0.758 | 0.617 | 0.142 | 0.8621 | 0.808 (0.73-0.87) | 0.0 | 1.0 | no | 5.3 (0.1502) |

## ticket_length  (best: short (<= 28 words); max route-acc gap 4.1 pp; max auto-rate spread 7.7 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| long (> 28 words) | 227 | 0.828 | 0.604 | 0.225 | 0.9387 | 0.758 (0.70-0.81) | 4.1 | 0.2726 | no | 0.0 (1.0) |
| short (<= 28 words) | 273 | 0.751 | 0.586 | 0.165 | 0.8711 | 0.798 (0.75-0.84) | 0.0 | 1.0 | no | 6.8 (0.0326) QUALITY FINDING |

## region  (best: europe; max route-acc gap 9.9 pp; max auto-rate spread 10.2 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| asia_pacific | 119 | 0.748 | 0.504 | 0.244 | 0.9079 | 0.723 (0.64-0.80) | 9.9 | 0.0532 | no | 0.3 (0.949) |
| europe | 151 | 0.795 | 0.649 | 0.146 | 0.887 | 0.821 (0.75-0.87) | 0.0 | 1.0 | no | 2.4 (0.5455) |
| latin_america | 60 | 0.850 | 0.633 | 0.217 | 0.907 | 0.767 (0.65-0.86) | 5.4 | 0.3665 | no | 0.4 (0.9436) |
| north_america | 170 | 0.782 | 0.594 | 0.188 | 0.9106 | 0.788 (0.72-0.84) | 3.3 | 0.4581 | no | 0.0 (1.0) |

## channel  (best: email; max route-acc gap 7.6 pp; max auto-rate spread 7.5 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| chat | 155 | 0.813 | 0.632 | 0.181 | 0.8992 | 0.774 (0.70-0.83) | 3.2 | 0.4492 | no | 3.8 (0.4329) |
| docs_comment | 78 | 0.744 | 0.500 | 0.244 | 0.9375 | 0.731 (0.62-0.82) | 7.6 | 0.1625 | no | 0.0 (1.0) |
| email | 212 | 0.774 | 0.604 | 0.170 | 0.8889 | 0.807 (0.75-0.85) | 0.0 | 1.0 | no | 4.9 (0.3263) |
| forum | 55 | 0.818 | 0.582 | 0.236 | 0.9189 | 0.764 (0.64-0.86) | 4.3 | 0.4796 | no | 1.9 (0.7402) |
