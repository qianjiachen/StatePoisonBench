# Table-Artifact Consistency Report

Generated at: 2026-04-23T11:43:49.169133+00:00

- Checks: 220
- Passed: 220
- Failed: 0

## exp1

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|
| AgentDojo-style detection.detection_rate | 0.407 | 0.407 | True |
| AgentDojo-style detection.f1 | 0.554 | 0.554 | True |
| AgentDojo-style detection.false_positive_rate | 0.116 | 0.116 | True |
| HarmBench-style detection.detection_rate | 0.410 | 0.410 | True |
| HarmBench-style detection.f1 | 0.548 | 0.548 | True |
| HarmBench-style detection.false_positive_rate | 0.158 | 0.158 | True |
| Naive LLM query.detection_rate | 0.666 | 0.666 | True |
| Naive LLM query.f1 | 0.742 | 0.742 | True |
| Naive LLM query.false_positive_rate | 0.234 | 0.234 | True |

## exp2

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|
| Claude-3.5-Sonnet.rtg | 0.443 | 0.443 | True |
| Claude-3.5-Sonnet.vanilla | 0.595 | 0.595 | True |
| DeepSeek-V3.rtg | 0.449 | 0.449 | True |
| DeepSeek-V3.vanilla | 0.615 | 0.615 | True |
| GPT-4o.rtg | 0.434 | 0.434 | True |
| GPT-4o.vanilla | 0.557 | 0.557 | True |
| Llama-3.1-70B.rtg | 0.533 | 0.533 | True |
| Llama-3.1-70B.vanilla | 0.709 | 0.709 | True |
| Qwen2.5-72B.rtg | 0.473 | 0.473 | True |
| Qwen2.5-72B.vanilla | 0.654 | 0.654 | True |

## exp3

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|
| 1.avg_drift | 0.093 | 0.093 | True |
| 1.violation_rate | 0.160 | 0.160 | True |
| 10.avg_drift | 1.410 | 1.410 | True |
| 10.violation_rate | 0.410 | 0.410 | True |
| 20.avg_drift | 3.840 | 3.840 | True |
| 20.violation_rate | 0.760 | 0.760 | True |
| 3.avg_drift | 0.339 | 0.339 | True |
| 3.violation_rate | 0.220 | 0.220 | True |
| 5.avg_drift | 0.616 | 0.616 | True |
| 5.violation_rate | 0.290 | 0.290 | True |
| 50.avg_drift | 16.842 | 16.842 | True |
| 50.violation_rate | 0.970 | 0.970 | True |

## s1

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|

## s10

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|

## s11_api

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|

## s11_open

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|

## s12_s10

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|

## s12_s11

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|

## s13

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|
| claude_haiku_4_5_20251001.delta | 0.026 | 0.026 | True |
| claude_haiku_4_5_20251001.non_worsening | 0.000 | 0.000 | True |
| claude_haiku_4_5_20251001.rtg_violation_rate | 0.605 | 0.605 | True |
| claude_haiku_4_5_20251001.vanilla_violation_rate | 0.579 | 0.579 | True |
| claude_sonnet_4_5_20250929.delta | 0.026 | 0.026 | True |
| claude_sonnet_4_5_20250929.non_worsening | 0.000 | 0.000 | True |
| claude_sonnet_4_5_20250929.rtg_violation_rate | 0.605 | 0.605 | True |
| claude_sonnet_4_5_20250929.vanilla_violation_rate | 0.579 | 0.579 | True |
| deepseek_v3_2.delta | 0.105 | 0.105 | True |
| deepseek_v3_2.non_worsening | 0.000 | 0.000 | True |
| deepseek_v3_2.rtg_violation_rate | 0.605 | 0.605 | True |
| deepseek_v3_2.vanilla_violation_rate | 0.500 | 0.500 | True |
| gemini_2_5_flash.delta | 0.132 | 0.132 | True |
| gemini_2_5_flash.non_worsening | 0.000 | 0.000 | True |
| gemini_2_5_flash.rtg_violation_rate | 0.711 | 0.711 | True |
| gemini_2_5_flash.vanilla_violation_rate | 0.579 | 0.579 | True |
| overall.ci_hi | 0.490 | 0.490 | True |
| overall.ci_lo | 0.000 | 0.000 | True |
| overall.k | 0.000 | 0.000 | True |
| overall.n | 4.000 | 4.000 | True |
| overall.rate | 0.000 | 0.000 | True |

