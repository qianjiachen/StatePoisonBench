import argparse
import json
import re
from pathlib import Path


LINE_RE = re.compile(r"^(?P<ts>\S+)\s+INFO\s+(?P<src>[^:]+):\s*(?P<msg>.*)$")
SESSION_RE = re.compile(r"sessionID=(?P<session>\S+)")
AGENT_RE = re.compile(r"agent=(?P<agent>\S+)")
MODEL_RE = re.compile(r"modelID=(?P<model>\S+)")


def normalize_kind(message: str) -> str:
    lowered = message.lower()
    if "server ready" in lowered or "restored" in lowered or "loading done" in lowered:
        return "state_restore"
    if "error" in lowered:
        return "tool_result"
    if "spawning sidecar" in lowered or "server listening" in lowered:
        return "tool_call"
    return "message"


def infer_tags(message: str) -> list[str]:
    lowered = message.lower()
    tags = set()
    if any(term in lowered for term in ["loading done", "server ready", "restored"]):
        tags.update(["resume", "recovery"])
    if "providermodelnotfounderror" in lowered or "ai_apicallerror" in lowered:
        tags.add("llm_error")
    if "session.processor error=aborted process" in lowered:
        tags.add("session_abort")
    if "modelid=" in lowered:
        tags.add("llm_request")
    return sorted(tags)


def infer_high_risk(kind: str, tags: list[str], message: str) -> bool:
    lowered = message.lower()
    if kind == "state_restore":
        return True
    if "session_abort" in tags or "llm_error" in tags:
        return True
    if "providermodelnotfounderror" in lowered:
        return True
    return False


def parse_log(path: Path) -> tuple[list[dict], dict]:
    steps = []
    session_ids = []
    agents = []
    models = []

    for idx, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        match = LINE_RE.match(line)
        if not match:
            continue

        message = match.group("msg")
        kind = normalize_kind(message)
        tags = infer_tags(message)
        high_risk = infer_high_risk(kind, tags, message)

        session_match = SESSION_RE.search(message)
        agent_match = AGENT_RE.search(message)
        model_match = MODEL_RE.search(message)

        if session_match:
            session_ids.append(session_match.group("session"))
        if agent_match:
            agents.append(agent_match.group("agent"))
        if model_match:
            models.append(model_match.group("model"))

        steps.append(
            {
                "step_id": len(steps) + 1,
                "kind": kind,
                "target": match.group("src"),
                "content": message,
                "high_risk": high_risk,
                "tags": tags,
                "timestamp": match.group("ts"),
            }
        )

    metadata = {
        "session_ids": sorted(set(session_ids)),
        "agents": sorted(set(agents)),
        "models": sorted(set(models)),
    }
    return steps, metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_log", type=Path)
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--defense-mode", default="vanilla")
    parser.add_argument("--agent-id", default="opencode_desktop")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    steps, metadata = parse_log(args.input_log)
    trajectory = {
        "trajectory_id": args.input_log.stem,
        "instance_id": args.instance_id,
        "defense_mode": args.defense_mode,
        "agent_id": args.agent_id,
        "run_metadata": {
            "source": "opencode_desktop_log",
            "notes": str(args.input_log),
            "session_ids": metadata["session_ids"],
            "agents": metadata["agents"],
            "models": metadata["models"],
        },
        "steps": steps,
        "outcome": {
            "task_completed": False,
            "artifacts_written": [],
            "final_summary": "trajectory extracted from OpenCode desktop log",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(trajectory, ensure_ascii=True, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "trajectory_id": trajectory["trajectory_id"],
                "steps": len(steps),
                "session_ids": metadata["session_ids"],
                "agents": metadata["agents"],
                "models": metadata["models"],
            },
            ensure_ascii=True,
        )
    )


if __name__ == "__main__":
    main()
