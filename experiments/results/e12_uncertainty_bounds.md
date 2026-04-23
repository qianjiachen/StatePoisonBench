# E12 Uncertainty and Small-Sample Bounds

Generated at: 2026-04-12T04:25:58.599567+00:00

## S10 Paired Replay Bootstrap CIs

| Family | N pairs | Violation Delta | 95% CI | State-Prop Delta | 95% CI |
|---|---:|---:|---:|---:|---:|
| recovered_context_write | 160 | 0.256 | [0.156, 0.350] | 0.581 | [0.494, 0.663] |
| recovery_state_poisoning | 160 | 0.269 | [0.181, 0.356] | 0.431 | [0.331, 0.531] |
| overall | 320 | 0.262 | [0.197, 0.328] | 0.506 | [0.441, 0.572] |

## S11 Open-Weight Direction Consistency CIs

| Model | Non-worsening / Runs | Direction Consistency | 95% Wilson CI |
|---|---:|---:|---:|
| qwen2.5-32b-instruct | 4/6 | 0.667 | [0.300, 0.903] |
| qwen2.5-14b-instruct | 21/24 | 0.875 | [0.690, 0.957] |
| overall | 25/30 | 0.833 | [0.664, 0.927] |

## S11 API Zero-Failure Small-Sample Bounds

| Model | Vanilla Fail | Vanilla one-sided 95% upper | RTG Fail | RTG one-sided 95% upper |
|---|---:|---:|---:|---:|
| gpt-5.4-mini | 0/12 | 0.221 | 0/12 | 0.221 |
| gpt-5.1-codex-mini | 0/12 | 0.221 | 0/12 | 0.221 |
| gpt-5.1-codex-max | 0/12 | 0.221 | 0/12 | 0.221 |
| pooled | 0/36 | 0.080 | 0/36 | 0.080 |

Interpretation: S10 deltas remain positive with CIs excluding zero; S11 API zero failures remain small-sample evidence only.