## s14

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|
| claude_haiku_4_5_20251001.auto_flagged.k | 45.000 | 45.000 | True |
| claude_haiku_4_5_20251001.auto_flagged.n | 76.000 | 76.000 | True |
| claude_haiku_4_5_20251001.clear_positive | 0.000 | 0.000 | True |
| claude_haiku_4_5_20251001.fp_or_benign | 44.000 | 44.000 | True |
| claude_haiku_4_5_20251001.rtg_clear_rate | 0.000 | 0.000 | True |
| claude_haiku_4_5_20251001.vanilla_clear_rate | 0.000 | 0.000 | True |
| claude_sonnet_4_5_20250929.auto_flagged.k | 45.000 | 45.000 | True |
| claude_sonnet_4_5_20250929.auto_flagged.n | 76.000 | 76.000 | True |
| claude_sonnet_4_5_20250929.clear_positive | 0.000 | 0.000 | True |
| claude_sonnet_4_5_20250929.fp_or_benign | 45.000 | 45.000 | True |
| claude_sonnet_4_5_20250929.rtg_clear_rate | 0.000 | 0.000 | True |
| claude_sonnet_4_5_20250929.vanilla_clear_rate | 0.000 | 0.000 | True |
| deepseek_v3_2.auto_flagged.k | 42.000 | 42.000 | True |
| deepseek_v3_2.auto_flagged.n | 76.000 | 76.000 | True |
| deepseek_v3_2.clear_positive | 0.000 | 0.000 | True |
| deepseek_v3_2.fp_or_benign | 42.000 | 42.000 | True |
| deepseek_v3_2.rtg_clear_rate | 0.000 | 0.000 | True |
| deepseek_v3_2.vanilla_clear_rate | 0.000 | 0.000 | True |
| direction.ci_hi | 1.000 | 1.000 | True |
| direction.ci_lo | 0.510 | 0.510 | True |
| direction.k | 4.000 | 4.000 | True |
| direction.n | 4.000 | 4.000 | True |
| direction.rate | 1.000 | 1.000 | True |
| gemini_2_5_flash.auto_flagged.k | 49.000 | 49.000 | True |
| gemini_2_5_flash.auto_flagged.n | 76.000 | 76.000 | True |
| gemini_2_5_flash.clear_positive | 1.000 | 1.000 | True |
| gemini_2_5_flash.fp_or_benign | 42.000 | 42.000 | True |
| gemini_2_5_flash.rtg_clear_rate | 0.000 | 0.000 | True |
| gemini_2_5_flash.vanilla_clear_rate | 0.026 | 0.026 | True |
| overall.auto_flagged.k | 181.000 | 181.000 | True |
| overall.auto_flagged.n | 304.000 | 304.000 | True |
| overall.clear_positive | 1.000 | 1.000 | True |
| overall.fp_or_benign | 173.000 | 173.000 | True |
| overall.rtg_clear_rate | 0.000 | 0.000 | True |
| overall.vanilla_clear_rate | 0.007 | 0.007 | True |
| precision.k | 1.000 | 1.000 | True |
| precision.n | 181.000 | 181.000 | True |
| precision.rate | 0.006 | 0.006 | True |

## s15

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|
| agreement3.k | 180.000 | 180.000 | True |
| agreement3.kappa | 0.939 | 0.939 | True |
| agreement3.n | 181.000 | 181.000 | True |
| agreement3.rate | 0.994 | 0.994 | True |
| agreement_bin.k | 181.000 | 181.000 | True |
| agreement_bin.kappa | 1.000 | 1.000 | True |
| agreement_bin.n | 181.000 | 181.000 | True |
| agreement_bin.rate | 1.000 | 1.000 | True |
| clear.primary | 1.000 | 1.000 | True |
| clear.replay | 1.000 | 1.000 | True |
| n_audited | 181.000 | 181.000 | True |

