# Fairness audit: gate_run_validation.json

Target: route-accuracy gap <= 5.0 pp. A gap is a *finding* only if it is above target AND p < 0.05 vs the best segment. Segments with n < 30 are marked low_n and excluded from 'best'.

## customer_tier  (best: standard; max route-acc gap 0.5 pp; max auto-rate spread 18.6 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| business | 30 | 0.900 | 0.667 | 0.233 | 0.9545 | 0.733 (0.56-0.86) | 0.5 | 0.9639 | no | 0.0 (1.0) |
| enterprise (low n) | 8 | 0.750 | 0.625 | 0.125 | 0.8333 | 0.750 (0.41-0.93) | 0.0 | 1.0 | no | 12.1 (0.3068) |
| standard | 42 | 0.714 | 0.476 | 0.238 | 0.84 | 0.738 (0.59-0.85) | 0.0 | 1.0 | no | 11.5 (0.2038) |

## language_fluency  (best: fluent; max route-acc gap 0.0 pp; max auto-rate spread 0.0 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| fluent | 61 | 0.787 | 0.623 | 0.164 | 0.8864 | 0.803 (0.69-0.88) | 0.0 | 1.0 | no | 0.0 (1.0) |
| non_fluent (low n) | 19 | 0.789 | 0.368 | 0.421 | 0.8889 | 0.526 (0.32-0.73) | 27.7 | 0.0166 | suggestive (low n) | 0.0 (1.0) |

## ticket_length  (best: short (<= 27 words); max route-acc gap 1.4 pp; max auto-rate spread 19.4 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| long (> 27 words) | 37 | 0.892 | 0.622 | 0.270 | 0.8519 | 0.730 (0.57-0.85) | 1.4 | 0.8835 | no | 7.1 (0.4133) |
| short (<= 27 words) | 43 | 0.698 | 0.512 | 0.186 | 0.9231 | 0.744 (0.60-0.85) | 0.0 | 1.0 | no | 0.0 (1.0) |

## region  (best: latin_america; max route-acc gap 19.0 pp; max auto-rate spread 26.9 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| asia_pacific (low n) | 21 | 0.809 | 0.619 | 0.191 | 0.9412 | 0.714 (0.50-0.86) | 14.3 | 0.4497 | no | 5.9 (0.6665) |
| europe (low n) | 25 | 0.840 | 0.640 | 0.200 | 0.7895 | 0.800 (0.61-0.91) | 5.7 | 0.7321 | no | 21.1 (0.3796) |
| latin_america (low n) | 7 | 0.571 | 0.429 | 0.143 | 1.0 | 0.857 (0.49-0.97) | 0.0 | 1.0 | no | 0.0 (1.0) |
| north_america (low n) | 27 | 0.778 | 0.481 | 0.296 | 0.9286 | 0.667 (0.48-0.81) | 19.0 | 0.3243 | no | 7.1 (0.6333) |

## channel  (best: email; max route-acc gap 0.0 pp; max auto-rate spread 0.0 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| chat (low n) | 22 | 0.727 | 0.545 | 0.182 | 0.8462 | 0.773 (0.57-0.90) | 0.0 | 1.0 | no | 6.3 (0.5718) |
| docs_comment (low n) | 16 | 0.688 | 0.438 | 0.250 | 0.9 | 0.688 (0.44-0.86) | 5.4 | 0.6926 | no | 0.9 (0.9348) |
| email | 31 | 0.871 | 0.645 | 0.226 | 0.9091 | 0.742 (0.57-0.86) | 0.0 | 1.0 | no | 0.0 (1.0) |
| forum (low n) | 11 | 0.818 | 0.545 | 0.273 | 0.875 | 0.727 (0.43-0.90) | 1.5 | 0.9243 | no | 3.4 (0.7831) |
