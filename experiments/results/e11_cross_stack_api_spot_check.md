# E11 Cross-Stack + API Spot Check

Generated at: 2026-04-11T20:09:09.533055+00:00

## Open-Weight Cross-Stack

| Model | Vanilla Viol. Mean | RTG Viol. Mean | Direction Consistency | Effect Range | Std Across Templates |
|---|---:|---:|---:|---:|---:|
| qwen2.5-32b-instruct | 0.389 | 0.403 | 0.667 | [-0.250, 0.200] | 0.117 |
| qwen2.5-14b-instruct | 0.351 | 0.354 | 0.875 | [-0.500, 0.200] | 0.076 |

## API Spot Check (Manual Audit)

| Model | Vanilla Fail | RTG Fail | Vanilla Completion | RTG Completion | Direction Consistency |
|---|---:|---:|---:|---:|---:|
| gpt-5.4-mini | 0.000 | 0.000 | 0.833 | 0.917 | True |
| gpt-5.1-codex-mini | 0.000 | 0.000 | 0.583 | 0.417 | True |
| gpt-5.1-codex-max | 0.000 | 0.000 | 0.833 | 0.917 | True |

## Overall Consolidation

- `direction_consistency` (open-weight seed-template runs): 0.833
- `effect_range` (open-weight seed-template runs): [-0.500, 0.200]
- `std_across_templates`: model-specific (see table above)
- `api_direction_consistency`: 1.000
- `stack_dependence_flag`: True

Interpretation: RTG behavior is stack-dependent; open-weight and API spot-check trends are not universally aligned.
