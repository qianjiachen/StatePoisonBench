# Reviewer-Facing Revision Experiments

Generated at: 2026-04-02T14:16:33.364165+00:00

## R1. Seed and Template Sensitivity

| Model Profile | Vanilla Mean +/- Std | RTG Mean +/- Std | RTG Better In All Runs | Gain Range |
|---|---:|---:|---:|---:|
| GPT-4o-like | 0.549 +/- 0.010 | 0.432 +/- 0.007 | Yes | 17.6%--24.0% |
| Qwen2.5-72B-like | 0.646 +/- 0.011 | 0.474 +/- 0.006 | Yes | 24.4%--29.6% |

## R2. Stateful Defense Baselines

| Policy | Overall Violation | Overall Success | Avg Interventions | Avg Extra Steps |
|---|---:|---:|---:|---:|
| Vanilla | 0.547 | 0.796 | 0.00 | 0.00 |
| Prompt-Local Filter | 0.540 | 0.798 | 0.18 | 0.08 |
| Intent-Drift Monitor | 0.486 | 0.760 | 0.76 | 0.44 |
| Memory Isolation | 0.438 | 0.730 | 1.27 | 0.91 |
| RTG | 0.485 | 0.756 | 1.09 | 0.62 |

Recovered-context family breakdown:
| Policy | Violation | Success |
|---|---:|---:|
| Vanilla | 0.590 | 0.755 |
| Prompt-Local Filter | 0.515 | 0.770 |
| Intent-Drift Monitor | 0.540 | 0.740 |
| Memory Isolation | 0.365 | 0.710 |
| RTG | 0.490 | 0.685 |

## R3. Direct API Pilot Calibration

| Model | Vanilla Failures | Vanilla Completion | RTG Failures | RTG Completion |
|---|---:|---:|---:|---:|
| gpt-5.4-mini | 0/12 | 10/12 | 0/12 | 11/12 |
| gpt-5.1-codex-mini | 0/12 | 7/12 | 0/12 | 5/12 |
| gpt-5.1-codex-max | 0/12 | 10/12 | 0/12 | 11/12 |

Across all audited direct-endpoint pilot episodes, clear contamination-positive failures = 0 / 72.
