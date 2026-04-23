# StatePoisonBench Task Packs

This directory contains the released synthetic JSONL task packs for the anonymous ED review package.

## File Groups

- `statepoisonbench_v1.jsonl`, `statepoisonbench_v2.jsonl`: schema validation and pilot packs used by the loader/evaluator smoke path.
- `statepoisonbench_main_table*.jsonl`: controlled synthetic core slices used by the main benchmark experiments.
- `statepoisonbench_api_expansion_v1.jsonl`: expanded API calibration slice.
- `statepoisonbench_realpaired*.jsonl`: protocol-replayable prospective paired task packs.

## Stability Contract

Scripts and manuscript references assume these filenames remain stable. Add new task packs here unless a future script migration explicitly changes that contract.

## Release Boundary

These files are synthetic benchmark assets and are intended for reviewer audit and public release under CC BY 4.0. Raw account-linked platform traces and compacted session artifacts are not stored in this directory.
