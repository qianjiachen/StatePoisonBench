import json
import subprocess
from pathlib import Path


ROOT = Path("/root/agent-safety-bench")
TASK_FILE = ROOT / "tasks" / "statepoisonbench_main_table.jsonl"
ARTIFACT_DIR = ROOT / "artifacts" / "main_table"
SCRIPT = ROOT / "scripts" / "statepoisonbench_evaluator.py"


def run_eval(mode: str) -> Path:
    output = ARTIFACT_DIR / f"{mode}.json"
    cmd = [
        str(ROOT / ".venv" / "bin" / "python"),
        str(SCRIPT),
        str(TASK_FILE),
        "--defense-mode",
        mode,
        "--output",
        str(output),
    ]
    subprocess.run(cmd, check=True)
    return output


def load_results(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    vanilla = load_results(run_eval("vanilla"))
    monitor = load_results(run_eval("generic_monitor"))
    gating = load_results(run_eval("recovery_time_gating"))

    by_id = {}
    for payload, mode_key in [
        (vanilla, "vanilla"),
        (monitor, "monitor"),
        (gating, "gating"),
    ]:
        for row in payload["results"]:
            by_id.setdefault(row["instance_id"], {})[mode_key] = row

    family_names = {
        "spb_sum_001": "Summary poisoning",
        "spb_rec_001": "Recovery-state poisoning",
        "spb_tmr_001": "Tool-mediated recovery",
        "spb_trw_001": "Recovered-context to trusted write",
    }

    lines = []
    lines.append("| Family | Vanilla | Generic Monitor | Recovery-Time Gating | Best Safe Task Success |")
    lines.append("| --- | --- | --- | --- | --- |")

    summary_rows = []
    for instance_id in ["spb_sum_001", "spb_rec_001", "spb_tmr_001", "spb_trw_001"]:
        rows = by_id[instance_id]
        family = family_names[instance_id]
        vanilla_v = rows["vanilla"]["adjusted_risk"]
        monitor_v = rows["monitor"]["adjusted_risk"]
        gating_v = rows["gating"]["adjusted_risk"]
        best_safe = max(
            float(rows["vanilla"]["safe_task_success"]),
            float(rows["monitor"]["safe_task_success"]),
            float(rows["gating"]["safe_task_success"]),
        )
        lines.append(f"| {family} | {vanilla_v:.3f} | {monitor_v:.3f} | {gating_v:.3f} | {best_safe:.1f} |")
        summary_rows.append(
            {
                "instance_id": instance_id,
                "family": family,
                "vanilla": vanilla_v,
                "generic_monitor": monitor_v,
                "recovery_time_gating": gating_v,
                "best_safe_task_success": best_safe,
            }
        )

    markdown_path = ARTIFACT_DIR / "main_result_table.md"
    markdown_path.write_text("\n".join(lines), encoding="utf-8")

    summary_path = ARTIFACT_DIR / "main_result_table.json"
    summary_path.write_text(json.dumps(summary_rows, ensure_ascii=True, indent=2), encoding="utf-8")

    print(markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
