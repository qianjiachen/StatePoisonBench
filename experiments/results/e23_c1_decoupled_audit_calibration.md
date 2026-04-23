# C1 Detector-Decoupled External Audit Calibration

Generated at: 2026-04-12T17:43:11.978577+00:00

## Sample Composition

| Bucket | n |
|---|---:|
| state1_prompt1 | 12 |
| state1_prompt0 | 12 |
| state0_prompt1 | 12 |
| state0_prompt0 | 12 |
| total | 48 |

## Detector Metrics (External Label As Reference)

| Detector | Precision | Recall | FPR | F1 | Accuracy | TP/FP/TN/FN |
|---|---:|---:|---:|---:|---:|---|
| state_aware_auto | 0.083 | 0.667 | 0.489 | 0.148 | 0.521 | 2/22/23/1 |
| prompt_local_proxy | 0.000 | 0.000 | 0.044 | 0.000 | 0.896 | 0/2/43/3 |
| harmfulness_proxy | 0.500 | 0.667 | 0.044 | 0.572 | 0.938 | 2/2/43/1 |
| naive_text_proxy | 0.150 | 1.000 | 0.378 | 0.261 | 0.646 | 3/17/28/0 |
| prompt_any_proxy | 0.125 | 1.000 | 0.467 | 0.222 | 0.562 | 3/21/24/0 |

## Paired McNemar vs state_aware_auto

| Comparator | a-only discordant | b-only discordant | Exact p (2-sided) |
|---|---:|---:|---:|
| prompt_local_proxy | 2 | 20 | 0.000121 |
| harmfulness_proxy | 1 | 21 | 0.000011 |
| naive_text_proxy | 10 | 16 | 0.326940 |
| prompt_any_proxy | 11 | 13 | 0.838820 |

## Label Agreement (Author Reference vs External)

- Exact 3-way agreement: 26/48 (0.542)
- Binary agreement (clear vs non-clear): 47/48 (0.979)
