"""
E22 / S21: aggregate audit results for the prepared second-human review packet.

Default input:
- experiments/results/e22_independent_audit_pack/e22_independent_audit_internal_manifest.json
- experiments/results/e22_independent_audit_pack/e22_independent_audit_sheet.csv

Outputs:
- experiments/results/e22_independent_audit_calibration.json
- experiments/results/e22_independent_audit_calibration.md
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "experiments" / "results"
PACK_DIR = RESULTS_DIR / "e22_independent_audit_pack"

DEFAULT_INTERNAL = PACK_DIR / "e22_independent_audit_internal_manifest.json"
DEFAULT_SHEET = PACK_DIR / "e22_independent_audit_sheet.csv"
OUT_JSON = RESULTS_DIR / "e22_independent_audit_calibration.json"
OUT_MD = RESULTS_DIR / "e22_independent_audit_calibration.md"

VALID_LABELS = {
    "clear_contamination_positive",
    "likely_false_positive_or_benign",
    "ambiguous",
}
VALID_CONFIDENCE = {"high", "medium", "low", ""}
NEGATIVE_BUCKETS = {"write_bearing_auto_negative", "random_auto_negative_no_write"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def load_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_label(value: str) -> str:
    norm = value.strip().lower()
    alias_map = {
        "clear": "clear_contamination_positive",
        "clear_positive": "clear_contamination_positive",
        "clear contamination positive": "clear_contamination_positive",
        "likely false positive or benign": "likely_false_positive_or_benign",
        "likely_false_positive": "likely_false_positive_or_benign",
        "likely benign": "likely_false_positive_or_benign",
        "likely fp or benign": "likely_false_positive_or_benign",
    }
    norm = alias_map.get(norm, norm.replace(" ", "_"))
    if norm not in VALID_LABELS:
        raise ValueError(f"invalid manual_label: {value}")
    return norm


def normalize_confidence(value: str) -> str:
    norm = value.strip().lower()
    if norm not in VALID_CONFIDENCE:
        raise ValueError(f"invalid confidence: {value}")
    return norm


def parse_markdown_sheet(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    for line in lines:
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 4 or cells[0] == "audit_id" or set(cells[0]) == {"-"}:
            continue
        rows.append(
            {
                "audit_id": cells[0],
                "manual_label": cells[1],
                "confidence": cells[2],
                "one_line_rationale": cells[3],
            }
        )
    return rows


def parse_sheet(path: Path) -> List[Dict[str, str]]:
    if path.suffix.lower() == ".md":
        return parse_markdown_sheet(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def binary_label(label: str) -> str:
    return "clear" if label == "clear_contamination_positive" else "non_clear"


def disagreement_type(author: str, reviewer: str) -> str:
    if reviewer == "clear_contamination_positive" and author != reviewer:
        return "reviewer_clear_vs_author_non_clear"
    if author == "clear_contamination_positive" and reviewer != author:
        return "author_clear_vs_reviewer_non_clear"
    if author == "likely_false_positive_or_benign" and reviewer == "ambiguous":
        return "likely_vs_ambiguous"
    if author == "ambiguous" and reviewer == "likely_false_positive_or_benign":
        return "ambiguous_vs_likely"
    return f"{author}_vs_{reviewer}"


def ratio(k: int, n: int) -> float:
    return round(k / n, 3) if n else 0.0


def bucket_summary(rows: Iterable[Dict[str, object]]) -> Dict[str, object]:
    rows = list(rows)
    n = len(rows)
    exact = sum(1 for row in rows if row["author_primary_label"] == row["reviewer_manual_label"])
    binary = sum(
        1
        for row in rows
        if binary_label(str(row["author_primary_label"])) == binary_label(str(row["reviewer_manual_label"]))
    )
    return {
        "n": n,
        "exact_agreement": {"k": exact, "n": n, "rate": ratio(exact, n)},
        "binary_clear_vs_non_clear_agreement": {"k": binary, "n": n, "rate": ratio(binary, n)},
        "reviewer_label_counts": dict(Counter(str(row["reviewer_manual_label"]) for row in rows)),
    }


def render_md(payload: Dict[str, object]) -> str:
    lines: List[str] = []
    meta = payload["meta"]
    lines.append(f"# {meta['name']}")
    lines.append("")
    lines.append(f"Generated at: {meta['generated_at_utc']}")
    lines.append("")

    sample = payload["sample_composition"]
    agree = payload["agreement"]
    hidden = payload["negative_slice_hidden_clear_positives"]

    lines.append("## Sample Composition")
    lines.append("")
    lines.append("| Bucket | n |")
    lines.append("|---|---:|")
    for bucket, info in sample["buckets"].items():
        lines.append(f"| {bucket} | {info['n']} |")
    lines.append(f"| total | {sample['total_n']} |")
    lines.append("")

    lines.append("## Agreement Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(
        f"| Overall exact agreement | {agree['overall_exact_agreement']['k']}/{agree['overall_exact_agreement']['n']} ({agree['overall_exact_agreement']['rate']:.3f}) |"
    )
    lines.append(
        f"| Clear vs non-clear binary agreement | {agree['overall_binary_clear_vs_non_clear_agreement']['k']}/{agree['overall_binary_clear_vs_non_clear_agreement']['n']} ({agree['overall_binary_clear_vs_non_clear_agreement']['rate']:.3f}) |"
    )
    lines.append(
        f"| Hidden clear positives in negative slice | {hidden['k']}/{hidden['n']} ({hidden['rate']:.3f}) |"
    )
    lines.append("")

    lines.append("## Per-Bucket Agreement")
    lines.append("")
    lines.append("| Bucket | Exact agreement | Binary agreement |")
    lines.append("|---|---:|---:|")
    for bucket, info in payload["per_bucket_agreement"].items():
        lines.append(
            f"| {bucket} | {info['exact_agreement']['k']}/{info['exact_agreement']['n']} ({info['exact_agreement']['rate']:.3f}) | "
            f"{info['binary_clear_vs_non_clear_agreement']['k']}/{info['binary_clear_vs_non_clear_agreement']['n']} ({info['binary_clear_vs_non_clear_agreement']['rate']:.3f}) |"
        )
    lines.append("")

    lines.append("## Disagreement Taxonomy")
    lines.append("")
    lines.append("| Taxonomy | Count |")
    lines.append("|---|---:|")
    for key, value in payload["disagreement_taxonomy"].items():
        lines.append(f"| {key} | {value} |")
    lines.append("")

    lines.append("## Disagreement List")
    lines.append("")
    if payload["disagreements"]:
        lines.append("| audit_id | bucket | author | reviewer | confidence | rationale |")
        lines.append("|---|---|---|---|---|---|")
        for row in payload["disagreements"]:
            rationale = str(row.get("one_line_rationale", "")).replace("|", "/")
            lines.append(
                f"| {row['audit_id']} | {row['source_bucket']} | {row['author_primary_label']} | {row['reviewer_manual_label']} | {row['confidence'] or 'n/a'} | {rationale or 'n/a'} |"
            )
    else:
        lines.append("No disagreements.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--internal-manifest", type=Path, default=DEFAULT_INTERNAL)
    parser.add_argument("--audit-sheet", type=Path, default=DEFAULT_SHEET)
    parser.add_argument("--out-json", type=Path, default=OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    parser.add_argument("--experiment-id", default="E22")
    parser.add_argument("--display-name", default="Independent Second-Human Audit Calibration")
    args = parser.parse_args()

    internal = load_json(args.internal_manifest)
    internal_rows = internal.get("records", [])
    if not isinstance(internal_rows, list) or not internal_rows:
        raise ValueError("internal manifest has no records")
    internal_by_id = {str(row["audit_id"]): row for row in internal_rows if isinstance(row, dict)}

    sheet_rows = parse_sheet(args.audit_sheet)
    if not sheet_rows:
        raise ValueError(f"no rows found in audit sheet: {args.audit_sheet}")

    merged: List[Dict[str, object]] = []
    seen_ids: set[str] = set()
    for row in sheet_rows:
        audit_id = str(row.get("audit_id", "")).strip()
        if not audit_id:
            continue
        if audit_id not in internal_by_id:
            raise ValueError(f"unknown audit_id in sheet: {audit_id}")
        manual_label_raw = str(row.get("manual_label", "")).strip()
        if not manual_label_raw:
            raise ValueError(f"missing manual_label for {audit_id}")
        confidence = normalize_confidence(str(row.get("confidence", "")))
        merged_row = dict(internal_by_id[audit_id])
        merged_row["reviewer_manual_label"] = normalize_label(manual_label_raw)
        merged_row["confidence"] = confidence
        merged_row["one_line_rationale"] = str(row.get("one_line_rationale", "")).strip()
        merged.append(merged_row)
        seen_ids.add(audit_id)

    missing_ids = sorted(set(internal_by_id) - seen_ids)
    if missing_ids:
        raise ValueError(f"audit sheet missing {len(missing_ids)} rows: {', '.join(missing_ids[:5])}")

    overall_exact = sum(1 for row in merged if row["author_primary_label"] == row["reviewer_manual_label"])
    overall_binary = sum(
        1
        for row in merged
        if binary_label(str(row["author_primary_label"])) == binary_label(str(row["reviewer_manual_label"]))
    )

    per_bucket_rows: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    for row in merged:
        per_bucket_rows[str(row["source_bucket"])].append(row)

    negative_slice = [row for row in merged if str(row["source_bucket"]) in NEGATIVE_BUCKETS]
    hidden_clear = [row for row in negative_slice if row["reviewer_manual_label"] == "clear_contamination_positive"]

    disagreements = [
        {
            "audit_id": row["audit_id"],
            "source_bucket": row["source_bucket"],
            "trajectory_path": row["trajectory_path"],
            "author_primary_label": row["author_primary_label"],
            "reviewer_manual_label": row["reviewer_manual_label"],
            "confidence": row["confidence"],
            "one_line_rationale": row["one_line_rationale"],
            "disagreement_type": disagreement_type(
                str(row["author_primary_label"]),
                str(row["reviewer_manual_label"]),
            ),
        }
        for row in merged
        if row["author_primary_label"] != row["reviewer_manual_label"]
    ]
    taxonomy = dict(Counter(str(row["disagreement_type"]) for row in disagreements))

    payload = {
        "meta": {
            "experiment_id": str(args.experiment_id),
            "name": str(args.display_name),
            "generated_at_utc": now_iso(),
            "internal_manifest": display_path(args.internal_manifest),
            "audit_sheet": display_path(args.audit_sheet),
        },
        "sample_composition": {
            "total_n": len(merged),
            "buckets": {
                bucket: {
                    "n": len(rows),
                    "author_label_counts": dict(Counter(str(row["author_primary_label"]) for row in rows)),
                }
                for bucket, rows in sorted(per_bucket_rows.items())
            },
        },
        "agreement": {
            "overall_exact_agreement": {"k": overall_exact, "n": len(merged), "rate": ratio(overall_exact, len(merged))},
            "overall_binary_clear_vs_non_clear_agreement": {
                "k": overall_binary,
                "n": len(merged),
                "rate": ratio(overall_binary, len(merged)),
            },
        },
        "per_bucket_agreement": {
            bucket: bucket_summary(rows)
            for bucket, rows in sorted(per_bucket_rows.items())
        },
        "negative_slice_hidden_clear_positives": {
            "k": len(hidden_clear),
            "n": len(negative_slice),
            "rate": ratio(len(hidden_clear), len(negative_slice)),
            "audit_ids": [row["audit_id"] for row in hidden_clear],
            "rows": [
                {
                    "audit_id": row["audit_id"],
                    "source_bucket": row["source_bucket"],
                    "trajectory_path": row["trajectory_path"],
                    "author_primary_label": row["author_primary_label"],
                    "reviewer_manual_label": row["reviewer_manual_label"],
                    "confidence": row["confidence"],
                    "one_line_rationale": row["one_line_rationale"],
                }
                for row in hidden_clear
            ],
        },
        "disagreement_taxonomy": taxonomy,
        "disagreements": disagreements,
    }

    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.out_md.write_text(render_md(payload), encoding="utf-8")

    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
