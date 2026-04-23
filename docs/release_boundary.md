# StatePoisonBench Release Boundary

## Released for ED Review

- Synthetic JSONL task packs under `tasks/`.
- Loader, evaluator, generation, aggregation, and consistency-check scripts.
- Paper-linked JSON/Markdown result artifacts under `experiments/results/`.
- Anonymous LaTeX source and built PDF.
- Dataset card, Croissant metadata, license files, and reviewer instructions.

## Not Released

- Raw account-linked OpenCode/Codex/platform traces.
- Compacted session state artifacts.
- Private workflow logs or filesystem snapshots.
- API keys, endpoint credentials, or provider account identifiers.
- Proprietary model weights.

## Reproducibility Layers

- Exact replay: synthetic task packs, seeded generators, deterministic evaluator, aggregation scripts, and table consistency checks.
- Protocol replay: hosted-endpoint studies with included prompts, task packs, and aggregation code, but non-frozen numeric outcomes.
- Non-redistributable: raw platform traces and private workflow state.

## Public Release Commitment

After acceptance, the authors intend to publicly release the core synthetic benchmark resources, evaluator, aggregation scripts, and paper-linked artifacts under the licenses stated in `LICENSE` and `DATA_LICENSE.md`. Non-redistributable trace material remains excluded.
