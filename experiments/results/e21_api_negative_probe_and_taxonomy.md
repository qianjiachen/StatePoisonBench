# E21 Targeted Auto-Negative Probe and Error Taxonomy

Generated at: 2026-04-12T11:36:11.894255+00:00

The negative probe audits all auto-negative episodes with at least one artifact write, because write-bearing negatives are the riskiest slice for hidden missed positives.

## Targeted Auto-Negative Probe

| Statistic | Value |
|---|---:|
| Audited auto-negative episodes with any write | 17 |
| Audited auto-negative episodes with trusted-write path markers | 12 |
| Clear hidden positives | 0 |
| Likely benign/compliant | 17 |
| Ambiguous | 0 |
| One-sided 95% upper bound on hidden clear-positive rate | 0.162 |

- Family breakdown: goal_drift=2, state_propagation=14, unauthorized_action=1
- Defense breakdown: rtg=5, vanilla=12
- Negative-probe buckets: context_separation_write=3, filtered_trusted_write=14

## Manual Error Taxonomy

| Bucket | Count |
|---|---:|
| Manually non-clear auto-flags | 180 |
| Likely false-positive / benign auto-flags | 173 |
| Ambiguous auto-flags | 7 |
| Likely FP top combo: goal_drift | 50 |
| Likely FP top combo: unauthorized_action | 45 |
| Likely FP top combo: goal_drift,persistence_success | 41 |
| Likely FP top combo: goal_drift,unauthorized_action | 17 |
| Likely FP top combo: goal_drift,persistence_success,unauthorized_action | 8 |
| Ambiguous combo: unsafe_tool_escalation | 4 |
| Ambiguous combo: persistence_success,unsafe_tool_escalation | 2 |
| Ambiguous combo: unauthorized_action | 1 |
| Auto-negative probe bucket: filtered_trusted_write | 14 |
| Auto-negative probe bucket: context_separation_write | 3 |

Interpretation: manually non-clear auto-flags are dominated by refusal-like goal-drift or unauthorized-action tag combinations, while the small ambiguous remainder concentrates in unsafe-tool-escalation-like traces. In the riskiest auto-negative write-bearing slice, we did not find hidden clear contamination-positives.
