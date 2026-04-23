# Anonymous Hosting Instructions

Use one anonymous, reviewer-accessible repository URL before OpenReview submission.

## Code Repository

Recommended target: the anonymous 4open/GitHub mirror for the review repository.

Required contents:

- `README.md`
- `LICENSE`
- `DATA_LICENSE.md`
- `requirements.txt`
- `tasks/`
- `scripts/`
- `experiments/`
- `neurips2026_submission/`
- `DATASET_CARD.md`
- `croissant_metadata.jsonld`
- `docs/`

Do not upload `_archive`, raw platform traces, API keys, private logs, or local build caches.

## Dataset / Artifact Hosting

For the current submission plan, the same anonymous repository also serves as the dataset/artifact host.

Required reviewer-visible contents:

- `tasks/*.jsonl`
- `experiments/results/*.json`
- `experiments/results/*.md`
- `DATASET_CARD.md`
- `croissant_metadata.jsonld`
- `docs/release_boundary.md`
- `docs/asset_license_matrix.md`
- `DATA_LICENSE.md`

## OpenReview Fields

Use the following URL:

- Code URL: `https://anonymous.4open.science/r/StatePoisonBench-C1D2`
- Dataset URL: `https://anonymous.4open.science/r/StatePoisonBench-C1D2`
- Supplement: upload the generated zip from `outputs/submission_packages/`

After replacing placeholders, run an anonymity scan for author names, private paths, API keys, and account-linked trace names.
