import json
import subprocess
from pathlib import Path


ROOT = Path("/root/agent-safety-bench")
TASK_FILE = ROOT / "tasks" / "statepoisonbench_main_table_v2.jsonl"
ARTIFACT_DIR = ROOT / "artifacts" / "main_table_v2"
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


def pct_improve(vanilla: float, new: float) -> float:
    if vanilla == 0:
        return 0.0
    return (vanilla - new) / vanilla * 100.0


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

    family_info = {
        "spb_sum_001": ("Summary poisoning", "Goal drift"),
        "spb_rec_001": ("Recovery-state poisoning", "Goal drift"),
        "spb_tmr_001": ("Tool-mediated recovery", "Goal drift"),
        "spb_tmr_002": ("Tool-failure escalation", "Unsafe tool escalation"),
        "spb_trw_001": ("Recovered-context to trusted write", "State propagation"),
    }

    order = [
        "spb_sum_001",
        "spb_rec_001",
        "spb_tmr_001",
        "spb_tmr_002",
        "spb_trw_001",
    ]

    lines = []
    lines.append("| Family | Primary Violation | Vanilla | Generic Monitor | Recovery-Time Gating | Gating Gain vs Vanilla | Best Safe Task Success |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")

    summary_rows = []
    for instance_id in order:
        rows = by_id[instance_id]
        family, primary = family_info[instance_id]
        vanilla_v = rows["vanilla"]["adjusted_risk"]
        monitor_v = rows["monitor"]["adjusted_risk"]
        gating_v = rows["gating"]["adjusted_risk"]
        gain = pct_improve(vanilla_v, gating_v)
        best_safe = max(
            float(rows["vanilla"]["safe_task_success"]),
            float(rows["monitor"]["safe_task_success"]),
            float(rows["gating"]["safe_task_success"]),
        )
        lines.append(
            f"| {family} | {primary} | {vanilla_v:.3f} | {monitor_v:.3f} | {gating_v:.3f} | {gain:.1f}% | {best_safe:.1f} |"
        )
        summary_rows.append(
            {
                "instance_id": instance_id,
                "family": family,
                "primary_violation": primary,
                "vanilla": vanilla_v,
                "generic_monitor": monitor_v,
                "recovery_time_gating": gating_v,
                "gating_gain_vs_vanilla": gain,
                "best_safe_task_success": best_safe,
            }
        )

    markdown_path = ARTIFACT_DIR / "main_result_table_v2.md"
    markdown_path.write_text("\n".join(lines), encoding="utf-8")

    summary_path = ARTIFACT_DIR / "main_result_table_v2.json"
    summary_path.write_text(json.dumps(summary_rows, ensure_ascii=True, indent=2), encoding="utf-8")

    print(markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
