import json
from pathlib import Path


def main() -> None:
    path = Path("/root/agent-safety-bench/tasks/statepoisonbench_v1.jsonl")
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    required = [
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
    missing = {}
    for row in rows:
        miss = [key for key in required if key not in row]
        if miss:
            missing[row.get("instance_id", "unknown")] = miss

    print(
        json.dumps(
            {
                "count": len(rows),
                "ids": [row["instance_id"] for row in rows],
                "missing": missing,
            },
            ensure_ascii=True,
        )
    )


if __name__ == "__main__":
    main()
