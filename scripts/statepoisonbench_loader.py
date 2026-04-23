import argparse
import json
from pathlib import Path


REQUIRED_KEYS = [
    "instance_id",
    "title",
    "task_family",
    "task_goal",
    "authorization_boundary",
    "state_artifact",
    "poisoning",
    "trigger",
    "expected_behavior",
    "labels",
    "evaluation",
]


def load_instances(path: Path) -> list[dict]:
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {line_no}: {exc}") from exc
        rows.append(row)
    return rows


def validate_instances(rows: list[dict]) -> dict:
    missing = {}
    duplicate_ids = []
    seen = set()

    for row in rows:
        row_id = row.get("instance_id", "unknown")
        miss = [key for key in REQUIRED_KEYS if key not in row]
        if miss:
            missing[row_id] = miss
        if row_id in seen:
            duplicate_ids.append(row_id)
        seen.add(row_id)

    return {
        "count": len(rows),
        "missing": missing,
        "duplicate_ids": duplicate_ids,
        "ids": [row.get("instance_id", "unknown") for row in rows],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_file", type=Path)
    args = parser.parse_args()

    rows = load_instances(args.task_file)
    report = validate_instances(rows)
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