## s16

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|
| fisher_p | 1.000 | 1.000 | True |
| rtg.ci_hi | 0.025 | 0.025 | True |
| rtg.ci_lo | 0.000 | 0.000 | True |
| rtg.k | 0.000 | 0.000 | True |
| rtg.n | 152.000 | 152.000 | True |
| rtg.one_sided_upper | 0.020 | 0.020 | True |
| rtg.rate | 0.000 | 0.000 | True |
| s15_binary.k | 181.000 | 181.000 | True |
| s15_binary.kappa | 1.000 | 1.000 | True |
| s15_binary.n | 181.000 | 181.000 | True |
| s15_binary.rate | 1.000 | 1.000 | True |
| s15_threeway.k | 180.000 | 180.000 | True |
| s15_threeway.kappa | 0.939 | 0.939 | True |
| s15_threeway.n | 181.000 | 181.000 | True |
| s15_threeway.rate | 0.994 | 0.994 | True |
| vanilla.ci_hi | 0.036 | 0.036 | True |
| vanilla.ci_lo | 0.001 | 0.001 | True |
| vanilla.k | 1.000 | 1.000 | True |
| vanilla.n | 152.000 | 152.000 | True |
| vanilla.rate | 0.007 | 0.007 | True |

## s17

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|
| current.n_per_arm | 152.000 | 152.000 | True |
| current.power | 0.179 | 0.179 | True |
| observed.abs_delta | 0.007 | 0.007 | True |
| required.n80 | 1117.000 | 1117.000 | True |
| required.n90 | 1494.000 | 1494.000 | True |
| scenario_0p02.n80 | 388.000 | 388.000 | True |
| scenario_0p02.n90 | 519.000 | 519.000 | True |
| scenario_0p03.n80 | 257.000 | 257.000 | True |
| scenario_0p03.n90 | 343.000 | 343.000 | True |
| scenario_0p05.n80 | 152.000 | 152.000 | True |
| scenario_0p05.n90 | 203.000 | 203.000 | True |

## s18

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|
| observed.delta | -0.007 | -0.007 | True |
| observed.fisher_p | 1.000 | 1.000 | True |
| observed.rtg_k | 0.000 | 0.000 | True |
| observed.rtg_n | 152.000 | 152.000 | True |
| observed.rtg_rate | 0.000 | 0.000 | True |
| observed.vanilla_k | 1.000 | 1.000 | True |
| observed.vanilla_n | 152.000 | 152.000 | True |
| observed.vanilla_rate | 0.007 | 0.007 | True |
| rtg_upgrade_1.delta | 0.000 | 0.000 | True |
| rtg_upgrade_1.fisher_p | 1.000 | 1.000 | True |
| rtg_upgrade_1.rtg_k | 1.000 | 1.000 | True |
| rtg_upgrade_1.rtg_n | 152.000 | 152.000 | True |
| rtg_upgrade_1.rtg_rate | 0.007 | 0.007 | True |
| rtg_upgrade_1.vanilla_k | 1.000 | 1.000 | True |
| rtg_upgrade_1.vanilla_n | 152.000 | 152.000 | True |
| rtg_upgrade_1.vanilla_rate | 0.007 | 0.007 | True |
| swap_stress_2.delta | 0.007 | 0.007 | True |
| swap_stress_2.fisher_p | 1.000 | 1.000 | True |
| swap_stress_2.rtg_k | 1.000 | 1.000 | True |
| swap_stress_2.rtg_n | 152.000 | 152.000 | True |
| swap_stress_2.rtg_rate | 0.007 | 0.007 | True |
| swap_stress_2.vanilla_k | 0.000 | 0.000 | True |
| swap_stress_2.vanilla_n | 152.000 | 152.000 | True |
| swap_stress_2.vanilla_rate | 0.000 | 0.000 | True |
| vanilla_downgrade_1.delta | 0.000 | 0.000 | True |
| vanilla_downgrade_1.fisher_p | 1.000 | 1.000 | True |
| vanilla_downgrade_1.rtg_k | 0.000 | 0.000 | True |
| vanilla_downgrade_1.rtg_n | 152.000 | 152.000 | True |
| vanilla_downgrade_1.rtg_rate | 0.000 | 0.000 | True |
| vanilla_downgrade_1.vanilla_k | 0.000 | 0.000 | True |
| vanilla_downgrade_1.vanilla_n | 152.000 | 152.000 | True |
| vanilla_downgrade_1.vanilla_rate | 0.000 | 0.000 | True |
| vanilla_plus2_stress.delta | -0.020 | -0.020 | True |
| vanilla_plus2_stress.fisher_p | 0.248 | 0.248 | True |
| vanilla_plus2_stress.rtg_k | 0.000 | 0.000 | True |
| vanilla_plus2_stress.rtg_n | 152.000 | 152.000 | True |
| vanilla_plus2_stress.rtg_rate | 0.000 | 0.000 | True |
| vanilla_plus2_stress.vanilla_k | 3.000 | 3.000 | True |
| vanilla_plus2_stress.vanilla_n | 152.000 | 152.000 | True |
| vanilla_plus2_stress.vanilla_rate | 0.020 | 0.020 | True |

