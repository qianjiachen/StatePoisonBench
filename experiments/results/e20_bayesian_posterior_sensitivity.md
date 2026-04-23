# E20 Bayesian Posterior Sensitivity

Generated at: 2026-04-12T09:00:40.015649+00:00

Posterior sensitivity over three symmetric priors using pooled S16 counts; delta is defined as RTG rate minus vanilla rate.

Base pooled counts from S16: vanilla 1/152, RTG 0/152.

| Prior | Pr(RTG <= Vanilla) | Pr(|Delta| <= 0.02) | 95% CrI of Delta (RTG - Vanilla) |
|---|---:|---:|---:|
| uniform_beta_1_1 | 0.750 | 0.884 | [-0.031, 0.015] |
| jeffreys_beta_0p5_0p5 | 0.818 | 0.919 | [-0.028, 0.010] |
| symmetric_beta_2_2 | 0.689 | 0.818 | [-0.036, 0.021] |

| Summary | Range |
|---|---:|
| Pr(RTG <= Vanilla) across priors | [0.689, 0.818] |
| Pr(|Delta| <= 0.02) across priors | [0.818, 0.919] |
| 95% CrI lower bound range | [-0.036, -0.028] |
| 95% CrI upper bound range | [0.010, 0.021] |
