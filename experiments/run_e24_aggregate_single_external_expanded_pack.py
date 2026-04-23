"""
E24: aggregate one-external-annotator results for expanded real-trace calibration pack.

Default input:
- experiments/results/e24_single_external_expanded_pack/e24_internal_manifest.json
- experiments/results/e24_single_external_expanded_pack/e24_sheet.csv

Outputs:
- experiments/results/e24_single_external_calibration.json
- experiments/results/e24_single_external_calibration.md
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
PACK_DIR = RESULTS_DIR / "e24_single_external_expanded_pack"

DEFAULT_INTERNAL = PACK_DIR / "e24_internal_manifest.json"
DEFAULT_SHEET = PACK_DIR / "e24_sheet.csv"
OUT_JSON = RESULTS_DIR / "e24_single_external_calibration.json"
OUT_MD = RESULTS_DIR / "e24_single_external_calibration.md"

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
        "likely fp or benign": "likely_false_positive_or_benign",
        "likely_false_positive": "likely_false_positive_or_benign",
        "likely benign": "likely_false_positive_or_benign",
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


def is_clear(label: str) -> bool:
    return label == "clear_contamination_positive"


def ratio(k: int, n: int) -> float:
    return round(k / n, 3) if n else 0.0


def bucket_summary(rows: Iterable[Dict[str, object]]) -> Dict[str, object]:
    rows = list(rows)
    n = len(rows)
    exact = sum(1 for row in rows if row["author_primary_label"] == row["external_manual_label"])
    binary = sum(
        1
        for row in rows
        if is_clear(str(row["author_primary_label"])) == is_clear(str(row["external_manual_label"]))
    )
    return {
        "n": n,
        "exact_3way_agreement": {"k": exact, "n": n, "rate": ratio(exact, n)},
        "binary_agreement_clear_vs_non_clear": {"k": binary, "n": n, "rate": ratio(binary, n)},
        "external_label_counts": dict(Counter(str(row["external_manual_label"]) for row in rows)),
    }


def disagreement_type(author: str, external: str) -> str:
    if author == external:
        return "agree"
    if external == "clear_contamination_positive" and author != external:
        return "external_clear_vs_author_non_clear"
    if author == "clear_contamination_positive" and external != author:
        return "author_clear_vs_external_non_clear"
    if author == "likely_false_positive_or_benign" and external == "ambiguous":
        return "likely_vs_ambiguous"
    if author == "ambiguous" and external == "likely_false_positive_or_benign":
        return "ambiguous_vs_likely"
    return f"{author}_vs_{external}"


def render_md(payload: Dict[str, object]) -> str:
    lines: List[str] = []
    lines.append(f"# {payload['meta']['name']}")
    lines.append("")
    lines.append(f"Generated at: {payload['meta']['generated_at_utc']}")
    lines.append("")

    comp = payload["sample_composition"]
    lines.append("## Sample Composition")
    lines.append("")
    lines.append("| Bucket | n |")
    lines.append("|---|---:|")
    for bucket, info in comp["buckets"].items():
        lines.append(f"| {bucket} | {info['n']} |")
    lines.append(f"| total | {comp['total_n']} |")
    lines.append("")

    agree = payload["agreement"]
    hidden = payload["negative_slice_hidden_clear"]
    lines.append("## Agreement Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(
        f"| Overall exact agreement | {agree['overall_exact_3way']['k']}/{agree['overall_exact_3way']['n']} ({agree['overall_exact_3way']['rate']:.3f}) |"
    )
    lines.append(
        f"| Overall binary agreement | {agree['overall_binary_clear_vs_non_clear']['k']}/{agree['overall_binary_clear_vs_non_clear']['n']} ({agree['overall_binary_clear_vs_non_clear']['rate']:.3f}) |"
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
            f"| {bucket} | {info['exact_3way_agreement']['k']}/{info['exact_3way_agreement']['n']} ({info['exact_3way_agreement']['rate']:.3f}) | "
            f"{info['binary_agreement_clear_vs_non_clear']['k']}/{info['binary_agreement_clear_vs_non_clear']['n']} ({info['binary_agreement_clear_vs_non_clear']['rate']:.3f}) |"
        )
    lines.append("")

    lines.append("## Disagreement Taxonomy")
    lines.append("")
    lines.append("| Taxonomy | Count |")
    lines.append("|---|---:|")
    for key, value in payload["disagreement_taxonomy"].items():
        lines.append(f"| {key} | {value} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--internal-manifest", type=Path, default=DEFAULT_INTERNAL)
    parser.add_argument("--audit-sheet", type=Path, default=DEFAULT_SHEET)
    parser.add_argument("--out-json", type=Path, default=OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    internal = load_json(args.internal_manifest)
    records = internal.get("records", [])
    if not isinstance(records, list) or not records:
        raise ValueError("internal manifest has no records")
    by_id = {str(row["audit_id"]): row for row in records if isinstance(row, dict)}

    sheet_rows = parse_sheet(args.audit_sheet)
    if not sheet_rows:
        raise ValueError("audit sheet is empty")

    merged: List[Dict[str, object]] = []
    seen = set()
    for row in sheet_rows:
        aid = str(row.get("audit_id", "")).strip()
        if not aid:
            continue
        if aid not in by_id:
            raise ValueError(f"unknown audit_id: {aid}")
        manual_label_raw = str(row.get("manual_label", "")).strip()
        if not manual_label_raw:
            raise ValueError(f"missing manual_label for {aid}")
        merged_row = dict(by_id[aid])
        merged_row["external_manual_label"] = normalize_label(manual_label_raw)
        merged_row["confidence"] = normalize_confidence(str(row.get("confidence", "")))
        merged_row["one_line_rationale"] = str(row.get("one_line_rationale", "")).strip()
        merged.append(merged_row)
        seen.add(aid)

    missing = sorted(set(by_id.keys()) - seen)
    if missing:
        raise ValueError(f"audit sheet missing {len(missing)} rows, first few: {missing[:5]}")

    overall_exact = sum(1 for row in merged if row["author_primary_label"] == row["external_manual_label"])
    overall_binary = sum(
        1
        for row in merged
        if is_clear(str(row["author_primary_label"])) == is_clear(str(row["external_manual_label"]))
    )

    by_bucket: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    for row in merged:
        by_bucket[str(row["source_bucket"])].append(row)

    negative_slice = [row for row in merged if str(row["source_bucket"]) in NEGATIVE_BUCKETS]
    hidden_clear = [row for row in negative_slice if is_clear(str(row["external_manual_label"]))]

    disagreements = []
    for row in merged:
        if row["author_primary_label"] == row["external_manual_label"]:
            continue
        disagreements.append(
            {
                "audit_id": row["audit_id"],
                "source_bucket": row["source_bucket"],
                "trajectory_path": row["trajectory_path"],
                "author_primary_label": row["author_primary_label"],
                "author_label_source": row["author_label_source"],
                "external_manual_label": row["external_manual_label"],
                "confidence": row["confidence"],
                "one_line_rationale": row["one_line_rationale"],
                "disagreement_type": disagreement_type(
                    str(row["author_primary_label"]),
                    str(row["external_manual_label"]),
                ),
            }
        )
    taxonomy = dict(Counter(str(row["disagreement_type"]) for row in disagreements))

    payload = {
        "meta": {
            "experiment_id": "E24",
            "name": "Expanded Single-External Real-Trace Calibration",
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
                    "external_label_counts": dict(Counter(str(row["external_manual_label"]) for row in rows)),
                }
                for bucket, rows in sorted(by_bucket.items())
            },
        },
        "agreement": {
            "overall_exact_3way": {"k": overall_exact, "n": len(merged), "rate": ratio(overall_exact, len(merged))},
            "overall_binary_clear_vs_non_clear": {
                "k": overall_binary,
                "n": len(merged),
                "rate": ratio(overall_binary, len(merged)),
            },
        },
        "per_bucket_agreement": {bucket: bucket_summary(rows) for bucket, rows in sorted(by_bucket.items())},
        "negative_slice_hidden_clear": {
            "k": len(hidden_clear),
            "n": len(negative_slice),
            "rate": ratio(len(hidden_clear), len(negative_slice)),
            "audit_ids": [row["audit_id"] for row in hidden_clear],
        },
        "disagreement_taxonomy": taxonomy,
        "disagreements": disagreements,
    }

    args.out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.out_md.write_text(render_md(payload), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()

