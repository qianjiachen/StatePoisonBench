"""
E23: aggregate one-external-annotator results for detector-decoupled C1 fairness audit.

Default input:
- experiments/results/e23_c1_decoupled_audit_pack/e23_c1_decoupled_internal_manifest.json
- experiments/results/e23_c1_decoupled_audit_pack/e23_c1_decoupled_sheet.csv

Outputs:
- experiments/results/e23_c1_decoupled_audit_calibration.json
- experiments/results/e23_c1_decoupled_audit_calibration.md
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "experiments" / "results"
PACK_DIR = RESULTS_DIR / "e23_c1_decoupled_audit_pack"

DEFAULT_INTERNAL = PACK_DIR / "e23_c1_decoupled_internal_manifest.json"
DEFAULT_SHEET = PACK_DIR / "e23_c1_decoupled_sheet.csv"
OUT_JSON = RESULTS_DIR / "e23_c1_decoupled_audit_calibration.json"
OUT_MD = RESULTS_DIR / "e23_c1_decoupled_audit_calibration.md"

VALID_LABELS = {
    "clear_contamination_positive",
    "likely_false_positive_or_benign",
    "ambiguous",
}
VALID_CONFIDENCE = {"high", "medium", "low", ""}
DETECTOR_KEYS = [
    "state_aware_auto",
    "prompt_local_proxy",
    "harmfulness_proxy",
    "naive_text_proxy",
    "prompt_any_proxy",
]


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
    alias = {
        "clear": "clear_contamination_positive",
        "clear_positive": "clear_contamination_positive",
        "clear contamination positive": "clear_contamination_positive",
        "likely false positive or benign": "likely_false_positive_or_benign",
        "likely fp or benign": "likely_false_positive_or_benign",
        "likely_false_positive": "likely_false_positive_or_benign",
        "likely benign": "likely_false_positive_or_benign",
    }
    norm = alias.get(norm, norm.replace(" ", "_"))
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
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
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


def is_positive_label(label: str) -> bool:
    return label == "clear_contamination_positive"


def safe_div(num: int, den: int) -> float:
    return round(num / den, 3) if den else 0.0


def detector_metrics(rows: List[Dict[str, object]], detector_key: str) -> Dict[str, object]:
    tp = fp = tn = fn = 0
    for row in rows:
        pred = bool(row["detectors"][detector_key])
        gold = bool(row["external_positive"])
        if pred and gold:
            tp += 1
        elif pred and not gold:
            fp += 1
        elif (not pred) and (not gold):
            tn += 1
        else:
            fn += 1
    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn)
    fpr = safe_div(fp, fp + tn)
    f1 = round(2 * precision * recall / (precision + recall), 3) if (precision + recall) > 0 else 0.0
    acc = safe_div(tp + tn, tp + fp + tn + fn)
    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "false_positive_rate": fpr,
        "f1": f1,
        "accuracy": acc,
    }


def binom_cdf(k: int, n: int, p: float) -> float:
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    total = 0.0
    for i in range(k + 1):
        total += math.comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
    return min(1.0, max(0.0, total))


def exact_mcnemar_p(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p_one = binom_cdf(k, n, 0.5)
    p_two = min(1.0, 2.0 * p_one)
    return round(p_two, 6)


def paired_mcnemar(rows: List[Dict[str, object]], key_a: str, key_b: str) -> Dict[str, object]:
    b = c = 0
    for row in rows:
        a_ok = bool(row["detectors"][key_a]) == bool(row["external_positive"])
        b_ok = bool(row["detectors"][key_b]) == bool(row["external_positive"])
        if a_ok and not b_ok:
            b += 1
        elif b_ok and not a_ok:
            c += 1
    return {
        "discordant_a_only": b,
        "discordant_b_only": c,
        "exact_p_two_sided": exact_mcnemar_p(b, c),
    }


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
    for key, value in comp["by_stratum"].items():
        lines.append(f"| {key} | {value} |")
    lines.append(f"| total | {comp['n_total']} |")
    lines.append("")

    lines.append("## Detector Metrics (External Label As Reference)")
    lines.append("")
    lines.append("| Detector | Precision | Recall | FPR | F1 | Accuracy | TP/FP/TN/FN |")
    lines.append("|---|---:|---:|---:|---:|---:|---|")
    for key, row in payload["detector_metrics"].items():
        lines.append(
            f"| {key} | {row['precision']:.3f} | {row['recall']:.3f} | {row['false_positive_rate']:.3f} | "
            f"{row['f1']:.3f} | {row['accuracy']:.3f} | {row['tp']}/{row['fp']}/{row['tn']}/{row['fn']} |"
        )
    lines.append("")

    lines.append("## Paired McNemar vs state_aware_auto")
    lines.append("")
    lines.append("| Comparator | a-only discordant | b-only discordant | Exact p (2-sided) |")
    lines.append("|---|---:|---:|---:|")
    for key, row in payload["paired_tests_vs_state_aware"].items():
        lines.append(
            f"| {key} | {row['discordant_a_only']} | {row['discordant_b_only']} | {row['exact_p_two_sided']:.6f} |"
        )
    lines.append("")

    lines.append("## Label Agreement (Author Reference vs External)")
    lines.append("")
    agree = payload["author_external_agreement"]
    lines.append(
        f"- Exact 3-way agreement: {agree['exact_3way']['k']}/{agree['exact_3way']['n']} ({agree['exact_3way']['rate']:.3f})"
    )
    lines.append(
        f"- Binary agreement (clear vs non-clear): {agree['binary_clear_vs_non_clear']['k']}/{agree['binary_clear_vs_non_clear']['n']} ({agree['binary_clear_vs_non_clear']['rate']:.3f})"
    )
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
        raise ValueError("empty audit sheet")

    merged: List[Dict[str, object]] = []
    seen_ids = set()
    for row in sheet_rows:
        audit_id = str(row.get("audit_id", "")).strip()
        if not audit_id:
            continue
        if audit_id not in by_id:
            raise ValueError(f"unknown audit_id: {audit_id}")
        manual_label_raw = str(row.get("manual_label", "")).strip()
        if not manual_label_raw:
            raise ValueError(f"missing manual_label for {audit_id}")
        label = normalize_label(manual_label_raw)
        confidence = normalize_confidence(str(row.get("confidence", "")))
        merged_row = dict(by_id[audit_id])
        merged_row["external_manual_label"] = label
        merged_row["external_positive"] = is_positive_label(label)
        merged_row["confidence"] = confidence
        merged_row["one_line_rationale"] = str(row.get("one_line_rationale", "")).strip()
        merged.append(merged_row)
        seen_ids.add(audit_id)

    missing = sorted(set(by_id.keys()) - seen_ids)
    if missing:
        raise ValueError(f"audit sheet missing {len(missing)} rows; first few: {missing[:5]}")

    metrics = {key: detector_metrics(merged, key) for key in DETECTOR_KEYS}

    paired = {}
    for key in DETECTOR_KEYS:
        if key == "state_aware_auto":
            continue
        paired[key] = paired_mcnemar(merged, "state_aware_auto", key)

    exact = sum(
        1
        for row in merged
        if str(row.get("author_reference_label")) == str(row.get("external_manual_label"))
    )
    binary = sum(
        1
        for row in merged
        if is_positive_label(str(row.get("author_reference_label")))
        == is_positive_label(str(row.get("external_manual_label")))
    )

    payload = {
        "meta": {
            "experiment_id": "E23",
            "name": "C1 Detector-Decoupled External Audit Calibration",
            "generated_at_utc": now_iso(),
            "internal_manifest": display_path(args.internal_manifest),
            "audit_sheet": display_path(args.audit_sheet),
            "note": (
                "Prompt-local detectors are text-only proxy scorers used for relative fairness calibration on this audit slice."
            ),
        },
        "sample_composition": {
            "n_total": len(merged),
            "by_stratum": dict(Counter(str(row.get("stratum")) for row in merged)),
            "by_model_alias": dict(Counter(str(row.get("model_alias")) for row in merged)),
            "by_defense_mode": dict(Counter(str(row.get("defense_mode")) for row in merged)),
            "external_label_counts": dict(Counter(str(row.get("external_manual_label")) for row in merged)),
        },
        "detector_metrics": metrics,
        "paired_tests_vs_state_aware": paired,
        "author_external_agreement": {
            "exact_3way": {"k": exact, "n": len(merged), "rate": safe_div(exact, len(merged))},
            "binary_clear_vs_non_clear": {"k": binary, "n": len(merged), "rate": safe_div(binary, len(merged))},
        },
    }

    args.out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.out_md.write_text(render_md(payload), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()

