# Fairness audit: dev_run.json

Target: route-accuracy gap <= 5.0 pp. A gap is a *finding* only if it is above target AND p < 0.05 vs the best segment. Segments with n < 30 are marked low_n and excluded from 'best'.

## customer_tier  (best: business; max route-acc gap 9.4 pp; max auto-rate spread 5.7 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| business | 164 | 0.805 | 0.640 | 0.165 | 0.8862 | 0.829 (0.76-0.88) | 0.0 | 1.0 | no | 6.3 (0.1718) |
| enterprise | 83 | 0.831 | 0.590 | 0.241 | 0.9492 | 0.735 (0.63-0.82) | 9.4 | 0.0814 | no | 0.0 (1.0) |
| standard | 253 | 0.775 | 0.573 | 0.202 | 0.9029 | 0.763 (0.71-0.81) | 6.7 | 0.1044 | no | 4.6 (0.2714) |

## language_fluency  (best: non_fluent; max route-acc gap 3.7 pp; max auto-rate spread 2.5 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| fluent | 380 | 0.800 | 0.590 | 0.210 | 0.9185 | 0.771 (0.73-0.81) | 3.7 | 0.3901 | no | 0.0 (1.0) |
| non_fluent | 120 | 0.775 | 0.625 | 0.150 | 0.8621 | 0.808 (0.73-0.87) | 0.0 | 1.0 | no | 5.6 (0.1188) |

## ticket_length  (best: short (<= 28 words); max route-acc gap 5.7 pp; max auto-rate spread 7.9 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| long (> 28 words) | 227 | 0.837 | 0.604 | 0.234 | 0.9387 | 0.749 (0.69-0.80) | 5.7 | 0.1258 | no | 0.0 (1.0) |
| short (<= 28 words) | 273 | 0.758 | 0.593 | 0.165 | 0.8763 | 0.806 (0.75-0.85) | 0.0 | 1.0 | no | 6.2 (0.0456) QUALITY FINDING |

## region  (best: europe; max route-acc gap 7.7 pp; max auto-rate spread 14.4 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| asia_pacific | 119 | 0.740 | 0.504 | 0.235 | 0.9079 | 0.731 (0.65-0.80) | 7.7 | 0.1338 | no | 1.1 (0.7911) |
| europe | 151 | 0.808 | 0.649 | 0.159 | 0.887 | 0.808 (0.74-0.86) | 0.0 | 1.0 | no | 3.2 (0.4075) |
| latin_america | 60 | 0.883 | 0.650 | 0.233 | 0.907 | 0.767 (0.65-0.86) | 4.1 | 0.5019 | no | 1.2 (0.8118) |
| north_america | 170 | 0.788 | 0.600 | 0.188 | 0.9187 | 0.794 (0.73-0.85) | 1.4 | 0.7569 | no | 0.0 (1.0) |

## channel  (best: email; max route-acc gap 7.1 pp; max auto-rate spread 9.5 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| chat | 155 | 0.839 | 0.652 | 0.187 | 0.9076 | 0.787 (0.72-0.84) | 1.5 | 0.7285 | no | 3.0 (0.5275) |
| docs_comment | 78 | 0.744 | 0.500 | 0.244 | 0.9375 | 0.731 (0.62-0.82) | 7.1 | 0.1928 | no | 0.0 (1.0) |
| email | 212 | 0.769 | 0.599 | 0.170 | 0.8889 | 0.802 (0.74-0.85) | 0.0 | 1.0 | no | 4.9 (0.3263) |
| forum | 55 | 0.836 | 0.582 | 0.255 | 0.9189 | 0.746 (0.62-0.84) | 5.6 | 0.3597 | no | 1.9 (0.7402) |
