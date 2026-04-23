# Final Submission Snapshot

Generated: 2026-04-23

## Frozen Scope

This snapshot records the artifact set used by the current ED submission-oriented draft after integrating the conservative `S24` prospective paired starter slice and preparing the reviewer-facing resource package.

- The paper is positioned for the NeurIPS 2026 `Evaluations & Datasets` track as a `persistent-state benchmark methodology` paper with `strong controlled evidence + calibrated but limited real-world grounding`.
- `S13--S23` remain the main real-world calibration ladder.
- `S24` is included only as execution-validating prospective pilot evidence, not as treatment-effect evidence.
- The stricter `E25 v2` redesign exists as an off-paper follow-up note and should not be cited as a paper result until expanded.
- The release commitment covers core synthetic benchmark resources, evaluator, aggregation scripts, documentation, and paper-linked artifacts; raw platform traces remain excluded.

## Key Artifacts

- Paper source: `neurips2026_submission/main.tex`
- ED package README: `README.md`
- Dataset card: `DATASET_CARD.md`
- Croissant metadata: `croissant_metadata.jsonld`
- Release boundary: `docs/release_boundary.md`
- Asset/license matrix: `docs/asset_license_matrix.md`
- Independent audit result: `experiments/results/e22_independent_audit_calibration.json`
- Detector-decoupled calibration: `experiments/results/e23_c1_decoupled_audit_calibration.json`
- Expanded external calibration: `experiments/results/e24_single_external_calibration.json`
- S24 paired starter artifact: `experiments/results/e25_realpaired_new12ai_gpt41mini_6pairs/e25_real_paired_gpt_4_1_mini_6pairs.json`
- Consistency report: `experiments/results/table_artifact_consistency_report.md`
- Rebuttal packet: `outputs/rebuttal_ready_packet_s13_s24.md`
- Reviewer-style internal review: `outputs/final_reviewer_style_internal_review.md`

## Current Verification State

- Canonical consistency source: `experiments/results/table_artifact_consistency_report.md` regenerated on `2026-04-23`.
- Table-artifact consistency checker: `220/220` passed, `failed=0`; the checker now expands local LaTeX `\input{...}` and `\include{...}` files before parsing.
- LaTeX compile: success after ED resource-documentation edits.
- PDF length: `25` pages.

## Interpretation Guardrails

- Do not upgrade `S14`, `S21`, `S23`, or `S24` into prevalence claims.
- Do not upgrade RTG into a deployment-ready defense claim.
- Treat `S13--S23` as an API calibration suite, and `S24` as a separate prospective execution-validating pilot rather than an effect-size estimate.
- OpenReview code URL and dataset URL should both point to `https://anonymous.4open.science/r/StatePoisonBench-C1D2`.
