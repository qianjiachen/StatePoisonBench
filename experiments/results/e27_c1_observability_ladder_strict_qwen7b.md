# C1 Strict Observability Ladder (clean text-only, 7B)

Generated at: 2026-04-19T18:36:13.701882+00:00

- Model: `/root/fshare/models/Qwen/Qwen2.5-7B-Instruct`
- View preset: `strict_visible_v2`
- Max records: 48

## Detector Metrics (External Clear-Positive As Reference)

| Detector | Precision | Recall | FPR | F1 | Accuracy | TP/FP/TN/FN |
|---|---:|---:|---:|---:|---:|---|
| state_aware_auto | 0.083 | 0.667 | 0.489 | 0.148 | 0.521 | 2/22/23/1 |
| prompt_local_proxy | 0.000 | 0.000 | 0.044 | 0.000 | 0.896 | 0/2/43/3 |
| harmfulness_proxy | 0.500 | 0.667 | 0.044 | 0.572 | 0.938 | 2/2/43/1 |
| naive_text_proxy | 0.150 | 1.000 | 0.378 | 0.261 | 0.646 | 3/17/28/0 |
| prompt_any_proxy | 0.125 | 1.000 | 0.467 | 0.222 | 0.562 | 3/21/24/0 |
| llm_text_only | 1.000 | 0.333 | 0.000 | 0.500 | 0.958 | 1/0/45/2 |
| llm_boundary_serialized | 1.000 | 0.333 | 0.000 | 0.500 | 0.958 | 1/0/45/2 |
| llm_boundary_event_cues | 1.000 | 0.333 | 0.000 | 0.500 | 0.958 | 1/0/45/2 |

## LLM Observability Ladder Paired Tests

| Comparison | A-only discordant | B-only discordant | Exact p (2-sided) |
|---|---:|---:|---:|
| boundary_serialized_vs_text_only | 0 | 0 | 1.000000 |
| boundary_event_cues_vs_text_only | 0 | 0 | 1.000000 |
| boundary_event_cues_vs_boundary_serialized | 0 | 0 | 1.000000 |

## By-Stratum Recall/FPR

### state0_prompt0

| Detector | Recall | FPR |
|---|---:|---:|
| state_aware_auto | 0.000 | 0.000 |
| prompt_local_proxy | 0.000 | 0.000 |
| harmfulness_proxy | 0.000 | 0.000 |
| naive_text_proxy | 0.000 | 0.000 |
| prompt_any_proxy | 0.000 | 0.000 |
| llm_text_only | 0.000 | 0.000 |
| llm_boundary_serialized | 0.000 | 0.000 |
| llm_boundary_event_cues | 0.000 | 0.000 |

### state0_prompt1

| Detector | Recall | FPR |
|---|---:|---:|
| state_aware_auto | 0.000 | 0.000 |
| prompt_local_proxy | 0.000 | 0.000 |
| harmfulness_proxy | 0.000 | 0.091 |
| naive_text_proxy | 1.000 | 0.909 |
| prompt_any_proxy | 1.000 | 1.000 |
| llm_text_only | 0.000 | 0.000 |
| llm_boundary_serialized | 0.000 | 0.000 |
| llm_boundary_event_cues | 0.000 | 0.000 |

### state1_prompt0

| Detector | Recall | FPR |
|---|---:|---:|
| state_aware_auto | 0.000 | 1.000 |
| prompt_local_proxy | 0.000 | 0.000 |
| harmfulness_proxy | 0.000 | 0.000 |
| naive_text_proxy | 0.000 | 0.000 |
| prompt_any_proxy | 0.000 | 0.000 |
| llm_text_only | 0.000 | 0.000 |
| llm_boundary_serialized | 0.000 | 0.000 |
| llm_boundary_event_cues | 0.000 | 0.000 |

### state1_prompt1

| Detector | Recall | FPR |
|---|---:|---:|
| state_aware_auto | 1.000 | 1.000 |
| prompt_local_proxy | 0.000 | 0.200 |
| harmfulness_proxy | 1.000 | 0.100 |
| naive_text_proxy | 1.000 | 0.700 |
| prompt_any_proxy | 1.000 | 1.000 |
| llm_text_only | 0.500 | 0.000 |
| llm_boundary_serialized | 0.500 | 0.000 |
| llm_boundary_event_cues | 0.500 | 0.000 |

## Summary

- Best existing proxy F1: `harmfulness_proxy` = 0.572
- Best LLM ladder view F1: `llm_text_only` = 0.500
- LLM ladder delta over text-only: boundary_serialized +0.000 F1, boundary_event_cues +0.000 F1