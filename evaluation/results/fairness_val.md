# Fairness audit: gate_run_validation.json

Target: route-accuracy gap <= 5.0 pp. A gap is a *finding* only if it is above target AND p < 0.05 vs the best segment. Segments with n < 30 are marked low_n and excluded from 'best'.

## customer_tier  (best: business; max route-acc gap 0.5 pp; max auto-rate spread 19.5 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| business | 30 | 0.933 | 0.700 | 0.233 | 1.0 | 0.767 (0.59-0.88) | 0.0 | 1.0 | no | 0.0 (1.0) |
| enterprise (low n) | 8 | 0.875 | 0.750 | 0.125 | 0.8333 | 0.875 (0.53-0.98) | 0.0 | 1.0 | no | 16.7 (0.0512) |
| standard | 42 | 0.738 | 0.500 | 0.238 | 0.92 | 0.762 (0.61-0.87) | 0.5 | 0.9626 | no | 8.0 (0.1752) |

## language_fluency  (best: fluent; max route-acc gap 0.0 pp; max auto-rate spread 0.0 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| fluent | 61 | 0.820 | 0.656 | 0.164 | 0.9318 | 0.836 (0.72-0.91) | 0.0 | 1.0 | no | 0.0 (1.0) |
| non_fluent (low n) | 19 | 0.842 | 0.421 | 0.421 | 1.0 | 0.579 (0.36-0.77) | 25.7 | 0.0191 | suggestive (low n) | 0.0 (1.0) |

## ticket_length  (best: short (<= 27 words); max route-acc gap 8.4 pp; max auto-rate spread 12.5 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| long (> 27 words) | 37 | 0.892 | 0.622 | 0.270 | 0.963 | 0.730 (0.57-0.85) | 8.4 | 0.3684 | no | 0.0 (1.0) |
| short (<= 27 words) | 43 | 0.767 | 0.581 | 0.186 | 0.9231 | 0.814 (0.67-0.90) | 0.0 | 1.0 | no | 4.0 (0.5299) |

## region  (best: latin_america; max route-acc gap 15.3 pp; max auto-rate spread 33.3 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| asia_pacific (low n) | 21 | 0.905 | 0.714 | 0.191 | 1.0 | 0.809 (0.60-0.92) | 4.8 | 0.7757 | no | 0.0 (1.0) |
| europe (low n) | 25 | 0.840 | 0.640 | 0.200 | 0.8947 | 0.800 (0.61-0.91) | 5.7 | 0.7321 | no | 10.5 (0.1687) |
| latin_america (low n) | 7 | 0.571 | 0.429 | 0.143 | 1.0 | 0.857 (0.49-0.97) | 0.0 | 1.0 | no | 0.0 (1.0) |
| north_america (low n) | 27 | 0.815 | 0.518 | 0.296 | 0.9286 | 0.704 (0.52-0.84) | 15.3 | 0.4122 | no | 7.1 (0.2626) |

## channel  (best: email; max route-acc gap 0.0 pp; max auto-rate spread 0.0 pp)

| Segment | n | Auto rate | Resolution rate | False-auto rate | Quality (hit@1) | Route acc (95% CI) | Gap pp | p | Finding | Quality gap pp (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| chat (low n) | 22 | 0.773 | 0.591 | 0.182 | 0.8462 | 0.818 (0.61-0.93) | 0.0 | 1.0 | no | 15.4 (0.1943) |
| docs_comment (low n) | 16 | 0.750 | 0.500 | 0.250 | 1.0 | 0.750 (0.51-0.90) | 2.4 | 0.8527 | no | 0.0 (1.0) |
| email | 31 | 0.903 | 0.677 | 0.226 | 0.9545 | 0.774 (0.60-0.89) | 0.0 | 1.0 | no | 4.5 (0.4934) |
| forum (low n) | 11 | 0.818 | 0.545 | 0.273 | 1.0 | 0.727 (0.43-0.90) | 4.7 | 0.7536 | no | 0.0 (1.0) |
