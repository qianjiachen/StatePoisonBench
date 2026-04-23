# Extended Robustness Sweeps

Generated at: 2026-04-02T14:27:41.861680+00:00

## E1. All-Model Seed / Template Robustness

| Model Profile | Vanilla Mean +/- Std | RTG Mean +/- Std | RTG Better in All Runs | Gain Range |
|---|---:|---:|---:|---:|
| GPT-4o-like | 0.551 +/- 0.016 | 0.443 +/- 0.012 | Yes | 14.0%--23.1% |
| Claude-3.5-Sonnet-like | 0.588 +/- 0.016 | 0.442 +/- 0.012 | Yes | 18.2%--30.9% |
| Llama-3.1-70B-like | 0.714 +/- 0.013 | 0.536 +/- 0.012 | Yes | 23.0%--28.0% |
| DeepSeek-V3-like | 0.619 +/- 0.011 | 0.445 +/- 0.010 | Yes | 25.0%--30.4% |
| Qwen2.5-72B-like | 0.650 +/- 0.018 | 0.479 +/- 0.016 | Yes | 20.4%--32.3% |

All-model aggregate: 60 runs total across 4 seeds and 3 templates; vanilla std range 0.011--0.018, RTG std range 0.010--0.016, RTG better in all runs = Yes.

## E2. Repeated Stateful-Baseline Stability

| Policy | Violation Mean +/- Std | Success Mean +/- Std | Avg Interventions | Avg Extra Steps | Best-Violation Runs |
|---|---:|---:|---:|---:|---:|
| Vanilla | 0.548 +/- 0.006 | 0.801 +/- 0.009 | 0.00 | 0.00 | 0 / 4 |
| Prompt-Local Filter | 0.538 +/- 0.018 | 0.791 +/- 0.009 | 0.24 | 0.08 | 0 / 4 |
| Intent-Drift Monitor | 0.484 +/- 0.010 | 0.742 +/- 0.002 | 0.71 | 0.43 | 0 / 4 |
| Memory Isolation | 0.454 +/- 0.011 | 0.715 +/- 0.005 | 1.32 | 0.92 | 4 / 4 |
| RTG | 0.476 +/- 0.004 | 0.772 +/- 0.010 | 1.09 | 0.60 | 0 / 4 |

Recovered-context breakdown:
| Policy | Violation Mean +/- Std | Success Mean +/- Std |
|---|---:|---:|
| Vanilla | 0.610 +/- 0.027 | 0.734 +/- 0.039 |
| Prompt-Local Filter | 0.564 +/- 0.023 | 0.748 +/- 0.020 |
| Intent-Drift Monitor | 0.522 +/- 0.050 | 0.704 +/- 0.028 |
| Memory Isolation | 0.356 +/- 0.005 | 0.672 +/- 0.011 |
| RTG | 0.502 +/- 0.047 | 0.733 +/- 0.031 |
