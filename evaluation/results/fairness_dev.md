# Fairness audit: dev_run.json

Target: route-accuracy gap <= 5.0 pp. A gap is a *finding* only if it is above target AND p < 0.05 vs the best segment. Segments with n < 30 are marked low_n and excluded from 'best'.

## customer_tier  (best: business; max route-acc gap 8.9 pp; max auto-rate spread 5.7 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| business | 164 | 0.799 | 0.646 | 0.152 | 0.8862 | 0.848 (0.78-0.89) | 0.0 | 1.0 | no | 6.3 (0.1718) |
| enterprise | 83 | 0.855 | 0.615 | 0.241 | 0.9492 | 0.759 (0.66-0.84) | 8.9 | 0.0887 | no | 0.0 (1.0) |
| standard | 253 | 0.814 | 0.597 | 0.217 | 0.8971 | 0.771 (0.72-0.82) | 7.7 | 0.055 | no | 5.2 (0.2268) |

## language_fluency  (best: non_fluent; max route-acc gap 6.3 pp; max auto-rate spread 1.2 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| fluent | 380 | 0.813 | 0.600 | 0.213 | 0.9148 | 0.779 (0.73-0.82) | 6.3 | 0.1386 | no | 0.0 (1.0) |
| non_fluent | 120 | 0.825 | 0.667 | 0.158 | 0.8621 | 0.842 (0.77-0.90) | 0.0 | 1.0 | no | 5.3 (0.1502) |

## ticket_length  (best: short (<= 28 words); max route-acc gap 8.3 pp; max auto-rate spread 5.5 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| long (> 28 words) | 227 | 0.846 | 0.608 | 0.238 | 0.9387 | 0.749 (0.69-0.80) | 8.3 | 0.023 | YES | 0.0 (1.0) |
| short (<= 28 words) | 273 | 0.791 | 0.623 | 0.169 | 0.8711 | 0.832 (0.78-0.87) | 0.0 | 1.0 | no | 6.8 (0.0326) QUALITY FINDING |

## region  (best: europe; max route-acc gap 9.5 pp; max auto-rate spread 10.2 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| asia_pacific | 119 | 0.765 | 0.521 | 0.244 | 0.9079 | 0.740 (0.65-0.81) | 9.5 | 0.0561 | no | 0.3 (0.949) |
| europe | 151 | 0.834 | 0.675 | 0.159 | 0.887 | 0.834 (0.77-0.89) | 0.0 | 1.0 | no | 2.4 (0.5455) |
| latin_america | 60 | 0.867 | 0.650 | 0.217 | 0.907 | 0.783 (0.66-0.87) | 5.1 | 0.3835 | no | 0.4 (0.9436) |
| north_america | 170 | 0.818 | 0.618 | 0.200 | 0.9106 | 0.800 (0.73-0.85) | 3.4 | 0.4266 | no | 0.0 (1.0) |

## channel  (best: email; max route-acc gap 7.2 pp; max auto-rate spread 7.0 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| chat | 155 | 0.852 | 0.664 | 0.187 | 0.8992 | 0.800 (0.73-0.86) | 1.6 | 0.6993 | no | 3.8 (0.4329) |
| docs_comment | 78 | 0.782 | 0.526 | 0.256 | 0.9375 | 0.744 (0.64-0.83) | 7.2 | 0.1742 | no | 0.0 (1.0) |
| email | 212 | 0.802 | 0.623 | 0.179 | 0.8889 | 0.816 (0.76-0.86) | 0.0 | 1.0 | no | 4.9 (0.3263) |
| forum | 55 | 0.818 | 0.582 | 0.236 | 0.9189 | 0.764 (0.64-0.86) | 5.2 | 0.3819 | no | 1.9 (0.7402) |
