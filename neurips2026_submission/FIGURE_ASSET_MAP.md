# Figure Asset Map

This note is the current source-of-truth for manuscript image placement and correspondence.

## Live manuscript assets

The LaTeX root uses `\graphicspath{{figures/}}` in `main.tex`, so `neurips2026_submission/figures/` is the only live manuscript image directory.

Only the six numbered assets below are retained as paper-source figures.

| Paper figure | Active asset | Referenced from | Topic / caption shorthand | Provenance |
| --- | --- | --- | --- | --- |
| Fig. 1 | `figures/figure1.png` | `sections/main_text.tex` | Persistent-state contamination pipeline | Scripted (`scripts/generate_concept_figures.py`) |
| Fig. 2 | `figures/figure2.png` | `sections/main_text.tex` | Three-tier evidence packet / evidence ladder | Scripted (`scripts/generate_concept_figures.py`) |
| Fig. 3 | `figures/figure3.png` | `sections/main_text.tex` | Ambiguous real-trace propagation chain | Manual / curated image asset |
| Fig. 4 | `figures/figure4.png` | `sections/appendix_benchmark.tex` | Synthetic task-schema lifecycle | Manual / curated image asset |
| Fig. 5 | `figures/figure5.png` | `sections/appendix_benchmark.tex` | Trace-ingestion architecture | Manual / curated image asset |
| Fig. 6 | `figures/figure6.png` | `sections/appendix_validation.tex` | Calibration ladder for supplementary grounding | Scripted (`scripts/generate_concept_figures.py`) |

## Removed non-live assets

The following non-live image holdings were intentionally removed during the 2026-04-23 cleanup:

- `neurips2026_submission/2026-04-20_ai_replacement/`
- `_archive/figure_backups/2026-04-20_ai_replacement/`
- `outputs/tmp_image_review/`
- `outputs/tmp_image_review_after/`
- `_tmp_pdf_review/`

Those directories contained candidate variants, historical backups, or temporary review screenshots. They are not part of the paper-source asset set.

## Non-source image folders

These locations may contain image files, but they are derived outputs rather than manuscript source assets:

- `neurips2026_submission/_build/`: build products and compile checks. PNG previews/crops were cleared during cleanup and should not be recreated as source assets.
- `outputs/submission_packages/.../neurips2026_submission/`: packaged copies of the submission snapshot.

Do not edit those copies when updating the paper figures; edit the live assets in `neurips2026_submission/figures/` instead.

## Dormant reference

`sections/appendix_validation.tex` contains a reference to `figA4_s13_s24_calibration_snapshot.pdf`, but that figure sits inside an `\iffalse ... \fi` block and is not part of the current compiled manuscript. It does not need to exist unless that archived block is re-enabled.

## Maintenance rule

Going forward:

- Keep the actively referenced numbered manuscript figures in `neurips2026_submission/figures/`.
- Treat any future candidate or review-only image as disposable unless it is explicitly promoted into `figures/`.
- Avoid direct `\includegraphics{other-folder/...}` references unless a figure is intentionally being tested and will be folded back into `figures/` before finalization.
