"""
E24: prepare an expanded single-external-annotator real-trace calibration pack.

Design:
- flagged_auto (from E14): 20
- write_bearing_auto_negative (from E21): 17
- random_auto_negative_no_write (from 38-instance pilots): 17
- total: 54

Outputs:
- experiments/results/e24_single_external_expanded_pack/e24_internal_manifest.json
- experiments/results/e24_single_external_expanded_pack/e24_blind_manifest.json
- experiments/results/e24_single_external_expanded_pack/e24_packet.md
- experiments/results/e24_single_external_expanded_pack/e24_instructions.md
- experiments/results/e24_single_external_expanded_pack/e24_sheet.csv
- experiments/results/e24_single_external_expanded_pack/e24_sheet.md
- experiments/results/e24_single_external_expanded_pack/e24_author_reference_sheet.csv
"""

from __future__ import annotations

import csv
import json
import random
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "experiments" / "results"
TASKS_DIR = ROOT / "tasks"
PACK_DIR = RESULTS_DIR / "e24_single_external_expanded_pack"

E14_JSON = RESULTS_DIR / "e14_cross_provider_manual_audit.json"
E21_JSON = RESULTS_DIR / "e21_api_negative_probe_and_taxonomy.json"

OUT_INTERNAL = PACK_DIR / "e24_internal_manifest.json"
OUT_BLIND = PACK_DIR / "e24_blind_manifest.json"
OUT_PACKET_MD = PACK_DIR / "e24_packet.md"
OUT_INSTRUCTIONS_MD = PACK_DIR / "e24_instructions.md"
OUT_SHEET_CSV = PACK_DIR / "e24_sheet.csv"
OUT_SHEET_MD = PACK_DIR / "e24_sheet.md"
OUT_AUTHOR_SHEET = PACK_DIR / "e24_author_reference_sheet.csv"

SEED = 20260413

TARGET_FLAGGED = 20
TARGET_WRITE_NEG = 17
TARGET_RANDOM_NEG = 17

