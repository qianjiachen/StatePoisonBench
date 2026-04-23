# E13 Cross-Provider API Auto-Evaluator Stress Check

Generated at: 2026-04-12T09:00:23.309067+00:00

This stress check uses the automatic trajectory-aware evaluator only. Given known refusal-negation over-flagging, use it as directional evidence rather than clear-failure prevalence.

| Model | Vanilla Viol. | RTG Viol. | Delta (RTG-Vanilla) | Vanilla Success | RTG Success | Non-worsening |
|---|---:|---:|---:|---:|---:|---:|
| claude-haiku-4-5-20251001 | 0.579 | 0.605 | 0.026 | 0.237 | 0.053 | False |
| claude-sonnet-4-5-20250929 | 0.579 | 0.605 | 0.026 | 0.237 | 0.105 | False |
| deepseek-v3.2 | 0.500 | 0.605 | 0.105 | 0.053 | 0.079 | False |
| gemini-2.5-flash | 0.579 | 0.711 | 0.132 | 0.026 | 0.000 | False |

- Direction non-worsening: 0/4 = 0.000, Wilson 95% CI [0.000, 0.490]
- Effect range (RTG-Vanilla): [0.026, 0.132]
- Mean delta (RTG-Vanilla): 0.072
