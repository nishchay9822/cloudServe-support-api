# Fairness audit: dev_run.json

Target: route-accuracy gap <= 5.0 pp. A gap is a *finding* only if it is above target AND p < 0.05 vs the best segment. Segments with n < 30 are marked low_n and excluded from 'best'.

## customer_tier  (best: business; max route-acc gap 12.5 pp; max auto-rate spread 4.5 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| business | 164 | 0.799 | 0.646 | 0.152 | 0.8862 | 0.848 (0.78-0.89) | 0.0 | 1.0 | no | 6.3 (0.1718) |
| enterprise | 83 | 0.819 | 0.578 | 0.241 | 0.9492 | 0.723 (0.62-0.81) | 12.5 | 0.0193 | YES | 0.0 (1.0) |
| standard | 253 | 0.775 | 0.573 | 0.202 | 0.8971 | 0.763 (0.71-0.81) | 8.5 | 0.0359 | YES | 5.2 (0.2268) |

## language_fluency  (best: non_fluent; max route-acc gap 5.4 pp; max auto-rate spread 0.2 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| fluent | 380 | 0.789 | 0.584 | 0.205 | 0.9148 | 0.771 (0.73-0.81) | 5.4 | 0.2106 | no | 0.0 (1.0) |
| non_fluent | 120 | 0.792 | 0.642 | 0.150 | 0.8621 | 0.825 (0.75-0.88) | 0.0 | 1.0 | no | 5.3 (0.1502) |

## ticket_length  (best: short (<= 28 words); max route-acc gap 5.6 pp; max auto-rate spread 6.2 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| long (> 28 words) | 227 | 0.824 | 0.599 | 0.225 | 0.9387 | 0.753 (0.69-0.80) | 5.6 | 0.1283 | no | 0.0 (1.0) |
| short (<= 28 words) | 273 | 0.762 | 0.597 | 0.165 | 0.8711 | 0.809 (0.76-0.85) | 0.0 | 1.0 | no | 6.8 (0.0326) QUALITY FINDING |

## region  (best: north_america; max route-acc gap 7.5 pp; max auto-rate spread 14.4 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| asia_pacific | 119 | 0.723 | 0.496 | 0.227 | 0.9079 | 0.731 (0.65-0.80) | 7.5 | 0.134 | no | 0.3 (0.949) |
| europe | 151 | 0.801 | 0.642 | 0.159 | 0.887 | 0.801 (0.73-0.86) | 0.5 | 0.9183 | no | 2.4 (0.5455) |
| latin_america | 60 | 0.867 | 0.650 | 0.217 | 0.907 | 0.783 (0.66-0.87) | 2.3 | 0.7074 | no | 0.4 (0.9436) |
| north_america | 170 | 0.800 | 0.612 | 0.188 | 0.9106 | 0.806 (0.74-0.86) | 0.0 | 1.0 | no | 0.0 (1.0) |

## channel  (best: chat; max route-acc gap 5.6 pp; max auto-rate spread 12.1 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| chat | 155 | 0.852 | 0.664 | 0.187 | 0.8992 | 0.800 (0.73-0.86) | 0.0 | 1.0 | no | 3.8 (0.4329) |
| docs_comment | 78 | 0.731 | 0.500 | 0.231 | 0.9375 | 0.744 (0.64-0.83) | 5.6 | 0.3257 | no | 0.0 (1.0) |
| email | 212 | 0.759 | 0.590 | 0.170 | 0.8889 | 0.792 (0.73-0.84) | 0.8 | 0.8594 | no | 4.9 (0.3263) |
| forum | 55 | 0.818 | 0.582 | 0.236 | 0.9189 | 0.764 (0.64-0.86) | 3.6 | 0.5692 | no | 1.9 (0.7402) |
