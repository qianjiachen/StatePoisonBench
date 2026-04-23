# Compute and Runtime Notes

## Exact-Replay Layer

The exact-replay layer runs on CPU with Python 3.10+ and minimal dependencies (`numpy`, `scipy`).

| Command | Resource class | Expected runtime |
|---|---|---|
| `python scripts/statepoisonbench_loader.py tasks/statepoisonbench_v1.jsonl` | CPU laptop/server | Seconds |
| `python scripts/statepoisonbench_loader.py tasks/statepoisonbench_v2.jsonl` | CPU laptop/server | Seconds |
| `python experiments/run_all_experiments.py` | CPU laptop/server | Seconds to a few minutes |
| `python experiments/run_supplementary_experiments.py` | CPU laptop/server | Seconds to a few minutes |
| `python experiments/check_table_artifact_consistency.py` | CPU laptop/server | Seconds |
| `latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=_build main.tex` | TeX Live environment | Minutes |

## Protocol-Replay Layer

Hosted endpoint and local open-weight studies are protocol-replayable but not numerically frozen.

| Study | Resource class | Notes |
|---|---|---|
| Hosted API pilots | OpenAI-compatible endpoint | Requires provider key and may vary by model/date |
| S6 robustness reruns | RTX 3090-class 24 GB server | Used for robustness sweeps |
| S9 open-weight pilots | A100 80 GB server | About 30 minutes for 32B pilot and 75 minutes for 14B sweep |
| E26/E27 observability diagnostics | RTX 3090-class 24 GB server | Uses local cached Qwen2.5 3B/7B judges |

The paper reports exact counts and role boundaries; wall-clock times for hosted providers are intentionally not treated as stable benchmark outcomes.
