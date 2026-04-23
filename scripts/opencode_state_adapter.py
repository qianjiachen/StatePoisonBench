import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))


def parse_nested_json(value: str):
    if not isinstance(value, str):
        return value
    value = value.strip()
    if not value:
        return value
    if value[0] not in "[{":
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def build_steps(global_data: dict, workspace_data: dict) -> tuple[list[dict], dict]:
    steps = []

    prompt_history = parse_nested_json(global_data.get("prompt-history", "{}"))
    if isinstance(prompt_history, dict):
        for entry in prompt_history.get("entries", [])[-20:]:
            prompt_items = entry.get("prompt", [])
            text = " ".join(item.get("content", "") for item in prompt_items if item.get("type") == "text")
            if text:
                steps.append(
                    {
                        "step_id": len(steps) + 1,
                        "kind": "message",
                        "target": "prompt-history",
                        "content": text,
                        "high_risk": False,
                        "tags": ["prompt_history"],
                    }
                )

    model_selection = parse_nested_json(workspace_data.get("workspace:model-selection", "{}"))
    session_meta = model_selection.get("session", {}) if isinstance(model_selection, dict) else {}
    for session_id, meta in session_meta.items():
        content = json.dumps({"session_id": session_id, "agent": meta.get("agent"), "model": meta.get("model")}, ensure_ascii=True)
        steps.append(
            {
                "step_id": len(steps) + 1,
                "kind": "state_restore",
                "target": "workspace:model-selection",
                "content": content,
                "high_risk": True,
                "tags": ["resume", "recovery", "session_state"],
            }
        )

    followup = parse_nested_json(workspace_data.get("workspace:followup", "{}"))
    if isinstance(followup, dict):
        paused = followup.get("paused", {})
        if paused:
            steps.append(
                {
                    "step_id": len(steps) + 1,
                    "kind": "decision",
                    "target": "workspace:followup",
                    "content": json.dumps({"paused": paused}, ensure_ascii=True),
                    "high_risk": True,
                    "tags": ["followup_state", "session_pause"],
                }
            )

    for key, raw in workspace_data.items():
        if not key.startswith("session:") or not key.endswith(":prompt"):
            continue
        nested = parse_nested_json(raw)
        if not isinstance(nested, dict):
            continue
        prompt_items = nested.get("prompt", [])
        text = " ".join(item.get("content", "") for item in prompt_items if item.get("type") == "text")
        steps.append(
            {
                "step_id": len(steps) + 1,
                "kind": "read",
                "target": key,
                "content": text,
                "high_risk": False,
                "tags": ["session_prompt"],
            }
        )

    metadata = {
        "session_ids": sorted(session_meta.keys()),
        "agents": sorted({meta.get("agent", "unknown") for meta in session_meta.values()}),
        "models": sorted(
            {
                (meta.get("model") or {}).get("modelID", "unknown")
                for meta in session_meta.values()
            }
        ),
    }
    return steps, metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("global_dat", type=Path)
    parser.add_argument("workspace_dat", type=Path)
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--defense-mode", default="vanilla")
    parser.add_argument("--agent-id", default="opencode_state_store")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    global_data = load_json(args.global_dat)
    workspace_data = load_json(args.workspace_dat)
    steps, metadata = build_steps(global_data, workspace_data)

    trajectory = {
        "trajectory_id": f"{args.workspace_dat.stem}_state",
        "instance_id": args.instance_id,
        "defense_mode": args.defense_mode,
        "agent_id": args.agent_id,
        "run_metadata": {
            "source": "opencode_state_dat",
            "global_dat": str(args.global_dat),
            "workspace_dat": str(args.workspace_dat),
            "session_ids": metadata["session_ids"],
            "agents": metadata["agents"],
            "models": metadata["models"],
        },
        "steps": steps,
        "outcome": {
            "task_completed": False,
            "artifacts_written": [],
            "final_summary": "trajectory extracted from OpenCode state dat files",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(trajectory, ensure_ascii=True, indent=2), encoding="utf-8")
    print(json.dumps({"trajectory_id": trajectory["trajectory_id"], "steps": len(steps), "session_ids": metadata["session_ids"], "agents": metadata["agents"], "models": metadata["models"]}, ensure_ascii=True))


if __name__ == "__main__":
    main()
