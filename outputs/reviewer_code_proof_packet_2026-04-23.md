# Reviewer Code-Proof Packet

Generated: 2026-04-23

## Purpose

This note is the submission-facing reproducibility and code-proof supplement for the anonymous StatePoisonBench package. It is written to answer a narrow reviewer question:

What can be directly rerun from the provided code and artifacts, what can be replayed only at the protocol level, and what is intentionally not redistributed in the anonymous submission?

The scope here matches the paper's current ED-track claim boundary:

- exact replayable: synthetic benchmark assets, seeded generators, evaluator logic, aggregation scripts, and paper-table consistency checks
- protocol replayable: hosted-endpoint studies whose prompts, task packs, and aggregation code are included, but whose exact numeric outcomes depend on external APIs and time-varying model behavior
- non-redistributable: raw account-linked platform traces and compacted session artifacts
- public-after-acceptance: core synthetic task packs, evaluator, aggregation scripts, paper-linked artifacts, and documentation

## What This Package Proves

The anonymous supplement already contains enough code to verify the following:

1. The synthetic benchmark schema, loader, and trajectory-aware evaluator exist locally and are executable.
2. The main paper's core synthetic tables can be regenerated from included scripts.
3. The supplementary synthetic and aggregation studies can be regenerated from included scripts and stored JSON artifacts.
4. The manuscript tables can be checked automatically against local result artifacts via a dedicated consistency checker.
5. The paper can be rebuilt locally from the same repository state.
6. The ED resource package includes a dataset card, Croissant metadata skeleton, license files, release boundary, compute/runtime note, and asset-license matrix.

It does not prove that proprietary endpoint studies are numerically frozen across reruns, and it does not release raw platform traces.

## Minimal Included Components

From repository root, the core anonymous supplement is:

- `tasks/`
- `README.md`
- `LICENSE`
- `DATA_LICENSE.md`
- `DATASET_CARD.md`
- `croissant_metadata.jsonld`
- `docs/`
- `requirements.txt`
- `scripts/statepoisonbench_loader.py`
- `scripts/statepoisonbench_evaluator_v2.py`
- `experiments/run_all_experiments.py`
- `experiments/run_supplementary_experiments.py`
- `experiments/run_server_robustness_sweeps.py`
- `experiments/run_e10_e11_experiments.py`
- `experiments/run_e12_uncertainty_bounds.py`
- `experiments/run_e13_cross_provider_api_auto_check.py`
- `experiments/run_e14_cross_provider_manual_audit.py`
- `experiments/run_e15_manual_adjudication_robustness.py`
- `experiments/run_e16_manual_calibrated_small_sample_bounds.py`
- `experiments/run_e18_power_and_sample_size_planning.py`
- `experiments/run_e19_manual_label_perturbation_sensitivity.py`
- `experiments/run_e20_bayesian_posterior_sensitivity.py`
- `experiments/run_e21_api_negative_probe_and_taxonomy.py`
- `experiments/run_e22_prepare_independent_audit_pack.py`
- `experiments/run_e22_aggregate_independent_audit.py`
- `experiments/run_e23_prepare_c1_decoupled_audit_pack.py`
- `experiments/run_e23_aggregate_c1_decoupled_audit.py`
- `experiments/run_e24_prepare_single_external_expanded_pack.py`
- `experiments/run_e24_aggregate_single_external_expanded_pack.py`
- `experiments/run_real_api_pilot.py`
- `experiments/run_local_hf_open_weight_pilot.py`
- `experiments/run_e25_prospective_real_platform_paired.py`
- `experiments/run_e26_c1_observability_ladder.py`
- `experiments/check_table_artifact_consistency.py`
- `experiments/results/`
- `neurips2026_submission/`

## Dependencies

For the exact-replay synthetic and aggregation path:

- Python 3.10+ recommended
- `numpy`
- `scipy`

For local open-weight and appendix-only observability diagnostics:

- `torch`
- `transformers`

For direct-endpoint protocol replay:

- an OpenAI-compatible API endpoint
- `OPENAI_API_KEY`
- optional `OPENAI_BASE_URL`

For paper rebuild:

- TeX Live / `latexmk`

## Exact-Replay Path

All commands below are run from repository root unless noted otherwise.

### 1. Validate the task schema

