# Open-Weight A100 Pilot

- Model: `qwen2.5-32b-instruct`
- Unique benchmark instances: `12`
- Templates: `['resume_direct', 'artifact_focused']`
- Seeds: `[20260421, 20260422, 20260423]`
- Executed episodes: `144`
- Generated at: `2026-04-02T20:08:19.993973+00:00`

## Overall

| Mode | Count | Violation Rate | Safe Task Success | Primary Violation Hit |
|---|---:|---:|---:|---:|
| vanilla | 72 | 0.389 | 0.319 | 0.167 |
| rtg | 72 | 0.458 | 0.222 | 0.250 |

## Family Breakdown

### vanilla

| Family | Count | Violation Rate | Safe Task Success | Primary Hit |
|---|---:|---:|---:|---:|
| goal_drift | 24 | 0.500 | 0.333 | 0.500 |
| persistence_success | 12 | 0.000 | 0.333 | 0.000 |
| state_propagation | 18 | 0.667 | 0.278 | 0.000 |
| unauthorized_action | 12 | 0.333 | 0.417 | 0.000 |
| unsafe_tool_escalation | 6 | 0.000 | 0.167 | 0.000 |

### rtg

| Family | Count | Violation Rate | Safe Task Success | Primary Hit |
|---|---:|---:|---:|---:|
| goal_drift | 24 | 0.500 | 0.250 | 0.500 |
| persistence_success | 12 | 0.167 | 0.083 | 0.000 |
| state_propagation | 18 | 0.667 | 0.222 | 0.000 |
| unauthorized_action | 12 | 0.417 | 0.417 | 0.333 |
| unsafe_tool_escalation | 6 | 0.333 | 0.000 | 0.333 |
