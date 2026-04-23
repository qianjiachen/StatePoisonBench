# StatePoisonBench Anonymous ED Supplement

StatePoisonBench is a benchmark methodology for persistent-state contamination in long-horizon tool-using agents. This anonymous package is prepared for NeurIPS 2026 Evaluations & Datasets review.

## Reviewer Entry Points

- Anonymous code repository: `<ANON_GITHUB_URL>`
- Anonymous dataset/artifact hosting: `<ANON_HF_DATASET_URL>`
- OpenReview supplement: mirrors the same code-proof package as a fallback.

Replace the placeholder URLs before submission. The local package is self-contained for the exact-replay layer.

## What Is Included

- Synthetic benchmark task packs in `tasks/`.
- Loader and trajectory-aware evaluator in `scripts/`.
- Seeded synthetic generators, aggregation scripts, and consistency checks in `experiments/`.
- Paper-linked result artifacts in `experiments/results/`.
- LaTeX source for the anonymous paper in `neurips2026_submission/`.
- ED resource metadata in `DATASET_CARD.md`, `croissant_metadata.jsonld`, and `docs/`.

## Quick Audit Path

```powershell
python scripts/statepoisonbench_loader.py tasks/statepoisonbench_v1.jsonl
python scripts/statepoisonbench_loader.py tasks/statepoisonbench_v2.jsonl
python experiments/run_all_experiments.py
python experiments/check_table_artifact_consistency.py
```

Optional paper rebuild:

```powershell
cd neurips2026_submission
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=_build main.tex
```

## Release Boundary

The release covers synthetic benchmark tasks, evaluator code, aggregation code, derived result artifacts, and documentation. It does not redistribute raw account-linked platform traces, compacted session artifacts, private workflow logs, API keys, proprietary model weights, or any non-redistributable platform data.

## Licenses

- Code: Apache License 2.0, see `LICENSE`.
- Synthetic task packs, result artifacts, and documentation: Creative Commons Attribution 4.0, see `DATA_LICENSE.md`.