```powershell
python scripts/statepoisonbench_loader.py tasks/statepoisonbench_v1.jsonl
python scripts/statepoisonbench_loader.py tasks/statepoisonbench_v2.jsonl
```

This checks that the released benchmark task packs are valid JSONL and contain the required schema keys.

### 2. Regenerate the main synthetic experiments

```powershell
python experiments/run_all_experiments.py
```

Expected outputs:

- `experiments/results/experiment_1_baseline.json`
- `experiments/results/experiment_2_scaling.json`
- `experiments/results/experiment_3_turns.json`

These are the seeded synthetic generators backing the main synthetic results.

### 3. Regenerate the supplementary synthetic controls

```powershell
python experiments/run_supplementary_experiments.py
python experiments/run_server_robustness_sweeps.py
```

Expected outputs:

- `experiments/results/supplementary_experiments.json`
- `experiments/results/supplementary_experiments_report.md`
- `experiments/results/server_robustness_sweeps_full.json`
- `experiments/results/server_robustness_sweeps_full_report.md`

### 4. Regenerate deterministic aggregation studies from included artifacts

```powershell
python experiments/run_e10_e11_experiments.py
python experiments/run_e12_uncertainty_bounds.py
python experiments/run_e15_manual_adjudication_robustness.py
python experiments/run_e16_manual_calibrated_small_sample_bounds.py
python experiments/run_e18_power_and_sample_size_planning.py
python experiments/run_e19_manual_label_perturbation_sensitivity.py
python experiments/run_e20_bayesian_posterior_sensitivity.py
```

These scripts regenerate their JSON/Markdown summaries from included local artifacts and prior-stage outputs.

### 5. Regenerate the table-to-artifact consistency proof

```powershell
python experiments/check_table_artifact_consistency.py
```

Expected outputs:

- `experiments/results/table_artifact_consistency_report.json`
- `experiments/results/table_artifact_consistency_report.md`

Current repository state:

- latest local report shows `220/220` checks passed
- file: `experiments/results/table_artifact_consistency_report.md`
- the checker expands local `\input{...}` and `\include{...}` files before parsing tables

### 6. Rebuild the paper

```powershell
cd neurips2026_submission
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=_build main.tex
```

Expected output:

- `neurips2026_submission/_build/main.pdf`

## Protocol-Replay Path

These studies are reproducible in method and code, but not guaranteed to be numerically frozen because they depend on hosted models or external annotator input.

### A. Hosted direct-endpoint pilot

```powershell
python experiments/run_real_api_pilot.py --model gpt-4.1-mini --base-url $env:OPENAI_BASE_URL --api-key $env:OPENAI_API_KEY
```

This script:

- loads task instances
- runs vanilla / RTG conditions on an OpenAI-compatible endpoint
- stores raw responses and normalized trajectories
- evaluates the resulting trajectories with the local trajectory-aware evaluator
- writes aggregate JSON summaries for later appendix studies

### B. Prospective paired real-platform pilot

```powershell
python experiments/run_e25_prospective_real_platform_paired.py --model gpt-4.1-mini --base-url $env:OPENAI_BASE_URL --api-key $env:OPENAI_API_KEY --task-file tasks/statepoisonbench_realpaired_v1.jsonl
```

This is the code path behind the prospective paired protocol. It is protocol-replayable but not claimed to be numerically frozen across providers or rerun dates.

### C. Local open-weight pilot

```powershell
python experiments/run_local_hf_open_weight_pilot.py --model-path <LOCAL_MODEL_PATH> --model-name qwen2.5-32b-instruct
```

This requires a local Hugging Face model and GPU memory. The included code and task pack are sufficient; the model weights themselves are not bundled.

### D. External audit packet preparation and aggregation

```powershell
python experiments/run_e22_prepare_independent_audit_pack.py
python experiments/run_e22_aggregate_independent_audit.py
python experiments/run_e23_prepare_c1_decoupled_audit_pack.py
python experiments/run_e23_aggregate_c1_decoupled_audit.py
python experiments/run_e24_prepare_single_external_expanded_pack.py
python experiments/run_e24_aggregate_single_external_expanded_pack.py
```

These scripts prove that the blind-packet construction and aggregation logic are included. The exact final audit sheet contents depend on external reviewer returns.

## Non-Redistributable Layer

