# Extended Robustness Sweeps

Generated at: 2026-04-02T14:29:02.618468+00:00

## E1. All-Model Seed / Template Robustness

| Model Profile | Vanilla Mean +/- Std | RTG Mean +/- Std | RTG Better in All Runs | Gain Range |
|---|---:|---:|---:|---:|
| GPT-4o-like | 0.552 +/- 0.011 | 0.432 +/- 0.010 | Yes | 15.3%--25.5% |
| Claude-3.5-Sonnet-like | 0.592 +/- 0.011 | 0.440 +/- 0.009 | Yes | 20.8%--28.9% |
| Llama-3.1-70B-like | 0.708 +/- 0.010 | 0.531 +/- 0.010 | Yes | 22.0%--28.0% |
| DeepSeek-V3-like | 0.617 +/- 0.009 | 0.451 +/- 0.011 | Yes | 23.0%--30.6% |
| Qwen2.5-72B-like | 0.654 +/- 0.012 | 0.474 +/- 0.013 | Yes | 24.1%--33.5% |

All-model aggregate: 120 runs total across 8 seeds and 3 templates; vanilla std range 0.009--0.012, RTG std range 0.009--0.013, RTG better in all runs = Yes.

## E2. Repeated Stateful-Baseline Stability

| Policy | Violation Mean +/- Std | Success Mean +/- Std | Avg Interventions | Avg Extra Steps | Best-Violation Runs |
|---|---:|---:|---:|---:|---:|
| Vanilla | 0.554 +/- 0.011 | 0.800 +/- 0.009 | 0.00 | 0.00 | 0 / 8 |
| Prompt-Local Filter | 0.541 +/- 0.007 | 0.784 +/- 0.014 | 0.24 | 0.08 | 0 / 8 |
| Intent-Drift Monitor | 0.498 +/- 0.011 | 0.758 +/- 0.007 | 0.71 | 0.44 | 0 / 8 |
| Memory Isolation | 0.453 +/- 0.007 | 0.713 +/- 0.013 | 1.31 | 0.91 | 8 / 8 |
| RTG | 0.477 +/- 0.009 | 0.754 +/- 0.009 | 1.11 | 0.63 | 0 / 8 |

Recovered-context breakdown:
| Policy | Violation Mean +/- Std | Success Mean +/- Std |
|---|---:|---:|
| Vanilla | 0.581 +/- 0.025 | 0.749 +/- 0.016 |
| Prompt-Local Filter | 0.580 +/- 0.029 | 0.746 +/- 0.025 |
| Intent-Drift Monitor | 0.558 +/- 0.029 | 0.716 +/- 0.023 |
| Memory Isolation | 0.368 +/- 0.012 | 0.670 +/- 0.018 |
| RTG | 0.497 +/- 0.018 | 0.708 +/- 0.030 |
