# NeurIPS 2026 ED Submission Checklist

## Must Pass Before Upload

- Paper builds successfully from `neurips2026_submission/main.tex`.
- `python experiments/check_table_artifact_consistency.py` reports `220/220` or a newer all-pass count.
- Anonymous package contains runnable loader, evaluator, experiment scripts, tasks, results, and paper source.
- README contains active anonymous GitHub and Hugging Face Dataset URLs.
- Dataset card and Croissant metadata are included in the hosted dataset package.
- License files and asset/license matrix are present.
- Raw account-linked traces, compacted session artifacts, credentials, and private logs are absent.

## OpenReview Entries

- Track: Evaluations & Datasets.
- Code URL: anonymous GitHub repository.
- Dataset/resource URL: anonymous Hugging Face Dataset.
- Supplement: generated anonymous code-proof zip.
- Resource statement: exact synthetic replay, protocol replay for hosted endpoints, raw trace exclusion.

## Final Local Commands

```powershell
python scripts/statepoisonbench_loader.py tasks/statepoisonbench_v1.jsonl
python scripts/statepoisonbench_loader.py tasks/statepoisonbench_v2.jsonl
python experiments/run_all_experiments.py
python experiments/run_supplementary_experiments.py
python experiments/check_table_artifact_consistency.py
.\scripts\build_submission.ps1
.\scripts\build_ed_submission_package.ps1
```