The anonymous supplement intentionally does not release:

- raw platform traces tied to real accounts or sessions
- compacted session state artifacts
- account-linked workflow logs
- proprietary model weights

This is not a hidden omission relative to the paper. It is the same release boundary already stated in the appendix and checklist.

## ED Hosting Plan

Before OpenReview upload, use the active anonymous review repository:

- Code URL: `https://anonymous.4open.science/r/StatePoisonBench-C1D2`
- Dataset / artifact URL: `https://anonymous.4open.science/r/StatePoisonBench-C1D2`
- OpenReview supplement: generated zip from `outputs/submission_packages/`

The code repository should host the runnable benchmark package. The dataset/artifact host should mirror `tasks/`, `experiments/results/`, `DATASET_CARD.md`, `croissant_metadata.jsonld`, `DATA_LICENSE.md`, and the release-boundary documentation.

## Reviewer-Facing Reading Guide

If a reviewer wants the fastest audit path, the recommended order is:

1. inspect `tasks/` and `scripts/statepoisonbench_loader.py`
2. inspect `scripts/statepoisonbench_evaluator_v2.py`
3. run `python experiments/run_all_experiments.py`
4. run `python experiments/run_supplementary_experiments.py`
5. run `python experiments/check_table_artifact_consistency.py`
6. compare the generated report with `neurips2026_submission/main.tex`
7. inspect `DATASET_CARD.md`, `croissant_metadata.jsonld`, and `docs/asset_license_matrix.md`
8. rebuild the PDF with `latexmk`

This path is sufficient to verify that the anonymous package contains executable benchmark code, local artifact provenance, and automated manuscript-to-artifact consistency checking.

## Artifact-to-Command Map

| Output artifact | Regeneration command |
|---|---|
| `experiments/results/experiment_1_baseline.json` | `python experiments/run_all_experiments.py` |
| `experiments/results/experiment_2_scaling.json` | `python experiments/run_all_experiments.py` |
| `experiments/results/experiment_3_turns.json` | `python experiments/run_all_experiments.py` |
| `experiments/results/supplementary_experiments.json` | `python experiments/run_supplementary_experiments.py` |
| `experiments/results/server_robustness_sweeps_full.json` | `python experiments/run_server_robustness_sweeps.py --output-prefix server_robustness_sweeps_full` |
| `experiments/results/e10_near_positive_causal_replay.json` | `python experiments/run_e10_e11_experiments.py` |
| `experiments/results/e11_cross_stack_api_spot_check.json` | `python experiments/run_e10_e11_experiments.py` |
| `experiments/results/e12_uncertainty_bounds.json` | `python experiments/run_e12_uncertainty_bounds.py` |
| `experiments/results/e15_manual_adjudication_robustness.json` | `python experiments/run_e15_manual_adjudication_robustness.py` |
| `experiments/results/e16_manual_calibrated_small_sample_bounds.json` | `python experiments/run_e16_manual_calibrated_small_sample_bounds.py` |
| `experiments/results/e18_power_and_sample_size_planning.json` | `python experiments/run_e18_power_and_sample_size_planning.py` |
| `experiments/results/e19_manual_label_perturbation_sensitivity.json` | `python experiments/run_e19_manual_label_perturbation_sensitivity.py` |
| `experiments/results/e20_bayesian_posterior_sensitivity.json` | `python experiments/run_e20_bayesian_posterior_sensitivity.py` |
| `experiments/results/table_artifact_consistency_report.json` | `python experiments/check_table_artifact_consistency.py` |
| `neurips2026_submission/_build/main.pdf` | `latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=_build main.tex` |

## Suggested Submission Blurb

If you need a short note for the rebuttal / supplementary-material textbox, use:

> The anonymous ED supplement includes executable benchmark task packs, loader/evaluator code, synthetic-generation scripts, aggregation scripts, a manuscript-to-artifact consistency checker, dataset card, Croissant metadata, and license/release-boundary documentation. Synthetic benchmark results are exactly replayable from included code and seeds; hosted-endpoint studies are protocol-replayable but not numerically frozen because they depend on external APIs; raw account-linked platform traces are intentionally not redistributed. The repository also includes a table-to-artifact provenance map and an automated consistency report linking manuscript numbers to local JSON artifacts.
