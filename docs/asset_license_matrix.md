# Asset and License Matrix

| Asset group | Included in review package | Public after acceptance | License or terms |
|---|---:|---:|---|
| Python source in `scripts/` and `experiments/` | Yes | Yes | Apache-2.0 |
| Synthetic task packs in `tasks/` | Yes | Yes | CC BY 4.0 |
| Paper-linked JSON/Markdown result artifacts | Yes | Yes | CC BY 4.0 |
| LaTeX source and documentation | Yes | Yes | CC BY 4.0 unless code-like |
| Croissant metadata and dataset card | Yes | Yes | CC BY 4.0 |
| Raw account-linked platform traces | No | No | Non-redistributable |
| Compacted session artifacts | No | No | Non-redistributable |
| Vendor-hosted model outputs rerunnable via API | Derived summaries only | Derived summaries only | Provider terms apply |
| Open-weight model weights | No | No | Upstream model licenses apply |
| NeurIPS style file | Yes, for compilation | Yes, if allowed by conference distribution | NeurIPS-provided terms |

The package intentionally separates code licensing from benchmark artifact licensing to support ED review without redistributing sensitive platform traces.
