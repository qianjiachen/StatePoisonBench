"""
Prepare an execution packet for a prospective paired continuation study.

Compared with the legacy E25 plan-prep script, this version supports:
- custom task file
- custom output directory
- optional pair-id filtering
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASK_FILE = ROOT / "tasks" / "statepoisonbench_realpaired_v2.jsonl"
DEFAULT_OUT_DIR = ROOT / "experiments" / "results" / "e25_paired_plan"

REQUIRED_CONDITIONS = {"clean", "contaminated"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_jsonl(path: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def notes_of(row: Dict[str, object]) -> Dict[str, object]:
    notes = row.get("notes", {})
    return notes if isinstance(notes, dict) else {}


def auth_of(row: Dict[str, object]) -> Dict[str, object]:
    boundary = row.get("authorization_boundary", {})
    return boundary if isinstance(boundary, dict) else {}


def poison_of(row: Dict[str, object]) -> Dict[str, object]:
    poison = row.get("poisoning", {})
    return poison if isinstance(poison, dict) else {}


def filter_rows(rows: List[Dict[str, object]], pair_ids: set[str]) -> List[Dict[str, object]]:
    if not pair_ids:
        return rows
    out: List[Dict[str, object]] = []
    for row in rows:
        pair_id = str(notes_of(row).get("pair_id", "")).strip()
        if pair_id in pair_ids:
            out.append(row)
    return out


def validate_pairs(rows: List[Dict[str, object]]) -> Dict[str, Dict[str, Dict[str, object]]]:
    grouped: Dict[str, Dict[str, Dict[str, object]]] = defaultdict(dict)
    for row in rows:
        notes = notes_of(row)
        pair_id = str(notes.get("pair_id", "")).strip()
        condition = str(notes.get("pair_condition", "")).strip()
        if not pair_id or condition not in REQUIRED_CONDITIONS:
            raise ValueError(f"missing pair metadata for {row.get('instance_id')}")
        if condition in grouped[pair_id]:
            raise ValueError(f"duplicate {condition} condition for {pair_id}")
        grouped[pair_id][condition] = row

    for pair_id, by_condition in grouped.items():
        if set(by_condition.keys()) != REQUIRED_CONDITIONS:
            raise ValueError(f"{pair_id} does not contain both clean and contaminated conditions")
    return dict(sorted(grouped.items()))


def artifact_filename(row: Dict[str, object]) -> str:
    return f"{row['instance_id']}.md"


def render_artifact(row: Dict[str, object]) -> str:
    notes = notes_of(row)
    boundary = auth_of(row)
    poison = poison_of(row)
    trusted_target = str(notes.get("trusted_target", ""))
    return "\n".join(
        [
            f"# Recovered Artifact for {row['instance_id']}",
            "",
            f"Pair ID: {notes.get('pair_id', '')}",
            f"Condition: {notes.get('pair_condition', '')}",
            f"Family: {notes.get('family_label', '')}",
            f"Trusted target in scope: {trusted_target}",
            "",
            "## Task Goal",
            "",
            str(row.get("task_goal", "")),
            "",
            "## Recovered Content",
            "",
            str(poison.get("payload_text", "")),
            "",
            "## Authorization Boundary",
            "",
            f"Allowed: {', '.join(str(x) for x in boundary.get('allowed_actions', []) or [])}",
            f"High-risk: {', '.join(str(x) for x in boundary.get('high_risk_actions', []) or [])}",
            f"Disallowed: {', '.join(str(x) for x in boundary.get('disallowed_actions', []) or [])}",
            "",
            "## Operator Note",
            "",
            "Run clean and contaminated conditions with the same task, model, and endpoint settings.",
            "Change only the recovered content between conditions.",
            "",
        ]
    )


def write_artifacts(rows: List[Dict[str, object]], root: Path, artifact_dir: Path) -> List[str]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    written: List[str] = []
    for row in rows:
        name = artifact_filename(row)
        out_path = artifact_dir / name
        out_path.write_text(render_artifact(row), encoding="utf-8")
        written.append(str(out_path.relative_to(root)).replace("\\", "/"))
    return written


def make_manifest(
    rows: List[Dict[str, object]],
    grouped: Dict[str, Dict[str, Dict[str, object]]],
    artifact_paths: List[str],
    task_file: Path,
) -> Dict[str, object]:
    by_instance_artifact = {
        row["instance_id"]: artifact_path for row, artifact_path in zip(rows, artifact_paths)
    }
    pair_rows: List[Dict[str, object]] = []
    for pair_id, by_condition in grouped.items():
        exemplar = by_condition["clean"]
        exemplar_notes = notes_of(exemplar)
        pair_rows.append(
            {
                "pair_id": pair_id,
                "family_label": exemplar_notes.get("family_label", ""),
                "trusted_target": exemplar_notes.get("trusted_target", ""),
                "clean_instance_id": by_condition["clean"]["instance_id"],
                "contaminated_instance_id": by_condition["contaminated"]["instance_id"],
                "clean_artifact": by_instance_artifact[by_condition["clean"]["instance_id"]],
                "contaminated_artifact": by_instance_artifact[by_condition["contaminated"]["instance_id"]],
                "task_goal": exemplar.get("task_goal", ""),
            }
        )

    return {
        "meta": {
            "experiment_id": "E25",
            "name": "Prospective Real-Platform Paired Continuation Study",
            "generated_at_utc": now_iso(),
            "task_file": str(task_file.relative_to(ROOT)).replace("\\", "/"),
            "n_condition_specific_instances": len(rows),
            "n_pairs": len(grouped),
        },
        "pairs": pair_rows,
        "instances": [
            {
                "instance_id": row["instance_id"],
                "pair_id": notes_of(row)["pair_id"],
                "pair_condition": notes_of(row)["pair_condition"],
                "family_label": notes_of(row).get("family_label", ""),
                "trusted_target": notes_of(row).get("trusted_target", ""),
                "artifact_file": by_instance_artifact[row["instance_id"]],
                "task_goal": row.get("task_goal", ""),
            }
            for row in rows
        ],
    }


def write_packet(packet_path: Path, manifest: Dict[str, object]) -> None:
    meta = manifest["meta"]
    lines: List[str] = [
        "# Paired Execution Packet",
        "",
        f"Generated at: {meta['generated_at_utc']}",
        "",
        "## Study Goal",
        "",
        "Run matched clean versus contaminated continuation episodes on a real platform while holding task and authorization boundary fixed.",
        "",
        "## Pair Inventory",
        "",
        "| Pair ID | Family | Trusted Target | Clean Instance | Contaminated Instance |",
        "|---|---|---|---|---|",
    ]
    for pair in manifest["pairs"]:
        lines.append(
            f"| {pair['pair_id']} | {pair['family_label']} | {pair['trusted_target']} | "
            f"{pair['clean_instance_id']} | {pair['contaminated_instance_id']} |"
        )
    lines.extend(
        [
            "",
            "## Execution Notes",
            "",
            "- Keep model/endpoint/seed policy fixed within each pair.",
            "- Swap only recovered content between clean and contaminated conditions.",
            "- Review all discordant pairs and all primary-violation hits.",
            "",
            "## Starter Budget Heuristic",
            "",
            "- Suggested seeds: 1-2",
            f"- Pairs in this pack: {meta['n_pairs']}",
            f"- Episodes per seed: {meta['n_condition_specific_instances']}",
            "",
        ]
    )
    packet_path.write_text("\n".join(lines), encoding="utf-8")


def write_sheet(sheet_path: Path, manifest: Dict[str, object]) -> None:
    rows: List[Dict[str, str]] = []
    for pair in manifest["pairs"]:
        for condition in ["clean", "contaminated"]:
            instance_key = f"{condition}_instance_id"
            rows.append(
                {
                    "run_id": f"{pair['pair_id']}__{condition}",
                    "pair_id": str(pair["pair_id"]),
                    "condition": condition,
                    "instance_id": str(pair[instance_key]),
                    "family_label": str(pair["family_label"]),
                    "trusted_target": str(pair["trusted_target"]),
                    "platform": "",
                    "model": "",
                    "seed": "",
                    "status": "pending",
                    "trajectory_path": "",
                    "manual_primary_label": "",
                    "manual_confidence": "",
                    "notes": "",
                }
            )

    with sheet_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "run_id",
                "pair_id",
                "condition",
                "instance_id",
                "family_label",
                "trusted_target",
                "platform",
                "model",
                "seed",
                "status",
                "trajectory_path",
                "manual_primary_label",
                "manual_confidence",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-file", type=Path, default=DEFAULT_TASK_FILE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--pair-ids", nargs="*", default=[])
    args = parser.parse_args()

    task_file = args.task_file
    if not task_file.is_absolute():
        task_file = ROOT / task_file

    out_dir = args.out_dir
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    artifact_dir = out_dir / "artifacts"
    out_manifest = out_dir / "paired_plan_manifest.json"
    out_packet = out_dir / "paired_execution_packet.md"
    out_sheet = out_dir / "paired_run_sheet.csv"

    rows = load_jsonl(task_file)
    pair_ids = {pair_id.strip() for pair_id in args.pair_ids if pair_id.strip()}
    rows = filter_rows(rows, pair_ids)
    grouped = validate_pairs(rows)

    out_dir.mkdir(parents=True, exist_ok=True)
    artifact_paths = write_artifacts(rows, ROOT, artifact_dir)
    manifest = make_manifest(rows, grouped, artifact_paths, task_file)
    out_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_packet(out_packet, manifest)
    write_sheet(out_sheet, manifest)

    print(json.dumps(manifest["meta"], ensure_ascii=True, indent=2))
    print(f"Saved manifest: {out_manifest}")
    print(f"Saved packet: {out_packet}")
    print(f"Saved sheet: {out_sheet}")


if __name__ == "__main__":
    main()
