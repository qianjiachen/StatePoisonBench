# C1 Detector-Decoupled External Audit Calibration

Generated at: 2026-04-12T17:33:20.504488+00:00

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
| state_aware_auto | 0.042 | 0.500 | 0.500 | 0.077 | 0.500 | 1/23/23/1 |
| prompt_local_proxy | 0.000 | 0.000 | 0.043 | 0.000 | 0.917 | 0/2/44/2 |
| harmfulness_proxy | 0.250 | 0.500 | 0.065 | 0.333 | 0.917 | 1/3/43/1 |
| naive_text_proxy | 0.100 | 1.000 | 0.391 | 0.182 | 0.625 | 2/18/28/0 |
| prompt_any_proxy | 0.083 | 1.000 | 0.478 | 0.153 | 0.542 | 2/22/24/0 |

## Paired McNemar vs state_aware_auto

| Comparator | a-only discordant | b-only discordant | Exact p (2-sided) |
|---|---:|---:|---:|
| prompt_local_proxy | 1 | 21 | 0.000011 |
| harmfulness_proxy | 1 | 21 | 0.000011 |
| naive_text_proxy | 10 | 16 | 0.326940 |
| prompt_any_proxy | 11 | 13 | 0.838820 |

## Label Agreement (Author Reference vs External)

- Exact 3-way agreement: 47/48 (0.979)
- Binary agreement (clear vs non-clear): 48/48 (1.000)
