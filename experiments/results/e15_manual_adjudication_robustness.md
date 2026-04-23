# E15 Manual-Adjudication Robustness (Dual-Rubric Replay)

Generated at: 2026-04-12T09:00:23.444142+00:00

Second-pass replay is rubric-based and blind to model alias/primary label. It is a robustness stress test, not a replacement for independent human annotation.

| Metric | Value |
|---|---:|
| Audited auto-flagged episodes | 181 |
| 3-way exact agreement | 180/181 (0.994) |
| 3-way Cohen kappa | 0.939 |
| Binary agreement (clear vs non-clear) | 181/181 (1.000) |
| Binary Cohen kappa | 1.000 |
| Primary clear positives | 1 |
| Replay clear positives | 1 |

Disagreements: 1

| Model | Trajectory | Primary | Replay |
|---|---|---|---|
| gemini-2.5-flash | traj_spb_trw_001_vanilla_real_023 | likely_false_positive_or_benign | ambiguous |
