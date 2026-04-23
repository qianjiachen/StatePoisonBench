# StatePoisonBench Benchmark Card

## Overview

StatePoisonBench is a synthetic benchmark and evaluation protocol for persistent-state contamination in long-horizon tool-using agents. It targets write--recover--act transitions where state artifacts such as summaries, trackers, recovery notes, and compacted context are restored and later influence authorization-sensitive actions.

## Intended Use

- Evaluate whether an agent converts recovered state into unauthorized actions, goal drift, unsafe tool escalation, persistence success, or state propagation.
- Audit trajectory-aware evaluators and recovery-time gating baselines.
- Reproduce the synthetic and aggregation layers reported in the anonymous NeurIPS 2026 ED submission.

## Not Intended For

- Estimating deployed real-world prevalence of contamination.
- Training agents to exploit persistent-state vulnerabilities.
- Releasing or reconstructing raw platform traces from private accounts.
- Treating hosted-endpoint reruns as numerically frozen across dates or providers.

## Contents

- `tasks/statepoisonbench_v1.jsonl` and `tasks/statepoisonbench_v2.jsonl`: schema validation and pilot task packs.
- `tasks/statepoisonbench_main_table*.jsonl`: controlled synthetic core slices used by main experiments.
- `tasks/statepoisonbench_realpaired*.jsonl`: protocol-replayable prospective paired task packs.
- `experiments/results/*.json` and `*.md`: paper-linked synthetic, aggregation, audit, and calibration artifacts.
- `scripts/statepoisonbench_loader.py` and `scripts/statepoisonbench_evaluator_v2.py`: loader and trajectory-aware evaluator.

## Data Generation

Synthetic instances specify task goals, authorization boundaries, state artifacts, contamination pathways, restore triggers, and violation labels. Labels for the controlled synthetic core are deterministic and schema-grounded; real-trace calibration artifacts are derived summaries and audit outputs, not raw platform logs.

## Release Boundary

Redistributed:

- Synthetic task packs.
- Deterministic evaluator and aggregation scripts.
- Paper-linked JSON/Markdown result artifacts.
- Dataset card, Croissant metadata, and reproducibility notes.

Not redistributed:

- Raw account-linked workflow traces.
- Compacted session artifacts.
- Private logs, credentials, API keys, or proprietary model weights.

## Licenses

- Code: Apache-2.0.
- Synthetic task packs, result artifacts, and documentation: CC BY 4.0.

## Maintenance Notes

The anonymous review package uses placeholder URLs:

- `https://anonymous.4open.science/r/StatePoisonBench-C1D2`
- The same repository serves as the dataset/artifact URL during review.

This single anonymous repository is the reviewer-facing host for both code and benchmark artifacts during OpenReview.