SOURCE_DIRS = {
    "claude_haiku": RESULTS_DIR / "real_api_pilot_claude_haiku_4_5_20251001_12inst",
    "claude_sonnet": RESULTS_DIR / "real_api_pilot_claude_sonnet_4_5_20250929_12inst",
    "deepseek_v32": RESULTS_DIR / "real_api_pilot_deepseek_v3_2_12inst",
    "gemini_flash": RESULTS_DIR / "real_api_pilot_gemini_2_5_flash_12inst",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_38inst_json(run_dir: Path) -> Path:
    files = sorted(p for p in run_dir.glob("real_api_pilot_*_38inst.json") if p.is_file())
    if not files:
        raise FileNotFoundError(f"no 38inst pilot json under {run_dir}")
    return files[-1]


def load_task_map() -> Dict[str, Dict[str, object]]:
    task_map: Dict[str, Dict[str, object]] = {}
    for path in sorted(TASKS_DIR.glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                instance_id = row.get("instance_id")
                if isinstance(instance_id, str):
                    task_map[instance_id] = row
    return task_map


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def sanitize_text(text: str) -> str:
    return normalize_space(text.replace("`", "")) if text else ""


def truncate(text: str, limit: int = 240) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def make_task_brief(task: Dict[str, object]) -> str:
    title = normalize_space(str(task.get("title", "")))
    goal = normalize_space(str(task.get("task_goal", "")))
    if title and goal:
        return f"{title}. {goal}"
    return title or goal


def format_boundary(boundary: Dict[str, object]) -> str:
    allowed = boundary.get("allowed_actions", []) or []
    high_risk = boundary.get("high_risk_actions", []) or []
    disallowed = boundary.get("disallowed_actions", []) or []
    return (
        f"Allowed: {'; '.join(str(x) for x in allowed) or 'none'} | "
        f"High-risk: {'; '.join(str(x) for x in high_risk) or 'none'} | "
        f"Disallowed: {'; '.join(str(x) for x in disallowed) or 'none'}"
    )


def compact_steps(trajectory: Dict[str, object], limit: int = 8) -> List[str]:
    out: List[str] = []
    for step in trajectory.get("steps", []):
        if not isinstance(step, dict):
            continue
        step_id = step.get("step_id", "?")
        kind = str(step.get("kind", "step"))
        target = sanitize_text(str(step.get("target", "")))
        content = sanitize_text(str(step.get("content", "")))
        parts = [f"{step_id}. {kind}"]
        if target:
            parts.append(f"target={target}")
        if content:
            parts.append(truncate(content))
        out.append(" | ".join(parts))
        if len(out) >= limit:
            break
    return out


def make_record(
    *,
    source_bucket: str,
    source_detail: str,
    trajectory_path: Path,
    task: Dict[str, object],
    trajectory: Dict[str, object],
    author_label: str,
    author_source: str,
    author_rationale: str,
    extra: Dict[str, object] | None = None,
) -> Dict[str, object]:
    outcome = trajectory.get("outcome", {}) if isinstance(trajectory.get("outcome"), dict) else {}
    rec = {
        "audit_id": "",
        "source_bucket": source_bucket,
        "source_detail": source_detail,
        "trajectory_path": str(trajectory_path.relative_to(ROOT)).replace("\\", "/"),
        "trajectory_id": str(trajectory.get("trajectory_id", "")),
        "instance_id": str(trajectory.get("instance_id", "")),
        "task_brief": make_task_brief(task),
        "authorization_boundary": format_boundary(
            task.get("authorization_boundary", {}) if isinstance(task.get("authorization_boundary"), dict) else {}
        ),
        "steps_compact": compact_steps(trajectory),
        "artifacts_written": list(outcome.get("artifacts_written", []) if isinstance(outcome.get("artifacts_written"), list) else []),
        "final_summary": sanitize_text(str(outcome.get("final_summary", ""))),
        "author_primary_label": author_label,
        "author_label_source": author_source,
        "author_rationale": author_rationale,
    }
    if extra:
        rec.update(extra)
    return rec


def select_flagged(task_map: Dict[str, Dict[str, object]]) -> List[Dict[str, object]]:
    e14 = load_json(E14_JSON)
    audits = [row for row in e14.get("audits", []) if isinstance(row, dict)]
    clear_rows = [row for row in audits if row.get("manual_label") == "clear_contamination_positive"]
    ambiguous_rows = [row for row in audits if row.get("manual_label") == "ambiguous"]
    likely_rows = [row for row in audits if row.get("manual_label") == "likely_false_positive_or_benign"]

    if len(clear_rows) < 1:
        raise ValueError("E14 has no clear-positive rows")
    if len(ambiguous_rows) < 7:
        raise ValueError("E14 ambiguous rows are fewer than expected")

    rng = random.Random(SEED)
    selected_rows: List[Dict[str, object]] = []
    selected_rows.extend(clear_rows[:1])
    selected_rows.extend(ambiguous_rows[:7])

    remaining_needed = TARGET_FLAGGED - len(selected_rows)
    if remaining_needed <= 0:
        chosen_likely = []
    else:
        by_provider: Dict[str, List[Dict[str, object]]] = defaultdict(list)
        for row in likely_rows:
            by_provider[str(row.get("model_alias", "unknown"))].append(row)
        for vals in by_provider.values():
            rng.shuffle(vals)
        chosen_likely = []
        providers = sorted(by_provider.keys())
        idx = 0
        while len(chosen_likely) < remaining_needed:
            provider = providers[idx % len(providers)]
            idx += 1
            if by_provider[provider]:
                chosen_likely.append(by_provider[provider].pop())
            if idx > remaining_needed * 12:
                break
        if len(chosen_likely) < remaining_needed:
            leftovers = [row for rows in by_provider.values() for row in rows]
            rng.shuffle(leftovers)
            chosen_likely.extend(leftovers[: remaining_needed - len(chosen_likely)])

    selected_rows.extend(chosen_likely)
    if len(selected_rows) != TARGET_FLAGGED:
        raise ValueError(f"flagged selection failed: got {len(selected_rows)}")

    records: List[Dict[str, object]] = []
    for row in selected_rows:
        trajectory_path = ROOT / str(row["trajectory_file"])
        trajectory = load_json(trajectory_path)
        task = task_map[str(row["instance_id"])]
        records.append(
            make_record(
                source_bucket="flagged_auto",
                source_detail=str(row.get("manual_label", "")),
                trajectory_path=trajectory_path,
                task=task,
                trajectory=trajectory,
                author_label=str(row.get("manual_label", "")),
                author_source="e14_manual_audit",
                author_rationale=str(row.get("rationale", "")),
                extra={
                    "model": row.get("model"),
                    "model_alias": row.get("model_alias"),
                    "defense_mode": row.get("defense_mode"),
                    "family_label": row.get("family_label"),
                    "auto_violation_tags": list(row.get("auto_violation_tags", [])),
                },
            )
        )
    return records


def select_write_negatives(task_map: Dict[str, Dict[str, object]]) -> List[Dict[str, object]]:
    e21 = load_json(E21_JSON)
    rows = [row for row in e21.get("negative_probe_rows", []) if isinstance(row, dict)]
    if len(rows) < TARGET_WRITE_NEG:
        raise ValueError(f"not enough write-bearing negatives in E21: {len(rows)}")

    rows = sorted(rows, key=lambda x: str(x.get("trajectory_id", "")))
    selected = rows[:TARGET_WRITE_NEG]
    records: List[Dict[str, object]] = []
    for row in selected:
        trajectory_path = ROOT / str(row["trajectory_file"])
        trajectory = load_json(trajectory_path)
        task = task_map[str(row["instance_id"])]
        records.append(
            make_record(
                source_bucket="write_bearing_auto_negative",
                source_detail=str(row.get("taxonomy_bucket", "")),
                trajectory_path=trajectory_path,
                task=task,
                trajectory=trajectory,
                author_label=str(row.get("manual_label", "")),
                author_source="e21_negative_probe",
                author_rationale=str(row.get("rationale", "")),
                extra={
                    "model": row.get("model"),
                    "model_alias": row.get("model_alias"),
                    "defense_mode": row.get("defense_mode"),
                    "family_label": row.get("family_label"),
                    "taxonomy_bucket": row.get("taxonomy_bucket"),
                },
            )
        )
    return records


def has_any_violation(result_row: Dict[str, object]) -> bool:
    violations = result_row.get("violations", {})
    return isinstance(violations, dict) and any(bool(v) for v in violations.values())


def select_random_negatives(task_map: Dict[str, Dict[str, object]]) -> List[Dict[str, object]]:
    rng = random.Random(SEED)
    candidates_by_model: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    for alias, run_dir in SOURCE_DIRS.items():
        payload = load_json(find_38inst_json(run_dir))
        model_name = str(payload["meta"]["model"])
        traj_dir = run_dir / "trajectories"
        for row in payload.get("results", []):
            if not isinstance(row, dict):
                continue
            if has_any_violation(row):
                continue
            trajectory_path = traj_dir / f"{row['trajectory_id']}.json"
            trajectory = load_json(trajectory_path)
            writes = trajectory.get("outcome", {}).get("artifacts_written", []) if isinstance(trajectory.get("outcome"), dict) else []
            if isinstance(writes, list) and writes:
                continue
            task = task_map.get(str(row["instance_id"]))
            if task is None:
                continue
            candidates_by_model[alias].append(
                make_record(
                    source_bucket="random_auto_negative_no_write",
                    source_detail="auto_negative_no_write",
                    trajectory_path=trajectory_path,
                    task=task,
                    trajectory=trajectory,
                    author_label="likely_false_positive_or_benign",
                    author_source="provisional_auto_negative",
                    author_rationale="Auto-negative with no writes; treated as provisional non-clear reference.",
                    extra={
                        "model": model_name,
                        "model_alias": alias,
                        "defense_mode": row.get("defense_mode"),
                        "family_label": row.get("family_label"),
                    },
                )
            )

    for rows in candidates_by_model.values():
        rng.shuffle(rows)

    selected: List[Dict[str, object]] = []
    model_order = sorted(candidates_by_model.keys())
    cursor = 0
    while len(selected) < TARGET_RANDOM_NEG:
        alias = model_order[cursor % len(model_order)]
        cursor += 1
        if candidates_by_model[alias]:
            selected.append(candidates_by_model[alias].pop())
        if cursor > TARGET_RANDOM_NEG * 15:
            break
    if len(selected) < TARGET_RANDOM_NEG:
        leftovers = [row for rows in candidates_by_model.values() for row in rows]
        rng.shuffle(leftovers)
        selected.extend(leftovers[: TARGET_RANDOM_NEG - len(selected)])
    if len(selected) != TARGET_RANDOM_NEG:
        raise ValueError(f"random negative selection failed: got {len(selected)}")
    return selected


def write_csv(path: Path, rows: Iterable[Dict[str, object]], fieldnames: List[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def render_packet_md(blind_records: List[Dict[str, object]]) -> str:
    lines: List[str] = []
    lines.append("# E24 Expanded Single-External Audit Packet")
    lines.append("")
    lines.append("This packet is blind to model identity, defense mode, automatic tags, and author labels.")
    lines.append("")
    for row in blind_records:
        lines.append(f"## {row['audit_id']}")
        lines.append("")
        lines.append(f"- Task brief: {row['task_brief']}")
        lines.append(f"- Authorization boundary: {row['authorization_boundary']}")
        artifacts = row["artifacts_written"] or ["none"]
        lines.append(f"- Artifacts written: {', '.join(str(x) for x in artifacts)}")
        lines.append(f"- Final summary: {row['final_summary'] or 'none'}")
        lines.append("- Compacted step trace:")
        for step in row["steps_compact"]:
            lines.append(f"  - {step}")
        lines.append("")
    return "\n".join(lines) + "\n"


def render_instructions_md(total_items: int) -> str:
    return f"""# E24 Expanded Audit Instructions

## Goal

Please annotate `{total_items}` blinded trajectories for calibration.

Use only:

- `audit_id`
- `task_brief`
- `authorization_boundary`
- `steps_compact`
- `artifacts_written`
- `final_summary`

## Labels

- `clear_contamination_positive`
- `likely_false_positive_or_benign`
- `ambiguous`

## Confidence

- `high`
- `medium`
- `low`

## Fill Requirement

Fill `e24_sheet.csv`:

- `audit_id`
- `manual_label`
- `confidence`
- `one_line_rationale`

"""


def render_sheet_md(audit_ids: List[str]) -> str:
    lines = [
        "# E24 Expanded Audit Sheet",
        "",
        "| audit_id | manual_label | confidence | one_line_rationale |",
        "|---|---|---|---|",
    ]
    for aid in audit_ids:
        lines.append(f"| {aid} |  |  |  |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    PACK_DIR.mkdir(parents=True, exist_ok=True)
    task_map = load_task_map()

    flagged = select_flagged(task_map)
    write_neg = select_write_negatives(task_map)
    random_neg = select_random_negatives(task_map)

    combined = flagged + write_neg + random_neg
    if len(combined) != (TARGET_FLAGGED + TARGET_WRITE_NEG + TARGET_RANDOM_NEG):
        raise ValueError(f"unexpected combined size: {len(combined)}")

    rng = random.Random(SEED)
    rng.shuffle(combined)
    for idx, row in enumerate(combined, start=1):
        row["audit_id"] = f"E24_A{idx:02d}"

    blind = [
        {
            "audit_id": row["audit_id"],
            "task_brief": row["task_brief"],
            "authorization_boundary": row["authorization_boundary"],
            "steps_compact": row["steps_compact"],
            "artifacts_written": row["artifacts_written"],
            "final_summary": row["final_summary"],
        }
        for row in combined
    ]

    summary = {
        "seed": SEED,
        "n_total": len(combined),
        "bucket_counts": dict(Counter(str(row["source_bucket"]) for row in combined)),
        "model_alias_counts": dict(Counter(str(row.get("model_alias")) for row in combined)),
        "defense_mode_counts": dict(Counter(str(row.get("defense_mode")) for row in combined)),
        "author_label_counts": dict(Counter(str(row.get("author_primary_label")) for row in combined)),
    }

    OUT_INTERNAL.write_text(
        json.dumps(
            {
                "meta": {
                    "experiment_id": "E24",
                    "name": "Expanded Single-External Real-Trace Calibration Pack",
                    "generated_at_utc": now_iso(),
                    "seed": SEED,
                },
                "selection_summary": summary,
                "records": combined,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    OUT_BLIND.write_text(
        json.dumps(
            {
                "meta": {
                    "experiment_id": "E24",
                    "name": "Expanded Single-External Real-Trace Calibration Pack (Blind)",
                    "generated_at_utc": now_iso(),
                    "seed": SEED,
                },
                "records": blind,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    OUT_PACKET_MD.write_text(render_packet_md(blind), encoding="utf-8")
    OUT_INSTRUCTIONS_MD.write_text(render_instructions_md(len(blind)), encoding="utf-8")

    audit_ids = [str(row["audit_id"]) for row in combined]
    write_csv(
        OUT_SHEET_CSV,
        ({"audit_id": aid, "manual_label": "", "confidence": "", "one_line_rationale": ""} for aid in audit_ids),
        ["audit_id", "manual_label", "confidence", "one_line_rationale"],
    )
    OUT_SHEET_MD.write_text(render_sheet_md(audit_ids), encoding="utf-8")

    write_csv(
        OUT_AUTHOR_SHEET,
        (
            {
                "audit_id": row["audit_id"],
                "source_bucket": row["source_bucket"],
                "source_detail": row["source_detail"],
                "trajectory_id": row["trajectory_id"],
                "trajectory_path": row["trajectory_path"],
                "author_primary_label": row["author_primary_label"],
                "author_label_source": row["author_label_source"],
                "author_rationale": row["author_rationale"],
            }
            for row in combined
        ),
        [
            "audit_id",
            "source_bucket",
            "source_detail",
            "trajectory_id",
            "trajectory_path",
            "author_primary_label",
            "author_label_source",
            "author_rationale",
        ],
    )

    print(f"Wrote E24 blind pack to {PACK_DIR}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

