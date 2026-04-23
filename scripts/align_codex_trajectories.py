import json
from pathlib import Path


ALIGNMENT = {
    # Long continuation/recovery-heavy real trace.
    "rollout-2026-03-28T16-06-08-019d337a-a32d-7901-8487-3c130851ff15": "spb_ses_001",
    # Short interrupted / greeting-style trace with turn abort semantics.
    "rollout-2026-03-30T18-48-19-019d3e5b-d6d4-7b32-9c31-51eac5102b73": "spb_int_001",
}


def main() -> None:
    src = Path("/root/agent-safety-bench/artifacts/trajectories_codex")
    dst = Path("/root/agent-safety-bench/artifacts/trajectories_codex_aligned")
    dst.mkdir(parents=True, exist_ok=True)

    for path in src.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        new_id = ALIGNMENT.get(data.get("trajectory_id"))
        if not new_id:
            continue
        data["instance_id"] = new_id
        (dst / path.name).write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding="utf-8")
        print(json.dumps({"trajectory": path.name, "instance_id": new_id}, ensure_ascii=True))


if __name__ == "__main__":
    main()