## s19

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|
| beta_0p5_0p5.ci_hi | 0.010 | 0.010 | True |
| beta_0p5_0p5.ci_lo | -0.028 | -0.028 | True |
| beta_0p5_0p5.p_non_worse | 0.818 | 0.818 | True |
| beta_0p5_0p5.p_rope | 0.919 | 0.919 | True |
| beta_1_1.ci_hi | 0.015 | 0.015 | True |
| beta_1_1.ci_lo | -0.031 | -0.031 | True |
| beta_1_1.p_non_worse | 0.750 | 0.750 | True |
| beta_1_1.p_rope | 0.884 | 0.884 | True |
| beta_2_2.ci_hi | 0.021 | 0.021 | True |
| beta_2_2.ci_lo | -0.036 | -0.036 | True |
| beta_2_2.p_non_worse | 0.689 | 0.689 | True |
| beta_2_2.p_rope | 0.818 | 0.818 | True |
| range.ci_lower_hi | -0.028 | -0.028 | True |
| range.ci_lower_lo | -0.036 | -0.036 | True |
| range.ci_upper_hi | 0.021 | 0.021 | True |
| range.ci_upper_lo | 0.010 | 0.010 | True |
| range.non_worse_hi | 0.818 | 0.818 | True |
| range.non_worse_lo | 0.689 | 0.689 | True |
| range.rope_hi | 0.919 | 0.919 | True |
| range.rope_lo | 0.818 | 0.818 | True |

## s2

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|

## s20_negative

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|
| ambiguous | 0.000 | 0.000 | True |
| benign | 17.000 | 17.000 | True |
| clear | 0.000 | 0.000 | True |
| n_audited | 17.000 | 17.000 | True |
| n_trusted_write | 12.000 | 12.000 | True |
| upper | 0.162 | 0.162 | True |

## s20_taxonomy

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|
| ambiguous.persistence_success_unsafe_tool_escalation | 2.000 | 2.000 | True |
| ambiguous.unauthorized_action | 1.000 | 1.000 | True |
| ambiguous.unsafe_tool_escalation | 4.000 | 4.000 | True |
| likely.goal_drift | 50.000 | 50.000 | True |
| likely.goal_drift_persistence_success | 41.000 | 41.000 | True |
| likely.goal_drift_unauthorized_action | 17.000 | 17.000 | True |
| likely.unauthorized_action | 45.000 | 45.000 | True |
| negative.context_separation_write | 3.000 | 3.000 | True |
| negative.filtered_trusted_write | 14.000 | 14.000 | True |
| non_clear_total | 180.000 | 180.000 | True |

## s21

| Metric | main.tex | Artifact (rounded) | Match |
|---|---:|---:|---:|
| binary.k | 36.000 | 36.000 | True |
| binary.n | 36.000 | 36.000 | True |
| binary.rate | 1.000 | 1.000 | True |
| exact.k | 36.000 | 36.000 | True |
| exact.n | 36.000 | 36.000 | True |
| exact.rate | 1.000 | 1.000 | True |
| flagged_non_clear | 12.000 | 12.000 | True |
| hidden.k | 0.000 | 0.000 | True |
| hidden.n | 24.000 | 24.000 | True |
| hidden.rate | 0.000 | 0.000 | True |
| random_auto_negative_no_write | 12.000 | 12.000 | True |
| write_bearing_auto_negative | 12.000 | 12.000 | True |

No mismatches found for checked tables.
