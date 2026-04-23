# Anonymous Hosting Instructions

Use two anonymous, reviewer-accessible URLs before OpenReview submission.

## Code Repository

Recommended target: anonymous GitHub repository or anonymous code-hosting mirror.

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

Recommended target: anonymous Hugging Face Dataset.

Required contents:

- `tasks/*.jsonl`
- `experiments/results/*.json`
- `experiments/results/*.md`
- `DATASET_CARD.md`
- `croissant_metadata.jsonld`
- `docs/release_boundary.md`
- `docs/asset_license_matrix.md`
- `DATA_LICENSE.md`

## OpenReview Fields

Use the following placeholders until the anonymous URLs are live:

- Code URL: `<ANON_GITHUB_URL>`
- Dataset URL: `<ANON_HF_DATASET_URL>`
- Supplement: upload the generated zip from `outputs/submission_packages/`

After replacing placeholders, run an anonymity scan for author names, private paths, API keys, and account-linked trace names.
