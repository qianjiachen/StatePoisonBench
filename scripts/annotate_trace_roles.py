import json
from pathlib import Path


ROLE_MAP = {
    # OpenCode desktop/system logs: realism coverage only.
    "opencode_2026-03-31_00-05-14.json": {
        "trace_role": "coverage",
        "alignment_confidence": "medium",
        "alignment_notes": "system-level desktop log with real session metadata but weak action semantics",
    },
    "opencode_2026-03-30_20-29-10.json": {
        "trace_role": "coverage",
        "alignment_confidence": "medium",
        "alignment_notes": "system-level desktop log with real agent/model metadata",
    },
    # OpenCode state-store traces: coverage evidence.
    "opencode_state_10t43id.json": {
        "trace_role": "coverage",
        "alignment_confidence": "medium",
        "alignment_notes": "state-store trace with prompt-history and session metadata but weak tool/action semantics",
    },
    "opencode_state_yy44j4.json": {
        "trace_role": "coverage",
        "alignment_confidence": "medium",
        "alignment_notes": "state-store trace with session metadata and prompt-history",
    },
    # Current real Codex traces: coverage with some ambiguity.
    "codex_019d337a.json": {
        "trace_role": "coverage",
        "alignment_confidence": "high",
        "alignment_notes": "true action-level Codex trace, primarily useful as continuation/recovery workflow coverage rather than direct contamination positive",
    },
    "codex_019d3e5b.json": {
        "trace_role": "ambiguous",
        "alignment_confidence": "medium",
        "alignment_notes": "short real Codex trace with interrupted-turn semantics; useful for ambiguity analysis rather than direct positive scoring",
    },
}


SOURCES = {
    "/root/agent-safety-bench/artifacts/trajectories_opencode": "real_coverage",
    "/root/agent-safety-bench/artifacts/trajectories_opencode_state": "real_coverage",
    "/root/agent-safety-bench/artifacts/trajectories_codex_aligned": None,
}


def main() -> None:
    base = Path("/root/agent-safety-bench/artifacts/trajectories_v3")
    for src_dir, forced_role in SOURCES.items():
        src = Path(src_dir)
        if not src.exists():
            continue
        for path in src.glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            role_info = ROLE_MAP.get(path.name, {})
            if forced_role and "trace_role" not in role_info:
                role_info["trace_role"] = forced_role.replace("real_", "")
            trace_role = role_info.get("trace_role", "coverage")
            data["trace_role"] = trace_role
            data["alignment_confidence"] = role_info.get("alignment_confidence", "low")
            data["alignment_notes"] = role_info.get("alignment_notes", "auto-assigned during v3 migration")

            out_dir = base / f"real_{trace_role}"
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / path.name).write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding="utf-8")
            print(json.dumps({"file": path.name, "trace_role": trace_role}, ensure_ascii=True))


if __name__ == "__main__":
    main()
