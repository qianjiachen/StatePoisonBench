# Supplementary Experiment Report

Generated at: 2026-04-01T10:45:46.232418+00:00
Random seed: 20260401

## S1. Clean vs Contaminated Causal Control
Overall violation rate rises from **0.178** (95% CI [0.154, 0.201]) to **0.541** (95% CI [0.509, 0.571]).
Paired delta = **0.363** (95% CI [0.324, 0.401]); McNemar p = 3.04e-65.

Family breakdown:
| Family | Clean | Contaminated | Delta | McNemar p |
|---|---:|---:|---:|---:|
| summary_poisoning | 0.195 | 0.500 | 0.305 | 2.72e-10 |
| recovery_state | 0.190 | 0.735 | 0.545 | 1.42e-26 |
| tool_mediated | 0.130 | 0.525 | 0.395 | 1.42e-16 |
| tool_failure | 0.145 | 0.395 | 0.250 | 2.25e-08 |
| recovered_context | 0.230 | 0.550 | 0.320 | 3.62e-11 |

## S2. RTG Safety-Utility Tradeoff
Recommended policy by utility-adjusted risk: **rtg_tau_0.50**

| Policy | Violation Rate | Success Rate | Avg Confirmations |
|---|---:|---:|---:|
| vanilla | 0.519 | 0.779 | 0.00 |
| rtg_tau_0.30 | 0.339 | 0.618 | 2.04 |
| rtg_tau_0.50 | 0.426 | 0.733 | 1.16 |
| rtg_tau_0.70 | 0.496 | 0.772 | 0.36 |
| rtg_tau_0.85 | 0.517 | 0.778 | 0.03 |

## S3. Annotation Reliability
Inter-annotator agreement = **0.819**, Cohen's kappa = **0.714** (95% CI [0.647, 0.775]).

Confusion matrix (A rows, B cols):
```text
148  14   2
 19  93   8
  4  18  54
```
