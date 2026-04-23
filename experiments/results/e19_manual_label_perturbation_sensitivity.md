# E19 Manual-Label Perturbation Sensitivity

Generated at: 2026-04-12T09:00:37.817814+00:00

Scenario-based perturbation on S16 pooled manual counts; used to stress-test low-count directional fragility.

Base pooled counts from S16: vanilla 1/152, RTG 0/152.

| Scenario | Vanilla k/n (rate) | RTG k/n (rate) | Delta (RTG - Vanilla) | Fisher p | Non-worsening |
|---|---:|---:|---:|---:|---:|
| observed | 1/152 (0.007) | 0/152 (0.000) | -0.007 | 1.000 | Yes |
| vanilla_downgrade_1 | 0/152 (0.000) | 0/152 (0.000) | 0.000 | 1.000 | Yes |
| rtg_upgrade_1 | 1/152 (0.007) | 1/152 (0.007) | 0.000 | 1.000 | Yes |
| swap_stress_2 | 0/152 (0.000) | 1/152 (0.007) | 0.007 | 1.000 | No |
| vanilla_plus2_stress | 3/152 (0.020) | 0/152 (0.000) | -0.020 | 0.248 | Yes |

| Summary | Value |
|---|---:|
| Direction non-worsening across scenarios | 4/5 (0.800) |
| Delta range (RTG - Vanilla) | [-0.020, 0.007] |
| Fisher p range | [0.248, 1.000] |
