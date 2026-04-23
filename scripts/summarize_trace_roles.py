import json
from pathlib import Path


def main() -> None:
    base = Path("/root/agent-safety-bench/artifacts/trajectories_v3")
    summary = {}
    for role_dir in base.glob("real_*"):
        role = role_dir.name.replace("real_", "")
        files = sorted(role_dir.glob("*.json"))
        summary[role] = {
            "count": len(files),
            "files": [f.name for f in files],
        }
    print(json.dumps(summary, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
