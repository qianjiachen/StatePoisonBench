import argparse
import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def normalize_event(row: dict, step_id: int) -> dict | None:
    row_type = row.get("type")
    payload = row.get("payload", {})
    content = ""
    target = ""
    tags = []
    high_risk = False
    kind = "message"

    if row_type == "session_meta":
        kind = "state_restore"
        content = json.dumps(
            {
                "cwd": payload.get("cwd"),
                "originator": payload.get("originator"),
                "model_provider": payload.get("model_provider"),
            },
            ensure_ascii=True,
        )
        target = "session_meta"
        tags = ["resume", "recovery", "session_meta"]
        high_risk = True
    elif row_type == "turn_context":
        kind = "state_restore"
        content = json.dumps(
            {
                "cwd": payload.get("cwd"),
                "model": payload.get("model"),
                "approval_policy": payload.get("approval_policy"),
                "sandbox_policy": payload.get("sandbox_policy"),
            },
            ensure_ascii=True,
        )
        target = "turn_context"
        tags = ["resume", "turn_context"]
        high_risk = True
    elif row_type == "event_msg":
        event_type = payload.get("type", "event_msg")
        if event_type == "user_message":
            kind = "message"
            content = payload.get("message", "")
            target = "user_message"
            tags = ["user_message"]
        elif event_type == "turn_aborted":
            kind = "decision"
            content = json.dumps(payload, ensure_ascii=True)
            target = "turn_aborted"
            tags = ["turn_aborted", "session_abort"]
            high_risk = True
        elif event_type == "task_started":
            kind = "decision"
            content = json.dumps(payload, ensure_ascii=True)
            target = "task_started"
            tags = ["task_started"]
        else:
            kind = "message"
            content = json.dumps(payload, ensure_ascii=True)
            target = event_type
            tags = ["event_msg"]
    elif row_type == "response_item":
        payload_type = payload.get("type")
        if payload_type == "message":
            role = payload.get("role", "unknown")
            text_parts = []
            for item in payload.get("content", []):
                text = item.get("text") or item.get("content") or item.get("output_text") or ""
                if text:
                    text_parts.append(text)
            kind = "message"
            content = " ".join(text_parts)
            target = role
            tags = [f"role:{role}"]
        elif payload_type == "function_call":
            kind = "tool_call"
            target = payload.get("name", "unknown_tool")
            content = payload.get("arguments", "")
            tags = ["tool_use"]
            high_risk = True
        elif payload_type == "function_call_output":
            kind = "tool_result"
            target = payload.get("call_id", "tool_result")
            content = payload.get("output", "")
            tags = ["tool_result"]
        elif payload_type == "custom_tool_call":
            kind = "tool_call"
            target = payload.get("name", "custom_tool")
            content = payload.get("input", "")
            tags = ["custom_tool_use"]
            high_risk = True
        elif payload_type == "custom_tool_call_output":
            kind = "tool_result"
            target = payload.get("call_id", "custom_tool_result")
            content = payload.get("output", "")
            tags = ["custom_tool_result"]
        elif payload_type == "reasoning":
            kind = "reasoning"
            content = payload.get("content") or json.dumps({"summary": payload.get("summary")}, ensure_ascii=True)
            target = "reasoning"
            tags = ["reasoning"]
        else:
            kind = "message"
            content = json.dumps(payload, ensure_ascii=True)
            target = payload_type or "response_item"
            tags = ["response_item"]
    else:
        return None

    return {
        "step_id": step_id,
        "kind": kind,
        "target": target,
        "content": content,
        "high_risk": high_risk,
        "tags": tags,
        "timestamp": row.get("timestamp"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("session_file", type=Path)
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--defense-mode", default="vanilla")
    parser.add_argument("--agent-id", default="codex_desktop")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = load_jsonl(args.session_file)
    steps = []
    session_id = None
    model = None
    cwd = None
    for row in rows:
        if row.get("type") == "session_meta":
            session_id = row.get("payload", {}).get("id")
            cwd = row.get("payload", {}).get("cwd")
        if row.get("type") == "turn_context" and model is None:
            model = row.get("payload", {}).get("model")

        step = normalize_event(row, len(steps) + 1)
        if step is not None:
            steps.append(step)

    trajectory = {
        "trajectory_id": args.session_file.stem,
        "instance_id": args.instance_id,
        "defense_mode": args.defense_mode,
        "agent_id": args.agent_id,
        "run_metadata": {
            "source": "codex_session_jsonl",
            "session_id": session_id,
            "cwd": cwd,
            "model": model,
            "session_file": str(args.session_file),
        },
        "steps": steps,
        "outcome": {
            "task_completed": False,
            "artifacts_written": [s["target"] for s in steps if s["kind"] == "tool_call" and s["target"] == "apply_patch"],
            "final_summary": "trajectory extracted from Codex session jsonl",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(trajectory, ensure_ascii=True, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "trajectory_id": trajectory["trajectory_id"],
                "session_id": session_id,
                "steps": len(steps),
                "model": model,
                "cwd": cwd,
            },
            ensure_ascii=True,
        )
    )


if __name__ == "__main__":
    main()
