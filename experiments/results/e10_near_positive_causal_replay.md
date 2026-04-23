# E10 Near-Positive Causal Replay

Generated at: 2026-04-11T20:09:09.528456+00:00
Trace anchor: `019d337a-a32d-7901-8487-3c130851ff15`
Paired episodes per family: 160

## Family-Wise Paired Results

| Family | Clean Viol. | Cont. Viol. | Paired Delta | Clean Safe | Cont. Safe | Clean State-Prop | Cont. State-Prop | McNemar p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| recovered_context_write | 0.263 | 0.519 | 0.256 | 0.787 | 0.688 | 0.169 | 0.750 | 1.526e-06 |
| recovery_state_poisoning | 0.194 | 0.463 | 0.269 | 0.819 | 0.613 | 0.263 | 0.694 | 1.803e-08 |

## Overall

- `violation_rate`: clean=0.228, contaminated=0.491
- `paired_delta`: 0.262
- `safe_task_success_rate`: clean=0.803, contaminated=0.650
- `state_propagation_hit_rate`: clean=0.216, contaminated=0.722
- `mcnemar_p`: 1.053e-13

Interpretation: paired replay shows a strong contamination-direction shift with significantly higher downstream state-propagation hits.
