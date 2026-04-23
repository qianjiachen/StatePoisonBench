"""
E13: Cross-provider API automatic-evaluator stress check.

Reads per-model real API pilot JSON artifacts (12 instances each), and writes:
- experiments/results/e13_cross_provider_api_auto_check.json
- experiments/results/e13_cross_provider_api_auto_check.md
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "experiments" / "results"

OUT_JSON = RESULTS_DIR / "e13_cross_provider_api_auto_check.json"
OUT_MD = RESULTS_DIR / "e13_cross_provider_api_auto_check.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def wilson_interval(k: int, n: int, z: float = 1.959963984540054) -> Tuple[float, float]:
    if n <= 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1.0 + (z * z) / n
    center = (p + (z * z) / (2 * n)) / denom
    half = (z / denom) * np.sqrt((p * (1 - p) / n) + ((z * z) / (4 * n * n)))
    lo = max(0.0, float(center - half))
    hi = min(1.0, float(center + half))
    return (lo, hi)


def find_single_json(run_dir: Path) -> Path:
    pilot_files = [p for p in run_dir.glob("real_api_pilot_*.json") if p.is_file()]
    if pilot_files:
        return max(pilot_files, key=lambda p: p.stat().st_mtime)
    files = [p for p in run_dir.glob("*.json") if p.is_file()]
    if not files:
        raise FileNotFoundError(f"no json file under {run_dir}")
    return max(files, key=lambda p: p.stat().st_mtime)


def load_model_payload(run_dir: Path) -> Dict[str, object]:
    path = find_single_json(run_dir)
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> Dict[str, object]:
    sources = {
        "claude_haiku": RESULTS_DIR / "real_api_pilot_claude_haiku_4_5_20251001_12inst",
        "claude_sonnet": RESULTS_DIR / "real_api_pilot_claude_sonnet_4_5_20250929_12inst",
        "deepseek_v32": RESULTS_DIR / "real_api_pilot_deepseek_v3_2_12inst",
        "gemini_flash": RESULTS_DIR / "real_api_pilot_gemini_2_5_flash_12inst",
    }

    rows: Dict[str, object] = {}
    deltas: List[float] = []
    non_worsening = 0

    for alias, run_dir in sources.items():
        payload = load_model_payload(run_dir)
        model = payload["meta"]["model"]  # type: ignore[index]
        n_instances = int(payload["meta"]["n_instances"])  # type: ignore[index]
        vanilla = payload["summary"]["vanilla"]  # type: ignore[index]
        rtg = payload["summary"]["rtg"]  # type: ignore[index]
        v_vio = float(vanilla["violation_rate"])
        r_vio = float(rtg["violation_rate"])
        v_succ = float(vanilla["safe_task_success_rate"])
        r_succ = float(rtg["safe_task_success_rate"])
        delta = r_vio - v_vio
        direction_non_worsening = bool(r_vio <= v_vio)
        non_worsening += int(direction_non_worsening)
        deltas.append(delta)

        rows[alias] = {
            "model": model,
            "n_instances": n_instances,
            "vanilla_violation_rate": round(v_vio, 3),
            "rtg_violation_rate": round(r_vio, 3),
            "violation_delta_rtg_minus_vanilla": round(delta, 3),
            "vanilla_safe_task_success_rate": round(v_succ, 3),
            "rtg_safe_task_success_rate": round(r_succ, 3),
            "direction_non_worsening": direction_non_worsening,
            "source_file": str(find_single_json(run_dir).relative_to(ROOT)).replace("\\", "/"),
        }

    n_models = len(rows)
    lo, hi = wilson_interval(non_worsening, n_models)
    summary = {
        "n_models": n_models,
        "direction_non_worsening": {
            "k": non_worsening,
            "n": n_models,
            "rate": round(non_worsening / n_models, 3),
            "wilson_ci95": [round(lo, 3), round(hi, 3)],
        },
        "effect_range": {
            "min": round(float(np.min(np.array(deltas, dtype=float))), 3),
            "max": round(float(np.max(np.array(deltas, dtype=float))), 3),
        },
        "mean_delta_rtg_minus_vanilla": round(float(np.mean(np.array(deltas, dtype=float))), 3),
    }

    return {
        "meta": {
            "experiment_id": "E13",
            "name": "Cross-Provider API Auto-Evaluator Stress Check",
            "generated_at_utc": now_iso(),
            "note": (
                "This stress check uses the automatic trajectory-aware evaluator only. "
                "Given known refusal-negation over-flagging, use it as directional evidence "
                "rather than clear-failure prevalence."
            ),
        },
        "models": rows,
        "summary": summary,
    }


def render_md(payload: Dict[str, object]) -> str:
    lines: List[str] = []
    lines.append("# E13 Cross-Provider API Auto-Evaluator Stress Check")
    lines.append("")
    lines.append(f"Generated at: {payload['meta']['generated_at_utc']}")
    lines.append("")
    lines.append(payload["meta"]["note"])
    lines.append("")
    lines.append("| Model | Vanilla Viol. | RTG Viol. | Delta (RTG-Vanilla) | Vanilla Success | RTG Success | Non-worsening |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    ordered = ["claude_haiku", "claude_sonnet", "deepseek_v32", "gemini_flash"]
    for key in ordered:
        row = payload["models"][key]
        lines.append(
            f"| {row['model']} | {row['vanilla_violation_rate']:.3f} | {row['rtg_violation_rate']:.3f} | "
            f"{row['violation_delta_rtg_minus_vanilla']:.3f} | {row['vanilla_safe_task_success_rate']:.3f} | "
            f"{row['rtg_safe_task_success_rate']:.3f} | {str(row['direction_non_worsening'])} |"
        )
    lines.append("")
    s = payload["summary"]
    d = s["direction_non_worsening"]
    lines.append(
        f"- Direction non-worsening: {d['k']}/{d['n']} = {d['rate']:.3f}, Wilson 95% CI [{d['wilson_ci95'][0]:.3f}, {d['wilson_ci95'][1]:.3f}]"
    )
    lines.append(
        f"- Effect range (RTG-Vanilla): [{s['effect_range']['min']:.3f}, {s['effect_range']['max']:.3f}]"
    )
    lines.append(f"- Mean delta (RTG-Vanilla): {s['mean_delta_rtg_minus_vanilla']:.3f}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    payload = build()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(f"[OK] wrote {OUT_JSON}")
    print(f"[OK] wrote {OUT_MD}")


if __name__ == "__main__":
    main()
